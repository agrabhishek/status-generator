# Jira AI Status Generator

Generate executive reports from Jira with AI-powered summaries.

## Features

- ✅ 4-section executive reports (Context, Achievements, Metrics, Next Steps)
- ✅ Multi-LLM support (Groq free-tier, OpenAI, xAI, Gemini)
- ✅ Persona-specific formatting (Team Lead, Manager, Group Manager, CTO)
- ✅ PDF and Excel export
- ✅ Secure credential management
- ✅ Dynamic Groq model selection

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Secrets

Create `.streamlit/secrets.toml`:

```toml
[jira]
jira_email = "your-email@company.com"
jira_token = "your-jira-api-token"
jira_default_url = "https://yourcompany.atlassian.net"

[groq]
groq_api_key = "gsk_your-groq-api-key"
```

### 3. Run Application

```bash
streamlit run app.py
```

## Project Structure

```
jira-status-generator/
├── config.py              # All prompts, settings, constants
├── auth.py                # Authentication protocols
├── jira_core.py          # Business logic (Jira API, JQL, reports)
├── llm_integrations.py   # LLM providers (Groq, OpenAI, xAI, Gemini)
├── app.py                # Streamlit UI
├── requirements.
├── Version_detector.py
└── tests/
    └── test_jira_core.py
```
## Backlog
- **Log number of calls**
- **add planner, executer, evaluator flow**
- **Pull custom ticket types, figure hierarchy and use to customize system prompt**
- **Improve jira test project setup**
- **Integrate with platforms other than Jira**

## Getting API Keys

- **Groq (Free):** https://console.groq.com/keys
- **Jira:** https://id.atlassian.com/manage-profile/security/api-tokens
- **OpenAI:** https://platform.openai.com/api-keys

## Deployment (Streamlit Cloud)

1. Push code to GitHub (secrets are gitignored)
2. Go to https://share.streamlit.io
3. Connect your repository
4. In App Settings → Secrets, paste your secrets.toml content
5. Deploy!

## Security

⚠️ **NEVER commit `.streamlit/secrets.toml` or `.env` files**

- Secrets are gitignored by default
- Use Streamlit Cloud secrets UI for deployment
- API keys are never logged or displayed

## Disclaimer

⚠️ **Important: Read Before Using**

This is an **open-source project provided "as-is"** with no warranties or guarantees. 

**Please note:**
- **Limited Testing:** This tool has undergone limited testing. Always test with your specific Jira setup before relying on it for critical reports.
- **AI-Generated Content:** Reports use AI (LLMs) to generate summaries. **Always proof-read and validate AI-generated content** before sharing with stakeholders.
- **Use at Your Own Risk:** The accuracy of reports depends on your Jira data quality and the LLM's interpretation. Verify all data before making business decisions.
- **No Guarantees:** I do not guarantee accuracy, reliability, or fitness for any particular purpose.
- **Starting Point, Not Final Output:** Use generated reports as a foundation to build upon, not as final deliverables.

**Recommended Practice:**
1. Generate your report
2. Review all data points for accuracy
3. Verify AI summaries match actual work completed
4. Edit/customize as needed for your audience
5. Double-check metrics and ticket counts

**Contributions Welcome:** This is early-stage software. Bug reports, feature requests, and PRs are appreciated on GitHub!

## License

This project is licensed under the [MIT License](LICENSE).
© 2025 Abhishek Agrawal.  
You are free to use, modify, and distribute this software under the terms of the MIT License.
For inquiries or collaboration, connect with me on [LinkedIn](https://www.linkedin.com/in/abhishekagrawal03/).

