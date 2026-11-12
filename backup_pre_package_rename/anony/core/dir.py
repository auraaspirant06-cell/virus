# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - Maintained by Aspirant (https://t.me/aspirant_u)

import shutil
from pathlib import Path
from anony import logger


def ensure_dirs():
    """
    Ensure that the necessary working directories exist,
    and verify optional/required external dependencies gracefully.
    """
    if not shutil.which("ffmpeg"):
        logger.warning("FFmpeg executable was not detected in PATH. Audio streaming may require FFmpeg at runtime.")

    if not shutil.which("deno"):
        logger.info("Deno is not installed in PATH. Standard yt-dlp extractor will be used.")

    for directory in ["cache", "downloads"]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    logger.info("Cache and downloads directories initialized.")
