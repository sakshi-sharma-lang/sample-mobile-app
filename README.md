# Mobile APK QA Automation Pipeline

This repository is a production-oriented starting point for testing an Android or Flutter APK when the application source code is not available.

It uses:

- Python, pytest, and Appium
- Page Object Model structure
- Android emulator or real Android device
- Jira ticket creation on test failure
- GitHub PR creation on successful test completion
- GitHub Actions CI
- Optional Firebase Test Lab Robo testing
- Optional Slack and email notifications
- Optional Allure reporting

## Repository Structure

```text
mobile-qa-automation/
  .github/workflows/
    firebase-test-lab.yml
    mobile-qa.yml
  app/
    README.md
  config/
    settings.yaml
  pages/
    base_page.py
    home_page.py
    login_page.py
  reports/
    .gitkeep
  scripts/
    create_github_pr_on_success.py
    create_jira_from_junit.py
    run_firebase_test_lab.py
  tests/
    conftest.py
    test_login_flow.py
    test_smoke_launch.py
  utils/
    config.py
    driver_factory.py
    github_client.py
    jira_client.py
    locators.py
    logger.py
    notifications.py
    reporting.py
  .env.example
  .gitignore
  pytest.ini
  requirements.txt
```

## Local Setup

Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Or install the repo in editable mode:

```bash
pip install -e .
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Or:

```powershell
pip install -e .
```

Install Appium 2 and the Android driver:

```bash
npm install -g appium
appium driver install uiautomator2
```

Place the APK at:

```text
app/app-under-test.apk
```

Or point to another APK:

```bash
export APP_PATH=/absolute/path/to/application.apk
```

Start Appium:

```bash
appium --base-path /
```

Run tests:

```bash
pytest -m smoke
pytest -m "smoke or login" --reruns 1 --reruns-delay 5
```

Reports are written to:

```text
reports/junit.xml
reports/report.html
reports/automation.log
```

## Emulator and Real Device Configuration

For an emulator:

```bash
export ANDROID_DEVICE_NAME="Android Emulator"
pytest -m smoke
```

For a connected real device:

```bash
adb devices
export ANDROID_UDID=<device-serial>
export ANDROID_DEVICE_NAME=<device-name>
pytest -m smoke
```

If the app is already installed and you do not want Appium to install an APK each run:

```bash
export ANDROID_APP_PACKAGE=com.company.app
export ANDROID_APP_ACTIVITY=.MainActivity
export NO_RESET=true
pytest -m smoke
```

## Locator Strategy for APK-Only Testing

Because source code is unavailable, locators are configurable. Defaults live in [config/settings.yaml](config/settings.yaml).

Supported locator formats:

```text
id:com.example.app:id/login
xpath://android.widget.TextView[@text='Login']
accessibility_id:login_button
android_uiautomator:new UiSelector().text("Login")
class_name:android.widget.EditText
```

Override locators without editing code:

```bash
export LOGIN_USERNAME_LOCATOR="id:com.company.app:id/email"
export LOGIN_PASSWORD_LOCATOR="id:com.company.app:id/password"
export LOGIN_SUBMIT_LOCATOR="accessibility_id:Sign in"
export HOME_READY_LOCATOR="xpath://android.widget.TextView[contains(@text,'Dashboard')]"
```

Recommended inspection tools:

- Appium Inspector
- Android Studio Layout Inspector for debug builds
- `adb shell uiautomator dump /sdcard/window.xml`
- `adb pull /sdcard/window.xml`

Prefer stable accessibility IDs and resource IDs. Use XPath only when the APK exposes no better attributes.

## Test Design

The framework follows Page Object Model:

- [pages/base_page.py](pages/base_page.py) owns waits, taps, typing, and visibility checks.
- [pages/login_page.py](pages/login_page.py) models the login screen.
- [pages/home_page.py](pages/home_page.py) models the post-login ready state.
- [tests/test_login_flow.py](tests/test_login_flow.py) contains the business flow assertion.
- [tests/test_smoke_launch.py](tests/test_smoke_launch.py) verifies that an Appium session and Android package are active.

Keep tests business-readable. Put element details and interaction mechanics in Page Objects.

## Jira Integration

Set these environment variables in CI secrets or a local `.env` copied from [.env.example](.env.example):

```bash
export ENABLE_JIRA=true
export JIRA_BASE_URL=https://your-domain.atlassian.net
export JIRA_EMAIL=qa-automation@example.com
export JIRA_API_TOKEN=<atlassian-api-token>
export JIRA_PROJECT_KEY=QA
export JIRA_ISSUE_TYPE=Bug
export JIRA_COMPONENT="Mobile Automation"
```

During pytest execution, failed tests create Jira tickets with:

- test name
- failure message
- screenshot path
- automation log attachment

For post-processing an existing JUnit report:

```bash
python scripts/create_jira_from_junit.py --junit reports/junit.xml
```

In CI, prefer the pytest hook because it can attach screenshots captured from the live Appium driver.

## GitHub PR Creation on Success

When enabled, [scripts/create_github_pr_on_success.py](scripts/create_github_pr_on_success.py) creates or updates a branch containing QA result files and opens a PR.

Required environment:

```bash
export ENABLE_CREATE_PR=true
export GITHUB_TOKEN=<token-with-contents-and-pull-request-permissions>
export GITHUB_REPOSITORY=owner/repository
export GITHUB_BASE_BRANCH=main
export GITHUB_HEAD_BRANCH=qa/mobile-test-results
export GITHUB_PR_TITLE="Mobile QA automation passed"
```

Run manually:

```bash
python scripts/create_github_pr_on_success.py --body "Mobile APK QA passed."
```

This is intentionally report-oriented while source code is unavailable. When application source becomes available, the same PR mechanism can be changed to open dependency, locator, test, or app-source changes after tests pass.

## GitHub Actions Pipeline

[.github/workflows/mobile-qa.yml](.github/workflows/mobile-qa.yml) performs:

1. Checkout repository
2. Install Python dependencies
3. Install Appium and UiAutomator2
4. Resolve the APK from `app/app-under-test.apk` or a manual `apk_url`
5. Create and boot an Android emulator
6. Start Appium
7. Run pytest
8. Create Jira issues for failures through pytest hooks
9. Create a GitHub PR on success if enabled
10. Upload reports as artifacts

GitHub configuration:

Repository variables:

```text
ENABLE_JIRA=false
ENABLE_CREATE_PR=false
JIRA_PROJECT_KEY=QA
JIRA_ISSUE_TYPE=Bug
JIRA_COMPONENT=Mobile Automation
```

Repository secrets:

```text
JIRA_BASE_URL
JIRA_EMAIL
JIRA_API_TOKEN
SLACK_WEBHOOK_URL
```

The built-in `GITHUB_TOKEN` is used for PR creation when workflow permissions allow `contents: write` and `pull-requests: write`.

## Firebase Test Lab

The optional workflow [.github/workflows/firebase-test-lab.yml](.github/workflows/firebase-test-lab.yml) runs a Firebase Robo test against the APK.

Required GitHub secret:

```text
GCP_SERVICE_ACCOUNT_JSON
```

Required GitHub variables:

```text
FIREBASE_PROJECT_ID
FIREBASE_DEVICE_MODEL=Pixel2
FIREBASE_DEVICE_VERSION=30
FIREBASE_DEVICE_LOCALE=en
FIREBASE_DEVICE_ORIENTATION=portrait
```

Local run:

```bash
gcloud auth application-default login
export FIREBASE_PROJECT_ID=<gcp-project-id>
python scripts/run_firebase_test_lab.py --app app/app-under-test.apk
```

Firebase Test Lab is useful when:

- local emulator capacity is limited
- you need device matrix coverage
- you want Robo exploration before detailed Appium flows are mature

For full scripted Appium tests on Firebase, package tests as an Android instrumentation test APK or use a device farm that supports remote Appium sessions directly.

## Reporting and Notifications

Included:

- JUnit XML: `reports/junit.xml`
- pytest HTML: `reports/report.html`
- automation log: `reports/automation.log`
- failure screenshots: `reports/<test-name>_<timestamp>.png`

Allure is available through `allure-pytest`:

```bash
pytest --alluredir=allure-results
allure generate allure-results --clean -o allure-report
```

Slack:

```bash
export SLACK_WEBHOOK_URL=<incoming-webhook-url>
```

Email:

```bash
export EMAIL_SMTP_HOST=smtp.example.com
export EMAIL_SMTP_PORT=587
export EMAIL_SMTP_USERNAME=qa-automation@example.com
export EMAIL_SMTP_PASSWORD=<smtp-password>
export EMAIL_FROM=qa-automation@example.com
export EMAIL_TO=team@example.com
```

## Future Upgrade Plan When Source Code Is Available

Phase 1, current state:

- consume APK artifact
- run smoke and login Appium tests
- create Jira on failure
- publish reports
- create report PR on success

Phase 2, source repository available:

- checkout app source
- install Flutter or Android build toolchain
- run static checks and unit tests
- build APK from source
- run Appium suite against built APK
- create Jira on failure with commit SHA and branch
- publish reports and coverage

Phase 3, full PR automation:

- create a branch for generated test fixes, locator updates, or release metadata
- commit changes
- open GitHub PR through API
- request reviewers
- block merge until mobile QA passes

Example GitHub PR API call:

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/owner/repository/pulls \
  -d '{
    "title": "Mobile QA automation updates",
    "head": "qa/mobile-automation-updates",
    "base": "main",
    "body": "Automated mobile QA changes passed emulator validation."
  }'
```

