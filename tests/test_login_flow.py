from pages.login_page import LoginPage
from utils.app_flow import handle_initial_flow


def test_valid_user_can_login(driver):
    handle_initial_flow(driver)

    LoginPage(driver).wait_until_loaded().login(
        username="testuser",
        password="password123"
    )

    # Replace with real assertion
    assert True