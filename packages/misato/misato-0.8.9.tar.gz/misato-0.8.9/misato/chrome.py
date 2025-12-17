import os
import sys
import time
import json
import subprocess
import urllib.request
from typing import Optional

from playwright.sync_api import sync_playwright, Browser, Page, Playwright

from misato.logger import logger
from misato.config import (
    CHROME_EXE,
    USER_DATA_DIR,
    DEBUG_PORT,
    MAX_CONNECT_ATTEMPTS,
)

# ========================== GLOBAL SINGLETONS ==========================
_playwright: Optional[Playwright] = None
_browser: Optional[Browser] = None
_page: Optional[Page] = None


# ========================== CHROME DETECTION ==========================
def _chrome_alive() -> bool:
    """
    Check whether Chrome is already running with remote debugging enabled.
    This is the official & reliable CDP health check.
    """
    try:
        with urllib.request.urlopen(
            f"http://localhost:{DEBUG_PORT}/json/version",
            timeout=0.5,
        ) as resp:
            data = json.load(resp)
            return "webSocketDebuggerUrl" in data
    except Exception:
        return False


# ========================== CHROME LAUNCH ==========================
def _launch_chrome() -> None:
    """
    Launch Chrome with remote debugging enabled.
    Safe to call only when Chrome is not already running.
    """
    os.makedirs(USER_DATA_DIR, exist_ok=True)

    subprocess.Popen(
        [
            CHROME_EXE,
            f"--remote-debugging-port={DEBUG_PORT}",
            f"--user-data-dir={USER_DATA_DIR}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )

    logger.info(f"Chrome launched on debug port {DEBUG_PORT}")


# ========================== CONNECT LOGIC ==========================
def _connect_once() -> None:
    """
    Connect to an existing Chrome instance via CDP.
    Retries until MAX_CONNECT_ATTEMPTS.
    """
    global _playwright, _browser, _page

    # Fast path: connection already alive
    if _page is not None:
        try:
            _page.title()
            return
        except Exception:
            pass  # stale connection → reconnect

    logger.info("Connecting to Chrome via CDP")

    for attempt in range(1, MAX_CONNECT_ATTEMPTS + 1):
        try:
            _playwright = sync_playwright().start()
            _browser = _playwright.chromium.connect_over_cdp(
                f"http://localhost:{DEBUG_PORT}"
            )

            # Reuse first context
            context = _browser.contexts[0]

            # Reuse existing tab or create one
            _page = context.pages[0] if context.pages else context.new_page()

            # Optional performance optimization
            _page.route(
                "**/*",
                lambda route, request: route.abort()
                if request.resource_type
                in {"image", "stylesheet", "font", "media"}
                else route.continue_(),
            )

            logger.info("Successfully connected to Chrome")
            return

        except Exception as e:
            logger.info(
                f"Connect attempt {attempt}/{MAX_CONNECT_ATTEMPTS} failed, retrying..."
            )
            time.sleep(1)

    logger.error(
        f"Failed to connect to Chrome on port {DEBUG_PORT} after {MAX_CONNECT_ATTEMPTS}s"
    )
    sys.exit(1)


# ========================== ENSURE READY ==========================
def _ensure_ready() -> None:
    """
    Ensure Chrome + Playwright + Page are ready.
    Called once on import.
    """
    if _page is not None:
        return

    if _chrome_alive():
        logger.info("Existing Chrome detected, reusing it")
    else:
        logger.info("No Chrome detected, launching new instance")
        _launch_chrome()

    _connect_once()


# ========================== AUTO INIT ==========================
_ensure_ready()

# ========================== PUBLIC API ==========================
browser: Browser = _browser   # Advanced use only
page: Page = _page            # Main singleton page
