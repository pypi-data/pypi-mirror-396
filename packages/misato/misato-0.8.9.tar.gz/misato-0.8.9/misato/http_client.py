"""
misato.http_client - HTTP client module (with optional singleton support)

Provides a robust HTTP client using curl_cffi for requests with Chrome impersonation,
and Playwright for rendering dynamic pages.

All original behavior is preserved. Singleton pattern is optionally applied
for cleaner global usage while maintaining full backward compatibility.
"""

from __future__ import annotations

import time
from typing import Optional, Dict

from curl_cffi import requests
from playwright.sync_api import Page

from misato.chrome import page as global_page
from misato.config import HEADERS, RETRY, DELAY, TIMEOUT
from misato.logger import logger


class HttpClient:
    """
    HTTP client with retry support and Playwright integration.

    Optional singleton: the first instance created becomes the global one.
    Subsequent calls to HttpClient() return the same instance.
    This preserves original behavior while ensuring only one instance exists.
    """

    _instance: Optional["HttpClient"] = None

    def __new__(cls, playwright_page: Optional[Page] = None) -> "HttpClient":
        """
        Implement singleton pattern.
        If an instance already exists, return it (ignoring new page parameter for safety).
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # First-time initialization will happen in __init__
        elif playwright_page is not None:
            # Warn if someone tries to inject a different page into an existing singleton
            logger.warning(
                "HttpClient is singleton; ignoring attempt to inject different Playwright page."
            )
        return cls._instance

    def __init__(self, playwright_page: Optional[Page] = None):
        """
        Initialize only on first creation.
        """
        # Prevent re-initialization on subsequent calls
        if hasattr(self, "_initialized"):
            return

        self.page: Page = playwright_page or global_page
        self._initialized = True  # Mark as initialized

    def get(
        self,
        url: str,
        cookies: Optional[Dict[str, str]] = None,
        retries: int = RETRY,
        delay: int = DELAY,
        timeout: int = TIMEOUT,
    ) -> Optional[bytes]:
        """Download content with retry logic using curl_cffi."""
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(
                    url=url,
                    headers=HEADERS,
                    cookies=cookies,
                    timeout=timeout,
                    verify=False,
                    impersonate="chrome124",
                )
                return response.content
            except Exception as e:
                logger.error(f"GET failed (attempt {attempt}/{retries}): {e} | URL: {url}")
                if attempt < retries:
                    time.sleep(delay)

        logger.error(f"Max retries ({retries}) exceeded for GET: {url}")
        return None

    def post(
        self,
        url: str,
        data: dict,
        cookies: Optional[Dict[str, str]] = None,
        retries: int = RETRY,
        delay: int = DELAY,
        timeout: int = TIMEOUT,
    ) -> Optional[requests.Response]:
        """Send POST request with retry logic."""
        for attempt in range(1, retries + 1):
            try:
                response = requests.post(
                    url=url,
                    data=data,
                    headers=HEADERS,
                    cookies=cookies,
                    timeout=timeout,
                    verify=False,
                    impersonate="chrome124",
                )
                return response
            except Exception as e:
                logger.error(f"POST failed (attempt {attempt}/{retries}): {e} | URL: {url}")
                if attempt < retries:
                    time.sleep(delay)

        logger.error(f"Max retries ({retries}) exceeded for POST: {url}")
        return None

    def get_page_html(self, url: str, cookies: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Fetch rendered HTML using Playwright with original memory-release behavior."""
        try:
            self.page.goto(url, wait_until="domcontentloaded")
            content = self.page.content()
            self.page.goto("about:blank")  # Original special behavior
            return content
        except Exception as e:
            logger.error(f"Failed to fetch page HTML: {e} | URL: {url}")
            return None