# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - Maintained by Aspirant (https://t.me/aspirant_u)

import os
import asyncio
import aiohttp
try:
    from PIL import (Image, ImageDraw, ImageEnhance,
                     ImageFilter, ImageFont, ImageOps)
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from anony import config, logger
from anony.helpers import Track


class Thumbnail:
    def __init__(self):
        self.rect = (914, 514)
        self.fill = (255, 255, 255)
        self.mask = Image.new("L", self.rect, 0) if HAS_PIL else None
        if HAS_PIL:
            try:
                self.font1 = ImageFont.truetype("anony/helpers/Raleway-Bold.ttf", 30)
                self.font2 = ImageFont.truetype("anony/helpers/Inter-Light.ttf", 30)
                self.font_brand = ImageFont.truetype("anony/helpers/Raleway-Bold.ttf", 22)
            except Exception:
                self.font1 = ImageFont.load_default()
                self.font2 = ImageFont.load_default()
                self.font_brand = ImageFont.load_default()
        self.session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def save_thumb(self, output_path: str, url: str) -> str:
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        async with self.session.get(url) as resp:
            with open(output_path, "wb") as f:
                f.write(await resp.read())
        return output_path

    def _render(self, temp: str, output: str, song: Track, size=(1280, 720)) -> str:
        thumb = Image.open(temp).convert("RGBA").resize(
            size, Image.Resampling.LANCZOS,
        )
        blur = thumb.filter(ImageFilter.GaussianBlur(25))
        image = ImageEnhance.Brightness(blur).enhance(.40)

        _rect = ImageOps.fit(
            thumb, self.rect,
            method=Image.LANCZOS, centering=(0.5, 0.5),
        )
        mask = Image.new("L", self.rect, 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, self.rect[0], self.rect[1]),
            radius=18,
            fill=255,
        )
        _rect.putalpha(mask)
        image.paste(_rect, (183, 30), _rect)

        draw = ImageDraw.Draw(image)

        # Branding tag
        draw.text(
            xy=(50, 520),
            text="VIRUS MUSIC",
            font=self.font_brand,
            fill=(180, 100, 255),
        )

        # Channel & views
        channel = song.channel_name[:25] if song.channel_name else "YouTube"
        views = f" | {song.view_count}" if song.view_count else ""
        draw.text(
            xy=(50, 560),
            text=f"{channel}{views}",
            font=self.font2,
            fill=self.fill,
        )

        # Title
        title = song.title[:50] if song.title else "VIRUS MUSIC Audio"
        draw.text((50, 600), title, font=self.font1, fill=self.fill)

        # Progress bar
        draw.text((40, 650), "0:00", font=self.font1, fill=self.fill)
        draw.line([(140, 670), (1160, 670)], fill=self.fill, width=5, joint="curve")
        duration = song.duration if song.duration else "00:00"
        draw.text((1185, 650), duration, font=self.font1, fill=self.fill)

        image.save(output)
        try:
            os.remove(temp)
        except Exception:
            pass
        return output

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        if not HAS_PIL:
            return config.DEFAULT_THUMB
        try:
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}.png"
            if os.path.exists(output):
                return output

            await self.save_thumb(temp, song.thumbnail)
            return await asyncio.to_thread(self._render, temp, output, song, size)
        except Exception as ex:
            logger.warning(f"Thumbnail generation error: {ex}")
            return config.DEFAULT_THUMB
