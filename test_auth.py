"""Quick test script to verify Jira authentication without Streamlit"""
from atlassian import Jira

# Read from secrets file
import toml
secrets = toml.load('.streamlit/secrets.toml')

url = secrets['jira']['jira_default_url']
email = secrets['jira']['jira_email']
token = secrets['jira']['jira_token']

print(f"Testing authentication...")
print(f"URL: {url}")
print(f"Email: {email}")
print(f"Token: {token[:20]}...{token[-20:]}")

try:
    jira = Jira(
        url=url,
        username=email,
        password=token,
        cloud=True
    )
    
    user = jira.myself()
    print(f"\n✅ SUCCESS!")
    print(f"Authenticated as: {user['displayName']}")
    print(f"Account ID: {user['accountId']}")
    print(f"Email: {user['emailAddress']}")
    
except Exception as e:
    print(f"\n❌ FAILED!")
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("1. Token is invalid or expired")
    print("2. Email doesn't match your Atlassian account")
    print("3. Token doesn't have required permissions")
    print("\nGenerate a new token at:")
    print("https://id.atlassian.com/manage-profile/security/api-tokens")
