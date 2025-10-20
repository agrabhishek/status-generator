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
email = "your-email@company.com"
api_token = "your-jira-api-token"
default_url = "https://yourcompany.atlassian.net"

[groq]
api_key = "gsk_your-groq-api-key"
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
├── requirements.txt
└── tests/
    └── test_jira_core.py
```

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

## License

MIT

Generated: 2025-10-19 18:28:32
