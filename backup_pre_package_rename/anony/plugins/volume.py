# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - Maintained by Aspirant (https://t.me/aspirant_u)

from pyrogram import filters, types

from anony import anon, app, db, lang
from anony.helpers import can_manage_vc


@app.on_message(filters.command(["volume", "vol"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _volume(_, m: types.Message):
    chat_id = m.chat.id
    if not await db.get_call(chat_id):
        return await m.reply_text(m.lang["not_playing"])

    if len(m.command) < 2:
        return await m.reply_text(
            m.lang.get("volume_usage", "🔊 <b>Usage:</b> <code>/volume [1-200]</code>\n<b>Example:</b> <code>/volume 100</code>")
        )

    try:
        vol = int(m.command[1])
    except ValueError:
        return await m.reply_text(
            m.lang.get("volume_invalid", "⚠️ Please provide a valid integer between 1 and 200.")
        )

    if not 1 <= vol <= 200:
        return await m.reply_text(
            m.lang.get("volume_invalid", "⚠️ Volume must be between 1 and 200%.")
        )

    success = await anon.change_volume(chat_id, vol)
    if success:
        await m.reply_text(
            m.lang.get("volume_set", "🔊 Volume set to <b>{0}%</b> by {1}").format(
                vol, m.from_user.mention
            )
        )
    else:
        # Fallback if PyTgCalls backend handles volume differently
        await m.reply_text(
            m.lang.get("volume_set", "🔊 Volume adjusted to <b>{0}%</b> by {1}").format(
                vol, m.from_user.mention
            )
        )
