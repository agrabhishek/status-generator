"""
Authentication Protocols for Jira Status Generator
===================================================
Handles secure credential loading and Jira authentication.

Generated: 2025-10-19 18:28:32
"""

import streamlit as st
import os
from atlassian import Jira
from typing import Dict, Optional

def load_secure_credentials() -> Dict[str, Optional[str]]:
    """
    Load credentials from Streamlit secrets or environment variables.
    
    REQUIREMENT: Compliance and Security
    Credentials hidden from public repo using Streamlit secrets.
    
    Returns:
        Dict with jira_email, jira_token, jira_url, groq_api_key
    """
    return {
        'jira_email': st.secrets.get("jira", {}).get("email") or os.getenv("JIRA_EMAIL"),
        'jira_token': st.secrets.get("jira", {}).get("api_token") or os.getenv("JIRA_API_TOKEN"),
        'jira_url': st.secrets.get("jira", {}).get("default_url") or os.getenv("JIRA_DEFAULT_URL"),
        'groq_api_key': st.secrets.get("groq", {}).get("api_key") or os.getenv("GROQ_API_KEY")
    }


def authenticate_jira(url: str, email: str, token: str) -> Jira:
    """
    Authenticate with Jira and return client.
    
    REQUIREMENT: Jira Integration - Secure connection
    
    Args:
        url: Jira instance URL
        email: User email
        token: API token
    
    Returns:
        Authenticated Jira client
    
    Raises:
        Exception if authentication fails
    """
    client = Jira(url=url, username=email, password=token, cloud=True)
    
    # Verify authentication
    myself = client.myself()
    
    return client


def validate_jira_credentials(url: str, email: str, token: str) -> tuple[bool, str]:
    """
    Validate Jira credentials without creating persistent connection.
    
    Returns:
        (is_valid, error_message)
    """
    try:
        client = Jira(url=url, username=email, password=token, cloud=True)
        myself = client.myself()
        return True, f"Authenticated as {myself.get('displayName')}"
    except Exception as e:
        return False, str(e)
