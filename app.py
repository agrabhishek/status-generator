"""
🏛️ JIRA AI REPORT GENERATOR - ENTERPRISE READY
═══════════════════════════════════════════════════════════════════════════════════
Single File Version | Multi-LLM | Hierarchical | Groq Free-Tier Integration
Version: 3.0.0 - Secure Credentials + Dynamic Model Fetching
"""

# 1. IMPORTS
import streamlit as st
from atlassian import Jira
import pandas as pd
from datetime import datetime, timedelta, timezone
import json
import os
from io import BytesIO
import requests

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


# ============================================================================
# SECURE CREDENTIAL LOADING
# ============================================================================
# REQUIREMENT: Compliance and Security - Credentials hidden from public repo
# Uses Streamlit secrets (cloud) or environment variables (local)

def load_secure_credentials():
    """Load credentials from Streamlit secrets or environment variables"""
    return {
        'jira_email': st.secrets.get("jira", {}).get("email") or os.getenv("JIRA_EMAIL"),
        'jira_token': st.secrets.get("jira", {}).get("api_token") or os.getenv("JIRA_API_TOKEN"),
        'jira_url': st.secrets.get("jira", {}).get("default_url") or os.getenv("JIRA_DEFAULT_URL"),
        'groq_api_key': st.secrets.get("groq", {}).get("api_key") or os.getenv("GROQ_API_KEY")
    }

CREDENTIALS = load_secure_credentials()


# ============================================================================
# GROQ INTEGRATION
# ============================================================================
# REQUIREMENT: Multi-LLM Integration - Groq free-tier models

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_groq_models(api_key: str) -> list:
    """
    Fetch available Groq models dynamically at runtime.
    
    REQUIREMENT: Dynamic model fetching (not hardcoded)
    Returns: List of model IDs, empty list on error
    """
    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        response.raise_for_status()
        models_data = response.json()
        model_ids = [model['id'] for model in models_data.get('data', [])]
        return sorted(model_ids)
    except Exception as e:
        st.error(f"❌ Failed to fetch Groq models: {e}")
        return []


def call_groq_llm(prompt: str, model: str, api_key: str) -> tuple:
    """
    Call Groq API with rate limit handling.
    
    REQUIREMENT: Handle 429 rate limits gracefully
    Returns: (response_text, is_rate_limited)
    """
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.7
            },
            timeout=30
        )
        
        # Handle rate limiting
        if response.status_code == 429:
            return "", True  # Signal rate limit hit
        
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'], False
        
    except requests.exceptions.Timeout:
        return "⚠️ Request timeout. Try a different model.", False
    except Exception as e:
        return f"❌ Error: {str(e)}", False


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def build_jql(spaces=None, labels=None, time_period=None, time_field='resolutiondate'):
    """
    Build JQL with proper quoting.
    
    REQUIREMENT: Business logic - resolutiondate for achievements, duedate for next steps
    """
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
    """Calculate next reporting period with same duration"""
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
    """Save preset to JSON file"""
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
    """Load preset from JSON file"""
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
    """Get all preset names"""
    presets_file = "jira_presets.json"
    if not os.path.exists(presets_file):
        return []
    with open(presets_file, 'r') as f:
        presets = json.load(f)
    return list(presets.keys())


def delete_preset(preset_name):
    """Delete preset from JSON file"""
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


# FETCH ISSUES
def fetch_issues(jira, jql, debug=False):
    """
    Fetch issues with pagination.
    
    REQUIREMENT: Pagination and Scalability - handles 1000+ issues
    """
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


def get_epic_context(jira, epic_key):
    """
    Fetch epic summary and description for context.
    
    REQUIREMENT: Context Section - Epic overview
    """
    try:
        issue = jira.issue(epic_key)
        fields = issue.get('fields', {})
        return {
            'summary': fields.get('summary') or 'No summary available',
            'description': fields.get('description') or 'No description available'
        }
    except:
        return {'summary': 'Unable to fetch epic', 'description': ''}


# EXPORT TO PDF
def export_to_pdf(report_text, initiative_name):
    """Export report to PDF with formatting"""
    if not PDF_AVAILABLE:
        raise ImportError("reportlab not installed. Run: pip install reportlab")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph(f"<b>{initiative_name} - Status Report</b>", styles['Title']))
    story.append(Spacer(1, 12))
    
    for line in report_text.split('\n'):
        if line.strip():
            story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 6))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


