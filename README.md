# status-generator
Generate Human readable Status Reports from jira tickets

# Copyright 2025 Abhishek Agrawal (https://www.linkedin.com/in/abhishekagrawal/)
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0

streamlit
pandas
atlassian-python-api
requests


Requirements


Generate Executive Reports: The app must produce structured status reports for Jira initiatives, tailored for different personas (e.g., team lead, manager, group manager, CTO), including key sections like context, completed work, metrics, and next steps.

User Input for Initiative Name: Users must provide a name for the initiative (e.g., "Q4 AWS Migration") to label reports and ensure context is personalized.
Context Section: Reports must include a "Context" section with two parts:
An overview (1-2 sentences) derived from the highest-level parent epic's summary and description in Jira.

Prior progress, summarizing work completed before the current reporting period.
Completed Work in Current Period: Summarize achievements from tickets completed during the user-specified time period, using hierarchical relationships (parents for high-level context, children for details), enhanced by LLM summarization.

Next Steps Section: Automatically predict and list upcoming tasks based on tickets targeted for the next reporting period (same duration as current, starting after current end), fetched from Jira.

Flexible Criteria Input: Allow users to specify Jira filters including project key, labels, time period (e.g., last week, custom dates), and time field (created/updated) to define the current reporting scope.


Persona-Specific Tailoring: Adapt report content and format based on selected persona, focusing on details for team leads, summaries for managers, metrics for group managers, and high-level overviews for CTOs.


Jira Integration: Securely connect to Jira Cloud using email and API token to fetch issues, including hierarchy fields (parent, subtasks, epics) and descriptions for accurate context and summaries.

Pagination and Scalability: Handle large datasets (up to 1000+ issues) with pagination to ensure reliable fetching without performance issues.
Error Handling and Feedback: Display clear error messages (e.g., invalid inputs, API failures) and success indicators (e.g., issues fetched, report generated) to guide users.

Usability Features: Include intuitive UI elements like sidebar inputs, progress spinners, expandable help sections, and auto-calculation of next periods for a seamless experience.

No Data Loss on Refresh: Use session state to persist inputs and reports during browser refreshes for uninterrupted workflow.

Compliance and Security: Do not store sensitive data (e.g., API keys) persistently; use password inputs and local JSON for non-sensitive presets only.

Additional requirements:
Multi-LLM Integration: Provide options to use xAI, OpenAI, or Gemini for AI-powered summaries of completed work, with user-provided API keys for the selected provider.
Export Options: Enable export of reports to PDF (professional formatting with headers/sections) and Excel (multiple sheets for issues, next steps, and context).
Save and Load Criteria: Users must be able to save input criteria (e.g., initiative name, filters, persona, LLM choice) as presets and reload them for quick reuse in future sessions.
