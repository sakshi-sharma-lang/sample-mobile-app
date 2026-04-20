from appium import webdriver
from appium.options.android import UiAutomator2Options
import os


def create_driver():
    options = UiAutomator2Options()

    options.platform_name = "Android"
    options.device_name = "emulator-5554"
    options.automation_name = "UiAutomator2"

    # APK will be downloaded by pipeline
    options.app = os.path.abspath("app.apk")

    driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4723",
        options=options
    )

    driver.implicitly_wait(10)
    return driver