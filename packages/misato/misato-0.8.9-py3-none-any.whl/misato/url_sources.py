"""
misato.url_sources - URL source providers for video links

Defines multiple strategies for obtaining video URLs:
- Auto detection (single video vs playlist)
- Authenticated saved collection
- Public playlist parsing
- Search by code
- File-based URL list

All original behavior is preserved with improved structure and type safety.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from enum import Enum

from misato.http_client import HttpClient
from misato.config import (
    HREF_REGEX_PUBLIC_PLAYLIST,
    HREF_REGEX_NEXT_PAGE,
    MATCH_UUID_PATTERN,
)
from misato.utils import ThreadSafeCounter
from misato.logger import logger


class UrlType(Enum):
    SINGLE = "single"
    PLAYLIST = "playlist"


class UrlSource(ABC):
    """Abstract base class for all URL sources."""

    def __init__(self, movie_counter: ThreadSafeCounter, limit: Optional[int] = None):
        self.movie_counter = movie_counter
        self.limit = limit

    @abstractmethod
    def get_urls(self) -> List[str]:
        """Return list of video URLs according to the source strategy."""
        ...

    @staticmethod
    def _log_movie_url(counter: ThreadSafeCounter, url: str) -> None:
        """Log discovered movie URL with incremental counter."""
        logger.info(f"Movie {counter.increment_and_get()} url: {url}")

    @staticmethod
    def _fetch_page_html(http_client: HttpClient, url: str, cookies: Optional[Dict] = None) -> Optional[str]:
        """Centralized HTML fetching with consistent error handling."""
        html = http_client.get_page_html(url, cookies)
        if not html:
            logger.error(f"Failed to fetch page HTML: {url}")
        return html

    @staticmethod
    def _extract_playlist_urls(
        http_client: HttpClient,
        start_url: str,
        limit: Optional[int],
        movie_counter: ThreadSafeCounter,
        cookies: Optional[Dict] = None,
    ) -> List[str]:
        """
        Extract video URLs from paginated playlist pages.
        Handles next-page navigation automatically.
        """
        urls: List[str] = []
        current_url = start_url

        while current_url and (limit is None or movie_counter.get() < limit):
            html = UrlSource._fetch_page_html(http_client, current_url, cookies)
            if not html:
                break

            matches = re.findall(HREF_REGEX_PUBLIC_PLAYLIST, html)
            unique_matches = list(dict.fromkeys(matches))  # Preserve order, remove duplicates

            for video_url in unique_matches:
                if limit and movie_counter.get() >= limit:
                    return urls
                UrlSource._log_movie_url(movie_counter, video_url)
                urls.append(video_url)

            next_page_matches = re.findall(HREF_REGEX_NEXT_PAGE, html)
            current_url = next_page_matches[0].replace('&amp;', '&') if next_page_matches else None

        return urls


class AutoUrlSource(UrlSource):
    """Handles mixed list of URLs: detects single videos vs playlists automatically."""

    def __init__(
        self,
        movie_counter: ThreadSafeCounter,
        auto_urls: List[str],
        limit: Optional[int] = None,
        http_client: Optional[HttpClient] = None,
    ):
        super().__init__(movie_counter, limit)
        self.auto_urls = auto_urls
        self.http_client = http_client or HttpClient()

    def get_urls(self) -> List[str]:
        urls: List[str] = []

        for url in self.auto_urls:
            if self.limit and self.movie_counter.get() >= self.limit:
                break

            if self._is_single_video(url):
                self._log_movie_url(self.movie_counter, url)
                urls.append(url)
            else:
                playlist_urls = self._extract_playlist_urls(
                    self.http_client, url, self.limit, self.movie_counter
                )
                urls.extend(playlist_urls)

        return urls

    def _is_single_video(self, url: str) -> bool:
        """Determine if URL points to a single video by checking for UUID pattern."""
        html = self.http_client.get_page_html(url, None)
        return bool(html and re.search(MATCH_UUID_PATTERN, html))


class AuthSource(UrlSource):
    """Fetches saved videos from authenticated user account."""

    def __init__(
        self,
        movie_counter: ThreadSafeCounter,
        username: str,
        password: str,
        limit: Optional[int] = None,
        http_client: Optional[HttpClient] = None,
    ):
        super().__init__(movie_counter, limit)
        self.http_client = http_client or HttpClient()
        self.cookies = self._login(username, password)

    def _login(self, username: str, password: str) -> Dict[str, str]:
        """Perform login and return cookies dict."""
        response = self.http_client.post(
            "https://missav.ai/api/login",
            data={"email": username, "password": password},
        )
        if response and response.status_code == 200:
            cookie_dict = response.cookies.get_dict()
            if "user_uuid" in cookie_dict:
                logger.info(f"Login successful – user_uuid: {cookie_dict['user_uuid']}")
                return cookie_dict

        logger.error("Login failed. Check credentials or network.")
        raise SystemExit(114514)

    def get_urls(self) -> List[str]:
        return self._extract_playlist_urls(
            self.http_client,
            "https://missav.ai/saved",
            self.limit,
            self.movie_counter,
            cookies=self.cookies,
        )


class SearchSource(UrlSource):
    """Search for a video by its code (e.g., SW-950)."""

    def __init__(
        self,
        movie_counter: ThreadSafeCounter,
        key: str,
        http_client: Optional[HttpClient] = None,
    ):
        super().__init__(movie_counter, None)  # Search typically returns one result
        self.key = key.upper()
        self.http_client = http_client or HttpClient()

    def get_urls(self) -> List[str]:
        search_url = f"https://missav.ai/search/{self.key}"
        search_regex = fr'<a href="([^"]+)" alt="{re.escape(self.key)}">'

        html = self.http_client.get_page_html(search_url, None)
        if not html:
            logger.error(f"Search failed for key: {self.key}")
            return []

        matches = re.findall(search_regex, html)
        unique_matches = list(dict.fromkeys(matches))

        if unique_matches:
            video_url = unique_matches[0]
            self._log_movie_url(self.movie_counter, video_url)
            return [video_url]

        logger.error(f"No results found for search key: {self.key}")
        return []


class FileSource(UrlSource):
    """Read URLs from a local text file (one URL per line)."""

    def __init__(
        self,
        movie_counter: ThreadSafeCounter,
        file_path: str,
        limit: Optional[int] = None,
        http_client: Optional[HttpClient] = None,
    ):
        super().__init__(movie_counter, limit)
        self.file_path = file_path
        self.http_client = http_client or HttpClient()

    def get_urls(self) -> List[str]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logger.error(f"URL file not found: {self.file_path}")
            return []
        except Exception as e:
            logger.error(f"Error reading URL file: {e}")
            return []

        # Reuse AutoUrlSource logic for mixed single/playlist detection
        auto_source = AutoUrlSource(
            movie_counter=self.movie_counter,
            auto_urls=urls,
            limit=self.limit,
            http_client=self.http_client,
        )
        return auto_source.get_urls()