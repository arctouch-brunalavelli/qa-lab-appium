"""
Login screen — iOS (XCUITest).

Parallel API to Android for the same Gherkin steps. Locators are accessibility identifiers
or iOS class chain / predicate; set via env or edit defaults when the iOS app is available.
"""
from __future__ import annotations

import os

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage

_DEFAULT_USER = (AppiumBy.ACCESSIBILITY_ID, "loginUsername")
_DEFAULT_PASS = (AppiumBy.ACCESSIBILITY_ID, "loginPassword")
_DEFAULT_SUBMIT = (AppiumBy.ACCESSIBILITY_ID, "loginButton")


def _by_from_env(name: str, default: tuple[str, str]) -> tuple[str, str]:
    raw = os.environ.get(name)
    if not raw:
        return default
    if raw.startswith("label=") or raw.startswith("name="):
        return (AppiumBy.IOS_PREDICATE, raw)
    return (AppiumBy.ACCESSIBILITY_ID, raw)


class IosLoginPage(BasePage):
    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)
        self._user = _by_from_env("IOS_LOCATOR_USERNAME", _DEFAULT_USER)
        self._password = _by_from_env("IOS_LOCATOR_PASSWORD", _DEFAULT_PASS)
        self._submit = _by_from_env("IOS_LOCATOR_LOGIN_BTN", _DEFAULT_SUBMIT)

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
