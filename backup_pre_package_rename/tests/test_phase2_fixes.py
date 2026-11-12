# Test Suite for VIRUS MUSIC BOT - Phase 2 Verification
# Tests Bug Fixes, New Commands, and Branding Integrity

import os
import sys
import json
import unittest
from unittest.mock import MagicMock

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SKIP_ENV_CHECK"] = "true"

# Safe mock for pyrogram and pytgcalls when testing in environments without compiled C bindings
if "pyrogram" not in sys.modules:
    pyro = MagicMock()
    class DummyClient:
        def __init__(self, *args, **kwargs):
            self.me = MagicMock()
            self.me.id = 12345
            self.me.first_name = "VIRUS MUSIC"
            self.me.username = "virusmusicbot"
            self.me.mention = "@virusmusicbot"
        def on_message(self, *args, **kwargs):
            return lambda f: f
        def on_callback_query(self, *args, **kwargs):
            return lambda f: f
    class DummyFilter:
        def __invert__(self): return self
        def __and__(self, o): return self
        def __or__(self, o): return self
    pyro.Client = DummyClient
    pyro.filters.user = lambda *a, **kw: DummyFilter()
    pyro.filters.command = lambda *a, **kw: DummyFilter()
    pyro.filters.group = DummyFilter()
    pyro.enums.ParseMode.HTML = "html"
    pyro.types.LinkPreviewOptions = lambda *a, **kw: None
    sys.modules["pyrogram"] = pyro
    sys.modules["pyrogram.types"] = pyro.types
    sys.modules["pyrogram.filters"] = pyro.filters
    sys.modules["pyrogram.enums"] = pyro.enums
    sys.modules["pyrogram.errors"] = pyro.errors

if "pymongo" not in sys.modules:
    pym = MagicMock()
    sys.modules["pymongo"] = pym

if "pytgcalls" not in sys.modules:
    pytg = MagicMock()
    sys.modules["pytgcalls"] = pytg
    sys.modules["pytgcalls.pytgcalls_session"] = MagicMock()

if "ntgcalls" not in sys.modules:
    sys.modules["ntgcalls"] = MagicMock()

if "py_yt" not in sys.modules:
    sys.modules["py_yt"] = MagicMock()


