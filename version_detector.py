"""
Jira Version Detection and API Compatibility Layer
===================================================
Auto-detects Jira version, API capabilities, and field mappings.

Handles differences between:
- Jira Cloud (API v3)
- Jira Server 8.x/9.x (API v2/v3)
- Jira Data Center (API v2/v3)

Generated for On-Prem Jira Support
"""

from atlassian import Jira
from typing import Dict, Optional, Tuple
import re


class JiraVersionDetector:
    """
    Detects Jira version and provides compatibility information.
    
    REQUIREMENT: On-Prem Jira Support
    Handles API version differences and field name variations
    """
    
    def __init__(self, jira_client: Jira):
        self.jira = jira_client
        self._version_info = None
        self._api_version = None
        self._field_mappings = None
    
    def detect_jira_type(self) -> str:
        """
        Detect if Jira is Cloud or On-Premise.
        
        Returns:
            "Cloud" or "On-Premise"
        """
        try:
            server_info = self.jira.get('rest/api/2/serverInfo')
            deployment_type = server_info.get('deploymentType', '').lower()
            
            if 'cloud' in deployment_type:
                return "Cloud"
            else:
                return "On-Premise"
        except:
            # Fallback: Check URL pattern
            url = str(self.jira.url)
            if '.atlassian.net' in url:
                return "Cloud"
            else:
                return "On-Premise"
    
    def detect_version(self) -> Dict[str, str]:
        """
        Detect Jira version information.
        
        Returns:
            Dict with version, build, type, deployment_type
        """
        if self._version_info:
            return self._version_info
        
        try:
            server_info = self.jira.get('rest/api/2/serverInfo')
            
            self._version_info = {
                'version': server_info.get('version', 'Unknown'),
                'version_numbers': server_info.get('versionNumbers', []),
                'build_number': server_info.get('buildNumber', 'Unknown'),
                'deployment_type': server_info.get('deploymentType', 'Unknown'),
                'server_title': server_info.get('serverTitle', 'Jira'),
                'base_url': server_info.get('baseUrl', str(self.jira.url))
            }
            
            return self._version_info
        except Exception as e:
            # Fallback for restricted permissions
            return {
                'version': 'Unknown',
                'version_numbers': [],
                'build_number': 'Unknown',
                'deployment_type': 'Unknown',
                'server_title': 'Jira',
                'base_url': str(self.jira.url),
                'error': str(e)
            }
    
    def detect_api_version(self) -> str:
        """
        Detect which REST API version is available.
        
        Returns:
            "v3", "v2", or "unknown"
        """
        if self._api_version:
            return self._api_version
        
        # Try v3 first
        try:
            self.jira.get('rest/api/3/serverInfo')
            self._api_version = "v3"
            return "v3"
        except:
            pass
        
        # Fallback to v2
        try:
            self.jira.get('rest/api/2/serverInfo')
            self._api_version = "v2"
            return "v2"
        except:
            self._api_version = "unknown"
            return "unknown"
    
    def get_major_version(self) -> Optional[int]:
        """
        Extract major version number (e.g., 8 from "8.20.3").
        
        Returns:
            Major version number or None
        """
        version_info = self.detect_version()
        version_numbers = version_info.get('version_numbers', [])
        
        if version_numbers and len(version_numbers) > 0:
            return version_numbers[0]
        
        # Fallback: Parse version string
        version_str = version_info.get('version', '')
        match = re.match(r'^(\d+)', version_str)
        if match:
            return int(match.group(1))
        
        return None
    
    def supports_api_v3(self) -> bool:
        """Check if Jira instance supports API v3"""
        api_version = self.detect_api_version()
        return api_version == "v3"
    
    def get_field_mappings(self) -> Dict[str, str]:
        """
        Get field name mappings for this Jira version.
        
        Handles field name differences between versions:
        - resolutiondate vs resolved
        - duedate variations
        - custom field differences
        
        Returns:
            Dict mapping standard names to actual field names
        """
        if self._field_mappings:
            return self._field_mappings
        
        version_info = self.detect_version()
        major_version = self.get_major_version()
        
        # Default mappings (Cloud / Server 8+)
        mappings = {
            'resolutiondate': 'resolutiondate',
            'duedate': 'duedate',
            'created': 'created',
            'updated': 'updated',
            'status': 'status',
            'priority': 'priority',
            'assignee': 'assignee',
            'reporter': 'reporter',
            'summary': 'summary',
            'description': 'description',
            'parent': 'parent',
            'subtasks': 'subtasks'
        }
        
        # Adjustments for older versions
        if major_version and major_version < 8:
            # Older Jira versions might use different field names
            mappings['resolutiondate'] = 'resolved'
        
        self._field_mappings = mappings
        return mappings
    
    def get_projects_endpoint(self) -> str:
        """
        Get appropriate projects endpoint for this Jira version.
        
        Returns:
            API endpoint path for listing projects
        """
        if self.supports_api_v3():
            return 'rest/api/3/project/search'
        else:
            return 'rest/api/2/project'
    
    def get_issue_search_endpoint(self) -> str:
        """Get appropriate issue search endpoint"""
        if self.supports_api_v3():
            return 'rest/api/3/search'
        else:
            return 'rest/api/2/search'
    
    def translate_jql_field(self, field_name: str) -> str:
        """
        Translate standard field name to version-specific field name.
        
        Args:
            field_name: Standard field name (e.g., 'resolutiondate')
        
        Returns:
            Version-specific field name
        """
        mappings = self.get_field_mappings()
        return mappings.get(field_name, field_name)
    
    def get_compatibility_report(self) -> Dict:
        """
        Generate comprehensive compatibility report.
        
        Returns:
            Dict with version info, API support, field mappings, recommendations
        """
        version_info = self.detect_version()
        api_version = self.detect_api_version()
        jira_type = self.detect_jira_type()
        major_version = self.get_major_version()
        
        # Determine compatibility level
        if jira_type == "Cloud":
            compatibility = "Full"
            notes = "Jira Cloud fully supported"
        elif major_version and major_version >= 9:
            compatibility = "Full"
            notes = "Jira Server 9.x fully supported"
        elif major_version and major_version >= 8:
            compatibility = "High"
            notes = "Jira Server 8.x well supported"
        elif major_version and major_version >= 7:
            compatibility = "Medium"
            notes = "Jira Server 7.x has limited support - some fields may differ"
        else:
            compatibility = "Low"
            notes = "Older Jira version - compatibility issues expected"
        
        return {
            'jira_type': jira_type,
            'version': version_info.get('version'),
            'major_version': major_version,
            'api_version': api_version,
            'deployment_type': version_info.get('deployment_type'),
            'compatibility_level': compatibility,
            'notes': notes,
            'supports_api_v3': self.supports_api_v3(),
            'field_mappings': self.get_field_mappings(),
            'projects_endpoint': self.get_projects_endpoint(),
            'recommendations': self._get_recommendations(jira_type, major_version, api_version)
        }
    
    def _get_recommendations(self, jira_type: str, major_version: Optional[int], 
                           api_version: str) -> list:
        """Generate recommendations based on detected version"""
        recommendations = []
        
        if jira_type == "On-Premise":
            recommendations.append("Using on-premise Jira - ensure network connectivity")
            
            if api_version == "v2":
                recommendations.append("Using API v2 - some features may be limited")
            
            if major_version and major_version < 8:
                recommendations.append("Older Jira version detected - field name mappings applied")
                recommendations.append("Consider upgrading Jira for better compatibility")
        
        if api_version == "unknown":
            recommendations.append("Could not detect API version - using fallback methods")
        
        return recommendations


