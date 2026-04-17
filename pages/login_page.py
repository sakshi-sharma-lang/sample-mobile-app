from pages.base_page import BasePage


class LoginPage(BasePage):

    username_locator = ("id", "com.example:id/username")
    password_locator = ("id", "com.example:id/password")
    login_button_locator = ("id", "com.example:id/login")

    def wait_until_loaded(self):
        try:
            self.visible(self.username_locator)
        except Exception:
            print("Login screen not loaded properly")
            raise
        return self

    def login(self, username, password):
        self.send_keys(self.username_locator, username)
        self.send_keys(self.password_locator, password)
        self.click(self.login_button_locator)