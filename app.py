"""
🏛️ JIRA AI REPORT GENERATOR - ENTERPRISE READY (FIXED)
═══════════════════════════════════════════════════════════════════════════════════
Version: 2.6.0 - All Requirements Met
"""

# 1. IMPORTS
import streamlit as st
from atlassian import Jira
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from io import BytesIO

# Optional PDF support
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Optional Excel support
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# 2. UTILITY FUNCTIONS
def build_jql(spaces=None, labels=None, time_period=None, time_field='created'):
    """Build JQL with proper quoting (no ORDER BY - handled by jql() method)"""
    jql_parts = []
    if spaces:
        space_list = [s.strip().strip("'\"") for s in spaces.split(',')]
        quoted_projects = [f'"{p}"' if ' ' in p else p for p in space_list]
        if len(space_list) == 1:
            jql_parts.append(f'project = {quoted_projects[0]}')
        else:
            jql_parts.append(f'project in ({", ".join(quoted_projects)})')
    if labels:
        label_list = [f'"{label.strip()}"' for label in labels.split(',')]
        jql_parts.append(f'labels IN ({", ".join(label_list)})')
    if time_period:
        if time_period == 'last_week':
            start_date = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
            jql_parts.append(f'{time_field} >= {start_date}')
        elif time_period == 'last_month':
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            jql_parts.append(f'{time_field} >= {start_date}')
        elif ' to ' in time_period:
            start, end = time_period.split(' to ')
            jql_parts.append(f'{time_field} >= {start} AND {time_field} <= {end}')
    return ' AND '.join(jql_parts) if jql_parts else 'project IS NOT EMPTY'

def get_next_period_dates(current_period):
    if current_period == 'last_week':
        end_date = datetime.now()
        next_start = end_date
        next_end = end_date + timedelta(weeks=1)
    elif current_period == 'last_month':
        end_date = datetime.now()
        next_start = end_date
        next_end = end_date + timedelta(days=30)
    elif ' to ' in current_period:
        start, end = current_period.split(' to ')
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        next_start = end_date
        next_end = end_date + (end_date - start_date)
    else:
        raise ValueError("Invalid period")
    return f"{next_start.strftime('%Y-%m-%d')} to {next_end.strftime('%Y-%m-%d')}"

# SAVE/LOAD PRESETS
def save_criteria(preset_name, criteria):
    presets_file = "jira_presets.json"
    try:
        if os.path.exists(presets_file):
            with open(presets_file, 'r') as f:
                presets = json.load(f)
        else:
            presets = {}
        presets[preset_name] = criteria
        with open(presets_file, 'w') as f:
            json.dump(presets, f, indent=2)
        st.success(f"✅ Saved: {preset_name}")
        return True
    except Exception as e:
        st.error(f"❌ Save failed: {e}")
        return False

def load_criteria(preset_name):
    presets_file = "jira_presets.json"
    if not os.path.exists(presets_file):
        return None
    try:
        with open(presets_file, 'r') as f:
            presets = json.load(f)
        return presets.get(preset_name)
    except:
        return None

def get_all_presets():
    presets_file = "jira_presets.json"
    if not os.path.exists(presets_file):
        return []
    with open(presets_file, 'r') as f:
        presets = json.load(f)
    return list(presets.keys())

def delete_preset(preset_name):
    presets_file = "jira_presets.json"
    try:
        if not os.path.exists(presets_file):
            return
        with open(presets_file, 'r') as f:
            presets = json.load(f)
        if preset_name in presets:
            del presets[preset_name]
            with open(presets_file, 'w') as f:
                json.dump(presets, f, indent=2)
            st.success(f"✅ Deleted: {preset_name}")
    except Exception as e:
        st.error(f"❌ Delete failed: {e}")

# 3. FETCH ISSUES (ENHANCED DEBUG)
def fetch_issues(jira, jql, debug=False):
    issues = []
    max_results = 50
    start_at = 0
    
    while True:
        try:
            result = jira.jql(jql, start=start_at, limit=max_results)
            
            if debug:
                st.json({
                    "total": result.get('total', 0),
                    "maxResults": result.get('maxResults', 0),
                    "startAt": result.get('startAt', 0),
                    "issues_count": len(result.get('issues', []))
                })
            
            batch = result.get('issues', [])
            
            if not batch:
                break
                
            issues.extend(batch)
            total = result.get('total', 0)
            
            if len(issues) >= total or len(batch) < max_results:
                break
                
            start_at += max_results
            
        except Exception as e:
            st.error(f"❌ Error fetching issues: {e}")
            import traceback
            st.code(traceback.format_exc())
            break
    
    return issues

