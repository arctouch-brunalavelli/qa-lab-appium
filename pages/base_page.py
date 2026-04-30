"""
Base page: shared driver access and small waits. Subclasses own locators and user-facing actions.
Keep assertions out of page objects (assert in steps or a dedicated assertion helper) for clearer BDD.
"""
from __future__ import annotations

from appium.webdriver.webdriver import WebDriver


class BasePage:
    """Minimal POM base; extend per screen. Driver is the only required dependency."""

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver

    @property
    def driver(self) -> WebDriver:
        return self._driver
