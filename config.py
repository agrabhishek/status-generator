"""
Configuration and System Prompts for Jira Status Generator
===========================================================
All prompts, settings, and constants centralized here.

Generated: 2025-10-19 18:28:32
"""

# Copy the complete config.py content from the artifact "config_file"
# This file already exists in our conversation as a complete artifact
# To get it: Look for artifact ID "config_file" 

# For now, this is a placeholder - you'll copy the actual config.py content here
# The full config.py was provided earlier with all prompts and settings

from typing import Dict, List

APP_NAME = "Jira AI Initiative Report Generator"
APP_VERSION = "3.0.0"
APP_ICON = "🚀"

# TODO: Copy full content from config.py artifact provided earlier
# This includes:
# - JIRA_MAX_RESULTS_PER_PAGE = 50
# - PERSONAS configuration
# - PERSONA_PROMPTS dictionary
# - ERROR_MESSAGES dictionary
# - UI_HELP_TEXT dictionary
# - LLM_CONFIG for Groq, OpenAI, xAI, Gemini
# - All utility functions
"""
Configuration and System Prompts for Jira Status Generator
===========================================================
REQUIREMENTS ADDRESSED:
- Persona-Specific Tailoring: All LLM prompts centralized
- Error Handling and Feedback: Centralized error messages
- Usability Features: Help text and tooltips
- Pagination and Scalability: Configurable page sizes
- Multi-LLM Integration: Provider settings
- Export Options: Format configurations

All constants, prompts, and settings in ONE place.
Modify prompts here to change AI behavior without touching core logic.

Comment Rule: 1 comment per 7-10 lines, connected to requirements
"""

from typing import Dict, List

# ============================================================================
# APPLICATION METADATA
# ============================================================================

APP_NAME = "Jira AI Initiative Report Generator"
APP_VERSION = "2.6.0"
APP_ICON = "🚀"


# ============================================================================
# JIRA API SETTINGS
# ============================================================================
# REQUIREMENT: Pagination and Scalability
# Controls how many issues fetched per API call to avoid timeouts

JIRA_MAX_RESULTS_PER_PAGE = 50  # Optimal for Jira Cloud API
JIRA_TOTAL_MAX_RESULTS = 1000   # Maximum issues to fetch per query
JIRA_API_VERSION = "3"           # Jira Cloud REST API version
JIRA_TIMEOUT_SECONDS = 30        # API request timeout


# ============================================================================
# REPORT GENERATION SETTINGS
# ============================================================================
# REQUIREMENT: Generate Executive Reports
# Controls report structure and content limits

REPORT_SECTIONS = [
    "Context",
    "Business Impact - Delivered",
    "Metrics", 
    "Business Impact - Forward Looking"
]

# Character limits for truncation
EPIC_SUMMARY_MAX_CHARS = 100
EPIC_DESCRIPTION_MAX_CHARS = 150
CONTEXT_OVERVIEW_MAX_CHARS = 200
NEXT_STEPS_PREVIEW_COUNT = 5  # Show top 5 upcoming tickets


# ============================================================================
# PERSONA CONFIGURATION
# ============================================================================
# REQUIREMENT: Persona-Specific Tailoring
# Defines available personas and their characteristics

PERSONAS = ["Team Lead", "Manager", "Group Manager", "CTO"]
DEFAULT_PERSONA = "Team Lead"

PERSONA_METADATA = {
    "team_lead": {
        "display_name": "Team Lead",
        "focus": "Technical details and implementation",
        "output_format": "Hierarchical ticket breakdown",
        "detail_level": "High"
    },
    "manager": {
        "display_name": "Manager",
        "focus": "Business outcomes and deliverables",
        "output_format": "Executive paragraph summary",
        "detail_level": "Medium"
    },
    "group_manager": {
        "display_name": "Group Manager",
        "focus": "Strategic metrics and portfolio health",
        "output_format": "Metrics-focused summary",
        "detail_level": "Medium-Low"
    },
    "cto": {
        "display_name": "CTO",
        "focus": "Technology strategy and innovation",
        "output_format": "Executive brief",
        "detail_level": "Low"
    }
}


# ============================================================================
# TIME PERIOD SETTINGS
# ============================================================================
# REQUIREMENT: Flexible Criteria Input
# Defines supported time periods and date field options

TIME_PERIODS = ["last_week", "last_month", "Custom"]
DEFAULT_TIME_PERIOD = "last_week"

