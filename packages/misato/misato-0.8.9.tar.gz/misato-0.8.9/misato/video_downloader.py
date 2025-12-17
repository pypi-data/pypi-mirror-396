"""
misato.video_downloader - Core video downloader implementation

Handles the complete download pipeline for a single video:
- Metadata extraction (UUID and title)
- Optional cover download
- Resolution selection from master playlist
- Multi-threaded segment download with original progress bar
- Integrity check
- Video assembly using FFmpeg or direct concatenation
- Optional renaming using full title

All original logic and behavior are preserved exactly.
"""

from __future__ import annotations

import os
import re
import threading
from pathlib import Path
from typing import Optional, Tuple

from misato.http_client import HttpClient
from misato.config import (
    MOVIE_SAVE_PATH_ROOT,
    MATCH_UUID_PATTERN,
    MATCH_TITLE_PATTERN,
    COVER_URL_PREFIX,
    TMP_HTML_FILE,
    RESOLUTION_PATTERN,
    VIDEO_M3U8_PREFIX,
    VIDEO_PLAYLIST_SUFFIX,
)
from misato.logger import logger
from misato.utils import (
    ThreadSafeCounter,
    split_integer_into_intervals,
    find_last_non_empty_line,
    find_closest,
    display_progress_bar,  # Original progress bar that increments counter internally
)
from misato.ffmpeg_processor import FFmpegProcessor


