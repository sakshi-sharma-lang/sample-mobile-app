from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

import requests

from utils.config import JiraSettings
from utils.logger import get_logger


log = get_logger(__name__)


class JiraClient:
    def __init__(self, settings: JiraSettings) -> None:
        self.settings = settings
        self.base_url = settings.base_url.rstrip("/")
        self.session = requests.Session()
        auth_token = base64.b64encode(f"{settings.email}:{settings.api_token}".encode("utf-8")).decode("utf-8")
        self.session.headers.update(
            {
                "Authorization": f"Basic {auth_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        self._validate()

    def _validate(self) -> None:
        missing = [
            name
            for name, value in {
                "JIRA_BASE_URL": self.settings.base_url,
                "JIRA_EMAIL": self.settings.email,
                "JIRA_API_TOKEN": self.settings.api_token,
                "JIRA_PROJECT_KEY": self.settings.project_key,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Missing Jira settings: {', '.join(missing)}")

    def create_issue_for_test_failure(
        self,
        test_name: str,
        error_message: str,
        screenshot_path: Path | None = None,
        logs_path: Path | None = None,
    ) -> str:
        issue_key = self.create_issue(
            summary=f"Mobile automation failure: {test_name}",
            description=self._failure_description(test_name, error_message, screenshot_path, logs_path),
        )

        for artifact in (screenshot_path, logs_path):
            if artifact and artifact.exists():
                self.attach_file(issue_key, artifact)

        log.info("Created Jira issue %s for failed test %s", issue_key, test_name)
        return issue_key

    def create_issue(self, summary: str, description: str) -> str:
        fields: dict = {
            "project": {"key": self.settings.project_key},
            "summary": summary[:255],
            "description": self._adf_description(description),
            "issuetype": {"name": self.settings.issue_type},
        }
        if self.settings.component:
            fields["components"] = [{"name": self.settings.component}]

        response = self.session.post(f"{self.base_url}/rest/api/3/issue", json={"fields": fields}, timeout=30)
        response.raise_for_status()
        return str(response.json()["key"])

    def attach_file(self, issue_key: str, file_path: Path) -> None:
        headers = {
            "Authorization": self.session.headers["Authorization"],
            "Accept": "application/json",
            "X-Atlassian-Token": "no-check",
        }
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        with file_path.open("rb") as handle:
            files = {"file": (file_path.name, handle, content_type)}
            response = requests.post(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/attachments",
                headers=headers,
                files=files,
                timeout=60,
            )
        response.raise_for_status()

    @staticmethod
    def _failure_description(
        test_name: str,
        error_message: str,
        screenshot_path: Path | None,
        logs_path: Path | None,
    ) -> str:
        lines = [
            "Automated mobile QA detected a failed test.",
            "",
            f"Test: {test_name}",
            "",
            "Failure:",
            error_message,
            "",
            "Artifacts:",
            f"- Screenshot: {screenshot_path if screenshot_path else 'not captured'}",
            f"- Logs: {logs_path if logs_path else 'not captured'}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _adf_description(text: str) -> dict:
        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": line or " "}],
                }
                for line in text.splitlines()
            ],
        }
