"""
utils/config.py
===============
Single source of truth for all test configuration.

Loading order (later wins):
  1. config/settings.yaml  – checked-in defaults for the whole team
  2. .env file             – local developer overrides (git-ignored)
  3. Environment variables – CI / GitHub Actions secrets

Usage
-----
    from utils.config import settings

    settings.appium.server_url                  # "http://127.0.0.1:4723"
    settings.appium.auto_grant_permissions      # True
    settings.test_data("username")              # "qa.user@example.com"
    settings.locator("login", "username")       # "id:com.example.app:id/email"
    settings.timeouts.explicit_wait_seconds     # 20
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
_SETTINGS_YAML = ROOT_DIR / "config" / "settings.yaml"


def _load_yaml() -> dict[str, Any]:
    """Load settings.yaml; return empty dict if file doesn't exist."""
    if _SETTINGS_YAML.exists():
        with open(_SETTINGS_YAML, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    return {}


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# Typed config dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AppiumSettings:
    server_url: str
    platform_name: str
    automation_name: str
    device_name: str
    app_path: Path
    no_reset: bool
    full_reset: bool
    auto_grant_permissions: bool   # ← was missing; caused the crash
    new_command_timeout: int
    app_wait_duration_ms: int
    adb_exec_timeout_ms: int = 60_000


@dataclass(frozen=True)
class JiraSettings:
    enabled: bool
    base_url: str
    email: str
    api_token: str
    project_key: str
    issue_type: str


@dataclass(frozen=True)
class TimeoutSettings:
    implicit_wait_seconds: int
    explicit_wait_seconds: int
    page_load_seconds: int


# ---------------------------------------------------------------------------
# Main Config class
# ---------------------------------------------------------------------------

class Config:
    """
    Lazy-loading config that merges YAML defaults with env-var overrides.
    Import the `settings` singleton at the bottom of this file.
    """

    def __init__(self) -> None:
        load_dotenv(ROOT_DIR / ".env")
        self._yaml: dict[str, Any] = _load_yaml()

    def _yaml_get(self, *keys: str, default: Any = None) -> Any:
        node: Any = self._yaml
        for k in keys:
            if not isinstance(node, dict):
                return default
            node = node.get(k, default)
        return node

    # ------------------------------------------------------------------
    # Typed sections
    # ------------------------------------------------------------------

    @property
    def appium(self) -> AppiumSettings:
        y: dict = self._yaml_get("appium") or {}
        raw_path = os.getenv("APP_PATH") or y.get("app_path", "app/app.apk")
        return AppiumSettings(
            server_url=os.getenv("APPIUM_SERVER_URL") or y.get("server_url", "http://127.0.0.1:4723"),
            platform_name=os.getenv("PLATFORM_NAME") or y.get("platform_name", "Android"),
            automation_name=os.getenv("AUTOMATION_NAME") or y.get("automation_name", "UiAutomator2"),
            device_name=os.getenv("DEVICE_NAME") or y.get("device_name", "Android Emulator"),
            app_path=Path(os.path.abspath(raw_path)),
            no_reset=_env_bool("NO_RESET", y.get("no_reset", False)),
            full_reset=_env_bool("FULL_RESET", y.get("full_reset", False)),
            auto_grant_permissions=_env_bool("AUTO_GRANT_PERMISSIONS", y.get("auto_grant_permissions", True)),
            new_command_timeout=_env_int("NEW_COMMAND_TIMEOUT", y.get("new_command_timeout", 300)),
            app_wait_duration_ms=_env_int("APP_WAIT_DURATION_MS", y.get("app_wait_duration_ms", 30_000)),
        )

    @property
    def jira(self) -> JiraSettings:
        y: dict = self._yaml_get("jira") or {}
        return JiraSettings(
            enabled=_env_bool("ENABLE_JIRA", y.get("enabled", False)),
            base_url=os.getenv("JIRA_BASE_URL") or y.get("base_url", ""),
            email=os.getenv("JIRA_EMAIL") or y.get("email", ""),
            api_token=os.getenv("JIRA_API_TOKEN") or y.get("api_token", ""),
            project_key=os.getenv("JIRA_PROJECT_KEY") or y.get("project_key", "SCRUM"),
            issue_type=os.getenv("JIRA_ISSUE_TYPE") or y.get("issue_type", "Task"),
        )

    @property
    def timeouts(self) -> TimeoutSettings:
        y: dict = self._yaml_get("timeouts") or {}
        return TimeoutSettings(
            implicit_wait_seconds=_env_int("IMPLICIT_WAIT", y.get("implicit_wait_seconds", 0)),
            explicit_wait_seconds=_env_int("EXPLICIT_WAIT", y.get("explicit_wait_seconds", 20)),
            page_load_seconds=_env_int("PAGE_LOAD_TIMEOUT", y.get("page_load_seconds", 45)),
        )

    # ------------------------------------------------------------------
    # Accessor helpers (called by page objects and tests)
    # ------------------------------------------------------------------

    def test_data(self, *keys: str, default: Any = None) -> Any:
        """
        Read a value from the ``test_data:`` YAML section.
        Env-var override: TEST_DATA_<KEY_UPPERCASED>.

        >>> settings.test_data("username")       # → "qa.user@example.com"
        >>> settings.test_data("nested", "key")  # → test_data.nested.key
        """
        env_key = "TEST_DATA_" + "_".join(k.upper() for k in keys)
        env_val = os.getenv(env_key)
        if env_val is not None:
            return env_val
        return self._yaml_get("test_data", *keys, default=default)

    def locator(self, page: str, element: str) -> str:
        """
        Read a locator string from the ``locators:`` YAML section.
        Env-var override: LOCATOR_<PAGE>_<ELEMENT> (uppercased).

        >>> settings.locator("login", "username")   # → "id:com.example.app:id/email"
        >>> settings.locator("home", "ready")       # → "xpath://..."
        """
        env_key = f"LOCATOR_{page.upper()}_{element.upper()}"
        env_val = os.getenv(env_key)
        if env_val is not None:
            return env_val

        value = self._yaml_get("locators", page, element)
        if value is None:
            raise KeyError(
                f"Locator '{page}.{element}' not found in settings.yaml "
                f"and env var {env_key!r} is not set."
            )
        return str(value)


# ---------------------------------------------------------------------------
# Module-level singleton — import this everywhere
# ---------------------------------------------------------------------------
settings = Config()