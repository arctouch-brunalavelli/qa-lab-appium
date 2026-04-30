"""Check Appium server TCP reachability before opening a session (fast fail, clear errors)."""
from __future__ import annotations

import socket
from urllib.parse import urlparse


def appium_tcp_reachable(url: str, timeout: float = 0.5) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 4723
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False