# Utility functions for easy access

def detect_jira_environment(jira_client: Jira) -> Tuple[str, str, Dict]:
    """
    Quick detection of Jira environment.
    
    Args:
        jira_client: Authenticated Jira client
    
    Returns:
        Tuple of (jira_type, api_version, compatibility_report)
    """
    detector = JiraVersionDetector(jira_client)
    
    jira_type = detector.detect_jira_type()
    api_version = detector.detect_api_version()
    report = detector.get_compatibility_report()
    
    return jira_type, api_version, report


def get_field_name(jira_client: Jira, standard_field: str) -> str:
    """
    Get version-specific field name.
    
    Args:
        jira_client: Authenticated Jira client
        standard_field: Standard field name (e.g., 'resolutiondate')
    
    Returns:
        Version-specific field name
    """
    detector = JiraVersionDetector(jira_client)
    return detector.translate_jql_field(standard_field)


def is_cloud_jira(jira_client: Jira) -> bool:
    """Quick check if Jira is Cloud"""
    detector = JiraVersionDetector(jira_client)
    return detector.detect_jira_type() == "Cloud"


def supports_advanced_features(jira_client: Jira) -> bool:
    """
    Check if Jira version supports advanced features.
    
    Returns:
        True if Jira is Cloud or Server 8+
    """
    detector = JiraVersionDetector(jira_client)
    jira_type = detector.detect_jira_type()
    major_version = detector.get_major_version()
    
    if jira_type == "Cloud":
        return True
    
    if major_version and major_version >= 8:
        return True
    
    return False