"""
utils/driver_factory.py
=======================
Creates and tears down the Appium WebDriver session.

Reads all capability values from `settings.appium` (utils/config.py).
No capability is hardcoded here — change settings.yaml or set env vars to
control behaviour without touching this file.
"""
from __future__ import annotations

import time
import logging
from pathlib import Path

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import WebDriverException

from utils.config import settings

log = logging.getLogger(__name__)


class DriverFactory:
    """
    Stateless factory.  Instantiate once per test session (or per worker
    when running in parallel) and call create_android_driver().

    Args:
        settings_obj: The Config singleton (passed in from conftest so
                      conftest stays testable with a mock config).
    """

    def __init__(self, settings_obj=None) -> None:
        # Accept an explicit settings object for testability; fall back to
        # the module-level singleton.
        self._cfg = settings_obj or settings

    def create_android_driver(self, retries: int = 3) -> webdriver.Remote:
        """
        Build UiAutomator2Options from config and connect to Appium.
        Retries up to `retries` times with 5-second back-off.
        """
        appium_cfg = self._cfg.appium
        options = self._build_options(appium_cfg)
        server_url = appium_cfg.server_url

        log.info("Connecting to Appium at %s (up to %d attempts) …", server_url, retries)
        last_exc: Exception | None = None

        for attempt in range(1, retries + 1):
            try:
                driver = webdriver.Remote(
                    command_executor=server_url,
                    options=options,
                )
                driver.implicitly_wait(self._cfg.timeouts.implicit_wait_seconds)
                log.info("Appium session started (attempt %d). ID: %s", attempt, driver.session_id)
                return driver
            except WebDriverException as exc:
                last_exc = exc
                log.warning("Attempt %d/%d failed: %s", attempt, retries, exc)
                time.sleep(5)

        raise RuntimeError(
            f"Could not connect to Appium at {server_url} after {retries} attempts. "
            f"Last error: {last_exc}"
        ) from last_exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_options(appium_cfg) -> UiAutomator2Options:
        """Assemble all Appium capabilities from the AppiumSettings dataclass."""
        apk_path = str(Path(appium_cfg.app_path).resolve())

        options = UiAutomator2Options()

        # Core capabilities
        options.platform_name   = appium_cfg.platform_name
        options.device_name     = appium_cfg.device_name
        options.automation_name = appium_cfg.automation_name
        options.app             = apk_path

        # App lifecycle
        options.set_capability("appium:noReset",              appium_cfg.no_reset)
        options.set_capability("appium:fullReset",            appium_cfg.full_reset)
        options.set_capability("appium:autoGrantPermissions", appium_cfg.auto_grant_permissions)

        # Timeouts
        options.set_capability("appium:newCommandTimeout", appium_cfg.new_command_timeout)
        options.set_capability("appium:adbExecTimeout",    appium_cfg.adb_exec_timeout_ms)
        options.set_capability("appium:appWaitDuration",   appium_cfg.app_wait_duration_ms)

        # Reliability
        options.set_capability("appium:ensureWebviewsHavePages", True)
        options.set_capability("appium:nativeWebScreenshot",     True)

        log.debug("Appium options: %s", options.to_capabilities())
        return options