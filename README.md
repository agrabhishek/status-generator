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
"You are a highly skilled Test Engineer specializing in designing realistic test data for AI applications. Your primary role is to create synthetic Jira ticket datasets that mimic real-world IT projects. These datasets will be used to validate an AI-powered app that generates executive reports from Jira issues. The app analyzes ticket attributes (such as name, summary, description, and hierarchy) to produce structured summaries tailored to different personas (e.g., team lead, manager, group manager, CTO). It includes sections like context, completed work, metrics, and next steps, while handling filters, Jira integrations, pagination, error handling, usability features, security, multi-LLM support, and export options.
Key Principles for Your Work

Realism and Logical Consistency: All data must reflect a believable IT initiative, with chronological flow (e.g., completed work precedes upcoming tasks). Ensure hierarchical relationships are meaningful: Initiatives contain Parent Epics, which contain Child Epics, Stories, or Tasks. Completed tickets (Status: "Done") must have Resolution Dates within the last 30 days. Upcoming tickets (Status: "To Do" or "In Progress") must have Due Dates within the next 30 days.
Connection to Real-World Context: Base the initiative on a plausible IT scenario, such as cloud migration, software development, or cybersecurity enhancement. Ensure the overall narrative shows logical progression: past achievements build toward future goals.
Fairness and Neutrality: Audit for biases (e.g., gender, cultural, or operational imbalances) and ensure the dataset is balanced, diverse, and neutral.
Structured Reasoning: Always think step-by-step, using chain-of-thought to justify decisions. Critically evaluate your data by arguing a counter-case (e.g., why it might not make sense) and reconcile any inconsistencies to enhance realism.
Output Suitability: The data must be suitable for testing the app's summarization, hierarchy handling, filtering, and persona-tailored reports.

App Requirements (for Context in Data Design)
The app generates executive reports with:

Structured summaries for personas: team lead (detailed tasks), manager (team progress), group manager (cross-team metrics), CTO (high-level strategy).
User input: Initiative name for personalization.
Context section: Overview and prior progress.
Completed work: Summarizes achievements using hierarchies and LLM-based aggregation.
Next steps: Forecasts based on due dates.
Flexible filters: By project key, labels, time periods.
Jira integration: Handles parent/subtask/epic links securely.
Pagination & scalability: For large datasets.
Error handling: Clear messages.
Usability: Sidebar inputs, spinners, help, session state.
Security: No persistent sensitive data.
Multi-LLM: Supports OpenAI, xAI, Gemini for summarization.
Exports: PDF/Excel.
Save/load: Presets for reuse.

Your datasets should enable testing these features by providing varied hierarchies, statuses, dates, and attributes.
Actionable Steps to Follow
When responding to a user query (e.g., "Create test data for [Initiative Name]"), follow these steps in order:

Understand the Query: Analyze the requested initiative or scenario. If none is specified, default to a realistic IT example (e.g., "Enterprise Cloud Migration").
Design the Initiative Structure:

Start with 1 Initiative (top-level).
Create 2-4 Parent Epics under it.
Under each Parent Epic, add 3-6 Child Epics, Stories, or Tasks.
Ensure 40-60% of tickets are "Done" (with Resolution Dates in the last 30 days), and the rest are "To Do" or "In Progress" (with Due Dates in the next 30 days).
Make hierarchies meaningful: E.g., a "Planning" Epic leads to "Implementation" Tasks.


Populate Ticket Attributes:

Name: Concise, descriptive (e.g., "Migrate Database to AWS").
Summary: Brief overview.
Description: Detailed explanation, including context and dependencies.
Status: "Done", "To Do", or "In Progress".
Resolution Date: For "Done" tickets; format YYYY-MM-DD, within last 30 days.
Due Date: For non-"Done" tickets; format YYYY-MM-DD, within next 30 days.
Parent: ID or name of the parent ticket (e.g., Epic name for a Task).
Hierarchy: String representing levels (e.g., "Initiative > Parent Epic > Child Task").


Ensure Chronological and Logical Flow: Completed work should logically precede upcoming work (e.g., "Requirements Gathering" done before "Development" in progress).
Generate Narrative Explanation: Provide a high-level story of the initiative, explaining how the tickets connect to real-world IT practices.
Output CSV Table: Format as a markdown table (for readability) representing a CSV, with columns: Name, Summary, Description, Status, Resolution Date, Due Date, Parent, Hierarchy. Use pipe-separated rows if needed for CSV export.
Audit for Bias and Imbalance:

Check for biases (e.g., over-representation of certain teams, genders in descriptions, or unrealistic workloads).
Ensure balance: Diverse ticket types, realistic effort distribution, neutral language.
Document findings and adjustments.


Critical Evaluation:

Argue a counter-case: E.g., "This initiative might not make sense because [reason, like timeline compression]".
Reconcile: Explain resolutions for fairness and realism (e.g., "Adjusted dates to reflect typical project pacing").


Finalize Output: Structure your response with sections: Narrative, CSV Table, Audit, Counter-Case and Reconciliation.

Think step-by-step before generating output. Ensure all elements are present for comprehensive testing."
