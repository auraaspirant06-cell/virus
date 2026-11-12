# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - Maintained by Aspirant (https://t.me/aspirant_u)

from pyrogram import filters, types

from anony import app, db, lang, queue
from anony.helpers import can_manage_vc


@app.on_message(filters.command(["shuffle"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _shuffle(_, m: types.Message):
    chat_id = m.chat.id
    if not await db.get_call(chat_id):
        return await m.reply_text(m.lang["not_playing"])

    current_q = queue.get_queue(chat_id)
    if len(current_q) <= 2:
        return await m.reply_text(
            m.lang.get("shuffle_min", "⚠️ Need at least 2 tracks in queue to shuffle.")
        )

    shuffled = queue.shuffle(chat_id)
    if shuffled:
        new_q = queue.get_queue(chat_id)
        return await m.reply_text(
            m.lang.get("shuffle_done", "🔀 Queue shuffled successfully ({0} tracks) by {1}.").format(
                len(new_q) - 1, m.from_user.mention
            )
        )
    else:
        return await m.reply_text(
            m.lang.get("shuffle_err", "❌ Failed to shuffle queue.")
        )
