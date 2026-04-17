from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "settings.yaml"

def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None: return default
    if isinstance(value, bool): return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}

def _env(name: str, default: Any = None) -> Any:
    value = os.getenv(name)
    return default if value in (None, "") else value

def _deep_get(data: dict[str, Any], keys: tuple[str, ...], default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current: return default
        current = current[key]
    return current

@dataclass(frozen=True)
class AppiumSettings:
    server_url: str
    platform_name: str
    automation_name: str
    device_name: str
    app_path: Path
    auto_grant_permissions: bool
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
    def __init__(self, config_path: Path | None = None) -> None:
        load_dotenv(ROOT_DIR / ".env")
        self.config_path = config_path or Path(_env("QA_CONFIG_PATH", DEFAULT_CONFIG_PATH))
        self._raw = {}
        if self.config_path.exists():
            with self.config_path.open("r", encoding="utf-8") as stream:
                self._raw = yaml.safe_load(stream) or {}

    @property
    def appium(self) -> AppiumSettings:
        raw_path = _env("APP_PATH", _deep_get(self._raw, ("appium", "app_path"), "app/app.apk"))
        app_path = Path(raw_path)
        if not app_path.is_absolute(): app_path = ROOT_DIR / app_path
        return AppiumSettings(
            server_url=str(_env("APPIUM_SERVER_URL", _deep_get(self._raw, ("appium", "server_url"), "http://127.0.0.1:4723"))),
            platform_name=str(_env("ANDROID_PLATFORM_NAME", _deep_get(self._raw, ("appium", "platform_name"), "Android"))),
            automation_name=str(_env("ANDROID_AUTOMATION_NAME", _deep_get(self._raw, ("appium", "automation_name"), "UiAutomator2"))),
            device_name=str(_env("ANDROID_DEVICE_NAME", _deep_get(self._raw, ("appium", "device_name"), "Android Emulator"))),
            app_path=app_path,
            auto_grant_permissions=_as_bool(_env("AUTO_GRANT_PERMISSIONS", True), True),
            new_command_timeout=int(_env("NEW_COMMAND_TIMEOUT", 300)),
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
        )

settings = Config()