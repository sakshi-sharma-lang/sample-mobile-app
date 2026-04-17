import requests
import os

def create_pr():
    url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPO')}/pulls"

    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }

    payload = {
        "title": "Auto PR after tests passed",
        "head": os.getenv("SOURCE_BRANCH"),
        "base": os.getenv("TARGET_BRANCH"),
        "body": "Auto-created PR"
    }

    res = requests.post(url, json=payload, headers=headers)
    print("PR:", res.status_code, res.text)