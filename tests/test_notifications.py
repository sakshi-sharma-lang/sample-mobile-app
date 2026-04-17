from __future__ import annotations

from pathlib import Path

import pytest

from utils.notifications import NotificationClient


def test_send_test_summary_continues_when_slack_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    client = NotificationClient(
        slack_webhook_url="https://hooks.slack.invalid/test",
        smtp_host="smtp.example.invalid",
        smtp_port=587,
        smtp_username=None,
        smtp_password=None,
        email_from="qa@example.com",
        email_to="team@example.com",
    )

    def fail_slack(self: NotificationClient, text: str) -> None:
        calls.append("slack")
        raise RuntimeError("slack down")

    def send_email(self: NotificationClient, subject: str, body: str) -> None:
        calls.append("email")

    monkeypatch.setattr(NotificationClient, "send_slack", fail_slack)
    monkeypatch.setattr(NotificationClient, "send_email", send_email)

    client.send_test_summary("passed", Path("reports/junit.xml"), Path("reports/report.html"))

    assert calls == ["slack", "email"]


def test_send_test_summary_swallows_email_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    client = NotificationClient(
        slack_webhook_url=None,
        smtp_host="smtp.example.invalid",
        smtp_port=587,
        smtp_username=None,
        smtp_password=None,
        email_from="qa@example.com",
        email_to="team@example.com",
    )

    def fail_email(self: NotificationClient, subject: str, body: str) -> None:
        calls.append("email")
        raise RuntimeError("smtp down")

    monkeypatch.setattr(NotificationClient, "send_email", fail_email)

    client.send_test_summary("failed", Path("reports/junit.xml"), Path("reports/report.html"))

    assert calls == ["email"]
