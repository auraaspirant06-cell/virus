import os
import sys
import importlib
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath("."))
os.environ["SKIP_ENV_CHECK"] = "true"

for mod in [
    "pyrogram", "pyrogram.types", "pyrogram.filters", "pyrogram.enums", "pyrogram.errors",
    "pytgcalls", "pytgcalls.pytgcalls_session", "ntgcalls", "pymongo", "py_yt"
]:
    if mod not in sys.modules:
        m = MagicMock()
        m.__version__ = "2.0.106"
        class DummyFilter:
            def __invert__(self): return self
            def __and__(self, o): return self
            def __or__(self, o): return self
        class DummyClient:
            def __init__(self, *args, **kwargs):
                self.me = MagicMock()
                self.me.id = 12345
                self.me.first_name = "VIRUS MUSIC"
                self.me.username = "virusmusicbot"
                self.me.mention = "@virusmusicbot"
            def on_message(self, *a, **k): return lambda f: f
            def on_callback_query(self, *a, **k): return lambda f: f
            def on_edited_message(self, *a, **k): return lambda f: f
            def on_inline_query(self, *a, **k): return lambda f: f
            def on_chosen_inline_result(self, *a, **k): return lambda f: f
        m.Client = DummyClient
        m.filters.user = lambda *a, **kw: DummyFilter()
        m.filters.command = lambda *a, **kw: DummyFilter()
        m.filters.group = DummyFilter()
        m.filters.private = DummyFilter()
        m.enums.ParseMode.HTML = "html"
        m.types.LinkPreviewOptions = lambda *a, **kw: None
        sys.modules[mod] = m

plugins = [f[:-3] for f in os.listdir("anony/plugins") if f.endswith(".py") and not f.startswith("__")]
print(f"Discovered {len(plugins)} plugins to import:")

failed = []
for p in sorted(plugins):
    try:
        importlib.import_module(f"anony.plugins.{p}")
        print(f"  [OK] anony.plugins.{p}")
    except Exception as ex:
        print(f"  [FAIL] anony.plugins.{p}: {ex}")
        failed.append((p, ex))

if failed:
    print(f"\nFAILURE: {len(failed)} plugins failed to import!")
    sys.exit(1)
else:
    print(f"\nSUCCESS: All {len(plugins)} plugins imported cleanly with 0 errors!")
