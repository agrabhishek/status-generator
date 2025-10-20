"""
Unit tests for jira_core.py
============================
Generated: 2025-10-19 18:28:32
"""

import pytest
from unittest.mock import Mock
from jira_core import JQLBuilder, get_next_period_dates


class TestJQLBuilder:
    """Test JQL query construction"""
    
    def test_achievements_query(self):
        """Test resolutiondate query for achievements"""
        jql = JQLBuilder.for_achievements("AWS", period="last_week")
        assert "resolutiondate >=" in jql
        assert "project = AWS" in jql
    
    def test_next_steps_query(self):
        """Test duedate query for next steps"""
        jql = JQLBuilder.for_next_steps("AWS", period="last_week")
        assert "duedate >=" in jql
        assert "project = AWS" in jql
    
    def test_multiple_projects(self):
        """Test multiple projects"""
        jql = JQLBuilder.for_achievements("AWS,CLOUD,DATA")
        assert "project in" in jql


class TestDateCalculations:
    """Test period calculations"""
    
    def test_next_week(self):
        """Test calculating next week"""
        next_period = get_next_period_dates("last_week")
        assert " to " in next_period
    
    def test_custom_period(self):
        """Test custom period extension"""
        next_period = get_next_period_dates("2025-10-01 to 2025-10-07")
        assert next_period == "2025-10-07 to 2025-10-13"


# TODO: Add more tests for:
# - JiraClient.fetch_issues with pagination
# - ReportGenerator with different personas
# - Error handling scenarios
