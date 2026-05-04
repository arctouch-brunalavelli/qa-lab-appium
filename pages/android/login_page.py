"""
Login screen — Android (UiAutomator2).

The build under test exposes proper resource-ids on the login widgets, so we
locate by id (most stable, fastest, and language-independent). Each locator can
still be overridden at runtime via env vars — see `_by_from_env` below.
"""
from __future__ import annotations

import os

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage

# Locators for the Login screen (resource-ids exposed by the app).
_DEFAULT_USER = (AppiumBy.ID, "login_email_input")
_DEFAULT_PASS = (AppiumBy.ID, "login_password_input")
_DEFAULT_SUBMIT = (AppiumBy.ID, "login_sign_in_button")


def _by_from_env(name: str, default: tuple[str, str]) -> tuple[str, str]:
    """
    Allow overriding locators via env without editing code. Supported prefixes:
      - `xpath=...` or a value starting with `//`  → XPath
      - `acc=...`                                  → accessibility id
      - `ui=...`                                   → UiAutomator selector
      - `id=...` or anything else                  → resource-id
    """
    raw = os.environ.get(name)
    if not raw:
        return default
    if raw.startswith("xpath=") or raw.startswith("//"):
        return (AppiumBy.XPATH, raw.removeprefix("xpath="))
    if raw.startswith("acc="):
        return (AppiumBy.ACCESSIBILITY_ID, raw.removeprefix("acc="))
    if raw.startswith("ui="):
        return (AppiumBy.ANDROID_UIAUTOMATOR, raw.removeprefix("ui="))
    return (AppiumBy.ID, raw.removeprefix("id="))


class AndroidLoginPage(BasePage):
    """User actions for login on Android. No assertions here — BDD steps own expectations."""

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)
        self._user = _by_from_env("ANDROID_LOCATOR_USERNAME", _DEFAULT_USER)
        self._password = _by_from_env("ANDROID_LOCATOR_PASSWORD", _DEFAULT_PASS)
        self._submit = _by_from_env("ANDROID_LOCATOR_LOGIN_BTN", _DEFAULT_SUBMIT)

    def enter_username(self, value: str) -> None:
        el = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located(self._user))
        el.clear()
        el.send_keys(value)

    def enter_password(self, value: str) -> None:
        el = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located(self._password))
        el.clear()
        el.send_keys(value)

    def tap_login(self) -> None:
        el = WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable(self._submit))
        el.click()
