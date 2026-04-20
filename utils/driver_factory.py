from appium import webdriver
from appium.options.android import UiAutomator2Options
import os

def create_driver():
    options = UiAutomator2Options()

    options.platform_name = "Android"
    options.device_name = "emulator-5554"
    options.automation_name = "UiAutomator2"

    options.app = os.path.abspath("app.apk")

    # 🔥 FIX: increase timeout (VERY IMPORTANT)
    options.set_capability("uiautomator2ServerInstallTimeout", 120000)
    options.set_capability("adbExecTimeout", 120000)
    options.set_capability("androidInstallTimeout", 120000)

    driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4723",
        options=options
    )

    driver.implicitly_wait(10)
    return driver