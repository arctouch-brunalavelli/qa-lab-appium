import sys
from pathlib import Path

import pytest

# Project root on sys.path for `import core` / `import pages` (run `pytest` from repo root)
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.config import AppConfig, PlatformName
from core.driver_factory import create_driver
from core.reachability import appium_tcp_reachable


@pytest.fixture
def app_config() -> AppConfig:
    return AppConfig.from_env()


@pytest.fixture
def driver(app_config: AppConfig):
    """
    Appium session for unit-style smoke tests. Same factory as Behave (single source of truth).
    Requires: device/emulator, app installed, Appium 2 and drivers on APPIUM_SERVER_URL.
    """
    if app_config.platform is not PlatformName.ANDROID:
        pytest.skip("Pytest smoke tests are configured for Android; use MOBILE_PLATFORM=android or Behave for iOS.")
    if not appium_tcp_reachable(app_config.appium_server_url):
        pytest.skip(
            f"Appium is not reachable at {app_config.appium_server_url}. "
            "Start Appium 2, boot the emulator, install the APK, then re-run."
        )
    drv = create_driver(app_config)
    yield drv
    drv.quit()
