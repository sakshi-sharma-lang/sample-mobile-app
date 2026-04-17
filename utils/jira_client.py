import requests
from pathlib import Path


class JiraClient:
    def __init__(self, settings):
        self.base_url = settings.base_url
        self.email = settings.email
        self.api_token = settings.api_token
        self.project_key = settings.project_key

    def create_issue_for_test_failure(
        self,
        test_name,
        error_message,
        screenshot_path=None,
        logs_path=None
    ):
        url = f"{self.base_url}/rest/api/3/issue"

        auth = (self.email, self.api_token)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        description_content = [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": f"Test Failed: {test_name}"}
                ],
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": error_message[:2000]}
                ],
            }
        ]

        if screenshot_path:
            description_content.append({
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": f"Screenshot: {screenshot_path}"}
                ],
            })

        if logs_path:
            description_content.append({
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": f"Logs: {logs_path}"}
                ],
            })

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": f"Automation Failure: {test_name}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": description_content
                },
                "issuetype": {"name": "Bug"}
            }
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=auth
        )

        print("Jira Response:", response.status_code, response.text)