"""
misato.ffmpeg_processor - FFmpeg processing utilities

Provides a safe wrapper for merging video segments using FFmpeg's concat demuxer,
with optional cover image embedding as attached picture (preview thumbnail).

All original behavior is preserved:
- Creates temporary concat list file
- Uses exactly the same ffmpeg command structure
- Supports optional cover attachment with correct mapping and disposition
- Logs success/failure identically
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional

from misato.config import FFMPEG_INPUT_FILE
from misato.logger import logger


class FFmpegProcessor:
    """
    Utility class for video assembly using FFmpeg.

    Static methods only – no instance state required.
    """

    @staticmethod
    def create_video_from_segments(
        segment_files: List[str | Path],
        output_file: str | Path,
        cover_file: Optional[str | Path] = None,
    ) -> None:
        """
        Merge video segments into a single MP4 file using FFmpeg concat demuxer.

        Args:
            segment_files: List of paths to segment files (typically .jpeg or .ts)
            output_file: Destination path for the final .mp4 file
            cover_file: Optional path to cover image to embed as attached picture (thumbnail)

        Raises:
            subprocess.CalledProcessError: If ffmpeg command fails
            FileNotFoundError: If ffmpeg is not available in PATH
        """
        # Convert to Path for consistent handling
        segment_paths = [Path(f) for f in segment_files]
        output_path = Path(output_file)
        cover_path: Optional[Path] = Path(cover_file) if cover_file else None

        # Validate inputs
        if not segment_paths:
            raise ValueError("segment_files cannot be empty")

        for seg in segment_paths:
            if not seg.exists():
                logger.warning(f"Missing segment file (will be skipped by ffmpeg): {seg}")

        if cover_path and not cover_path.exists():
            logger.warning(f"Cover file not found (will be ignored): {cover_path}")
            cover_path = None

        # Write concat list file (automatically cleaned up on scope exit)
        concat_list_path = Path(FFMPEG_INPUT_FILE)
        try:
            concat_list_path.write_text(
                "\n".join(f"file '{p.resolve()}'" for p in segment_paths),
                encoding="utf-8",
            )
            logger.debug(f"FFmpeg concat list written to: {concat_list_path}")
        except Exception as e:
            logger.error(f"Failed to write FFmpeg input list: {e}")
            raise

        # Build ffmpeg command exactly as original
        cmd: List[str] = [
            "ffmpeg",
            "-y",                  # Overwrite output without asking
            "-loglevel", "error",  # Suppress info/warning output
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_path),
        ]

        if cover_path:
            cmd.extend([
                "-i", str(cover_path.resolve()),
                "-map", "0",           # Map all streams from first input (video segments)
                "-map", "1",           # Map image from second input
                "-c", "copy",          # Stream copy – no re-encoding
                "-disposition:v:1", "attached_pic",  # Mark second video stream as cover
            ])
        else:
            cmd.extend(["-c", "copy"])

        cmd.append(str(output_path))

        # Execute ffmpeg
        logger.info(f"Starting FFmpeg merge → {output_path.name}")
        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info("FFmpeg execution completed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg merge failed with return code {e.returncode}")
            raise
        except FileNotFoundError:
            logger.error("ffmpeg command not found in PATH. Please install FFmpeg.")
            raise
        finally:
            # Optional: clean up concat list file (safe even if it doesn't exist)
            try:
                if concat_list_path.exists():
                    concat_list_path.unlink()
            except Exception:
                pass