# Date field mappings for different query types
# REQUIREMENT: Business logic - resolutiondate for achievements, duedate for next steps
DATE_FIELD_ACHIEVEMENTS = "resolutiondate"  # When work was COMPLETED
DATE_FIELD_NEXT_STEPS = "duedate"          # When work is DUE
DATE_FIELD_CREATED = "created"             # When ticket was created
DATE_FIELD_UPDATED = "updated"             # When ticket was last modified

TIME_PERIOD_DAYS = {
    "last_week": 7,
    "last_month": 30
}


# ============================================================================
# LLM PROVIDER SETTINGS
# ============================================================================
# REQUIREMENT: Multi-LLM Integration
# Configuration for OpenAI, xAI, Gemini providers

LLM_PROVIDERS = ["OpenAI", "xAI", "Gemini", "None"]
DEFAULT_LLM_PROVIDER = "None"

LLM_CONFIG = {
    "OpenAI": {
        "model": "gpt-4o-mini",
        "max_tokens": 400,
        "temperature": 0.7,
        "api_url": "https://api.openai.com/v1/chat/completions",
        "status": "available"
    },
    "xAI": {
        "model": "grok-beta",
        "max_tokens": 400,
        "temperature": 0.7,
        "api_url": "https://api.x.ai/v1/chat/completions",
        "status": "coming_soon"  # Not fully implemented
    },
    "Gemini": {
        "model": "gemini-pro",
        "max_tokens": 400,
        "temperature": 0.7,
        "api_url": None,  # Uses SDK, not direct API
        "status": "coming_soon"  # Not fully implemented
    }
}


# ============================================================================
# EXPORT SETTINGS
# ============================================================================
# REQUIREMENT: Export Options
# Configuration for PDF and Excel export

EXPORT_FORMATS = ["PDF", "Excel"]

PDF_CONFIG = {
    "page_size": "letter",
    "library": "reportlab",
    "font_size_title": 16,
    "font_size_body": 11,
    "margins": 72  # 1 inch in points
}

EXCEL_CONFIG = {
    "engine": "openpyxl",
    "sheets": [
        "Current Issues",
        "Next Steps", 
        "Full Report"
    ],
    "freeze_panes": True
}


# ============================================================================
# STORAGE SETTINGS
# ============================================================================
# REQUIREMENT: Save and Load Criteria
# Configuration for preset management

PRESET_STORAGE_FILE = "jira_presets.json"
PRESET_FIELDS = [
    "initiative_name",
    "url",
    "email",
    "spaces",
    "labels",
    "llm_provider",
    "persona",
    "period"
]
# REQUIREMENT: Compliance and Security - API keys NOT stored in presets


# ============================================================================
# PERSONA-SPECIFIC LLM PROMPTS
# ============================================================================
# REQUIREMENT: Persona-Specific Tailoring
# Each persona gets optimized prompts for their reporting needs

PERSONA_PROMPTS = {
    "team_lead": """You are summarizing completed Jira tickets for a Technical Team Lead.

CONTEXT:
The team lead needs technical depth to understand implementation details, guide future work, and mentor the team.

REQUIREMENTS:
- Include specific technical achievements (APIs, databases, components, services)
- Mention key technologies and architectural decisions made
- Highlight blockers resolved and dependencies completed
- Use precise technical terminology that engineers understand
- Reference critical tickets by ID when relevant for tracking

COMPLETED TICKETS:
{tickets_text}

INSTRUCTIONS:
Write a technical summary in 2-3 paragraphs focusing on:
1. What systems/components were built or modified
2. Key technical decisions or approaches used
3. Any technical debt addressed or created

OUTPUT:""",
    
    "manager": """You are summarizing achievements for an Engineering Manager.

CONTEXT:
The manager needs to understand business outcomes, team velocity, and deliverables without deep technical details. They report progress to leadership.

REQUIREMENTS:
- Focus on WHAT was delivered, not HOW it was built
- Emphasize business value and customer impact
- Use plain language, avoid technical jargon
- Quantify results where possible (e.g., "improved performance by 40%")
- Connect work to business objectives and strategic goals

COMPLETED TICKETS:
{tickets_text}

INSTRUCTIONS:
Write an executive summary in ONE concise paragraph answering:
- What business capabilities were delivered?
- What customer/user problems were solved?
- How does this advance our strategic goals?

OUTPUT:""",
    
    "group_manager": """You are summarizing achievements for a Group Manager overseeing multiple teams.

CONTEXT:
The group manager needs strategic insights about team performance, resource allocation, and program-level progress. They manage portfolio priorities.

REQUIREMENTS:
- Focus on strategic impact and portfolio health indicators
- Highlight cross-team dependencies or collaborations
- Identify risks, bottlenecks, or resource constraints
- Emphasize alignment to company OKRs and strategic initiatives
- Use metrics and data points to support insights

COMPLETED TICKETS:
{tickets_text}

INSTRUCTIONS:
Write a strategic summary in 2 paragraphs addressing:
1. Program-level outcomes achieved this period
2. Team velocity and efficiency trends
3. Portfolio health indicators (risks, blockers, dependencies)

OUTPUT:""",
    
    "cto": """You are summarizing achievements for a Chief Technology Officer.

CONTEXT:
The CTO needs a high-level view of technology strategy execution, innovation, technical debt management, and alignment with company vision. This informs board reporting.

REQUIREMENTS:
- Focus on strategic technology initiatives and their business impact
- Connect technical work to business strategy and competitive advantage
- Highlight innovation, architectural improvements, or tech debt reduction
- Use business language with strategic technical insights
- Quantify business impact (revenue enabled, efficiency gains, risk reduction)

COMPLETED TICKETS:
{tickets_text}

INSTRUCTIONS:
Write an executive brief in 3-4 sentences covering:
- Strategic technology capabilities delivered
- Alignment with technology vision and roadmap
- Notable architectural improvements or innovations
- Measurable business impact

OUTPUT:"""
}


