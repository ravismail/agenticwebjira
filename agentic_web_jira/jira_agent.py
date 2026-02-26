from jira import JIRA
import logging
import config
from logger import get_logger

logger = get_logger("JiraAgent")

class JiraAgent:
    def __init__(self, email=None):
        options = {"server": config.JIRA_URL}
        self.email = email or config.JIRA_EMAIL
        self.api_token = config.JIRA_API_TOKEN
        self.jira = None

    def connect(self, email):
        """Connects to Jira using Email and the Token from config."""
        try:
            self.jira = JIRA(basic_auth=(email, self.api_token), options={"server": config.JIRA_URL})
            user = self.jira.myself()
            logger.info(f"Connected to Jira as {user['displayName']}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {e}")
            return False

    def get_projects(self):
        """Returns a list of available projects."""
        try:
            projects = self.jira.projects()
            return [(p.key, p.name) for p in projects]
        except Exception as e:
            print(f"Failed to list projects: {e}")
            return []

    def get_issue_types(self, project_key):
        """Returns a list of issue types for a project."""
        try:
            # Get project meta data
            meta = self.jira.createmeta(projectKeys=project_key, expand='projects.issuetypes')
            if 'projects' in meta and len(meta['projects']) > 0:
                issuetypes = meta['projects'][0]['issuetypes']
                return [t['name'] for t in issuetypes]
            return []
        except Exception as e:
            print(f"Failed to get issue types: {e}")
            return []

    def create_story(self, project_key, summary, description, issue_type="Story"):
        """Creates a story in Jira."""
        if not self.jira:
            print("Not connected to Jira.")
            return None
        
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
        }
        
        try:
            new_issue = self.jira.create_issue(fields=issue_dict)
            print(f"Created issue {new_issue.key}: {summary}")
            return new_issue.key
        except Exception as e:
            print(f"Failed to create issue: {e}")
            return None

if __name__ == "__main__":
    # Test stub
    pass
