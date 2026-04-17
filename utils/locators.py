from appium.webdriver.common.appiumby import AppiumBy


def parse_locator(locator: tuple):
    strategy, value = locator

    mapping = {
        "id": AppiumBy.ID,
        "xpath": AppiumBy.XPATH,
        "accessibility_id": AppiumBy.ACCESSIBILITY_ID
    }

    if strategy not in mapping:
        raise ValueError(f"Unsupported locator strategy: {strategy}")

    return mapping[strategy], value