import requests
import json
import base64

class JiraClient:
    def __init__(self, settings):
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
                    "content": [{"type": "paragraph", "content": [{"text": error_message[:2000], "type": "text"}]}]
                },
                "issuetype": {"name": self.settings.issue_type}
            }
        }

        response = requests.post(api_url, data=json.dumps(payload), headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        })
        
        if response.status_code != 201:
            print(f"Jira API Error: {response.text}")