# 4. FETCH EPIC DETAILS
def get_epic_context(jira, epic_key):
    """Fetch epic summary and description for context"""
    try:
        issue = jira.issue(epic_key)
        fields = issue.get('fields', {})
        return {
            'summary': fields.get('summary') or 'No summary available',
            'description': fields.get('description') or 'No description available'
        }
    except:
        return {'summary': 'Unable to fetch epic', 'description': ''}

# 5. EXPORT TO PDF
def export_to_pdf(report_text, initiative_name):
    if not PDF_AVAILABLE:
        raise ImportError("reportlab not installed. Run: pip install reportlab")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph(f"<b>{initiative_name} - Status Report</b>", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Content
    for line in report_text.split('\n'):
        if line.strip():
            story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 6))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# 6. EXPORT TO EXCEL
def export_to_excel(df, next_df, report_text):
    if not EXCEL_AVAILABLE:
        raise ImportError("openpyxl not installed. Run: pip install openpyxl")
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Current Issues', index=False)
        next_df.to_excel(writer, sheet_name='Next Steps', index=False)
        
        # Context sheet
        context_df = pd.DataFrame({'Report': [report_text]})
        context_df.to_excel(writer, sheet_name='Full Report', index=False)
    
    buffer.seek(0)
    return buffer

# 7. LLM INTEGRATION (FIXED)
def get_llm_summary(llm_provider, api_key, prompt):
    """Get AI summary from selected provider"""
    try:
        if llm_provider.lower() == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            return response.choices[0].message.content
        
        elif llm_provider.lower() == "xai":
            import requests
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "grok-beta",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300
                }
            )
            return response.json()['choices'][0]['message']['content']
        
        elif llm_provider.lower() == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        
        return ""
    except Exception as e:
        return f"AI summary error: {str(e)}"

