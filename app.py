"""
Streamlit UI for Jira Status Generator
=======================================
Pure UI layer - delegates to core modules.

Generated: 2025-10-19 18:28:32
"""

import streamlit as st
from atlassian import Jira

from jira_core import (
    JiraClient, 
    JQLBuilder, 
    get_next_period_dates, 
    build_jql, 
    fetch_issues,
    generate_report,
    #get_epic_context  
)

# Import from modular files
from auth import load_secure_credentials, authenticate_jira
from llm_integrations import fetch_groq_models, get_llm_summary

# from config import * (import all settings and prompts)

from storage import save_criteria, load_criteria, get_all_presets, delete_preset

st.set_page_config(page_title="Jira AI Reports", page_icon="🚀", layout="wide")

# Initialize session state
if 'generated_report' not in st.session_state:
    st.session_state.generated_report = None

st.title("🚀 Jira AI Initiative Report Generator")
st.markdown("***4-Section Executive Reports | Multi-LLM | Groq Free-Tier***")

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
CREDENTIALS = st.secrets["jira"]
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

CREDENTIALS = st.secrets["groq"]

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