class VideoDownloader:
    """
    Main class responsible for downloading a single video.

    Preserves the exact original download flow and progress display behavior.
    """

    def __init__(self, url: str, http_client: HttpClient, options: dict):
        self.url = url.rstrip("/")
        self.http_client = http_client
        self.options = options

        self.movie_name = Path(self.url).name
        self.movie_folder = Path(MOVIE_SAVE_PATH_ROOT) / self.movie_name
        self.movie_folder.mkdir(parents=True, exist_ok=True)

        self.uuid: Optional[str] = None
        self.title: Optional[str] = None
        self.final_quality: Optional[str] = None

        self.counter = ThreadSafeCounter()

    def _fetch_metadata(self) -> bool:
        """Fetch video page and extract UUID and title."""
        html = self.http_client.get_page_html(self.url, None)
        if not html:
            logger.error(f"Failed to fetch HTML for {self.url}")
            return False

        Path(TMP_HTML_FILE).write_text(html, encoding="utf-8")

        match = re.search(MATCH_UUID_PATTERN, html)
        if not match:
            logger.error("Failed to match UUID pattern.")
            return False
        self.uuid = "-".join(reversed(match.group(1).split("|")))
        logger.info(f"UUID extracted successfully: {self.uuid}")

        title_match = re.search(MATCH_TITLE_PATTERN, html)
        if title_match:
            origin_title = title_match.group(1)
            safe_title = re.sub(r'[<>:"/\\|?* ]', '_', origin_title)
            if "uncensored" in self.url.lower():
                safe_title += "_uncensored"
            self.title = safe_title

        return True

    def _download_cover(self) -> None:
        """Download video cover image if enabled."""
        if not self.options.get('cover_action'):
            return

        cover_url = f"{COVER_URL_PREFIX}{self.movie_name}/cover-n.jpg"
        content = self.http_client.get(cover_url)
        if content:
            cover_path = Path(MOVIE_SAVE_PATH_ROOT) / f"{self.movie_name}-cover.jpg"
            cover_path.write_bytes(content)
        else:
            logger.error(f"Failed to download cover for {self.movie_name}")

    def _get_final_quality_and_resolution(self, playlist: str) -> Tuple[Optional[str], Optional[str]]:
        """Select desired resolution from master playlist and return quality label + sub-playlist URL."""
        matches = re.findall(RESOLUTION_PATTERN, playlist)
        quality_map = {height: width for width, height in matches}
        quality_list = list(quality_map.keys())

        if not quality_list:
            logger.error("No resolutions found in playlist.")
            return None, None

        quality = self.options.get('quality')
        if quality is None:
            final_quality = quality_list[-1] + 'p'
            resolution_url = find_last_non_empty_line(playlist)
        else:
            target = int(quality)
            closest_height = find_closest([int(h) for h in quality_list], target)
            final_quality = str(closest_height) + 'p'
            url_type_x = f"{quality_map[str(closest_height)]}x{closest_height}/video.m3u8"
            url_type_p = f"{closest_height}p/video.m3u8"
            resolution_url = (
                url_type_x if url_type_x in playlist
                else url_type_p if url_type_p in playlist
                else find_last_non_empty_line(playlist)
            )
        return final_quality, resolution_url

    def _thread_task(
        self,
        start: int,
        end: int,
        uuid: str,
        resolution: str,
        video_offset_max: int,
    ) -> None:
        """Thread worker function that downloads segments and updates progress."""
        for i in range(start, end):
            url = f"https://surrit.com/{uuid}/{resolution}/video{i}.jpeg"
            content = self.http_client.get(
                url,
                retries=self.options.get('retry', 5),
                delay=self.options.get('delay', 2),
                timeout=self.options.get('timeout', 10),
            )
            if content:
                file_path = self.movie_folder / f"video{i}.jpeg"
                file_path.write_bytes(content)
                # Critical: Only call display_progress_bar – it increments counter internally
                display_progress_bar(video_offset_max + 1, self.counter)
            else:
                logger.error(f"Failed to download segment {i} for {self.movie_name}")

    def _download_segments(self, uuid: str, resolution: str, video_offset_max: int) -> None:
        """Launch threads to download all video segments with original progress behavior."""
        if not self.options.get('download_action'):
            return

        intervals = split_integer_into_intervals(
            video_offset_max + 1,
            self.options.get('num_threads', os.cpu_count()),
        )
        self.counter.reset()

        threads = []
        for start, end in intervals:
            thread = threading.Thread(
                target=self._thread_task,
                args=(start, end, uuid, resolution, video_offset_max),
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.counter.reset()

    def _check_integrity(self, video_offset_max: int) -> None:
        """Check and log download completeness."""
        downloaded_files = len(list(self.movie_folder.glob("video*.jpeg")))
        total_files = video_offset_max + 1
        integrity = downloaded_files / total_files
        print()  # Ensure newline after progress bar
        logger.info(
            f"File integrity for {self.movie_name}: {integrity:.2%} "
            f"({downloaded_files}/{total_files} files)"
        )

    def _assemble_video(self, video_offset_max: int) -> None:
        """Assemble downloaded segments into final MP4 file."""
        if not self.options.get('write_action'):
            return

        output_name = f"{self.movie_name}_{self.final_quality}.mp4"
        output_path = Path(MOVIE_SAVE_PATH_ROOT) / output_name

        segment_files = [
            self.movie_folder / f"video{i}.jpeg"
            for i in range(video_offset_max + 1)
            if (self.movie_folder / f"video{i}.jpeg").exists()
        ]

        cover_file = None
        if self.options.get('cover_as_preview'):
            cover_candidate = Path(MOVIE_SAVE_PATH_ROOT) / f"{self.movie_name}-cover.jpg"
            if cover_candidate.exists():
                cover_file = str(cover_candidate)

        if self.options.get('ffmpeg_action'):
            FFmpegProcessor.create_video_from_segments(segment_files, str(output_path), cover_file)
        else:
            with output_path.open("wb") as outfile:
                for seg_path in segment_files:
                    outfile.write(seg_path.read_bytes())

        if self.options.get('title_action') and self.title:
            titled_path = Path(MOVIE_SAVE_PATH_ROOT) / f"{self.title}.mp4"
            output_path.rename(titled_path)

    def download(self) -> None:
        """Execute the full download pipeline."""
        if not self._fetch_metadata():
            return

        playlist_url = f"{VIDEO_M3U8_PREFIX}{self.uuid}{VIDEO_PLAYLIST_SUFFIX}"
        playlist_content = self.http_client.get(playlist_url)
        if not playlist_content:
            logger.error("Failed to fetch master playlist.")
            return
        playlist_text = playlist_content.decode("utf-8")

        self.final_quality, resolution_url = self._get_final_quality_and_resolution(playlist_text)
        if not self.final_quality:
            return

        video_m3u8_url = f"{VIDEO_M3U8_PREFIX}{self.uuid}/{resolution_url}"
        video_m3u8_content = self.http_client.get(video_m3u8_url)
        if not video_m3u8_content:
            logger.error("Failed to fetch video m3u8 playlist.")
            return
        video_m3u8_text = video_m3u8_content.decode("utf-8")

        video_offset_max_str = video_m3u8_text.splitlines()[-2]
        video_offset_max = int(re.search(r"\d+", video_offset_max_str).group(0))

        self._download_cover()
        self._download_segments(self.uuid, resolution_url.split("/")[0], video_offset_max)
        self._check_integrity(video_offset_max)
        self._assemble_video(video_offset_max)