# EXPORT TO EXCEL
def export_to_excel(df, next_df, report_text):
    """Export to Excel with multiple sheets"""
    if not EXCEL_AVAILABLE:
        raise ImportError("openpyxl not installed. Run: pip install openpyxl")
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Current Issues', index=False)
        next_df.to_excel(writer, sheet_name='Next Steps', index=False)
        
        context_df = pd.DataFrame({'Report': [report_text]})
        context_df.to_excel(writer, sheet_name='Full Report', index=False)
    
    buffer.seek(0)
    return buffer


# LLM INTEGRATION
def get_llm_summary(llm_provider, api_key, prompt, groq_model=None):
    """
    Get AI summary from selected provider.
    
    REQUIREMENT: Multi-LLM Integration
    Supports: Groq (free-tier), OpenAI, xAI, Gemini
    """
    try:
        if llm_provider == "Groq (Free Tier)":
            if not groq_model:
                return "❌ No Groq model selected"
            
            summary, rate_limited = call_groq_llm(prompt, groq_model, api_key)
            
            if rate_limited:
                return f"⚠️ Rate limit hit for {groq_model}. Please select another model and regenerate the report."
            
            return summary
        
        elif llm_provider == "OpenAI":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            return response.choices[0].message.content
        
        elif llm_provider == "xAI":
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
        
        elif llm_provider == "Gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        
        return ""
    except Exception as e:
        return f"AI summary error: {str(e)}"


