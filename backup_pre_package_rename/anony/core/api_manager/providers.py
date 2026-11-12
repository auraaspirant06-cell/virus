# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - API Reliability Architecture
# Maintained by Aspirant (https://t.me/aspirant_u)

import re
import json
import logging
import asyncio
from typing import Optional, List as TList
from abc import ABC, abstractmethod

from anony.helpers._dataclass import Track
from anony.helpers._utilities import Utilities

logger = logging.getLogger(__name__)
utils = Utilities()


class BaseMusicProvider(ABC):
    """Abstract interface for music metadata and search providers."""

    def __init__(self, name: str, priority: int = 1):
        self.name = name
        self.priority = priority
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency_ms = 0.0

    @abstractmethod
    async def search(self, query: str, video: bool = False, limit: int = 1) -> TList[Track]:
        """Performs search and returns list of Track dataclass instances."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Checks if the provider is reachable and functioning."""
        pass

    def record_metrics(self, success: bool, latency_ms: float):
        self.total_requests += 1
        self.total_latency_ms += latency_ms
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

    def get_stats(self) -> dict:
        avg_latency = (
            round(self.total_latency_ms / self.total_requests, 1)
            if self.total_requests > 0
            else 0.0
        )
        success_rate = (
            round(self.successful_requests / self.total_requests * 100, 1)
            if self.total_requests > 0
            else 100.0
        )
        return {
            "name": self.name,
            "priority": self.priority,
            "total_requests": self.total_requests,
            "success_rate_percent": success_rate,
            "avg_latency_ms": avg_latency,
        }


class PyYTSearchProvider(BaseMusicProvider):
    """Primary YouTube search provider via py-yt-search adapter."""

    def __init__(self, priority: int = 1):
        super().__init__(name="YouTubeSearch-Primary", priority=priority)

    async def search(self, query: str, video: bool = False, limit: int = 1) -> TList[Track]:
        try:
            from py_yt import VideosSearch
        except ImportError:
            logger.warning("[PyYTSearchProvider] py_yt module not installed.")
            return []

        _search = VideosSearch(query, limit=limit, with_live=False)
        results = await _search.next()

        tracks: TList[Track] = []
        if results and results.get("result"):
            for data in results["result"][:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", "Unknown Artist"),
                    duration=data.get("duration", "00:00"),
                    duration_sec=utils.to_seconds(data.get("duration", "00:00")),
                    title=data.get("title", "VIRUS Track")[:50],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url", "").split("?")[0],
                    url=data.get("link", f"https://www.youtube.com/watch?v={data.get('id')}"),
                    view_count=data.get("viewCount", {}).get("short", ""),
                    video=video,
                )
                tracks.append(track)
        return tracks

    async def health_check(self) -> bool:
        try:
            res = await self.search("test", limit=1)
            return len(res) > 0
        except Exception:
            return False


class DirectYTHtmlProvider(BaseMusicProvider):
    """
    Secondary fallback search provider using lightweight direct HTML scraping.
    Operates without third-party dependencies as an authorized backup.
    """

    def __init__(self, priority: int = 2):
        super().__init__(name="YouTube-DirectFallback", priority=priority)
        self.search_url = "https://www.youtube.com/results?search_query="

    async def search(self, query: str, video: bool = False, limit: int = 1) -> TList[Track]:
        import aiohttp
        from urllib.parse import quote_plus

        url = self.search_url + quote_plus(query)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return []
                html = await resp.text()

        # Extract initial data json
        match = re.search(r"var ytInitialData = ({.*?});</script>", html)
        if not match:
            return []

        try:
            data = json.loads(match.group(1))
            contents = (
                data.get("contents", {})
                .get("twoColumnSearchResultsRenderer", {})
                .get("primaryContents", {})
                .get("sectionListRenderer", {})
                .get("contents", [{}])[0]
                .get("itemSectionRenderer", {})
                .get("contents", [])
            )
        except Exception:
            return []

        tracks: TList[Track] = []
        for item in contents:
            v_data = item.get("videoRenderer")
            if not v_data or not v_data.get("videoId"):
                continue

            vid_id = v_data.get("videoId")
            title = (
                v_data.get("title", {})
                .get("runs", [{}])[0]
                .get("text", "VIRUS Track")
            )
            dur_text = v_data.get("lengthText", {}).get("simpleText", "03:00")
            thumbs = v_data.get("thumbnail", {}).get("thumbnails", [])
            thumb_url = thumbs[-1].get("url") if thumbs else ""
            channel = (
                v_data.get("ownerText", {})
                .get("runs", [{}])[0]
                .get("text", "YouTube Artist")
            )

            tracks.append(
                Track(
                    id=vid_id,
                    channel_name=channel,
                    duration=dur_text,
                    duration_sec=utils.to_seconds(dur_text),
                    title=title[:50],
                    thumbnail=thumb_url,
                    url=f"https://www.youtube.com/watch?v={vid_id}",
                    view_count="",
                    video=video,
                )
            )
            if len(tracks) >= limit:
                break

        return tracks

    async def health_check(self) -> bool:
        try:
            tracks = await self.search("music", limit=1)
            return len(tracks) > 0
        except Exception:
            return False
