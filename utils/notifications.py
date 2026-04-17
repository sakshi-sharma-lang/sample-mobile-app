from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

import requests

from utils.logger import get_logger


log = get_logger(__name__)


@dataclass(frozen=True)
class NotificationClient:
    slack_webhook_url: str | None
    smtp_host: str | None
    smtp_port: int
    smtp_username: str | None
    smtp_password: str | None
    email_from: str | None
    email_to: str | None

    @classmethod
    def from_env(cls) -> "NotificationClient":
        return cls(
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL") or None,
            smtp_host=os.getenv("EMAIL_SMTP_HOST") or None,
            smtp_port=int(os.getenv("EMAIL_SMTP_PORT", "587")),
            smtp_username=os.getenv("EMAIL_SMTP_USERNAME") or None,
            smtp_password=os.getenv("EMAIL_SMTP_PASSWORD") or None,
            email_from=os.getenv("EMAIL_FROM") or None,
            email_to=os.getenv("EMAIL_TO") or None,
        )

    def send_test_summary(self, status: str, junit_path: Path, html_report_path: Path) -> None:
        message = (
            f"Mobile QA automation {status.upper()}.\n"
            f"JUnit: {junit_path}\n"
            f"HTML report: {html_report_path}"
        )
        if self.slack_webhook_url:
            try:
                self.send_slack(message)
            except Exception as exc:  # pragma: no cover - depends on external service
                log.exception("Failed to send Slack notification: %s", exc)
        if self.smtp_host and self.email_from and self.email_to:
            try:
                self.send_email(subject=f"Mobile QA automation {status}", body=message)
            except Exception as exc:  # pragma: no cover - depends on external service
                log.exception("Failed to send email notification: %s", exc)

    def send_slack(self, text: str) -> None:
        response = requests.post(self.slack_webhook_url, json={"text": text}, timeout=15)
        response.raise_for_status()
        log.info("Sent Slack notification")

    def send_email(self, subject: str, body: str) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.email_from
        message["To"] = self.email_to
        message.set_content(body)

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as smtp:
            smtp.starttls()
            if self.smtp_username and self.smtp_password:
                smtp.login(self.smtp_username, self.smtp_password)
            smtp.send_message(message)
        log.info("Sent email notification to %s", self.email_to)
