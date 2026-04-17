from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_app_launches(driver) -> None:
    assert driver.session_id, "Appium session was not created"
    assert driver.current_package, "Android package was not detected after app launch"
