"""
Appium WebDriver construction per platform.

Factory pattern: callers depend on a single `create_driver(config)` entry point.
Android uses UiAutomator2Options; iOS uses XCUITestOptions — both are created here so
new platforms add one branch, not changes scattered across steps.
"""
from __future__ import annotations

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.webdriver import WebDriver

from core.config import AppConfig, PlatformName


def _build_android_options(config: AppConfig) -> UiAutomator2Options:
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.set_capability("appium:appPackage", config.android_app_package)
    options.set_capability("appium:appActivity", config.android_app_activity)
    options.set_capability("appium:noReset", config.no_reset)
    return options


def _build_ios_options(config: AppConfig) -> XCUITestOptions:
    # iOS: install path or bundle id is typically required. Replace bundle id and add
    # `app` capability (path to .app/.ipa) when you wire a real iOS build.
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.automation_name = "XCUITest"
    options.set_capability("appium:bundleId", config.ios_bundle_id)
    options.set_capability("appium:noReset", config.no_reset)
    return options


def create_driver(config: AppConfig) -> WebDriver:
    """
    Return a new Appium session for the configured platform.
    Callers own lifecycle: quit in after_scenario / fixture teardown.
    """
    if config.platform is PlatformName.ANDROID:
        opts = _build_android_options(config)
    elif config.platform is PlatformName.IOS:
        opts = _build_ios_options(config)
    else:  # pragma: no cover - enum exhaustive
        raise ValueError(f"Unsupported platform: {config.platform!r}")
    return webdriver.Remote(config.appium_server_url, options=opts)