# ============================================================================
# ERROR MESSAGES
# ============================================================================
# REQUIREMENT: Error Handling and Feedback
# Clear, actionable error messages guide users to resolution

ERROR_MESSAGES = {
    "no_issues_found": """❌ No issues found for initiative '{initiative_name}'. 

Check your filters:
- Verify project key is correct (case-sensitive)
- Ensure date range captures completed work (uses resolution date)
- Check if tickets have resolution dates set in Jira
- Try a wider date range or remove label filters""",
    
    "no_next_steps": """📋 No upcoming tickets scheduled for next period.

Consider:
- Adding due dates to planned work in Jira
- Reviewing sprint/release planning
- Checking if tickets are properly scoped and scheduled""",
    
    "api_auth_failed": """🔐 Jira authentication failed.

Please verify:
- Email address matches your Jira account exactly
- API token is valid (regenerate at https://id.atlassian.com/manage-profile/security/api-tokens)
- URL includes https:// and ends with .atlassian.net
- You have permission to access the specified project""",
    
    "llm_error": """⚠️ AI summary generation failed: {error}

Troubleshooting:
- Verify API key is valid for {provider}
- Check internet connection
- Ensure you have API credits/quota remaining
- Try regenerating without AI summary (select 'None')""",
    
    "export_pdf_error": """📄 PDF export failed: {error}

Resolution:
- Install reportlab: pip install reportlab
- Check file write permissions
- Ensure sufficient disk space""",
    
    "export_excel_error": """📊 Excel export failed: {error}

Resolution:
- Install openpyxl: pip install openpyxl
- Check file write permissions
- Close the file if already open""",
    
    "jql_syntax_error": """❌ JQL query syntax error: {error}

Common issues:
- Project key must match exactly (case-sensitive)
- Labels must be comma-separated
- Date format must be YYYY-MM-DD""",
    
    "pagination_error": """⚠️ Error fetching issues (pagination failed): {error}

This usually means:
- Too many issues to fetch (>1000)
- API timeout due to complex query
- Try narrowing your date range or filters""",
    
    "preset_save_error": """❌ Failed to save preset: {error}

Check:
- File write permissions in current directory
- Disk space available
- Preset name contains only valid characters""",
    
    "preset_load_error": """❌ Failed to load preset '{preset_name}': {error}

The preset file may be corrupted. Try:
- Creating a new preset
- Checking jira_presets.json file format"""
}


# ============================================================================
# SUCCESS MESSAGES
# ============================================================================
# REQUIREMENT: Error Handling and Feedback
# Positive feedback confirms successful operations

SUCCESS_MESSAGES = {
    "issues_fetched": "✅ Found {count} matching issues!",
    "report_generated": "✅ Report generated successfully!",
    "authenticated": "✅ AUTHENTICATED as: {name} ({email})",
    "preset_saved": "✅ Saved preset: {name}",
    "preset_loaded": "✅ Loaded preset: {name}",
    "preset_deleted": "✅ Deleted preset: {name}",
    "project_discovered": "✅ Found {count} accessible projects",
    "export_ready": "✅ Export ready for download"
}


