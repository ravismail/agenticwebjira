import config
from jira import JIRA
import sys

def test_connection():
    print("Starting Jira connection test...")
    try:
        print(f"Connecting to {config.JIRA_URL} with {config.JIRA_EMAIL}")
        # Basic auth with email and token
        jira = JIRA(
            basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN), 
            options={"server": config.JIRA_URL}
        )
        print("JIRA object created. Fetching myself...")
        user = jira.myself()
        print(f"Success! Connected as {user.get('displayName')}")
    except Exception as e:
        print(f"Caught exception: {e}")

if __name__ == "__main__":
    test_connection()
    print("Test finished.")
