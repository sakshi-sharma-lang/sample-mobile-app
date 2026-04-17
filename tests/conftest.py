import pytest
from pathlib import Path
from utils.driver_factory import create_driver
from utils.jira_client import JiraClient
from utils.driver_factory import get_driver as create_driver


@pytest.fixture(scope="function")
def driver():
    driver = create_driver()
    yield driver
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver", None)

        if driver:
            test_name = item.nodeid.replace("/", "_").replace("::", "_")
            screenshot_path = Path("reports") / f"{test_name}.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)

            driver.save_screenshot(str(screenshot_path))

            try:
                settings = item.config._settings  # assuming you already have settings
                JiraClient(settings.jira).create_issue_for_test_failure(
                    test_name=item.nodeid,
                    error_message=str(rep.longrepr),
                    screenshot_path=screenshot_path,
                    logs_path=Path("reports/automation.log")
                )
            except Exception as e:
                print("Failed to create Jira ticket:", e)