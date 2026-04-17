from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy


class LocatorError(ValueError):
    pass


def parse_locator(locator: str) -> tuple[str, str]:
    """
    Parses portable locator strings such as:
    - id:com.example.app:id/login
    - xpath://android.widget.TextView[@text='Login']
    - accessibility_id:login_button
    - android_uiautomator:new UiSelector().text("Login")
    """
    if not locator or ":" not in locator:
        raise LocatorError(f"Locator must use '<strategy>:<value>' format. Got: {locator!r}")

    strategy, value = locator.split(":", 1)
    strategy = strategy.strip().lower()
    value = value.strip()

    mapping = {
        "id": AppiumBy.ID,
        "xpath": AppiumBy.XPATH,
        "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
        "accessibility": AppiumBy.ACCESSIBILITY_ID,
        "aid": AppiumBy.ACCESSIBILITY_ID,
        "class_name": AppiumBy.CLASS_NAME,
        "class": AppiumBy.CLASS_NAME,
        "android_uiautomator": AppiumBy.ANDROID_UIAUTOMATOR,
        "uiautomator": AppiumBy.ANDROID_UIAUTOMATOR,
    }

    by = mapping.get(strategy)
    if by is None:
        supported = ", ".join(sorted(mapping))
        raise LocatorError(f"Unsupported locator strategy '{strategy}'. Supported: {supported}")
    if not value:
        raise LocatorError(f"Locator value is empty for strategy '{strategy}'")
    return by, value
