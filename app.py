"""
🏛️ JIRA AI REPORT GENERATOR - ENTERPRISE READY
═══════════════════════════════════════════════════════════════════════════════════
Single File Version | Multi-LLM | Hierarchical | SAVE/LOAD CRITERIA ✅ NEW!
Version: 2.3 (Rewritten for atlassian-python-api compatibility)
"""

# 1. IMPORTS
import streamlit as st
from atlassian import Jira
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
from io import BytesIO
import base64
import json
import os

# 2. UTILITY FUNCTIONS
def build_jql(project=None, labels=None, time_period=None, time_field='created'):
    jql_parts = []
    if project: jql_parts.append(f'project = "{project}"')
    if labels:
        label_list = [f'"{label.strip()}"' for label in labels.split(',')]
        jql_parts.append(f'labels IN ({", ".join(label_list)})')
    if time_period:
        if time_period == 'last_week':
            start_date = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
            jql_parts.append(f'{time_field} >= "{start_date}"')
        elif time_period == 'last_month':
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            jql_parts.append(f'{time_field} >= "{start_date}"')
        elif ' to ' in time_period:
            start, end = time_period.split(' to ')
            jql_parts.append(f'{time_field} >= "{start}" AND {time_field} <= "{end}"')
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

# 3. FETCH ISSUES (COMPATIBLE WITH atlassian-python-api)
def fetch_issues(jira, jql):
    issues = []
    start = 0
    max_results = 50
    while True:
        result = jira.jql(jql, start=start, limit=max_results)
        batch = result.get('issues', [])
        if not batch:
            break
        issues.extend(batch)
        if len(batch) < max_results:
            break
        start += max_results
    return issues

# 4. SAFE REPORT GENERATOR
def generate_report(issues, persona, llm_provider, api_key, initiative_name, current_period, jira_client, project, labels):
    if not issues: return f"❌ No issues found for {initiative_name}."
    data = []; issues_dict = {}
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
    
    roots = [key for key in achieved_keys if issues_dict[key]['Parent'] is None or issues_dict[key]['Parent'] not in achieved_keys]
    
    # Build hierarchy text
    def build_hierarchical_text(issues_dict, roots, indent=''):
        text = ''
        for key in roots:
            row = issues_dict.get(key, {})
            text += f"{indent}{key}: {row.get('Summary', 'N/A')}\n"
            subtasks = row.get('Subtasks', [])
            text += build_hierarchical_text(issues_dict, subtasks, indent + '  ')
        return text
    hierarchy_text = build_hierarchical_text(issues_dict, roots)
    
    # Epic context
    epic_key = None
    for key in achieved_keys:
        current = key
        while current and issues_dict.get(current, {}).get('Parent'):
            current = issues_dict[current]['Parent']
        if current and current.startswith('PROJ-'):
            epic_key = current
            break
    if epic_key and epic_key in issues_dict:
        epic = issues_dict[epic_key]
        overview = f"{epic.get('Summary', '')[:100]}. {epic.get('Description', '')[:150]}"[:200].strip().replace('\n', ' ')
    else:
        overview = f"{initiative_name} initiative overview not available in Jira."
    
    prior_keys = [k for k in achieved_keys if issues_dict[k].get('Resolved', '') < datetime.now().strftime('%Y-%m-%d')]
    prior_summary = f"{len(prior_keys)} items completed prior to this period." if prior_keys else "No prior progress."
    epic_context = f"{overview}\n{prior_summary}"
    
    full_text = f"EPIC: {initiative_name}\nCONTEXT: {epic_context}\n\nHIERARCHY:\n{hierarchy_text}"
    achievements_summary = full_text
    
    # Placeholder LLM integration (optional)
    if api_key and achieved_keys and llm_provider != "None":
        achievements_summary += "\n\n[AI Summary would appear here]"
    
    # Next steps
    next_period = get_next_period_dates(current_period)
    next_jql = build_jql(project, labels, next_period)
    next_issues = fetch_issues(jira_client, next_jql)
    next_df = pd.DataFrame([{
        'Key': i.get('key'),
        'Summary': i.get('fields', {}).get('summary', 'N/A'),
        'Status': i.get('fields', {}).get('status', {}).get('name', 'N/A') if i.get('fields', {}).get('status') else 'N/A',
        'Priority': i.get('fields', {}).get('priority', {}).get('name', 'N/A') if i.get('fields', {}).get('priority') else 'N/A'
    } for i in next_issues])
    upcoming = next_df[next_df['Status'].isin(['To Do', 'In Progress'])]
    next_steps = "📋 **NEXT STEPS**: No tickets scheduled for next period." if len(upcoming) == 0 else \
        f"📋 **NEXT STEPS** ({len(upcoming)} tickets):\n" + "\n".join(
            [f"• {row['Key']}: {row['Summary'][:50]}... ({row['Priority']})" for _, row in upcoming.head(5).iterrows()]
        ) + (f"\n...and {len(upcoming)-5} more" if len(upcoming) > 5 else "")
    
    overdue_count = len(df[(df['Due Date'].notna()) & (df['Due Date'] < datetime.now().strftime('%Y-%m-%d')) & (df['Status'] != 'Done')])
    
    return f"""
🏛️ **{initiative_name} - {persona.upper()} REPORT**

**1. CONTEXT**
{epic_context}

**2. COMPLETED THIS PERIOD**
{achievements_summary}

**3. METRICS**
Total: {len(df)} | Completed: {len(achieved_df)} ({len(achieved_df)/len(df)*100:.0f}%)
Overdue: {overdue_count}

**4. NEXT STEPS**
{next_steps}
"""