# 8. REPORT GENERATOR (ENHANCED)
def generate_report(issues, persona, llm_provider, api_key, initiative_name, current_period, jira_client, spaces, labels):
    if not issues:
        return f"❌ No issues found for {initiative_name}."
    
    data = []
    issues_dict = {}
    for issue in issues:
        fields = issue.get('fields', {})
        key = issue.get('key')
        parent_key = fields.get('parent', {}).get('key') if fields.get('parent') else None
        subtasks_keys = [sub.get('key') for sub in fields.get('subtasks', [])]
        issues_dict[key] = {
            'Key': key,
            'Summary': fields.get('summary', 'N/A'),
            'Description': fields.get('description', ''),
            'Status': fields.get('status', {}).get('name', 'N/A') if fields.get('status') else 'N/A',
            'Assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
            'Priority': fields.get('priority', {}).get('name', 'N/A') if fields.get('priority') else 'N/A',
            'Due Date': fields.get('duedate'),
            'Created': fields.get('created'),
            'Updated': fields.get('updated'),
            'Resolved': fields.get('resolutiondate'),
            'Parent': parent_key,
            'Subtasks': subtasks_keys
        }
        data.append(issues_dict[key])
    
    df = pd.DataFrame(data)
    achieved_df = df[df['Status'] == 'Done']
    achieved_keys = achieved_df['Key'].tolist()
    
    # Get epic context
    roots = [key for key in achieved_keys if issues_dict[key]['Parent'] is None or issues_dict[key]['Parent'] not in achieved_keys]
    epic_key = roots[0] if roots else None
    
    if epic_key:
        epic_data = get_epic_context(jira_client, epic_key)
        summary = epic_data.get('summary') or ''
        description = epic_data.get('description') or ''
        overview = f"{summary[:100]}. {description[:150]}"[:200].strip()
    else:
        overview = f"{initiative_name} initiative overview not available."
    
    # Prior progress (FIXED date comparison with timezone handling)
    from datetime import timezone
    
    if current_period in ['last_week', 'last_month']:
        period_end = datetime.now(timezone.utc)
    else:
        # Parse the end date from custom period and make it timezone-aware
        end_date_str = current_period.split(' to ')[1]
        period_end = datetime.strptime(end_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    prior_keys = []
    for k in achieved_keys:
        resolved_date = issues_dict[k].get('Resolved')
        if resolved_date:
            try:
                # Parse Jira datetime (already has timezone info)
                resolved_dt = datetime.fromisoformat(resolved_date.replace('Z', '+00:00'))
                if resolved_dt < period_end:
                    prior_keys.append(k)
            except:
                pass  # Skip if date parsing fails
    
    prior_summary = f"{len(prior_keys)} items completed prior to this period." if prior_keys else "No prior progress."
    
    # Build hierarchy
    def build_hierarchical_text(issues_dict, roots, indent=''):
        text = ''
        for key in roots:
            row = issues_dict.get(key, {})
            text += f"{indent}{key}: {row.get('Summary', 'N/A')}\n"
            subtasks = row.get('Subtasks', [])
            text += build_hierarchical_text(issues_dict, subtasks, indent + '  ')
        return text
    
    hierarchy_text = build_hierarchical_text(issues_dict, roots)
    
    # AI Summary
    achievements_summary = hierarchy_text
    if api_key and achieved_keys and llm_provider != "None":
        prompt = f"Summarize these completed Jira tickets for {persona}:\n{hierarchy_text}"
        ai_summary = get_llm_summary(llm_provider, api_key, prompt)
        achievements_summary += f"\n\n📖 AI SUMMARY:\n{ai_summary}"
    
    # Next steps
    next_period = get_next_period_dates(current_period)
    next_jql = build_jql(spaces, labels, next_period)
    next_issues = fetch_issues(jira_client, next_jql)
    next_df = pd.DataFrame([{
        'Key': i.get('key'),
        'Summary': i.get('fields', {}).get('summary', 'N/A'),
        'Status': i.get('fields', {}).get('status', {}).get('name', 'N/A') if i.get('fields', {}).get('status') else 'N/A',
        'Priority': (i.get('fields', {}).get('priority') or {}).get('name', 'N/A')
    } for i in next_issues])
    
    upcoming = next_df[next_df['Status'].isin(['To Do', 'In Progress'])]
    next_steps = "📋 **NEXT STEPS**: No tickets scheduled." if len(upcoming) == 0 else \
        f"📋 **NEXT STEPS** ({len(upcoming)} tickets):\n" + "\n".join(
            [f"• {row['Key']}: {row['Summary'][:50]}... ({row['Priority']})" for _, row in upcoming.head(5).iterrows()]
        )
    
    overdue_count = len(df[(df['Due Date'].notna()) & (df['Status'] != 'Done')])
    
    report = f"""
🏛️ **{initiative_name} - {persona.upper()} REPORT**

**1. CONTEXT**
{overview}
{prior_summary}

**2. COMPLETED THIS PERIOD**
{achievements_summary}

**3. METRICS**
Total: {len(df)} | Completed: {len(achieved_df)} ({len(achieved_df)/len(df)*100:.0f}%)
Overdue: {overdue_count}

**4. NEXT STEPS**
{next_steps}
"""
    
    return report, df, next_df

# 9. STREAMLIT UI (ENHANCED)
st.set_page_config(page_title="Jira AI Reports", page_icon="🚀", layout="wide")

# Initialize session state
if 'generated_report' not in st.session_state:
    st.session_state.generated_report = None
if 'generated_df' not in st.session_state:
    st.session_state.generated_df = None
if 'generated_next_df' not in st.session_state:
    st.session_state.generated_next_df = None

st.title("🚀 Jira AI Initiative Report Generator")
st.markdown("***4-Section Executive Reports | Multi-LLM | PDF/Excel Export***")

# Sidebar presets
st.sidebar.markdown("### 💾 PRESETS")
presets = get_all_presets()
selected_preset = st.sidebar.selectbox("Load Preset", ["None"] + presets)

col1, col2 = st.sidebar.columns(2)
with col1:
    preset_name = st.text_input("Save As", key="save_name")
with col2:
    if st.button("💾 Save"):
        criteria = {
            'initiative_name': st.session_state.get('initiative_name', ''),
            'url': st.session_state.get('url', ''),
            'email': st.session_state.get('email', ''),
            'spaces': st.session_state.get('spaces', ''),
            'labels': st.session_state.get('labels', ''),
            'llm_provider': st.session_state.get('llm_provider', 'OpenAI'),
            'persona': st.session_state.get('persona', 'Team Lead'),
            'period': st.session_state.get('period', 'last_week')
        }
        save_criteria(preset_name, criteria)

if st.sidebar.button("🗑 Delete Preset") and selected_preset != "None":
    delete_preset(selected_preset)

# Load preset
if selected_preset != "None":
    criteria = load_criteria(selected_preset)
    if criteria:
        for k, v in criteria.items():
            st.session_state[k] = v

# Main inputs
initiative_name = st.text_input("Initiative / Epic Name*", key="initiative_name")
url = st.text_input("Jira URL*", key="url", placeholder="https://yourcompany.atlassian.net")
email = st.text_input("Email*", key="email")
jira_token = st.text_input("Jira API Token*", type="password", key="jira_token")

# Add project discovery button
col1, col2 = st.columns([3, 1])
with col1:
    spaces = st.text_input("Jira Spaces* (comma-separated)", key="spaces", placeholder="PROJ1,PROJ2")
with col2:
    st.write("")  # spacing
    if st.button("🔍 Discover"):
        if url and email and jira_token:
            try:
                with st.spinner("Fetching projects..."):
                    temp_jira = Jira(url=url, username=email, password=jira_token, cloud=True)
                    
                    # Try getting user info first
                    try:
                        myself = temp_jira.myself()
                        st.success(f"✅ Authenticated as: {myself.get('displayName', 'Unknown')}")
                    except:
                        pass
                    
                    # Method 1: Get all projects via REST API directly
                    try:
                        st.info("Fetching all projects...")
                        # Use get method directly
                        response = temp_jira.get('rest/api/3/project/search')
                        if response and 'values' in response:
                            projects = response['values']
                            if projects:
                                project_info = {p['key']: p.get('name', 'Unknown') for p in projects}
                                st.success(f"✅ Found {len(project_info)} projects:")
                                st.code('\n'.join([f"{k}: {v}" for k, v in sorted(project_info.items())]))
                                st.info(f"💡 Copy one of these keys: **{', '.join(sorted(project_info.keys()))}**")
                            else:
                                st.warning("No projects returned from API")
                        else:
                            st.warning("Unexpected API response format")
                    except Exception as e1:
                        st.error(f"Direct API failed: {e1}")
                    
                    # Method 2: Try JQL without date filter
                    try:
                        st.info("Trying JQL query...")
                        result = temp_jira.jql('assignee = currentUser() OR reporter = currentUser()', limit=100)
                        total = result.get('total', 0)
                        st.info(f"Query returned {total} total issues")
                        
                        issues = result.get('issues', [])
                        if issues:
                            unique_projects = {}
                            for issue in issues:
                                proj = issue.get('fields', {}).get('project', {})
                                if proj:
                                    key = proj.get('key')
                                    name = proj.get('name', 'Unknown')
                                    unique_projects[key] = name
                            if unique_projects:
                                st.success(f"✅ Found {len(unique_projects)} projects from YOUR issues:")
                                st.code('\n'.join([f"{k}: {v}" for k, v in sorted(unique_projects.items())]))
                        else:
                            st.warning("You have no issues assigned or reported")
                            
                    except Exception as e2:
                        st.error(f"JQL query failed: {e2}")
                        
            except Exception as e:
                st.error(f"Connection failed: {e}")
                import traceback
                st.code(traceback.format_exc())
        else:
            st.warning("Fill Jira URL, Email, and Token first")

labels = st.text_input("Labels (optional)", key="labels")
persona = st.selectbox("Persona", ["Team Lead", "Manager", "Group Manager", "CTO"], key="persona")
llm_provider = st.selectbox("LLM Provider", ["OpenAI", "xAI", "Gemini", "None"], key="llm_provider")
llm_key = st.text_input("LLM API Key (if using AI)", type="password", key="llm_key")
period = st.selectbox("Period", ["last_week", "last_month", "Custom"], key="period")

if period == "Custom":
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    period = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

# Validate inputs
if st.button("📄 Generate Report"):
    if not all([initiative_name, url, email, jira_token, spaces]):
        st.error("❌ Please fill all required fields marked with *")
    else:
        try:
            # Step 1: Create connection
            with st.spinner("Connecting to Jira..."):
                st.info(f"🔗 Attempting connection to: {url}")
                st.info(f"👤 Using email: {email}")
                jira_client = Jira(url=url, username=email, password=jira_token, cloud=True)
                st.success("✅ Jira client object created")
            
            # Step 2: Verify authentication
            with st.spinner("Authenticating..."):
                try:
                    myself = jira_client.myself()
                    st.success(f"✅ AUTHENTICATED as: {myself.get('displayName')} ({myself.get('emailAddress')})")
                    st.info(f"Account ID: {myself.get('accountId')}")
                except Exception as auth_error:
                    st.error(f"❌ Authentication failed: {auth_error}")
                    st.warning("Check your API token at: https://id.atlassian.com/manage-profile/security/api-tokens")
                    st.stop()
            
            # Step 3: Test project access
            st.info("🔌 Testing project access...")
            try:
                # Try the user's exact project directly
                project_key = spaces.split(',')[0].strip().strip("'\"")
                test_jql = f"project = {project_key}"
                st.info(f"Testing: {test_jql}")
                test_result = jira_client.jql(test_jql, limit=5)
                
                issues_returned = len(test_result.get('issues', []))
                total = test_result.get('total', issues_returned)
                
                st.json({
                    "total": total if total is not None else "NULL",
                    "returned": issues_returned,
                    "maxResults": test_result.get('maxResults', "NULL")
                })
                
                if issues_returned > 0:
                    st.success(f"✅ Connected! Project {project_key} has issues accessible")
                    # Show sample issues
                    for issue in test_result.get('issues', [])[:3]:
                        st.info(f"📋 {issue.get('key')} - {issue.get('fields', {}).get('summary', 'N/A')}")
                else:
                    st.error(f"❌ Project {project_key} returned 0 issues")
                    st.stop()
            except Exception as conn_error:
                st.error(f"❌ Connection failed: {conn_error}")
                import traceback
                st.code(traceback.format_exc())
                st.stop()
            
            # Try to get projects (with error handling if it hangs)
            with st.spinner("Discovering projects..."):
                try:
                    projects = jira_client.projects(included_archived=None)
                    project_keys = [p.get('key') for p in projects]
                    st.success(f"✅ You have access to {len(project_keys)} projects")
                    
                    with st.expander("📂 View all accessible projects"):
                        st.write(", ".join(project_keys))
                    
                    # Check if user's project exists
                    user_project = spaces.split(',')[0].strip().strip("'\"")
                    if user_project not in project_keys:
                        st.warning(f"⚠️ Project '{user_project}' not in your project list")
                        st.info(f"💡 Available projects: {', '.join(project_keys[:10])}")
                    else:
                        st.success(f"✅ Project '{user_project}' found")
                        
                except Exception as proj_error:
                    st.warning(f"⚠️ Couldn't fetch project list: {proj_error}")
                    st.info("Continuing anyway - will test project directly...")
            
            # Test simple project query
            with st.spinner("Testing project access..."):
                project_key = spaces.split(',')[0].strip().strip("'\"")
                simple_jql = f'project = "{project_key}"' if ' ' in project_key else f'project = {project_key}'
                st.info(f"🧪 Query: `{simple_jql}`")
                test_issues = fetch_issues(jira_client, simple_jql, debug=True)
                
                if len(test_issues) == 0:
                    st.error(f"❌ No issues found in project '{project_key}'. Check:")
                    st.markdown("- Is the project key correct? (case-sensitive)")
                    st.markdown("- Do you have permission to view issues?")
                    st.markdown("- Does the project have any issues?")
                    st.stop()
                else:
                    st.success(f"✅ Project has {len(test_issues)} total issues")
            
            # Now try with date filter
            with st.spinner("Fetching issues with filters..."):
                jql = build_jql(spaces, labels, period)
                st.info(f"🔍 JQL: `{jql}`")
                issues = fetch_issues(jira_client, jql, debug=True)
                
                if not issues:
                    st.warning("⚠️ No issues match your filters")
                    st.info("💡 Try a wider date range or remove label filters")
                else:
                    st.success(f"✅ Found {len(issues)} matching issues!")
                    
            # Generate report
            if issues:
                with st.spinner("Generating report..."):
                    report, df, next_df = generate_report(
                        issues, persona.lower().replace(' ', '_'), 
                        llm_provider, llm_key, initiative_name, 
                        period, jira_client, spaces, labels
                    )
                    # Store in different session state keys to avoid widget conflict
                    st.session_state['generated_report'] = report
                    st.session_state['generated_df'] = df
                    st.session_state['generated_next_df'] = next_df
                    st.session_state['generated_initiative_name'] = initiative_name
                    st.success("✅ Report generated!")
                    
        except Exception as e:
            st.error(f"❌ Error: {e}")
            import traceback
            st.code(traceback.format_exc())

# Display report
if 'generated_report' in st.session_state and st.session_state.generated_report:
    st.markdown("---")
    st.text_area("Generated Report", st.session_state.generated_report, height=600)
    
    # Export buttons
    col1, col2 = st.columns(2)
    with col1:
        if PDF_AVAILABLE:
            pdf_buffer = export_to_pdf(st.session_state.generated_report, st.session_state.generated_initiative_name)
            st.download_button(
                "📥 Download PDF",
                pdf_buffer,
                file_name=f"{st.session_state.generated_initiative_name}_report.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("PDF export unavailable. Install: pip install reportlab")
    with col2:
        if EXCEL_AVAILABLE:
            excel_buffer = export_to_excel(st.session_state.generated_df, st.session_state.generated_next_df, st.session_state.generated_report)
            st.download_button(
                "📥 Download Excel",
                excel_buffer,
                file_name=f"{st.session_state.generated_initiative_name}_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Excel export unavailable. Install: pip install openpyxl")