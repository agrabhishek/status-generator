"""
Core Business Logic for Jira Status Generator
==============================================
Jira API interactions, JQL building, report generation.

Generated: 2025-10-19 18:28:32
"""

from atlassian import Jira
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Optional


class JiraClient:
    """
    Wrapper for Jira API interactions.
    
    REQUIREMENT: Jira Integration, Pagination and Scalability
    """
    
    def __init__(self, jira: Jira):
        self.jira = jira
    
    def fetch_issues(self, jql: str, max_results: int = 1000, debug: bool = False) -> List[Dict]:
        """
        Fetch issues with pagination.
        
        REQUIREMENT: Pagination and Scalability - handles 1000+ issues
        """
        issues = []
        page_size = 50
        start_at = 0
        
        while len(issues) < max_results:
            result = self.jira.jql(jql, start=start_at, limit=page_size)
            batch = result.get('issues', [])
            
            if not batch:
                break
            
            issues.extend(batch)
            total = result.get('total', 0)
            
            if len(issues) >= total or len(batch) < page_size:
                break
            
            start_at += page_size
        
        return issues
    
    def get_epic_context(self, epic_key: str) -> Dict:
        """Fetch epic summary and description for context"""
        try:
            issue = self.jira.issue(epic_key)
            fields = issue.get('fields', {})
            return {
                'summary': fields.get('summary') or 'No summary available',
                'description': fields.get('description') or 'No description available'
            }
        except:
            return {'summary': 'Unable to fetch epic', 'description': ''}
    
    def discover_projects(self) -> List[Dict]:
        """Get all accessible projects"""
        try:
            response = self.jira.get('rest/api/3/project/search')
            return response.get('values', [])
        except:
            # Fallback to JQL method
            result = self.jira.jql('assignee = currentUser() OR reporter = currentUser()', limit=100)
            issues = result.get('issues', [])
            unique_projects = {}
            for issue in issues:
                proj = issue.get('fields', {}).get('project', {})
                if proj:
                    unique_projects[proj.get('key')] = proj.get('name', 'Unknown')
            return [{'key': k, 'name': v} for k, v in unique_projects.items()]


class JQLBuilder:
    """
    Constructs JQL queries with business logic.
    
    REQUIREMENT: Flexible Criteria Input
    """
    
    @staticmethod
    def for_achievements(projects: str, labels: str = None, period: str = None) -> str:
        """
        Build query for completed work using resolutiondate.
        
        REQUIREMENT: Business logic - shows what was DELIVERED
        """
        jql_parts = []
        
        if projects:
            space_list = [s.strip().strip("'\"") for s in projects.split(',')]
            quoted_projects = [f'"{p}"' if ' ' in p else p for p in space_list]
            if len(space_list) == 1:
                jql_parts.append(f'project = {quoted_projects[0]}')
            else:
                jql_parts.append(f'project in ({", ".join(quoted_projects)})')
        
        if labels:
            label_list = [f'"{label.strip()}"' for label in labels.split(',')]
            jql_parts.append(f'labels IN ({", ".join(label_list)})')
        
        if period:
            if period == 'last_week':
                start_date = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
                jql_parts.append(f'resolutiondate >= {start_date}')
            elif period == 'last_month':
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                jql_parts.append(f'resolutiondate >= {start_date}')
            elif ' to ' in period:
                start, end = period.split(' to ')
                jql_parts.append(f'resolutiondate >= {start} AND resolutiondate <= {end}')
        
        return ' AND '.join(jql_parts) if jql_parts else 'project IS NOT EMPTY'
    
    @staticmethod
    def for_next_steps(projects: str, labels: str = None, period: str = None) -> str:
        """
        Build query for upcoming work using duedate.
        
        REQUIREMENT: Business logic - shows what is DUE
        """
        jql_parts = []
        
        if projects:
            space_list = [s.strip().strip("'\"") for s in projects.split(',')]
            quoted_projects = [f'"{p}"' if ' ' in p else p for p in space_list]
            if len(space_list) == 1:
                jql_parts.append(f'project = {quoted_projects[0]}')
            else:
                jql_parts.append(f'project in ({", ".join(quoted_projects)})')
        
        if labels:
            label_list = [f'"{label.strip()}"' for label in labels.split(',')]
            jql_parts.append(f'labels IN ({", ".join(label_list)})')
        
        if period:
            if period == 'last_week':
                start_date = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
                jql_parts.append(f'duedate >= {start_date}')
            elif period == 'last_month':
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                jql_parts.append(f'duedate >= {start_date}')
            elif ' to ' in period:
                start, end = period.split(' to ')
                jql_parts.append(f'duedate >= {start} AND duedate <= {end}')
        
        return ' AND '.join(jql_parts) if jql_parts else 'project IS NOT EMPTY'


def get_next_period_dates(current_period: str) -> str:
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