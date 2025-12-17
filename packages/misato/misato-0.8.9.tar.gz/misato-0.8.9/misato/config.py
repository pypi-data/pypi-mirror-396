"""
misato.config - Application configuration module

Centralized configuration using Pydantic Settings for type safety,
environment variable support, and easy overrides.

All original constant values are preserved for full backward compatibility.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from pydantic import Field, AnyHttpUrl, DirectoryPath, FilePath
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.

    Field names are uppercase to match conventional config style.
    All values have defaults matching the original hard-coded constants.
    """

    # ==================== File Paths ====================
    RECORD_FILE: str = "downloaded_urls_misato.txt"
    FFMPEG_INPUT_FILE: str = "ffmpeg_input_misato.txt"
    TMP_HTML_FILE: str = "tmp_movie_misato.html"
    MOVIE_SAVE_PATH_ROOT: str = "movies_folder_misato"

    # ==================== URLs and Patterns ====================
    COVER_URL_PREFIX: AnyHttpUrl = Field(
        default="https://fourhoi.com/",
        description="Base URL for downloading video covers"
    )
    VIDEO_M3U8_PREFIX: AnyHttpUrl = Field(
        default="https://surrit.com/",
        description="Base URL for video playlist and segments"
    )
    VIDEO_PLAYLIST_SUFFIX: str = "/playlist.m3u8"

    HREF_REGEX_MOVIE_COLLECTION: str = r'<a class="text-secondary group-hover:text-primary" href="([^"]+)" alt="'
    HREF_REGEX_PUBLIC_PLAYLIST: str = r'<a href="([^"]+)" alt="'
    HREF_REGEX_NEXT_PAGE: str = r'<a href="([^"]+)" rel="next"'
    MATCH_UUID_PATTERN: str = r'm3u8\|([a-f0-9\|]+)\|com\|surrit\|https\|video'
    MATCH_TITLE_PATTERN: str = r'<title>([^"]+)</title>'
    RESOLUTION_PATTERN: str = r'RESOLUTION=(\d+)x(\d+)'

    # ==================== Magic & Retry Settings ====================
    MAGIC_NUMBER: int = 114514
    RETRY: int = Field(default=5, ge=1, description="Default number of download retries")
    DELAY: int = Field(default=2, ge=0, description="Delay in seconds between retries")
    TIMEOUT: int = Field(default=10, ge=1, description="Timeout in seconds for HTTP requests")

    # ==================== HTTP Headers ====================
    HEADERS: dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

    # ==================== Browser Configuration ====================
    CHROME_EXE: FilePath = Field(
        default=os.getenv('MISATO_CHROME_EXE', r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        description="Path to Chrome executable"
    )
    USER_DATA_DIR: DirectoryPath = Field(
        default=os.getenv('MISATO_CHROME_USER_DATA_DIR', r"C:\workspace\chrome_auto_userdata"),
        description="Chrome user data directory for persistent session"
    )
    DEBUG_PORT: int = Field(default=9222, ge=1024, le=65535)
    MAX_CONNECT_ATTEMPTS: int = Field(default=30, ge=5)

    class Config:
        env_prefix = "MISATO_"   # All env vars will be prefixed with MISATO_
        case_sensitive = False   # Allow lowercase env vars
        env_file = ".env"        # Automatically load .env if present
        env_file_encoding = "utf-8"


# ==================== Global Settings Instance ====================

settings: Final[Settings] = Settings()


# ==================== Backward Compatibility Constants ====================
# These constants preserve exact original names for import compatibility
# e.g., from misato.config import RECORD_FILE  (unchanged)

RECORD_FILE: Final[str] = settings.RECORD_FILE
FFMPEG_INPUT_FILE: Final[str] = settings.FFMPEG_INPUT_FILE
TMP_HTML_FILE: Final[str] = settings.TMP_HTML_FILE
MOVIE_SAVE_PATH_ROOT: Final[str] = settings.MOVIE_SAVE_PATH_ROOT
COVER_URL_PREFIX: Final[str] = str(settings.COVER_URL_PREFIX)
VIDEO_M3U8_PREFIX: Final[str] = str(settings.VIDEO_M3U8_PREFIX)
VIDEO_PLAYLIST_SUFFIX: Final[str] = settings.VIDEO_PLAYLIST_SUFFIX

HREF_REGEX_MOVIE_COLLECTION: Final[str] = settings.HREF_REGEX_MOVIE_COLLECTION
HREF_REGEX_PUBLIC_PLAYLIST: Final[str] = settings.HREF_REGEX_PUBLIC_PLAYLIST
HREF_REGEX_NEXT_PAGE: Final[str] = settings.HREF_REGEX_NEXT_PAGE
MATCH_UUID_PATTERN: Final[str] = settings.MATCH_UUID_PATTERN
MATCH_TITLE_PATTERN: Final[str] = settings.MATCH_TITLE_PATTERN
RESOLUTION_PATTERN: Final[str] = settings.RESOLUTION_PATTERN

MAGIC_NUMBER: Final[int] = settings.MAGIC_NUMBER
RETRY: Final[int] = settings.RETRY
DELAY: Final[int] = settings.DELAY
TIMEOUT: Final[int] = settings.TIMEOUT
HEADERS: Final[dict[str, str]] = settings.HEADERS

CHROME_EXE: Final[Path] = Path(settings.CHROME_EXE)
USER_DATA_DIR: Final[Path] = Path(settings.USER_DATA_DIR)
DEBUG_PORT: Final[int] = settings.DEBUG_PORT
MAX_CONNECT_ATTEMPTS: Final[int] = settings.MAX_CONNECT_ATTEMPTS