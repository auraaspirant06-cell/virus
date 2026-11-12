# VIRUS MUSIC BOT - Configuration
# Maintained by Aspirant (Owner: https://t.me/aspirant_u)
# Based on upstream AnonXMusic (MIT License - Copyright (c) 2025 AnonymousX1025)

from os import getenv
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        # Telegram API credentials
        self.API_ID = int(getenv("API_ID", 0))
        self.API_HASH = getenv("API_HASH", "")

        # Bot credentials & branding
        self.BOT_TOKEN = getenv("BOT_TOKEN", "")
        self.BOT_NAME = getenv("BOT_NAME", "VIRUS MUSIC BOT")
        self.BOT_USERNAME = getenv("BOT_USERNAME", "")
        self.OWNER_NAME = getenv("OWNER_NAME", "Aspirant")
        self.OWNER_USERNAME = getenv("OWNER_USERNAME", "aspirant_u")
        self.OWNER_TELEGRAM = getenv("OWNER_TELEGRAM", "https://t.me/aspirant_u")

        # Database
        self.MONGO_URL = getenv("MONGO_URL", "")
        self.MONGO_DB_NAME = getenv("MONGO_DB_NAME", "VirusMusic")

        # Redis Cache (Optional with in-memory fallback)
        self.REDIS_URL = getenv("REDIS_URL", None)

        # Logging & Permissions
        self.LOGGER_ID = int(getenv("LOGGER_ID", 0))
        self.OWNER_ID = int(getenv("OWNER_ID", 0))

        # Limits & Playback
        self.DURATION_LIMIT = int(getenv("DURATION_LIMIT", 60)) * 60
        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", 20))
        self.PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", 20))

        # Pyrogram Assistant Sessions
        self.SESSION1 = getenv("SESSION", None)
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)

        # Configurable Support & Updates Links
        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/kuchupuchuupdates")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/+qqghU-fZtUw4ODQ9")

        # Assistant Behaviour
        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", "False").lower() == "true"
        self.AUTO_END: bool = getenv("AUTO_END", "False").lower() == "true"

        # Media & Feature Flags
        self.THUMB_GEN: bool = getenv("THUMB_GEN", "True").lower() == "true"
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", "True").lower() == "true"

        self.LANG_CODE = getenv("LANG_CODE", "en")

        # API Manager & Reliability Architecture
        self.API_TIMEOUT = int(getenv("API_TIMEOUT", 15))
        self.API_MAX_RETRIES = int(getenv("API_MAX_RETRIES", 3))
        self.API_RETRY_BACKOFF = float(getenv("API_RETRY_BACKOFF", 1.5))
        self.API_CACHE_TTL = int(getenv("API_CACHE_TTL", 3600))
        self.RATE_LIMIT_PER_MINUTE = int(getenv("RATE_LIMIT_PER_MINUTE", 30))
        self.CIRCUIT_BREAKER_FAIL_THRESHOLD = int(getenv("CIRCUIT_BREAKER_FAIL_THRESHOLD", 5))
        self.CIRCUIT_BREAKER_RESET_TIMEOUT = int(getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", 60))

        # YouTube & Streaming
        self.COOKIES_URL = [
            url for url in getenv("COOKIES_URL", "").split(" ")
            if url and ("batbin.me" in url or "pastebin" in url)
        ]
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://te.legra.ph/file/3e40a408286d4eda24191.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://files.catbox.moe/haagg2.png")
        self.START_IMG = getenv("START_IMG", "https://files.catbox.moe/zvziwk.jpg")

    def check(self):
        """Validates critical required variables before bot boot."""
        if getenv("SKIP_ENV_CHECK", "false").lower() == "true":
            return
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID", "SESSION1"]
            if not getattr(self, var)
        ]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")
