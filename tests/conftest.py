from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import pytest

from utils.config import settings
from utils.driver_factory import DriverFactory
from utils.jira_client import JiraClient
from utils.logger import get_logger
from utils.notifications import NotificationClient
from utils.reporting import capture_screenshot, ensure_reports_dir


log = get_logger(__name__)


def _jira_creation_enabled() -> bool:
    return settings.jira.enabled and os.getenv("JIRA_CREATE_DURING_PYTEST", "true").lower() == "true"


def _failure_message(report: pytest.TestReport, call: pytest.CallInfo) -> str:
    if call.excinfo:
        return str(call.excinfo.value)
    if report.longrepr:
        return str(report.longrepr)
    return "Unknown test failure"


def _capture_failure_screenshot(item: pytest.Item, test_name: str) -> Path | None:
    driver_instance = getattr(item, "driver", None)
    if not driver_instance:
        return None

    try:
        screenshot_path = capture_screenshot(driver_instance, test_name)
        log.info("Captured failure screenshot: %s", screenshot_path)
        return screenshot_path
    except Exception as exc:  # pragma: no cover - best-effort artifact capture
        log.warning("Unable to capture screenshot for %s: %s", test_name, exc)
        return None


def _create_jira_ticket_for_failure(item: pytest.Item, report: pytest.TestReport, call: pytest.CallInfo) -> None:
    if not _jira_creation_enabled() or getattr(item, "_jira_issue_created", False):
        return

    test_name = f"{item.nodeid} [{report.when}]"
    screenshot_path = _capture_failure_screenshot(item, test_name)
    error_message = _failure_message(report, call)

    try:
        JiraClient(settings.jira).create_issue_for_test_failure(
            test_name=test_name,
            error_message=error_message,
            screenshot_path=screenshot_path,
            logs_path=Path("reports/automation.log"),
        )
        setattr(item, "_jira_issue_created", True)
    except Exception as exc:  # pragma: no cover - avoid masking test result
        log.exception("Failed to create Jira ticket for %s: %s", test_name, exc)


@pytest.fixture(scope="session", autouse=True)
def prepare_reports_dir() -> None:
    ensure_reports_dir()


@pytest.fixture(scope="function")
def driver(request: pytest.FixtureRequest) -> Generator:
    driver_instance = DriverFactory(settings).create_android_driver()
    request.node.driver = driver_instance
    yield driver_instance
    driver_instance.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if not report.failed:
        return

    _create_jira_ticket_for_failure(item, report, call)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    status = "passed" if exitstatus == 0 else "failed"
    if os.getenv("SLACK_WEBHOOK_URL") or os.getenv("EMAIL_SMTP_HOST"):
        try:
            NotificationClient.from_env().send_test_summary(
                status=status,
                junit_path=Path("reports/junit.xml"),
                html_report_path=Path("reports/report.html"),
            )
        except Exception as exc:  # pragma: no cover - best-effort notification
            log.exception("Failed to send test summary notification: %s", exc)
