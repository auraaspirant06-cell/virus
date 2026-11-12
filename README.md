# 🦠 VIRUS MUSIC BOT — Next Generation Telegram Music Platform

<div align="center">

<h2>VIRUS MUSIC BOT</h2>
<b>Ultra Fast, High-Fidelity Telegram Voice Chat Music Streaming Bot</b><br>
<i>Engineered for Stability, High Concurrency, and Premium Sound Quality</i>

<br>

**Owner / Maintainer:** Aspirant ([@aspirant_u](https://t.me/aspirant_u))  
**Support Group:** [Join Support](https://t.me/+qqghU-fZtUw4ODQ9)  
**Updates Channel:** [Join Updates](https://t.me/kuchupuchuupdates)  
**License:** [MIT License](LICENSE) (Originally forked from AnonXMusic by AnonymousX1025)

</div>

---

## 🚀 Key Features

- 🎧 **High Quality Audio Streaming**: Crystal-clear 48kHz audio powered by PyTgCalls & NTgCalls.
- ⚡ **Zero-Lag Voice Chat Playback**: Optimized queue and pre-fetch engine (downloads next track 30s before end).
- 🔀 **Queue Management**: Full queue controls (`/queue`, `/shuffle`, `/skip`, `/loop`, `/stop`, `/end`).
- 🔊 **Live Volume Control**: `/volume [1-200]` lets admins adjust playback volume on the fly.
- 🔍 **Fast Music Search & Details**: `/song [query]` retrieves metadata, channel details, and direct links.
- 🌐 **Multilingual Support**: Built-in localization across 13 languages (Hindi, English, Spanish, Russian, etc.).
- 🛡️ **Anti-Flood & Security**: FloodWait protection, blacklist management, and authorized user permissions.
- 👥 **Multi-Assistant Support**: Balances load across up to 3 Pyrogram userbot client sessions.
- 🐳 **Docker & Production Ready**: Pre-configured Dockerfile, Heroku stack, and environment presets.
- 🔄 **API Reliability Manager**: Circuit breaker, exponential backoff with jitter, and intelligent multi-tier caching.

---

## 📋 Available Commands

### 🎵 Music Commands
| Command | Description | Permission |
|---|---|---|
| `/play <query/link>` | Streams audio in the group voice chat | All / Admins (mode dependent) |
| `/vplay <query/link>` | Streams video + audio in voice chat | All / Admins (mode dependent) |
| `/pause` | Pauses the current stream | Admins / Auth Users |
| `/resume` | Resumes the paused stream | Admins / Auth Users |
| `/skip` or `/next` | Skips to the next track in queue | Admins / Auth Users |
| `/stop` or `/end` | Ends playback, clears queue and leaves call | Admins / Auth Users |
| `/shuffle` | Shuffles all upcoming queued songs | Admins / Auth Users |
| `/volume <1-200>` | Adjusts playback volume percentage | Admins / Auth Users |
| `/seek <seconds>` | Seeks forward in the current stream | Admins / Auth Users |
| `/seekback <seconds>` | Seeks backward in the current stream | Admins / Auth Users |
| `/loop <1-10/off>` | Loops the current track N times | Admins / Auth Users |
| `/queue` or `/playing` | Displays currently playing track and upcoming queue | All Members |
| `/song <query/link>` | Searches for song details and stream link | All Members |

### 🛠️ Admin & Settings Commands
| Command | Description | Permission |
|---|---|---|
| `/settings` or `/playmode` | Configure group playmode, language, and command deletion | Admins |
| `/auth <user>` | Authorizes a user to control playback without admin rights | Admins |
| `/unauth <user>` | Revokes playback authorization | Admins |
| `/reload` | Refreshes group administrator cache | Admins |
| `/lang` | Changes the bot display language for the chat | Admins |

### 👑 Sudo & Owner Commands
| Command | Description | Permission |
|---|---|---|
| `/stats` | View bot system statistics, memory, CPU & active calls | Sudo Users |
| `/ac` or `/activevc` | Lists active voice chat streams across groups | Sudo Users |
| `/broadcast <reply>` | Broadcasts message to all chats / users | Sudo Users |
| `/addsudo <user>` | Promotes user to bot sudo | Owner Only |
| `/delsudo <user>` | Demotes user from bot sudo | Owner Only |
| `/restart` | Safely restarts the bot and clears temporary cache | Sudo Users |
| `/logs` | Exports bot operational logs | Sudo Users |

---

## ⚙️ Configuration (.env)

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Description | Required |
|---|---|---|
| `API_ID` | Telegram API ID from my.telegram.org | Yes |
| `API_HASH` | Telegram API Hash from my.telegram.org | Yes |
| `BOT_TOKEN` | Bot token from @BotFather | Yes |
| `OWNER_ID` | Telegram User ID of bot owner | Yes |
| `LOGGER_ID` | Telegram group ID for startup logs | Yes |
| `MONGO_URL` | MongoDB Atlas connection string | Yes |
| `SESSION` | Pyrogram String Session for assistant | Yes |
| `SUPPORT_CHANNEL` | Telegram channel URL for updates | Optional |
| `SUPPORT_CHAT` | Telegram group URL for support | Optional |

---

## 🛠️ Quick Installation

### Method 1: Using Bash Script (Ubuntu / Debian)
```bash
bash setup
```

### Method 2: Manual Setup with UV
```bash
# 1. Install uv
curl -Ls https://astral.sh/uv/install.sh | sh

# 2. Sync dependencies
uv sync --frozen

# 3. Start bot
bash start
```

### Method 3: Docker
```bash
docker build -t virusmusicbot .
docker run --env-file .env virusmusicbot
```

---

## ⚖️ License & Attribution

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md) files for details.

- **Original Base:** AnonXMusic © 2022–present AnonymousX1025
- **VIRUS MUSIC BOT Edition:** Customized, enhanced, and maintained by **Aspirant**.