# ============================================================================
# UI HELP TEXT & TOOLTIPS
# ============================================================================
# REQUIREMENT: Usability Features
# Contextual help for intuitive user experience

UI_HELP_TEXT = {
    "initiative_name": """📝 **Initiative Name**

Give this report a clear, descriptive name (e.g., "Q4 AWS Migration" or "Payment API Rewrite").

This name appears in:
- Report title and headers
- Exported PDF/Excel file names
- Saved presets""",
    
    "jira_url": """🌐 **Jira Instance URL**

Your Jira Cloud instance URL.

Format: https://yourcompany.atlassian.net

❌ Don't include:
- /browse/ paths
- Issue keys (AWS-123)
- Trailing slashes""",
    
    "api_token": """🔑 **Jira API Token**

Generate a personal API token at:
https://id.atlassian.com/manage-profile/security/api-tokens

Security notes:
- Keep this secure - it's equivalent to your password
- Never commit to version control
- Tokens are NOT saved in presets
- Regenerate if compromised""",
    
    "project_spaces": """📂 **Jira Project Keys**

One or more project keys (case-sensitive).

Examples:
- Single: AWS
- Multiple: AWS,CLOUD,DATA
- With spaces: "Cloud Migration"

💡 Tip: Click 'Discover' to see available projects""",
    
    "labels": """🏷️ **Jira Labels (Optional)**

Filter by specific labels for focused reports.

Examples:
- Single: security
- Multiple: security,infrastructure,compliance

Leave blank to include all tickets in the project.""",
    
    "period_selection": """📅 **Reporting Period Logic**

CRITICAL: Different sections use different date fields:

**Section 2: Achievements** (What was DELIVERED)
├─ Filtered by: RESOLUTION DATE
├─ Shows: Tickets COMPLETED in this period
└─ Example: Ticket created 3 months ago but resolved this week
   → Correctly counted as THIS WEEK's achievement ✅

**Section 4: Next Steps** (What is DUE)
├─ Filtered by: DUE DATE
├─ Shows: Tickets DUE in upcoming period
└─ Example: Ticket created yesterday but due next week
   → Correctly counted as NEXT WEEK's commitment ✅

Why this matters:
✅ Captures business value DELIVERED (not started)
✅ Shows forward-looking commitments
✅ Aligns with executive reporting standards""",
    
    "persona_selection": """👤 **Persona Determines Report Style**

Each persona gets a customized report format:

**Team Lead** (Technical)
├─ Focus: Implementation details
├─ Format: Hierarchical ticket breakdown
├─ Detail: High - includes ticket IDs, subtasks
└─ Use for: Sprint reviews, technical planning

**Manager** (Business)
├─ Focus: Business outcomes, deliverables
├─ Format: Executive paragraph summary
├─ Detail: Medium - focuses on WHAT, not HOW
└─ Use for: Status updates to leadership

**Group Manager** (Strategic)
├─ Focus: Portfolio health, metrics
├─ Format: Metrics-focused with highlights
├─ Detail: Medium-Low - emphasizes trends
└─ Use for: Program reviews, resource planning

**CTO** (Executive)
├─ Focus: Technology strategy, innovation
├─ Format: Executive brief (3-4 sentences)
├─ Detail: Low - strategic overview only
└─ Use for: Board updates, investor relations""",
    
    "llm_provider": """🤖 **AI Summary Enhancement (Optional)**

Add AI-generated summaries tailored to your persona.

**OpenAI** ✅ Available
├─ Model: gpt-4o-mini
├─ Quality: Excellent
├─ Speed: Fast
└─ Requires: OpenAI API key

**xAI** 🚧 Coming Soon
├─ Model: grok-beta
└─ Status: Implementation in progress

**Gemini** 🚧 Coming Soon
├─ Model: gemini-pro
└─ Status: Implementation in progress

**None** (Default)
├─ No AI enhancement
├─ Uses raw ticket data
└─ No API key required

Note: AI summaries consume API tokens and may incur costs.""",
    
    "llm_api_key": """🔐 **LLM API Key**

Required only if using AI summaries (OpenAI, xAI, Gemini).

Get your key:
- OpenAI: https://platform.openai.com/api-keys
- xAI: https://x.ai/ (when available)
- Gemini: https://makersuite.google.com/app/apikey

Security:
- NOT saved in presets
- Transmitted securely via HTTPS
- Only used for summary generation"""
}


