from __future__ import annotations

from scripts.create_jira_from_junit import ROOT_DIR, failed_tests


def test_failed_tests_reads_empty_failure_and_error_elements() -> None:
    junit_path = ROOT_DIR / "reports" / "junit-parser-test.xml"
    junit_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        junit_path.write_text(
            """<?xml version="1.0" encoding="utf-8"?>
<testsuite>
  <testcase classname="tests.test_login" name="test_login">
    <failure message="assert failed" />
  </testcase>
  <testcase classname="tests.test_smoke" name="test_launch">
    <error />
  </testcase>
</testsuite>
""",
            encoding="utf-8",
        )

        assert failed_tests(junit_path) == [
            ("tests.test_login.test_login", "assert failed"),
            ("tests.test_smoke.test_launch", "Test failed"),
        ]
    finally:
        try:
            junit_path.unlink(missing_ok=True)
        except PermissionError:
            pass
