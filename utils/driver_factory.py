from appium import webdriver
from appium.options.android import UiAutomator2Options
import os

class DriverFactory:
    def __init__(self, settings_obj):
        # Now accepts 'settings' from conftest.py
        self.settings = settings_obj

    def create_android_driver(self):
        appium_cfg = self.settings.appium
        
        options = UiAutomator2Options()
        options.platform_name = appium_cfg.platform_name
        options.device_name = appium_cfg.device_name
        options.automation_name = appium_cfg.automation_name
        options.app = str(appium_cfg.app_path)
        
        # Stability settings for CI
        options.set_capability("appium:newCommandTimeout", appium_cfg.new_command_timeout)
        options.set_capability("appium:adbExecTimeout", 60000)
        options.set_capability("autoGrantPermissions", appium_cfg.auto_grant_permissions)

        driver = webdriver.Remote(
            command_executor=appium_cfg.server_url,
            options=options
        )

        driver.implicitly_wait(20)
        return driver