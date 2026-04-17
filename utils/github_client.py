from __future__ import annotations

import base64
from pathlib import Path

import requests

from utils.config import GitHubSettings
from utils.logger import get_logger


log = get_logger(__name__)


class GitHubClient:
    def __init__(self, settings: GitHubSettings) -> None:
        self.settings = settings
        self.api_base = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {settings.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        self._validate()

    def _validate(self) -> None:
        missing = [
            name
            for name, value in {
                "GITHUB_TOKEN": self.settings.token,
                "GITHUB_REPOSITORY": self.settings.repository,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Missing GitHub settings: {', '.join(missing)}")

    def create_or_update_report_pr(self, report_files: list[Path], body: str) -> str:
        base_sha = self._get_branch_sha(self.settings.base_branch)
        self._ensure_branch(self.settings.head_branch, base_sha)

        for report_file in report_files:
            if report_file.exists():
                repo_path = f"qa-results/{report_file.name}"
                self._put_file(
                    path=repo_path,
                    content=report_file.read_bytes(),
                    message=f"Update mobile QA report {report_file.name}",
                    branch=self.settings.head_branch,
                )

        pr_url = self._create_or_get_pull_request(
            title=self.settings.pr_title,
            body=body,
            head=self.settings.head_branch,
            base=self.settings.base_branch,
        )
        log.info("Created or found GitHub PR: %s", pr_url)
        return pr_url

    def _get_branch_sha(self, branch: str) -> str:
        response = self.session.get(
            f"{self.api_base}/repos/{self.settings.repository}/git/ref/heads/{branch}",
            timeout=30,
        )
        response.raise_for_status()
        return str(response.json()["object"]["sha"])

    def _ensure_branch(self, branch: str, sha: str) -> None:
        response = self.session.get(
            f"{self.api_base}/repos/{self.settings.repository}/git/ref/heads/{branch}",
            timeout=30,
        )
        if response.status_code == 200:
            return
        if response.status_code != 404:
            response.raise_for_status()

        create_response = self.session.post(
            f"{self.api_base}/repos/{self.settings.repository}/git/refs",
            json={"ref": f"refs/heads/{branch}", "sha": sha},
            timeout=30,
        )
        create_response.raise_for_status()

    def _put_file(self, path: str, content: bytes, message: str, branch: str) -> None:
        current_sha = self._get_file_sha(path, branch)
        payload = {
            "message": message,
            "content": base64.b64encode(content).decode("utf-8"),
            "branch": branch,
        }
        if current_sha:
            payload["sha"] = current_sha

        response = self.session.put(
            f"{self.api_base}/repos/{self.settings.repository}/contents/{path}",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

    def _get_file_sha(self, path: str, branch: str) -> str | None:
        response = self.session.get(
            f"{self.api_base}/repos/{self.settings.repository}/contents/{path}",
            params={"ref": branch},
            timeout=30,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return str(response.json()["sha"])

    def _create_or_get_pull_request(self, title: str, body: str, head: str, base: str) -> str:
        existing = self.session.get(
            f"{self.api_base}/repos/{self.settings.repository}/pulls",
            params={"head": f"{self.settings.repository.split('/')[0]}:{head}", "base": base, "state": "open"},
            timeout=30,
        )
        existing.raise_for_status()
        pulls = existing.json()
        if pulls:
            return str(pulls[0]["html_url"])

        response = self.session.post(
            f"{self.api_base}/repos/{self.settings.repository}/pulls",
            json={"title": title, "body": body, "head": head, "base": base},
            timeout=30,
        )
        response.raise_for_status()
        return str(response.json()["html_url"])
