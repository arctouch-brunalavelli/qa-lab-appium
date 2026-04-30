"""
Central configuration for Appium and the app under test.

Environment variables allow CI/local overrides without code changes. Defaults match
the existing arctouch demo app used in pytest smoke tests.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class PlatformName(str, Enum):
    """Supported automation targets. Extend (e.g. HARMONY) as needed."""

    ANDROID = "android"
    IOS = "ios"


@dataclass(frozen=True)
class AppConfig:
    """App identifiers and server URL. Immutable so hooks share a single source of truth."""

    appium_server_url: str
    platform: PlatformName
    android_app_package: str
    android_app_activity: str
    # Placeholder: set MOBILE_IOS_BUNDLE_ID when you run on iOS Simulator/device.
    ios_bundle_id: str
    # Session flags — tune per app (e.g. fullReset for clean installs).
    no_reset: bool = True

    @classmethod
    def from_env(cls) -> "AppConfig":
        platform_raw = os.environ.get("MOBILE_PLATFORM", "android").strip().lower()
        if platform_raw not in ("android", "ios"):
            platform_raw = "android"
        return cls(
            appium_server_url=os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723"),
            platform=PlatformName(platform_raw),
            android_app_package=os.environ.get("ANDROID_APP_PACKAGE", "com.arctouch.arctouch_demo_app"),
            android_app_activity=os.environ.get(
                "ANDROID_APP_ACTIVITY",
                "com.arctouch.arctouch_demo_app.MainActivity",
            ),
            ios_bundle_id=os.environ.get("MOBILE_IOS_BUNDLE_ID", "com.example.app"),
            no_reset=os.environ.get("APPIUM_NO_RESET", "true").lower() in ("1", "true", "yes"),
        )
