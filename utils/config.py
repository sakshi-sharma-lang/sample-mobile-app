from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Path resolution
ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "settings.yaml"

def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}

def _env(name: str, default: Any = None) -> Any:
    value = os.getenv(name)
    return default if value in (None, "") else value

def _deep_get(data: dict[str, Any], keys: tuple[str, ...], default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current

@dataclass(frozen=True)
class AppiumSettings:
    server_url: str
    platform_name: str
    automation_name: str
    device_name: str
    app_path: Path
    platform_version: str | None
    udid: str | None
    app_package: str | None
    app_activity: str | None
    no_reset: bool
    full_reset: bool
    auto_grant_permissions: bool
    new_command_timeout: int
    app_wait_duration_ms: int

@dataclass(frozen=True)
class TimeoutSettings:
    implicit_wait_seconds: int
    explicit_wait_seconds: int
    page_load_seconds: int

@dataclass(frozen=True)
class JiraSettings:
    enabled: bool
    base_url: str
    email: str
    api_token: str
    project_key: str
    issue_type: str
    component: str | None

@dataclass(frozen=True)
class GitHubSettings:
    enabled: bool
    token: str
    repository: str
    base_branch: str
    head_branch: str
    pr_title: str

# RENAMED from Settings to Config to fix the ImportError
class Config:
    def __init__(self, config_path: Path | None = None) -> None:
        load_dotenv(ROOT_DIR / ".env")
        self.config_path = config_path or Path(_env("QA_CONFIG_PATH", DEFAULT_CONFIG_PATH))
        
        # Ensure directory exists and handle missing YAML gracefully
        if self.config_path.exists():
            with self.config_path.open("r", encoding="utf-8") as stream:
                self._raw: dict[str, Any] = yaml.safe_load(stream) or {}
        else:
            self._raw = {}

    @property
    def root_dir(self) -> Path:
        return ROOT_DIR

    # Alias properties for compatibility with DriverFactory and JiraClient
    @property
    def PLATFORM_NAME(self) -> str: return self.appium.platform_name
    @property
    def DEVICE_NAME(self) -> str: return self.appium.device_name
    @property
    def APP_PATH(self) -> str: return str(self.appium.app_path)
    @property
    def AUTOMATION_NAME(self) -> str: return self.appium.automation_name
    @property
    def APPIUM_SERVER(self) -> str: return self.appium.server_url
    
    @property
    def JIRA_BASE_URL(self) -> str: return self.jira.base_url
    @property
    def JIRA_EMAIL(self) -> str: return self.jira.email
    @property
    def JIRA_API_TOKEN(self) -> str: return self.jira.api_token
    @property
    def JIRA_PROJECT_KEY(self) -> str: return self.jira.project_key

    @property
    def appium(self) -> AppiumSettings:
        raw_path = _env("APP_PATH", _deep_get(self._raw, ("appium", "app_path"), "app/app.apk"))
        app_path = Path(raw_path)
        if not app_path.is_absolute():
            app_path = ROOT_DIR / app_path
        return AppiumSettings(
            server_url=str(_env("APPIUM_SERVER_URL", _deep_get(self._raw, ("appium", "server_url"), "http://127.0.0.1:4723"))),
            platform_name=str(_env("ANDROID_PLATFORM_NAME", _deep_get(self._raw, ("appium", "platform_name"), "Android"))),
            automation_name=str(_env("ANDROID_AUTOMATION_NAME", _deep_get(self._raw, ("appium", "automation_name"), "UiAutomator2"))),
            device_name=str(_env("ANDROID_DEVICE_NAME", _deep_get(self._raw, ("appium", "device_name"), "Android Emulator"))),
            app_path=app_path,
            platform_version=_env("ANDROID_PLATFORM_VERSION"),
            udid=_env("ANDROID_UDID"),
            app_package=_env("ANDROID_APP_PACKAGE"),
            app_activity=_env("ANDROID_APP_ACTIVITY"),
            no_reset=_as_bool(_env("NO_RESET", _deep_get(self._raw, ("appium", "no_reset"), False))),
            full_reset=_as_bool(_env("FULL_RESET", _deep_get(self._raw, ("appium", "full_reset"), False))),
            auto_grant_permissions=_as_bool(_env("AUTO_GRANT_PERMISSIONS", _deep_get(self._raw, ("appium", "auto_grant_permissions"), True)), True),
            new_command_timeout=int(_env("NEW_COMMAND_TIMEOUT", _deep_get(self._raw, ("appium", "new_command_timeout"), 300))),
            app_wait_duration_ms=int(_env("APP_WAIT_DURATION_MS", _deep_get(self._raw, ("appium", "app_wait_duration_ms"), 30000))),
        )

    @property
    def jira(self) -> JiraSettings:
        return JiraSettings(
            enabled=_as_bool(_env("ENABLE_JIRA", False)),
            base_url=str(_env("JIRA_BASE_URL", "")),
            email=str(_env("JIRA_EMAIL", "")),
            api_token=str(_env("JIRA_API_TOKEN", "")),
            project_key=str(_env("JIRA_PROJECT_KEY", "SCRUM")),
            issue_type=str(_env("JIRA_ISSUE_TYPE", "Task")),
            component=_env("JIRA_COMPONENT"),
        )
# Instantiate as 'settings' for conftest.py
settings = Config()
