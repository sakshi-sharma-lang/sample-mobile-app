from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.config import Config
import os

def create_driver():
    options = UiAutomator2Options()
    options.platform_name = Config.PLATFORM_NAME
    options.device_name = Config.DEVICE_NAME
    options.app = os.path.abspath(Config.APP_PATH)
    options.automation_name = Config.AUTOMATION_NAME
    
    # Stability capabilities for CI environments
    options.set_capability("appium:newCommandTimeout", 300)
    options.set_capability("appium:adbExecTimeout", 60000)
    options.set_capability("appium:uiautomator2ServerInstallTimeout", 60000)
    options.set_capability("appium:uiautomator2ServerReadTimeout", 60000)
    options.set_capability("autoGrantPermissions", True)
    
    # Prevent the session from quitting if a service briefly hangs
    options.set_capability("appium:noReset", False)

    driver = webdriver.Remote(
        command_executor=Config.APPIUM_SERVER,
        options=options,
        direct_connection=True
    )

    # Increased wait for UI elements to appear on slow emulators
    driver.implicitly_wait(20)
    return driver