class TestVirusMusicBot(unittest.TestCase):

    def test_01_config_branding(self):
        """Verify VIRUS MUSIC branding in Config defaults."""
        from config import Config
        cfg = Config()
        self.assertEqual(cfg.BOT_NAME, "VIRUS MUSIC BOT")
        self.assertEqual(cfg.OWNER_NAME, "Aspirant")
        self.assertEqual(cfg.OWNER_TELEGRAM, "https://t.me/aspirant_u")
        self.assertEqual(cfg.SUPPORT_CHANNEL, "https://t.me/kuchupuchuupdates")
        self.assertEqual(cfg.SUPPORT_CHAT, "https://t.me/+qqghU-fZtUw4ODQ9")
        self.assertNotIn("fallenx", cfg.SUPPORT_CHANNEL)
        self.assertNotIn("DevilsHeavenMF", cfg.SUPPORT_CHAT)
        print(" [PASS] Test 1: Config Branding verified.")

    def test_02_queue_shuffle(self):
        """Verify /shuffle maintains current track and shuffles remaining."""
        from anony.helpers._queue import Queue
        from anony.helpers._dataclass import Track

        q = Queue()
        chat_id = 99999

        # Case 1: Empty or 1-2 tracks -> should return False
        self.assertFalse(q.shuffle(chat_id))

        t1 = Track(id="track1", title="Song 1")
        q.add(chat_id, t1)
        self.assertFalse(q.shuffle(chat_id))

        t2 = Track(id="track2", title="Song 2")
        q.add(chat_id, t2)
        self.assertFalse(q.shuffle(chat_id))

        # Case 2: 3+ tracks -> should shuffle remaining while keeping current
        for i in range(3, 10):
            q.add(chat_id, Track(id=f"track{i}", title=f"Song {i}"))

        initial_first = q.get_current(chat_id).id
        self.assertEqual(initial_first, "track1")

        result = q.shuffle(chat_id)
        self.assertTrue(result)
        self.assertEqual(q.get_current(chat_id).id, "track1", "First track must not change during shuffle!")
        self.assertEqual(len(q.get_queue(chat_id)), 9)
        print(" [PASS] Test 2: Queue Shuffle verified.")

    def test_03_bug1_play_next_none_safety(self):
        """Verify play_next handles empty queue without AttributeError."""
        from anony.helpers._queue import Queue
        q = Queue()
        chat_id = 12345
        media = q.get_next(chat_id)
        self.assertIsNone(media)
        # Verify calls.py play_next has the guard BEFORE media.message_id
        with open("anony/core/calls.py", "r", encoding="utf-8") as f:
            code = f.read()
        idx_get_next = code.find("media = queue.get_next(chat_id)")
        idx_stop = code.find("return await self.stop(chat_id)", idx_get_next)
        idx_msg_id = code.find("if media.message_id:", idx_get_next)
        self.assertTrue(idx_get_next < idx_stop < idx_msg_id, "if not media check must come BEFORE media.message_id access!")
        print(" [PASS] Test 3: Bug 1 (play_next None dereference fix) verified.")

    def test_04_bug2_queue_thumbnail_variable(self):
        """Verify queue.py uses local _thumb instead of global Thumbnail class instance."""
        with open("anony/plugins/queue.py", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("if _thumb:", content, "queue.py must check 'if _thumb:', not 'if thumb:'")
        self.assertNotIn("if thumb:\n        await _reply.edit_media", content)
        print(" [PASS] Test 4: Bug 2 (queue thumbnail boolean check) verified.")

    def test_05_bug3_hardcoded_chat_ids_removed(self):
        """Verify hardcoded developer IDs are removed from misc.py."""
        with open("anony/plugins/misc.py", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("-1001686672798", content)
        self.assertNotIn("-1001549206010", content)
        print(" [PASS] Test 5: Bug 3 (hardcoded group IDs) verified removed.")

    def test_06_bug4_forced_channel_join_removed(self):
        """Verify userbot does not auto-join developer channel."""
        with open("anony/core/userbot.py", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn('join_chat("fallenx")', content)
        print(" [PASS] Test 6: Bug 4 (forced channel auto-join) verified removed.")

    def test_07_bug5_uptime_formatting(self):
        """Verify ping.py format_uptime handles 0 hours, seconds, and days properly."""
        from anony.plugins.ping import format_uptime
        self.assertEqual(format_uptime(45), "45s")
        self.assertEqual(format_uptime(125), "2m 5s")
        self.assertEqual(format_uptime(3665), "1h 1m 5s")
        self.assertEqual(format_uptime(90065), "1d 1h 1m 5s")
        print(" [PASS] Test 7: Bug 5 (uptime formatting) verified.")

    def test_08_bug8_cmd_delete_safety(self):
        """Verify mongo.py set_cmd_delete does not raise ValueError on unlisted chat_id."""
        with open("anony/core/mongo.py", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("if chat_id in self.cmd_delete:", content)
        print(" [PASS] Test 8: Bug 8 (cmd_delete ValueError safety) verified.")

    def test_09_bug10_notified_user_tracking(self):
        """Verify blacklisted user notification records notified status."""
        with open("anony/plugins/start.py", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("db.notified.append(message.from_user.id)", content)
        print(" [PASS] Test 9: Bug 10 (db.notified tracking) verified.")

    def test_10_deno_fallback_in_dir_and_youtube(self):
        """Verify dir.py and youtube.py safely handle absence of Deno."""
        with open("anony/core/dir.py", "r", encoding="utf-8") as f:
            dir_content = f.read()
        self.assertNotIn('raise RuntimeError("Deno and FFmpeg', dir_content)

        with open("anony/core/youtube.py", "r", encoding="utf-8") as f:
            yt_content = f.read()
        self.assertIn('if shutil.which("deno"):', yt_content)
        print(" [PASS] Test 10: Deno graceful fallback verified.")

    def test_11_locales_valid_and_synchronized(self):
        """Verify all 13 locale files are valid JSON and have required new keys."""
        locale_dir = "anony/locales"
        required_keys = ["owner", "shuffle_done", "volume_set", "song_usage"]

        files = [f for f in os.listdir(locale_dir) if f.endswith(".json")]
        self.assertEqual(len(files), 13, "Expected 13 locale files.")

        for fname in files:
            fpath = os.path.join(locale_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k in required_keys:
                self.assertIn(k, data, f"Locale '{fname}' is missing key '{k}'")

        # Check en.json branding
        with open(os.path.join(locale_dir, "en.json"), "r", encoding="utf-8") as f:
            en = json.load(f)
        self.assertIn("VIRUS MUSIC", en["start_pm"])
        self.assertIn("Aspirant", en["start_pm"])

        # Check hi.json branding
        with open(os.path.join(locale_dir, "hi.json"), "r", encoding="utf-8") as f:
            hi = json.load(f)
        self.assertIn("VIRUS MUSIC", hi["start_pm"])
        self.assertIn("Aspirant", hi["start_pm"])
        print(" [PASS] Test 11: All 13 locales valid, key-synchronized, and branded.")

    def test_12_new_plugins_exist(self):
        """Verify new plugins shuffle.py, volume.py, song.py exist."""
        for plugin in ["shuffle.py", "volume.py", "song.py", "stop.py"]:
            path = os.path.join("anony", "plugins", plugin)
            self.assertTrue(os.path.exists(path), f"Plugin {plugin} must exist!")
        print(" [PASS] Test 12: New plugins verified present.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
