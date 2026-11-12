# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - Maintained by Aspirant (https://t.me/aspirant_u)

from pyrogram import filters, types

from anony import app, config, lang, yt
from anony.helpers import buttons


@app.on_message(filters.command(["song", "music"]) & ~app.bl_users)
@lang.language()
async def _song(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(
            m.lang.get(
                "song_usage",
                "🎵 <b>Usage:</b> <code>/song [song name or YouTube link]</code>\n"
                "<b>Example:</b> <code>/song Believer</code>"
            )
        )

    query = " ".join(m.command[1:])
    sent = await m.reply_text(m.lang["play_searching"])

    track = await yt.search(query, sent.id, video=False)
    if not track:
        return await sent.edit_text(
            m.lang["play_not_found"].format(config.SUPPORT_CHAT)
        )

    caption = (
        f"👑 <b>VIRUS MUSIC — Song Information</b>\n\n"
        f"📌 <b>Title:</b> <a href='{track.url}'>{track.title}</a>\n"
        f"👤 <b>Artist/Channel:</b> {track.channel_name or 'N/A'}\n"
        f"⏱ <b>Duration:</b> {track.duration or 'N/A'}\n"
        f"👁 <b>Views:</b> {track.view_count or 'N/A'}\n\n"
        f"🎧 <b>Play in VC:</b> <code>/play {track.url}</code>\n"
        f"✨ <i>Powered by VIRUS MUSIC</i>"
    )

    ikm = types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton(text="▶️ Stream On YouTube", url=track.url),
                types.InlineKeyboardButton(text="💬 Support", url=config.SUPPORT_CHAT),
            ]
        ]
    )

    if track.thumbnail:
        try:
            await sent.edit_media(
                media=types.InputMediaPhoto(
                    media=track.thumbnail,
                    caption=caption,
                ),
                reply_markup=ikm,
            )
            return
        except Exception:
            pass

    await sent.edit_text(caption, reply_markup=ikm)
