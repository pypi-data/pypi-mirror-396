"""
misato.main - Command-line entry point for the Misato video downloader

Modernized argparse implementation that preserves the exact original command syntax
(-auto, -ffcover, etc.) while providing improved type safety, validation, and help output.
All comments and documentation are in English for professional consistency.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from misato.logger import logger
from misato.config import settings, MOVIE_SAVE_PATH_ROOT, RECORD_FILE, MAGIC_NUMBER
from misato.http_client import HttpClient
from misato.utils import delete_all_subfolders, ThreadSafeCounter, exit_with_cleanup
from misato.video_downloader import VideoDownloader
from misato.url_sources import AutoUrlSource, AuthSource, SearchSource, FileSource


banner = """                                                                                                                                                                                                                 
                  ███                     █████            
                 ░░░                     ░░███             
 █████████████   ████   █████   ██████   ███████    ██████ 
░░███░░███░░███ ░░███  ███░░   ░░░░░███ ░░░███░    ███░░███
 ░███ ░███ ░███  ░███ ░░█████   ███████   ░███    ░███ ░███
 ░███ ░███ ░███  ░███  ░░░░███ ███░░███   ░███ ███░███ ░███
 █████░███ █████ █████ ██████ ░░████████  ░░█████ ░░██████ 
░░░░░ ░░░ ░░░░░ ░░░░░ ░░░░░░   ░░░░░░░░    ░░░░░   ░░░░░░                                                                                                                                                                                                                                                                                                                                   
"""


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="misato",  # Ensures "Usage: misato" in help output
        description="Misato - MissAV video downloader",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  misato -auto https://missav.ws/roe-414 -ffcover -title -quality 720
  misato -auto https://missav.ws/actresses/JULIA -limit 20 -ffmpeg
  misato -search roe-414 -ffcover
  misato -file urls.txt -title -proxy localhost:7890
        """,
    )

    # Mutually exclusive source selection (exactly one required)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "-auto",
        nargs="+",
        metavar="URL",
        help="One or more video or playlist URLs (can be mixed)",
    )
    # source_group.add_argument(
    #     "-auth",
    #     nargs=2,
    #     metavar=("USER", "PASS"),
    #     help="Username and password to download saved collection",
    # )
    source_group.add_argument("-search", metavar="CODE", help="Search video by code (e.g., roe-414)")
    source_group.add_argument(
        "-file",
        type=Path,
        metavar="PATH",
        help="Text file containing URLs (one per line)",
    )

    # Optional parameters
    parser.add_argument("-limit", type=int, help="Maximum number of videos to download")
    parser.add_argument("-proxy", help="HTTP/HTTPS proxy (host:port)")
    parser.add_argument("-ffmpeg", action="store_true", help="Enable FFmpeg merging for best quality")
    parser.add_argument("-cover", action="store_true", help="Download video cover image")
    parser.add_argument(
        "-ffcover",
        action="store_true",
        help="Embed cover as video thumbnail (requires FFmpeg)",
    )
    parser.add_argument(
        "-noban",
        "--no-banner",
        action="store_true",
        help="Suppress the ASCII art banner",
    )
    parser.add_argument("-title", action="store_true", help="Use full video title as filename")
    parser.add_argument("-quality", type=int, help="Preferred resolution (e.g., 720, 1080)")
    parser.add_argument("-retry", type=int, help="Number of retries per segment")
    parser.add_argument("-delay", type=int, help="Delay between retries in seconds")
    parser.add_argument("-timeout", type=int, help="Timeout per segment download in seconds")

    return parser


def main() -> None:
    """Main entry point for the application."""
    parser = create_parser()
    args = parser.parse_args()

    # Display banner unless suppressed
    if not args.no_banner:
        print(banner)

    # Configure proxy if provided
    if args.proxy:
        proxy_url = f"http://{args.proxy}"
        os.environ["http_proxy"] = proxy_url
        os.environ["https_proxy"] = proxy_url
        logger.info(f"Proxy configured: {args.proxy}")

    # -ffcover implies -ffmpeg and -cover
    if args.ffcover:
        args.ffmpeg = True
        args.cover = True

    # Build download options dictionary
    options = {
        "download_action": True,
        "write_action": True,
        "ffmpeg_action": args.ffmpeg,
        "num_threads": os.cpu_count(),
        "cover_action": args.cover,
        "title_action": args.title,
        "cover_as_preview": args.ffcover,
        "quality": args.quality,
        "retry": args.retry or settings.RETRY,
        "delay": args.delay or settings.DELAY,
        "timeout": args.timeout or settings.TIMEOUT,
    }

    # Initialize shared components
    http_client = HttpClient()
    counter = ThreadSafeCounter()

    # Determine URL source
    if args.auto:
        source = AutoUrlSource(movie_counter=counter, auto_urls=args.auto, limit=args.limit)
    elif args.auth:
        source = AuthSource(
            movie_counter=counter,
            username=args.auth[0],
            password=args.auth[1],
            limit=args.limit,
        )
    elif args.search:
        source = SearchSource(movie_counter=counter, key=args.search)
    elif args.file:
        if not args.file.is_file():
            logger.error(f"URL file not found: {args.file}")
            exit_with_cleanup(1)
        source = FileSource(movie_counter=counter, file_path=str(args.file), limit=args.limit)

    # Retrieve video URLs
    urls = source.get_urls()
    if not urls:
        logger.error("No valid URLs retrieved from source.")
        exit_with_cleanup(1)

    # Load download record for deduplication
    record_path = Path(RECORD_FILE)
    downloaded_urls = set()
    if record_path.exists():
        try:
            downloaded_urls = {
                line.strip()
                for line in record_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            }
        except Exception as e:
            logger.warning(f"Failed to read download record file: {e}")

    # Main download loop
    for url in urls:
        if url in downloaded_urls:
            logger.info(f"Already downloaded, skipping: {url}")
            continue

        delete_all_subfolders(MOVIE_SAVE_PATH_ROOT)
        logger.info(f"Starting download: {url}")

        try:
            downloader = VideoDownloader(url=url, http_client=http_client, options=options)
            downloader.download()

            # Record successful download (safe append mode)
            try:
                with record_path.open("a", encoding="utf-8") as f:
                    f.write(url + "\n")
                logger.debug(f"Recorded download: {url}")
            except Exception as e:
                logger.warning(f"Failed to record download: {e}")

            logger.info(f"Successfully completed: {url}\n")
        except Exception as e:
            logger.error(f"Download failed: {url} | Error: {e}")

    # Final cleanup of temporary folders
    delete_all_subfolders(MOVIE_SAVE_PATH_ROOT)
    logger.info("Temporary segment folders cleaned up.")

    logger.info("All tasks completed. Enjoy your videos! ❤️")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        exit_with_cleanup(MAGIC_NUMBER)