# REPORT GENERATOR
def generate_report(issues, persona, llm_provider, api_key, initiative_name, current_period, 
                   jira_client, spaces, labels, groq_model=None):
    """
    Generate complete 4-section executive report.
    
    REQUIREMENT: Generate Executive Reports - Structured status reports
    """
    if not issues:
        return f"❌ No issues found for {initiative_name}.", pd.DataFrame(), pd.DataFrame()
    
    # Build issues dictionary
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
    
    # Prior progress
    if current_period in ['last_week', 'last_month']:
        period_end = datetime.now(timezone.utc)
    else:
        end_date_str = current_period.split(' to ')[1]
        period_end = datetime.strptime(end_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    prior_keys = []
    for k in achieved_keys:
        resolved_date = issues_dict[k].get('Resolved')
        if resolved_date:
            try:
                resolved_dt = datetime.fromisoformat(resolved_date.replace('Z', '+00:00'))
                if resolved_dt < period_end:
                    prior_keys.append(k)
            except:
                pass
    
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
    
    # Persona-specific formatting
    if persona == 'team_lead':
        hierarchy_text = build_hierarchical_text(issues_dict, roots)
    elif persona == 'manager':
        completed_summaries = [issues_dict[k]['Summary'] for k in achieved_keys[:10]]
        hierarchy_text = f"Completed {len(achieved_keys)} tickets this period. Key accomplishments include: " + \
                        ", ".join(completed_summaries[:5]) + \
                        (f", and {len(achieved_keys)-5} other items" if len(achieved_keys) > 5 else ".")
    elif persona == 'group_manager':
        hierarchy_text = f"Team completed {len(achieved_keys)} of {len(df)} tickets ({len(achieved_keys)/len(df)*100:.0f}% completion rate). " + \
                        f"Major deliverables: {', '.join([issues_dict[k]['Summary'][:40] for k in roots[:3]])}."
    elif persona == 'cto':
        hierarchy_text = f"Initiative delivered {len(achieved_keys)} items. " + \
                        f"Primary outcomes: {', '.join([issues_dict[k]['Summary'][:50] for k in roots[:2]])}. " + \
                        f"Team velocity: {len(achieved_keys)} items completed in period."
    else:
        hierarchy_text = build_hierarchical_text(issues_dict, roots)
    
    # AI Summary
    achievements_summary = hierarchy_text
    if api_key and achieved_keys and llm_provider != "None":
        if persona == 'team_lead':
            prompt = f"Summarize these completed Jira tickets for a team lead (technical details matter):\n{hierarchy_text}"
        elif persona == 'manager':
            prompt = f"Write a concise executive paragraph summarizing these achievements for a manager (focus on outcomes, not technical details):\n{hierarchy_text}"
        elif persona == 'group_manager':
            prompt = f"Write a strategic summary for a group manager highlighting business impact and team performance:\n{hierarchy_text}"
        elif persona == 'cto':
            prompt = f"Write a high-level executive summary for CTO highlighting strategic value and key deliverables:\n{hierarchy_text}"
        else:
            prompt = f"Summarize these completed Jira tickets:\n{hierarchy_text}"
            
        ai_summary = get_llm_summary(llm_provider, api_key, prompt, groq_model)
        
        if persona in ['manager', 'group_manager', 'cto']:
            achievements_summary = f"📖 {ai_summary}"
        else:
            achievements_summary += f"\n\n📖 AI SUMMARY:\n{ai_summary}"
    
    # Next steps - USE DUE DATE
    next_period = get_next_period_dates(current_period)
    next_jql = build_jql(spaces, labels, next_period, time_field='duedate')
    next_issues = fetch_issues(jira_client, next_jql)
    
    if next_issues:
        next_df = pd.DataFrame([{
            'Key': i.get('key'),
            'Summary': i.get('fields', {}).get('summary', 'N/A'),
            'Status': i.get('fields', {}).get('status', {}).get('name', 'N/A') if i.get('fields', {}).get('status') else 'N/A',
            'Priority': (i.get('fields', {}).get('priority') or {}).get('name', 'N/A')
        } for i in next_issues])
        
        upcoming = next_df[next_df['Status'].isin(['To Do', 'In Progress'])]
    else:
        next_df = pd.DataFrame(columns=['Key', 'Summary', 'Status', 'Priority'])
        upcoming = pd.DataFrame()
    
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

**2. BUSINESS IMPACT - DELIVERED THIS PERIOD**
(Based on resolution date: {current_period})
{achievements_summary}

**3. METRICS**
Total Issues: {len(df)} | Completed: {len(achieved_df)} ({len(achieved_df)/len(df)*100:.0f}%)
Overdue: {overdue_count}

**4. BUSINESS IMPACT - FORWARD LOOKING**
(Based on due dates in upcoming period)
{next_steps}
"""
    
    return report, df, next_df


# ============================================================================
# STREAMLIT UI
# ============================================================================

st.set_page_config(page_title="Jira AI Reports", page_icon="🚀", layout="wide")

# Initialize session state
if 'generated_report' not in st.session_state:
    st.session_state.generated_report = None
if 'generated_df' not in st.session_state:
    st.session_state.generated_df = None
if 'generated_next_df' not in st.session_state:
    st.session_state.generated_next_df = None

st.title("🚀 Jira AI Initiative Report Generator")
st.markdown("***4-Section Executive Reports | Multi-LLM | PDF/Excel Export | Groq Free-Tier***")

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
            'spaces': st.session_state.get('spaces', ''),
            'labels': st.session_state.get('labels', ''),
            'llm_provider': st.session_state.get('llm_provider', 'None'),
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
initiative_name = st.text_input("Initiative / Epic Name* (Type AWS for test setup)", key="initiative_name")

# Jira URL - User choice or default
use_default_jira = st.checkbox("Use default Jira configuration", value=True if CREDENTIALS['jira_url'] else False)

if use_default_jira and CREDENTIALS['jira_url']:
    # Use pre-configured Jira
    url = CREDENTIALS['jira_url']
    email = CREDENTIALS['jira_email']
    jira_token = CREDENTIALS['jira_token']
    
    # Default project space
    spaces = st.text_input("Jira Spaces*(Type AWS for test setup)", value="AWS Migration", key="spaces")
    
else:
    # User provides their own Jira
    url = st.text_input("Jira URL*", key="url", placeholder="https://yourcompany.atlassian.net")
    email = st.text_input("Jira Email*", key="email")
    jira_token = st.text_input("Jira API Token*", type="password", key="jira_token")
    
    # Fetch and allow project selection
    if url and email and jira_token:
        if st.button("🔍 Discover Projects"):
            try:
                with st.spinner("Fetching projects..."):
                    temp_jira = Jira(url=url, username=email, password=jira_token, cloud=True)
                    try:
                        response = temp_jira.get('rest/api/3/project/search')
                        projects = response.get('values', [])
                        if projects:
                            project_info = {p['key']: p.get('name', 'Unknown') for p in projects}
                            st.session_state['available_projects'] = list(project_info.keys())
                            st.session_state['project_names'] = project_info
                    except:
                        result = temp_jira.jql('assignee = currentUser() OR reporter = currentUser()', limit=100)
                        issues = result.get('issues', [])
                        unique_projects = {}
                        for issue in issues:
                            proj = issue.get('fields', {}).get('project', {})
                            if proj:
                                key = proj.get('key')
                                name = proj.get('name', 'Unknown')
                                unique_projects[key] = name
                        if unique_projects:
                            st.session_state['available_projects'] = list(unique_projects.keys())
                            st.session_state['project_names'] = unique_projects
            except Exception as e:
                st.error(f"Failed to fetch projects: {e}")
        
        # Multi-select for projects
        if 'available_projects' in st.session_state:
            selected_projects = st.multiselect(
                "Select Jira Projects*",
                st.session_state['available_projects'],
                format_func=lambda x: f"{x} - {st.session_state['project_names'].get(x, 'Unknown')}"
            )
            spaces = ','.join(selected_projects) if selected_projects else None
        else:
            spaces = st.text_input("Jira Spaces* (comma-separated)", key="spaces_manual", 
                                  placeholder="AWS,CLOUD", 
                                  help="Click 'Discover Projects' above to see available options")
    else:
        spaces = None

labels = st.text_input("Labels (optional)", key="labels")
persona = st.selectbox("Persona", ["Team Lead", "Manager", "Group Manager", "CTO"], key="persona")

# LLM Provider Selection
llm_provider = st.selectbox(
    "LLM Provider", 
    ["Groq (Free Tier)", "OpenAI", "xAI", "Gemini", "None"], 
    key="llm_provider"
)

llm_key = None
selected_groq_model = None

if llm_provider == "Groq (Free Tier)":
    if not CREDENTIALS['groq_api_key']:
        st.error("⚠️ Groq API key not configured. Please set up secrets.")
        st.stop()
    else:
        # Fetch available models dynamically
        with st.spinner("Loading models..."):
            available_models = fetch_groq_models(CREDENTIALS['groq_api_key'])
        
        if not available_models:
            st.error("❌ Could not fetch Groq models. Check configuration.")
            st.stop()
        
        # Set default to kimi-k2-instruct if available
        default_index = 0
        if "moonshot-ai/kimi-k2-instruct" in available_models:
            default_index = available_models.index("moonshot-ai/kimi-k2-instruct")
        
        selected_groq_model = st.selectbox(
            "Select Model (suggestion use moonshotai/kimi-k2-instruct)",
            available_models,
            index=default_index,
            help="If you encounter rate limits, select a different model."
        )
        
        llm_key = CREDENTIALS['groq_api_key']

elif llm_provider in ["OpenAI", "xAI", "Gemini"]:
    llm_key = st.text_input(
        f"{llm_provider} API Key", 
        type="password", 
        key="user_llm_key"
    )

# Period selection
period = st.selectbox("Reporting Period", ["last_week", "last_month", "Custom"], key="period")

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
        st.error("❌ Please fill all required fields")
    else:
        try:
            # Authentication
            with st.spinner("Connecting to Jira..."):
                jira_client = Jira(url=url, username=email, password=jira_token, cloud=True)
                
                try:
                    myself = jira_client.myself()
                except Exception as auth_error:
                    st.error(f"❌ Authentication failed: {auth_error}")
                    st.stop()
            
            # Fetch issues with resolution date filter
            with st.spinner("Fetching data..."):
                jql = build_jql(spaces, labels, period, time_field='resolutiondate')
                issues = fetch_issues(jira_client, jql, debug=False)
                
                if not issues:
                    st.warning("⚠️ No issues found matching your criteria")
                    st.stop()
            
            # Generate report
            with st.spinner("Generating report..."):
                report, df, next_df = generate_report(
                    issues, 
                    persona.lower().replace(' ', '_'), 
                    llm_provider, 
                    llm_key, 
                    initiative_name, 
                    period, 
                    jira_client, 
                    spaces, 
                    labels,
                    groq_model=selected_groq_model
                )
                
                # Store in session state
                st.session_state['generated_report'] = report
                st.session_state['generated_df'] = df
                st.session_state['generated_next_df'] = next_df
                st.session_state['generated_initiative_name'] = initiative_name
                
                # Check for rate limit warning in report
                if "⚠️ Rate limit hit" in report:
                    st.warning("Rate limit encountered. Please select a different model and try again.")
                    
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Display report
if 'generated_report' in st.session_state and st.session_state.generated_report:
    st.markdown("---")
    st.text_area("Generated Report", st.session_state.generated_report, height=600)
    
    # Export buttons
    col1, col2 = st.columns(2)
    with col1:
        if PDF_AVAILABLE:
            try:
                pdf_buffer = export_to_pdf(
                    st.session_state.generated_report, 
                    st.session_state.generated_initiative_name
                )
                st.download_button(
                    "📥 Download PDF",
                    pdf_buffer,
                    file_name=f"{st.session_state.generated_initiative_name}_report.pdf",
                    mime="application/pdf"
                )
            except Exception as pdf_error:
                st.error(f"PDF export failed: {pdf_error}")
        else:
            st.warning("PDF export unavailable. Install: pip install reportlab")
    
    with col2:
        if EXCEL_AVAILABLE:
            try:
                excel_buffer = export_to_excel(
                    st.session_state.generated_df, 
                    st.session_state.generated_next_df, 
                    st.session_state.generated_report
                )
                st.download_button(
                    "📥 Download Excel",
                    excel_buffer,
                    file_name=f"{st.session_state.generated_initiative_name}_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as excel_error:
                st.error(f"Excel export failed: {excel_error}")
        else:
            st.warning("Excel export unavailable. Install: pip install openpyxl")