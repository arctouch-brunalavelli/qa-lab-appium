"""
Behave environment: hooks own Appium driver lifecycle (one session per scenario by default).

Why one session per scenario: isolates failures, mimics user cold start, and avoids state leaks.
For faster runs, switch to `before_all` / `after_all` with care (shared state, ordering).

Test reporting (integration ideas):
- JUnit XML: `behave -f junit -o reports/junit.xml` (CI-friendly)
- Allure: install `allure-behave`, add `allure_behave` to formatters, publish `allure-results/`
- Pretty HTML: `behave -f allure_behave --allure-capture=stdout` or third-party `behave-html-pretty`
- TestRail: custom formatter or run Behave in CI and push results via API

See `behave.ini` for default formatter options you can override in CI.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Project root on sys.path so `core`, `pages`, and `steps` import without installing a package
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Step modules live in `features/steps/`; Behave loads them automatically.
from behave import use_step_matcher

use_step_matcher("parse")

from core.config import AppConfig
from core.driver_factory import create_driver
from core.reachability import appium_tcp_reachable

logger = logging.getLogger(__name__)


def before_scenario(context, scenario) -> None:
    """Start a fresh Appium session; attach config + driver to `context` for steps."""
    # Not `context.config` — Behave already uses that for its own RunnerConfig.
    context.app_config = AppConfig.from_env()
    if not appium_tcp_reachable(context.app_config.appium_server_url):
        scenario.skip(
            f"Appium is not reachable at {context.app_config.appium_server_url}. "
            "Start Appium 2, boot a device/simulator, install the app, then re-run."
        )
        return
    try:
        context.driver = create_driver(context.app_config)
    except Exception:
        logger.exception("Failed to create Appium session")
        raise
    # Pages are created on demand in steps via factory (no heavy work here).
    context._login_page = None  # cache reset for the lazy accessor in step modules


def after_scenario(context, scenario) -> None:
    """Always quit the driver to free the device and avoid orphaned sessions."""
    driver = getattr(context, "driver", None)
    if driver is not None:
        try:
            driver.quit()
        except Exception:
            logger.exception("driver.quit() failed; device may need manual cleanup")
        finally:
            context.driver = None
