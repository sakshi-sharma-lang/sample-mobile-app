from __future__ import annotations

import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage
from utils.config import settings


@pytest.mark.login
@pytest.mark.regression
def test_valid_user_can_login(driver) -> None:
    LoginPage(driver).wait_until_loaded().login(
        username=settings.test_data("username"),
        password=settings.test_data("password"),
    )

    HomePage(driver).wait_until_loaded()
