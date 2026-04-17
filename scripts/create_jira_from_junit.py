from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from utils.config import settings  # noqa: E402
from utils.jira_client import JiraClient  # noqa: E402


def failed_tests(junit_path: Path) -> list[tuple[str, str]]:
    tree = ET.parse(junit_path)
    failures: list[tuple[str, str]] = []
    for testcase in tree.iter("testcase"):
        name = testcase.attrib.get("name", "unknown-test")
        classname = testcase.attrib.get("classname", "")
        full_name = f"{classname}.{name}" if classname else name
        failure = testcase.find("failure")
        if failure is None:
            failure = testcase.find("error")
        if failure is not None:
            failures.append((full_name, failure.attrib.get("message") or failure.text or "Test failed"))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Jira issues from a pytest JUnit XML file.")
    parser.add_argument("--junit", default="reports/junit.xml", help="Path to JUnit XML report")
    args = parser.parse_args()

    junit_path = Path(args.junit)
    if not junit_path.exists():
        print(f"JUnit file not found: {junit_path}", file=sys.stderr)
        return 2

    failures = failed_tests(junit_path)
    if not failures:
        print("No failed tests found. Jira ticket creation skipped.")
        return 0

    client = JiraClient(settings.jira)
    for test_name, error_message in failures:
        issue_key = client.create_issue_for_test_failure(test_name, error_message, logs_path=Path("reports/automation.log"))
        print(f"Created {issue_key} for {test_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
