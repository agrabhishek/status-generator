# Troubleshooting Guide

## 401 Unauthorized Error

If you're getting a `401 Client Error: Unauthorized` error, here are the most common causes and solutions:

### 1. **Incorrect Field Names in secrets.toml** (Most Common)

The application expects specific field names. Make sure your `.streamlit/secrets.toml` uses these **exact** names:

✅ **CORRECT:**
```toml
[jira]
jira_email = "your-email@company.com"
jira_token = "your-api-token"
jira_default_url = "https://yourcompany.atlassian.net"

[groq]
groq_api_key = "gsk_your-groq-key"
```

❌ **INCORRECT:**
```toml
[jira]
email = "your-email@company.com"          # Missing 'jira_' prefix
api_token = "your-api-token"              # Missing 'jira_' prefix
default_url = "https://yourcompany.atlassian.net"  # Missing 'jira_' prefix

[groq]
api_key = "gsk_your-groq-key"             # Missing 'groq_' prefix
```

### 2. **Invalid or Expired API Token**

**For Jira Cloud:**
- Generate a new API token at: https://id.atlassian.com/manage-profile/security/api-tokens
- Make sure you copy the ENTIRE token (they're long!)
- Check for extra spaces or line breaks when pasting
- Tokens don't expire automatically, but can be revoked

**Test your token:**
```bash
curl -u your-email@company.com:YOUR_API_TOKEN https://yourcompany.atlassian.net/rest/api/2/myself
```

If this returns 401, your token is invalid.

### 3. **Email Mismatch**

The email in `secrets.toml` must EXACTLY match your Atlassian account email:
- ✅ Check capitalization (though usually case-insensitive)
- ✅ No typos
- ✅ Must be the email you use to log into Jira

### 4. **Wrong Jira URL**

**For Jira Cloud:**
```toml
jira_default_url = "https://yourcompany.atlassian.net"
```

Common mistakes:
- ❌ `https://yourcompany.atlassian.net/` (trailing slash)
- ❌ `https://yourcompany.atlassian.net/browse/PROJECT-123` (includes path)
- ❌ `yourcompany.atlassian.net` (missing https://)

### 5. **Account Permissions**

Verify you have access to the projects you're querying:
- Log into Jira via browser
- Try to access the project manually
- Check if your account has "Browse Projects" permission

### 6. **Whitespace Issues**

Check for invisible characters:
```toml
# BAD - has trailing space after token
jira_token = "your-token-here "

# GOOD
jira_token = "your-token-here"
```

## Quick Validation Steps

1. **Stop the app** (Ctrl+C)
2. **Update `.streamlit/secrets.toml`** with correct field names
3. **Restart the app**: `streamlit run app.py`
4. The app will now validate credentials on startup and show helpful errors

## Still Having Issues?

### Check the secrets file is being loaded:
```python
import streamlit as st
print(st.secrets)  # Should show your configuration
```

### Test authentication manually:
```python
from atlassian import Jira

jira = Jira(
    url="https://yourcompany.atlassian.net",
    username="your-email@company.com",
    password="your-api-token",
    cloud=True
)

try:
    user = jira.myself()
    print(f"✅ Authenticated as: {user['displayName']}")
except Exception as e:
    print(f"❌ Failed: {e}")
```

### Environment Variables (Alternative)
If you don't want to use secrets.toml, set environment variables:

**Windows (PowerShell):**
```powershell
$env:JIRA_EMAIL="your-email@company.com"
$env:JIRA_API_TOKEN="your-token"
$env:JIRA_DEFAULT_URL="https://yourcompany.atlassian.net"
```

**Linux/Mac:**
```bash
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-token"
export JIRA_DEFAULT_URL="https://yourcompany.atlassian.net"
```

## Contact

If you're still stuck after trying these steps, please open an issue with:
1. The exact error message (remove sensitive data)
2. Your Jira type (Cloud or On-Premise)
3. Steps you've already tried
