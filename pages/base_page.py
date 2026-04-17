from __future__ import annotations

from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import settings
from utils.locators import parse_locator


class BasePage:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.timeouts.explicit_wait_seconds)

    def find(self, locator: str) -> WebElement:
        return self.wait.until(ec.presence_of_element_located(parse_locator(locator)))

    def visible(self, locator: str) -> WebElement:
        return self.wait.until(ec.visibility_of_element_located(parse_locator(locator)))

    def clickable(self, locator: str) -> WebElement:
        return self.wait.until(ec.element_to_be_clickable(parse_locator(locator)))

    def tap(self, locator: str) -> None:
        self.clickable(locator).click()

    def type_text(self, locator: str, value: str, clear_first: bool = True) -> None:
        element = self.visible(locator)
        if clear_first:
            element.clear()
        element.send_keys(value)

    def is_visible(self, locator: str, timeout_seconds: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout_seconds).until(ec.visibility_of_element_located(parse_locator(locator)))
            return True
        except TimeoutException:
            return False