# 5. STREAMLIT UI
st.set_page_config(page_title="Jira AI Reports", page_icon="🚀", layout="wide")
st.title("🚀 Jira AI Initiative Report Generator")
st.markdown("***4-Section Executive Reports | SAVE/LOAD Presets ✅***")

# Sidebar presets
preset_col1, preset_col2, preset_col3 = st.sidebar.columns(3)
with preset_col1:
    st.markdown("**💾 PRESETS**")
    presets = get_all_presets()
    selected_preset = st.selectbox("Load", ["None"] + presets, key="load_preset")
with preset_col2:
    preset_name = st.text_input("Save As", key="save_name")
with preset_col3:
    if st.button("💾 Save", key="save_btn"):
        criteria = {
            'initiative_name': st.session_state.get('initiative_name', ''),
            'url': st.session_state.get('url', ''),
            'email': st.session_state.get('email', ''),
            'project': st.session_state.get('project', ''),
            'labels': st.session_state.get('labels', ''),
            'current_period': st.session_state.get('current_period', ''),
            'time_field': st.session_state.get('time_field', 'created'),
            'persona': st.session_state.get('persona', 'manager'),
            'llm_provider': st.session_state.get('llm_provider', 'None')
        }
        save_criteria(preset_name, criteria)

if selected_preset != "None":
    preset_data = load_criteria(selected_preset)
    if preset_data:
        st.session_state.update(preset_data)
        st.success(f"✅ Loaded: {selected_preset}")

# Sidebar inputs
with st.sidebar:
    st.header("🏛️ INITIATIVE")
    initiative_name = st.text_input("Initiative Name", value=st.session_state.get('initiative_name', 'Q4 Digital Transformation'), key="initiative_name")
    
    st.header("🔌 JIRA")
    url = st.text_input("URL", value=st.session_state.get('url', 'https://your-domain.atlassian.net'), key="url")
    email = st.text_input("Email", value=st.session_state.get('email', ''), key="email")
    token = st.text_input("Token", type="password", key="token")
    
    st.header("🔍 CURRENT PERIOD")
    project = st.text_input("Project", value=st.session_state.get('project', ''), key="project")
    labels = st.text_input("Labels", value=st.session_state.get('labels', ''), key="labels")
    time_period_option = st.selectbox("Period", ["Last Week", "Last Month", "Custom"], index=0, key="period_option")
    current_period = None
    if time_period_option == "Last Week": current_period = "last_week"
    elif time_period_option == "Last Month": current_period = "last_month"
    elif time_period_option == "Custom":
        col1, col2 = st.columns(2)
        start = col1.date_input("Start", value=datetime.now().date())
        end = col2.date_input("End", value=datetime.now().date())
        if start and end: current_period = f"{start} to {end}"
    st.session_state.current_period = current_period

    time_field = st.selectbox("Time Field", ["created", "updated"], index=0, key="time_field")
    
    st.header("👤 PERSONA")
    persona = st.selectbox("Persona", ["manager", "cto", "group_manager"], key="persona")
    
    st.header("🤖 AI")
    llm_provider = st.selectbox("LLM", ["None", "xai", "openai", "gemini"], key="llm_provider")
    api_key = None
    if llm_provider != "None":
        api_key = st.text_input(f"{llm_provider.upper()} API Key", type="password", key=f"api_{llm_provider}")

# Generate report
if st.button("📊 GENERATE INITIATIVE REPORT", type="primary"):
    missing_fields = []
    for field_name, val in {"URL": url, "Email": email, "Token": token, "Initiative": initiative_name, "Period": current_period}.items():
        if not val:
            missing_fields.append(field_name)
    if missing_fields:
        st.error(f"⚠️ Fill missing fields: {', '.join(missing_fields)}")
    else:
        try:
            with st.spinner("🔌 Connecting to Jira..."):
                jira_client = Jira(url=url, username=email, password=token, cloud=True)
            jql = build_jql(project, labels, current_period, time_field)
            st.info(f"**🔍 JQL:** `{jql}`")
            issues = fetch_issues(jira_client, jql)
            report = generate_report(issues, persona, llm_provider, api_key, initiative_name, current_period, jira_client, project, labels)
            st.session_state.update({'report': report})
            st.success(f"✅ {initiative_name} Report Ready!")
        except Exception as e:
            st.error(f"❌ {e}")

if 'report' in st.session_state:
    st.markdown("## 📋 INITIATIVE REPORT")
    st.markdown(st.session_state.report)

st.markdown("*Built with ❤️ by Grok AI | Oct 17, 2025*")
