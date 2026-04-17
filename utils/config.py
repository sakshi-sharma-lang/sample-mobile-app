from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "settings.yaml"

def _env(name: str, default: Any = None) -> Any:
    value = os.getenv(name)
    return default if value in (None, "") else value

@dataclass(frozen=True)
class AppiumSettings:
    server_url: str
    platform_name: str
    automation_name: str
    device_name: str
    app_path: Path
    new_command_timeout: int
    auto_grant_permissions: bool

@dataclass(frozen=True)
class TimeoutSettings:
    explicit_wait_seconds: int

@dataclass(frozen=True)
class JiraSettings:
    enabled: bool
    base_url: str
    email: str
    api_token: str
    project_key: str
    issue_type: str

class Config:
    def __init__(self, config_path: Path | None = None) -> None:
        load_dotenv(ROOT_DIR / ".env")
        self.config_path = config_path or Path(_env("QA_CONFIG_PATH", DEFAULT_CONFIG_PATH))
        self._raw = {}
        if self.config_path.exists():
            with self.config_path.open("r", encoding="utf-8") as stream:
                self._raw = yaml.safe_load(stream) or {}

    @property
    def appium(self) -> AppiumSettings:
        return AppiumSettings(
            server_url=str(_env("APPIUM_SERVER_URL", "http://127.0.0.1:4723")),
            platform_name="Android",
            automation_name="UiAutomator2",
            device_name=str(_env("ANDROID_DEVICE_NAME", "Android Emulator")),
            app_path=Path(os.path.abspath(_env("APP_PATH", "app/app.apk"))),
            new_command_timeout=300,
            auto_grant_permissions=True
        )

    @property
    def timeouts(self) -> TimeoutSettings:
        # Added to fix the AttributeError in base_page.py
        return TimeoutSettings(explicit_wait_seconds=20)

    @property
    def jira(self) -> JiraSettings:
        return JiraSettings(
            enabled=str(_env("ENABLE_JIRA", "false")).lower() == "true",
            base_url=str(_env("JIRA_BASE_URL", "")),
            email=str(_env("JIRA_EMAIL", "")),
            api_token=str(_env("JIRA_API_TOKEN", "")),
            project_key=str(_env("JIRA_PROJECT_KEY", "SCRUM")),
            issue_type=str(_env("JIRA_ISSUE_TYPE", "Task"))
        )

settings = Config()