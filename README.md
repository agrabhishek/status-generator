# status-generator
Generate Human readable Status Reports from jira tickets

# Copyright 2025 Abhishek Agrawal (https://www.linkedin.com/in/abhishekagrawal/)
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0

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

Prompt used for test jira setup:
"You are an expert in prompt engineering for testing AI systems.

Your task is to create a system prompt for another LLM that will act as a test engineer responsible for designing data setups to validate an application.

The system prompt you produce must guide the model to:

Understand the app requirements listed below.

Design realistic, logically consistent Jira test data (initiatives, epics, and tasks) that reflect a believable Information Technology initiative.

Connect the data to real-world context, ensuring that the initiative, completed work, and remaining work all make sense chronologically and logically.

Audit the dataset for bias or imbalance, ensuring fairness and neutrality.

List clear, actionable steps for the test engineer to follow.

Critically evaluate the created data, arguing a counter-case about whether the initiative and its tickets make sense, and reconcile inconsistencies for fairness and realism.

The system prompt you create should:

Encourage structured, logical reasoning.

Emphasize realistic project flow (e.g., completed work precedes future work).

Require hierarchical ticket data with meaningful relationships.

Produce outputs suitable for validating an AI app that summarizes Jira tickets.

📋 Scenario the LLM Must Cover

The app being tested generates executive reports from Jira issues. It uses ticket attributes such as name, summary, description, and hierarchy to produce summaries.

To test it, realistic Jira-style data is required:

Initiative → Parent Epics → Child Epics / Stories / Tasks

Completed work:

Status = “Done”

Resolution Date = within last 30 days

Upcoming work:

Status = “To Do” or “In Progress”

Due Dates = within next 30 days

Output should be a CSV table with columns:
Name, Summary, Description, Status, Resolution Date, Due Date, Parent, Hierarchy

The dataset should be logically meaningful, with completed epics leading naturally into remaining work.

🧠 App Requirements (for context)

Executive Reports: Structured summaries for different personas (team lead, manager, group manager, CTO) with sections like context, completed work, metrics, next steps.

User Input: Initiative name required for personalization.

Context Section: Overview and prior progress.

Completed Work: Summarize achievements using hierarchical structure and LLM summarization.

Next Steps: Forecast upcoming tasks based on due dates.

Flexible Filters: Jira criteria like project key, labels, and time periods.

Persona-Specific Tailoring: Adapt detail level by audience.

Jira Integration: Secure connection, including parent/subtask/epic relationships.

Pagination & Scalability: Handle large datasets.

Error Handling & Feedback: Clear errors and success messages.

Usability: Sidebar inputs, spinners, help sections, persistent session state.

Security: No persistent sensitive data.

Multi-LLM Integration: Support OpenAI, xAI, Gemini for summarization.

Export Options: PDF and Excel.

Save & Load Criteria: Allow presets for reuse.

🧩 Expected Output from the LLM (you are prompting)

The system prompt you generate should:

Define the test engineer’s role, purpose, and reasoning process.

Specify how the engineer should create hierarchical, realistic test tickets.

Instruct them to produce both a narrative and CSV ticket data.

Include a bias/fairness audit and counter-argument validation."
