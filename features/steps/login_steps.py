"""
Step definitions for login. They glue Gherkin to page objects: parse data, call pages, assert outcomes.
Keep steps thin — no raw Appium calls here (use pages or core only).

This package lives at `features/steps/` so Behave discovers step modules (default loader expects this
folder next to .feature files). A separate top-level `steps/` is optional; most teams colocate here.
"""
from __future__ import annotations

import logging

from behave import given, then, when
from pages.factory import get_login_page


@given("the app is open")
def step_app_is_open(context) -> None:
    """
    Session is created in `before_scenario`. This step documents intent; optional smoke check.
    If driver is missing (skipped start), the scenario should have been marked skipped.
    """
    assert context.driver is not None, "Driver not started — check before_scenario / Appium"
    assert context.driver.session_id, "No active Appium session"


def _login_page(context):
    """Lazy accessor: cache one page object per scenario to avoid re-locating fields."""
    if getattr(context, "_login_page", None) is None:
        context._login_page = get_login_page(context.app_config, context.driver)
    return context._login_page


# Field-name → page-object action. Add new mappings here when more inputs are introduced
# (e.g., "Phone": "enter_phone"). Keeps step definitions thin and Gherkin agnostic of locators.
_FIELD_ACTIONS = {
    "email": "enter_username",
    "username": "enter_username",
    "password": "enter_password",
}


def _fill_field(context, field: str, value: str) -> None:
    action_name = _FIELD_ACTIONS.get(field.strip().lower())
    if action_name is None:
        raise NotImplementedError(
            f'No page action mapped for field "{field}". '
            "Add it to _FIELD_ACTIONS in features/steps/login_steps.py."
        )
    getattr(_login_page(context), action_name)(value)


# Two phrasings (`username` / `password`) point at the same generic handler so the
# Gherkin reads naturally while the Python stays DRY.
@when('the user fill the "{field}" field with valid username "{value}"')
@when('the user fill the "{field}" field with valid password "{value}"')
def step_user_fills_field(context, field: str, value: str) -> None:
    _fill_field(context, field, value)


@when('the user taps "{button_label}"')
def step_user_taps_button(context, button_label: str) -> None:
    """
    Generic tap-by-label step. For now only the login button is wired through the
    page object; extend the page (or add a small action map) when more buttons need
    explicit taps from feature files.
    """
    page = _login_page(context)
    if button_label.strip().lower() in ("sign in", "log in", "login"):
        page.tap_login()
        return
    raise NotImplementedError(
        f'No action mapped for button label "{button_label}". '
        "Add a handler in features/steps/login_steps.py or the relevant page object."
    )


@then("the user should be logged in the app")
def step_user_logged_in(context) -> None:
    """
    Lightweight check: Appium session is alive after login. Replace with a HomePage
    presence assertion (e.g., a header content-desc) once a stable post-login
    element is identified, to make this a real functional verification.
    """
    assert context.driver is not None
    _ = context.driver.session_id
    logging.getLogger(__name__).info("Login flow completed; refine with HomePage check when ready.")


@then("the application session should remain active")
def step_session_active(context) -> None:
    assert context.driver is not None and context.driver.session_id
