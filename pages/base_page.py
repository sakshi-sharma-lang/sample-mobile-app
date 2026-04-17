from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class BasePage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def visible(self, locator):
        try:
            return self.wait.until(
                ec.presence_of_element_located(locator)
            )
        except Exception as e:
            print("Element not found:", locator)
            print("Current Activity:", self.driver.current_activity)
            print("Page Source:", self.driver.page_source[:2000])
            raise e

    def click(self, locator):
        element = self.visible(locator)
        element.click()

    def send_keys(self, locator, text):
        element = self.visible(locator)
        element.send_keys(text)