import requests
import json
import base64
from pathlib import Path
from utils.config import Config

class JiraClient:
    def __init__(self):
        # Maps to the env variables in the workflow
        self.url = Config.JIRA_BASE_URL
        self.email = Config.JIRA_EMAIL
        self.token = Config.JIRA_API_TOKEN
        self.project = Config.JIRA_PROJECT_KEY
        self.issue_type = os.getenv("JIRA_ISSUE_TYPE", "Task")

    def create_issue_for_test_failure(self, test_name, error_message, screenshot_path=None):
        if os.getenv("ENABLE_JIRA", "false").lower() != "true":
            return

        api_url = f"{self.url.rstrip('/')}/rest/api/3/issue"
        auth_str = f"{self.email}:{self.token}"
        auth_header = base64.b64encode(auth_str.encode()).decode()

        payload = {
            "fields": {
                "project": {"key": self.project},
                "summary": f"Mobile Failure: {test_name}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": f"Error: {error_message}"}]
                    }]
                },
                "issuetype": {"name": self.issue_type}
            }
        }

        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 201:
            issue_key = response.json().get("key")
            if screenshot_path and Path(screenshot_path).exists():
                self.attach_screenshot(issue_key, screenshot_path, auth_header)
            return issue_key
        else:
            print(f"Jira Error: {response.text}")

    def attach_screenshot(self, issue_key, path, auth_header):
        url = f"{self.url.rstrip('/')}/rest/api/3/issue/{issue_key}/attachments"
        headers = {"Authorization": f"Basic {auth_header}", "X-Atlassian-Token": "no-check"}
        with open(path, "rb") as f:
            requests.post(url, headers=headers, files={"file": f})
