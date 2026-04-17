import requests
import os

def create_jira_ticket(test_name, error):
    url = f"{os.getenv('JIRA_URL')}/rest/api/3/issue"

    auth = (os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))

    payload = {
        "fields": {
            "project": {"key": os.getenv("JIRA_PROJECT_KEY")},
            "summary": f"Test Failed: {test_name}",
            "description": str(error),
            "issuetype": {"name": "Bug"}
        }
    }

    res = requests.post(url, json=payload, auth=auth)
    print("Jira:", res.status_code, res.text)