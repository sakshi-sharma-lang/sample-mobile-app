import requests
import json
import base64
from pathlib import Path
from utils.config import JiraSettings

class JiraClient:
    def __init__(self, settings: JiraSettings):
        # Now correctly accepts only 1 positional argument
        self.settings = settings

    def create_issue_for_test_failure(self, test_name, error_message, screenshot_path=None):
        if not self.settings.enabled:
            return

        api_url = f"{self.settings.base_url.rstrip('/')}/rest/api/3/issue"
        auth_str = f"{self.settings.email}:{self.settings.api_token}"
        auth_header = base64.b64encode(auth_str.encode()).decode()

        payload = {
            "fields": {
                "project": {"key": self.settings.project_key},
                "summary": f"Mobile Failure: {test_name}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": error_message[:2000]}]
                    }]
                },
                "issuetype": {"name": self.settings.issue_type}
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
            print(f"Jira API Error: {response.text}")

    def attach_screenshot(self, issue_key, path, auth_header):
        url = f"{self.settings.base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/attachments"
        headers = {"Authorization": f"Basic {auth_header}", "X-Atlassian-Token": "no-check"}
        with open(path, "rb") as f:
            requests.post(url, headers=headers, files={"file": f})