# ============================================================================
# UI LABELS & DISPLAY TEXT
# ============================================================================
# REQUIREMENT: Usability Features
# Consistent labeling across the interface

UI_LABELS = {
    "required_field": "*",
    "optional_field": "(optional)",
    "loading": "Loading...",
    "generating": "Generating report...",
    "fetching": "Fetching from Jira...",
    "authenticating": "Authenticating...",
    "exporting": "Exporting...",
    "sidebar_title": "💾 PRESETS",
    "main_title": "🚀 Jira AI Initiative Report Generator",
    "subtitle": "4-Section Executive Reports | Multi-LLM | PDF/Excel Export"
}


# ============================================================================
# VALIDATION RULES
# ============================================================================
# REQUIREMENT: Error Handling and Feedback
# Input validation rules for user data

VALIDATION = {
    "initiative_name": {
        "min_length": 3,
        "max_length": 100,
        "required": True
    },
    "jira_url": {
        "pattern": r"^https://[\w-]+\.atlassian\.net/?$",
        "required": True,
        "example": "https://yourcompany.atlassian.net"
    },
    "email": {
        "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$",
        "required": True
    },
    "project_spaces": {
        "min_length": 1,
        "required": True,
        "separator": ","
    },
    "preset_name": {
        "min_length": 1,
        "max_length": 50,
        "pattern": r"^[\w\s\-]+$",  # Alphanumeric, spaces, hyphens only
        "invalid_chars": ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    }
}


# ============================================================================
# FEATURE FLAGS
# ============================================================================
# Control which features are enabled/disabled

FEATURES = {
    "llm_openai": True,
    "llm_xai": False,      # Not fully implemented
    "llm_gemini": False,   # Not fully implemented
    "export_pdf": True,
    "export_excel": True,
    "preset_management": True,
    "project_discovery": True,
    "debug_mode": False    # Enable for verbose logging
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_prompt(persona: str, tickets_text: str) -> str:
    """
    Get formatted LLM prompt for persona.
    
    REQUIREMENT: Persona-Specific Tailoring
    Returns appropriate prompt template with variable injection
    
    Args:
        persona: One of ['team_lead', 'manager', 'group_manager', 'cto']
        tickets_text: Formatted string of completed tickets
    
    Returns:
        Complete prompt ready for LLM API call
    """
    persona_key = persona.lower().replace(' ', '_')
    template = PERSONA_PROMPTS.get(persona_key, PERSONA_PROMPTS["team_lead"])
    return template.format(tickets_text=tickets_text)


def get_error_message(error_type: str, **kwargs) -> str:
    """
    Get formatted error message with variable substitution.
    
    REQUIREMENT: Error Handling and Feedback
    Provides actionable guidance for common errors
    
    Args:
        error_type: Key from ERROR_MESSAGES dict
        **kwargs: Variables to substitute in message
    
    Returns:
        Formatted error message
    """
    template = ERROR_MESSAGES.get(error_type, "An error occurred: {error}")
    return template.format(**kwargs)


def get_success_message(message_type: str, **kwargs) -> str:
    """Get formatted success message"""
    template = SUCCESS_MESSAGES.get(message_type, "Operation successful")
    return template.format(**kwargs)


def get_help_text(field: str) -> str:
    """Get help text for UI field"""
    return UI_HELP_TEXT.get(field, "")


def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURES.get(feature, False)


def get_llm_config(provider: str) -> dict:
    """Get LLM configuration for provider"""
    return LLM_CONFIG.get(provider, {})


def validate_input(field: str, value: str) -> tuple[bool, str]:
    """
    Validate user input against rules.
    
    REQUIREMENT: Error Handling and Feedback
    Returns (is_valid, error_message)
    """
    import re
    
    rules = VALIDATION.get(field, {})
    
    # Required check
    if rules.get("required") and not value:
        return False, f"{field} is required"
    
    # Length checks
    if "min_length" in rules and len(value) < rules["min_length"]:
        return False, f"{field} must be at least {rules['min_length']} characters"
    
    if "max_length" in rules and len(value) > rules["max_length"]:
        return False, f"{field} must be at most {rules['max_length']} characters"
    
    # Pattern check
    if "pattern" in rules and not re.match(rules["pattern"], value):
        example = rules.get("example", "")
        return False, f"{field} format invalid. Example: {example}"
    
    # Invalid characters check
    if "invalid_chars" in rules:
        for char in rules["invalid_chars"]:
            if char in value:
                return False, f"{field} contains invalid character: {char}"
    
    return True, ""

