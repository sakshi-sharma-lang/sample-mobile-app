from __future__ import annotations

from pages.base_page import BasePage
from utils.config import settings


class HomePage(BasePage):
    @property
    def ready_locator(self) -> str:
        return settings.locator("home", "ready")

    def wait_until_loaded(self) -> "HomePage":
        self.visible(self.ready_locator)
        return self
