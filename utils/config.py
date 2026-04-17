from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class AppiumSettings:
    server_url: str
    platform_name: str
    automation_name: str
    device_name: str
    app_path: Path
    new_command_timeout: int

@dataclass(frozen=True)
class JiraSettings:
    enabled: bool
    base_url: str
    email: str
    api_token: str
    project_key: str
    issue_type: str

class Config:
    def __init__(self) -> None:
        load_dotenv(ROOT_DIR / ".env")

    @property
    def appium(self) -> AppiumSettings:
        return AppiumSettings(
            server_url=os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723"),
            platform_name="Android",
            automation_name="UiAutomator2",
            device_name="Android Emulator",
            app_path=Path(os.path.abspath(os.getenv("APP_PATH", "app/app.apk"))),
            new_command_timeout=300
        )

    @property
    def jira(self) -> JiraSettings:
        return JiraSettings(
            enabled=os.getenv("ENABLE_JIRA", "false").lower() == "true",
            base_url=os.getenv("JIRA_BASE_URL", ""),
            email=os.getenv("JIRA_EMAIL", ""),
            api_token=os.getenv("JIRA_API_TOKEN", ""),
            project_key=os.getenv("JIRA_PROJECT_KEY", "SCRUM"),
            issue_type=os.getenv("JIRA_ISSUE_TYPE", "Task")
        )

    @property
    def timeouts(self):
        # Dummy class to prevent AttributeError in BasePage
        class Timeouts:
            explicit_wait_seconds = 20
        return Timeouts()

settings = Config()