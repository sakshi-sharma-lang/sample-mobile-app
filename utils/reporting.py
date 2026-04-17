from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from appium.webdriver.webdriver import WebDriver


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "reports"


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    return cleaned[:180] or "artifact"


def timestamp_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_reports_dir() -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR


def capture_screenshot(driver: WebDriver, test_name: str) -> Path:
    reports_dir = ensure_reports_dir()
    screenshot_path = reports_dir / f"{safe_filename(test_name)}_{timestamp_utc()}.png"
    driver.save_screenshot(str(screenshot_path))
    return screenshot_path
