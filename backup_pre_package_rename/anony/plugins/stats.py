# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - Maintained by Aspirant (https://t.me/aspirant_u)


import os
import platform
import sys

try:
    import psutil
except ImportError:
    psutil = None
from pyrogram import __version__, filters, types
from pytgcalls import __version__ as pytgver

from anony import app, config, db, lang, userbot
from anony.plugins import all_modules


@app.on_message(filters.command(["stats"]) & filters.group & ~app.bl_users)
@lang.language()
async def _stats(_, m: types.Message):
    sent = await m.reply_photo(
        photo=config.PING_IMG,
        caption=m.lang["stats_fetching"],
    )

    pid = os.getpid()
    _utext = m.lang["stats_user"].format(
        app.name,
        len(userbot.clients),
        config.AUTO_LEAVE,
        len(db.blacklisted),
        len(app.bl_users),
        len(app.sudoers),
        len(await db.get_chats()),
        len(await db.get_users()),
    )
    if m.from_user.id in app.sudoers:
        process = psutil.Process(pid)
        storage = psutil.disk_usage("/")
        _utext += m.lang["stats_sudo"].format(
            len(all_modules),
            platform.system(),
            f"{process.memory_info().rss / 1024**2:.2f}",
            round(psutil.virtual_memory().total / (1024.0**3)),
            process.cpu_percent(interval=1.0),
            psutil.cpu_count(),
            f"{storage.used / (1024.0**3):.2f}",
            f"{storage.total / (1024.0**3):.2f}",
            sys.version.split()[0],
            __version__,
            pytgver,
        )
    await sent.edit_caption(_utext)


@app.on_message(filters.command(["apistats", "apihealth"]) & app.sudoers)
@lang.language()
async def _api_stats(_, m: types.Message):
    from anony.core.api_manager import api_manager
    dashboard = await api_manager.get_health_dashboard()

    circuits = "\n".join(
        f"  • <b>{c['name']}</b>: <code>{c['state']}</code> (Failures: {c['failure_count']}, Success: {c['success_count']})"
        for c in dashboard["circuits"]
    )
    providers = "\n".join(
        f"  • <b>{p['name']}</b> (P{p['priority']}): {p['success_rate_percent']}% success | {p['avg_latency_ms']}ms"
        for p in dashboard["providers"]
    )
    cache = dashboard["cache"]
    limiter = dashboard["rate_limiter"]

    text = (
        "👑 <b>VIRUS MUSIC — API Reliability Dashboard</b>\n\n"
        f"📊 <b>System Status:</b> <code>{dashboard['status']}</code>\n\n"
        f"🔌 <b>Circuit Breakers:</b>\n{circuits}\n\n"
        f"🌐 <b>Providers:</b>\n{providers}\n\n"
        f"💾 <b>Cache:</b> {cache['backend']} ({cache['memory_items']} items) | "
        f"Hits: {cache['hits']} | Misses: {cache['misses']} (<b>{cache['hit_ratio_percent']}%</b>)\n\n"
        f"⚡ <b>Rate Limiter:</b> {limiter['total_requests']} requests ({limiter['throttled_requests']} throttled)\n"
        f"⚙️ <b>Timeout:</b> {dashboard['config']['timeout']}s | <b>Retries:</b> {dashboard['config']['max_retries']}"
    )
    await m.reply_text(text)
