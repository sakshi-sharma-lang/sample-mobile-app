from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.config import settings
import os

class DriverFactory:
    @staticmethod
    def create_driver():
        # Using the alias properties from our new Config class
        options = UiAutomator2Options()
        options.platform_name = settings.PLATFORM_NAME
        options.device_name = settings.DEVICE_NAME
        options.app = settings.APP_PATH
        options.automation_name = settings.AUTOMATION_NAME
        
        # CI stability settings
        options.set_capability("appium:newCommandTimeout", settings.appium.new_command_timeout)
        options.set_capability("appium:adbExecTimeout", 60000)
        options.set_capability("autoGrantPermissions", settings.appium.auto_grant_permissions)

        driver = webdriver.Remote(
            command_executor=settings.APPIUM_SERVER,
            options=options
        )

        # Use the implicit wait from the config
        driver.implicitly_wait(20)
        return driver
