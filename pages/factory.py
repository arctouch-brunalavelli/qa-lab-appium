"""
Page factory: returns the right screen object for the current platform.

This avoids if/else in every step and keeps Gherkin platform-agnostic. Add new screens by
implementing both Android and iOS classes and a branch here.
"""
from __future__ import annotations

from appium.webdriver.webdriver import WebDriver

from core.config import AppConfig, PlatformName
from pages.android.login_page import AndroidLoginPage
from pages.ios.login_page import IosLoginPage


def get_login_page(config: AppConfig, driver: WebDriver):
    if config.platform is PlatformName.ANDROID:
        return AndroidLoginPage(driver)
    if config.platform is PlatformName.IOS:
        return IosLoginPage(driver)
    raise ValueError(f"Unsupported platform: {config.platform!r}")