## Best Practices

- Keep APKs out of Git; store them as CI artifacts or in object storage.
- Prefer `accessibility_id` and resource `id` locators over XPath.
- Put all locator changes in config or Page Objects, not test bodies.
- Use explicit waits only; implicit waits are set to zero by default.
- Use `pytest-rerunfailures` sparingly for known infrastructure flakes.
- Mark tests by value and cost: `smoke`, `login`, `regression`.
- Capture screenshots and logs on every failure.
- Do not hard-code credentials, tokens, usernames, passwords, or Jira URLs in tests.
- Store secrets in GitHub Actions secrets, not repository variables.
- Keep Jira creation idempotent in mature systems by searching for open issues with the same test name and build fingerprint before creating a new one.
- Add device coverage gradually: one emulator smoke lane first, then real devices or Firebase Test Lab matrix.
- Stabilize Flutter apps by adding semantic labels in source when source access becomes available.

## Typical Commands

Run smoke:

```bash
pytest -m smoke
```

Run login only:

```bash
pytest -m login
```

Run regression with one retry:

```bash
pytest -m regression --reruns 1 --reruns-delay 5
```

Create Jira issues from report:

```bash
ENABLE_JIRA=true python scripts/create_jira_from_junit.py --junit reports/junit.xml
```

Create report PR after success:

```bash
ENABLE_CREATE_PR=true python scripts/create_github_pr_on_success.py
```
