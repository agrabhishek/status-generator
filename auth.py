"""
Authentication Protocols for Jira Status Generator
===================================================
Handles secure credential loading and Jira authentication.
Supports both Jira Cloud and On-Premise installations.

REQUIREMENTS ADDRESSED:
- Jira Integration: Secure connection with email+token or username+password
- Compliance and Security: Credentials hidden from public repo
- On-Premise Support: Username/password authentication, SSL options

Generated: 2025-10-19
"""

import streamlit as st
import os
from atlassian import Jira
from typing import Dict, Optional, Tuple
import requests


def load_secure_credentials() -> Dict[str, Optional[str]]:
    """
    Load credentials from Streamlit secrets or environment variables.
    
    REQUIREMENT: Compliance and Security
    Credentials hidden from public repo using Streamlit secrets.
    
    Returns:
        Dict with jira_email, jira_token, jira_url, groq_api_key
    """
    return {
        'jira_email': st.secrets.get("jira", {}).get("jira_email") or os.getenv("JIRA_EMAIL"),
        'jira_token': st.secrets.get("jira", {}).get("jira_token") or os.getenv("JIRA_API_TOKEN"),
        'jira_url': st.secrets.get("jira", {}).get("jira_default_url") or os.getenv("JIRA_DEFAULT_URL"),
        'groq_api_key': st.secrets.get("groq", {}).get("groq_api_key") or os.getenv("GROQ_API_KEY")
    }


def authenticate_jira_cloud(url: str, email: str, token: str) -> Jira:
    """
    Authenticate with Jira Cloud using email and API token.
    
    REQUIREMENT: Jira Integration - Secure Cloud connection
    
    Args:
        url: Jira Cloud URL (*.atlassian.net)
        email: User email address
        token: API token (not password)
    
    Returns:
        Authenticated Jira client
    
    Raises:
        Exception if authentication fails
    """
    client = Jira(
        url=url, 
        username=email, 
        password=token, 
        cloud=True
    )
    
    # Verify authentication
    myself = client.myself()
    
    return client


def authenticate_jira_onprem(url: str, username: str, password: str, 
                             verify_ssl: bool = True) -> Jira:
    """
    Authenticate with Jira On-Premise using username and password.
    
    REQUIREMENT: On-Premise Support
    
    Args:
        url: Jira Server URL (can be any domain/IP)
        username: Jira username (not email)
        password: User password or Personal Access Token
        verify_ssl: Whether to verify SSL certificates (False for self-signed)
    
    Returns:
        Authenticated Jira client
    
    Raises:
        Exception if authentication fails
    
    Security Note:
        Setting verify_ssl=False is insecure and should only be used with
        self-signed certificates in trusted environments.
    """
    # Disable SSL warnings if verification is turned off
    if not verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    client = Jira(
        url=url,
        username=username,
        password=password,
        cloud=False,
        verify_ssl=verify_ssl
    )
    
    # Verify authentication
    try:
        myself = client.myself()
    except Exception as e:
        # Try to provide helpful error message
        if "401" in str(e):
            raise Exception("Authentication failed. Check username and password.")
        elif "certificate" in str(e).lower():
            raise Exception("SSL certificate error. Try disabling SSL verification.")
        elif "connection" in str(e).lower():
            raise Exception("Cannot connect to server. Check URL and network/VPN.")
        else:
            raise
    
    return client


def authenticate_jira(url: str, username: str, credential: str, 
                     jira_type: str = "Cloud", 
                     verify_ssl: bool = True) -> Jira:
    """
    Universal authentication method for both Cloud and On-Premise.
    
    REQUIREMENT: Flexible authentication for both deployment types
    
    Args:
        url: Jira instance URL
        username: Email (Cloud) or Username (On-Premise)
        credential: API Token (Cloud) or Password (On-Premise)
        jira_type: "Cloud" or "On-Premise"
        verify_ssl: SSL verification (only applies to On-Premise)
    
    Returns:
        Authenticated Jira client
    """
    if jira_type == "Cloud":
        return authenticate_jira_cloud(url, username, credential)
    else:
        return authenticate_jira_onprem(url, username, credential, verify_ssl)


def validate_jira_credentials(url: str, username: str, credential: str,
                              jira_type: str = "Cloud",
                              verify_ssl: bool = True) -> Tuple[bool, str]:
    """
    Validate Jira credentials without creating persistent connection.
    
    Args:
        url: Jira instance URL
        username: Email (Cloud) or Username (On-Premise)
        credential: API Token (Cloud) or Password (On-Premise)
        jira_type: "Cloud" or "On-Premise"
        verify_ssl: SSL verification (only for On-Premise)
    
    Returns:
        (is_valid, message)
        - message contains user name if valid
        - message contains error description if invalid
    """
    try:
        client = authenticate_jira(url, username, credential, jira_type, verify_ssl)
        myself = client.myself()
        return True, f"Authenticated as {myself.get('displayName')}"
    except Exception as e:
        return False, str(e)


def detect_jira_type(url: str) -> str:
    """
    Auto-detect if URL is Jira Cloud or On-Premise.
    
    Args:
        url: Jira URL
    
    Returns:
        "Cloud" if *.atlassian.net, otherwise "On-Premise"
    """
    if ".atlassian.net" in url:
        return "Cloud"
    else:
        return "On-Premise"


def test_jira_connectivity(url: str, verify_ssl: bool = True) -> Tuple[bool, str]:
    """
    Test if Jira server is reachable before authentication.
    
    Useful for diagnosing connection issues before credentials are checked.
    
    Args:
        url: Jira instance URL
        verify_ssl: Whether to verify SSL
    
    Returns:
        (is_reachable, message)
    """
    try:
        # Try to reach the base URL
        response = requests.get(
            url,
            timeout=10,
            verify=verify_ssl,
            allow_redirects=True
        )
        
        if response.status_code < 500:
            return True, f"Server reachable (status: {response.status_code})"
        else:
            return False, f"Server error (status: {response.status_code})"
            
    except requests.exceptions.SSLError:
        return False, "SSL certificate error. Try disabling SSL verification."
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect. Check URL and network/VPN connection."
    except requests.exceptions.Timeout:
        return False, "Connection timeout. Server may be slow or unreachable."
    except Exception as e:
        return False, f"Connection test failed: {str(e)}"


def get_jira_version(client: Jira) -> Optional[str]:
    """
    Get Jira server version.
    
    Useful for determining API compatibility.
    
    Args:
        client: Authenticated Jira client
    
    Returns:
        Version string (e.g., "8.20.3") or None if unable to detect
    """
    try:
        server_info = client.get('rest/api/2/serverInfo')
        return server_info.get('version')
    except:
        return None


def supports_api_v3(client: Jira) -> bool:
    """
    Check if Jira instance supports REST API v3.
    
    Args:
        client: Authenticated Jira client
    
    Returns:
        True if v3 is supported, False otherwise
    """
    try:
        # Try to access a v3 endpoint
        client.get('rest/api/3/serverInfo')
        return True
    except:
        return False