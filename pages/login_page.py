from __future__ import annotations

from pages.base_page import BasePage
from utils.config import settings


class LoginPage(BasePage):
    @property
    def username_locator(self) -> str:
        return settings.locator("login", "username")

    @property
    def password_locator(self) -> str:
        return settings.locator("login", "password")

    @property
    def submit_locator(self) -> str:
        return settings.locator("login", "submit")

    def wait_until_loaded(self) -> "LoginPage":
        self.visible(self.username_locator)
        self.visible(self.password_locator)
        return self

    def login(self, username: str, password: str) -> None:
        self.type_text(self.username_locator, username)
        self.type_text(self.password_locator, password)
        self.tap(self.submit_locator)
