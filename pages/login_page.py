from pages.base_page import BasePage


class LoginPage(BasePage):

    # ✅ FIXED LOCATORS (based on your app package)
    username_locator = ("id", "com.skill2lead.appiumdemo:id/etEmail")
    password_locator = ("id", "com.skill2lead.appiumdemo:id/etPassword")
    login_button_locator = ("id", "com.skill2lead.appiumdemo:id/btnLogin")

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