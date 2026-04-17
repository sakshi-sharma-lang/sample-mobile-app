import pytest
from utils.jira_client import create_jira_ticket
from utils.github_client import create_pr

results = []

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        results.append(rep)

        if rep.failed:
            create_jira_ticket(item.name, rep.longrepr)

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    # If ALL tests passed → create PR
    if all(r.passed for r in results):
        create_pr()