from __future__ import annotations

from pathlib import Path

from appium import webdriver
from appium.options.android import UiAutomator2Options

from utils.config import Settings, settings
from utils.logger import get_logger


log = get_logger(__name__)


class DriverFactory:
    def __init__(self, config: Settings = settings) -> None:
        self.config = config

    def create_android_driver(self) -> webdriver.Remote:
        appium = self.config.appium
        options = UiAutomator2Options()
        options.platform_name = appium.platform_name
        options.automation_name = appium.automation_name
        options.device_name = appium.device_name
        options.no_reset = appium.no_reset
        options.full_reset = appium.full_reset
        options.auto_grant_permissions = appium.auto_grant_permissions
        options.new_command_timeout = appium.new_command_timeout
        options.app_wait_duration = appium.app_wait_duration_ms

        if appium.platform_version:
            options.platform_version = appium.platform_version
        if appium.udid:
            options.udid = appium.udid

        self._configure_app_target(options, appium.app_path, appium.app_package, appium.app_activity)
        log.info("Creating Appium session at %s for device '%s'", appium.server_url, appium.device_name)
        driver = webdriver.Remote(command_executor=appium.server_url, options=options)
        driver.implicitly_wait(self.config.timeouts.implicit_wait_seconds)
        return driver

    @staticmethod
    def _configure_app_target(
        options: UiAutomator2Options,
        app_path: Path,
        app_package: str | None,
        app_activity: str | None,
    ) -> None:
        if app_package and app_activity:
            options.app_package = app_package
            options.app_activity = app_activity
            return

        if not app_path.exists():
            raise FileNotFoundError(
                f"APK not found at {app_path}. Place it in app/ or set APP_PATH to the APK location."
            )
        options.app = str(app_path)
