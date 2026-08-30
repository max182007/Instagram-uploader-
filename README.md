# Instagram Reel Auto-Upload Telegram Bot

Send a video + caption + thumbnail to your Telegram bot, and it auto-posts it as an Instagram Reel.

⚠️ **Note:** This uses `instagrapi`, an unofficial library that mimics the Instagram app.
It's not Meta's official API, so there's a small risk of your IG account being flagged for
automated activity. Use a secondary/test account first if you're unsure.

---

## How it works

1. You send `/post` to your bot
2. Bot asks for the video → send it
3. Bot asks for a caption → send text
4. Bot asks for a thumbnail → send an image, or `/skip`
5. Bot uploads the Reel to Instagram automatically

---

## Setup — entirely from your phone

### 1. Create your Telegram bot
- Open Telegram, message **@BotFather**
- Send `/newbot`, follow the prompts
- Copy the token it gives you (looks like `123456:ABC-...`)

### 2. Put this code on GitHub
- Open **github.com** in your phone browser, log in (or create a free account)
- Tap **+** → **New repository** → name it e.g. `insta-reel-bot` → Create
- Tap **Add file → Upload files**
- Upload every file from this project (`bot.py`, `requirements.txt`, `Procfile`,
  `.gitignore`, `.env.example`, `README.md`)
- Commit the changes

⚠️ Never upload a real `.env` file with your actual password — only `.env.example`.
Real secrets go into Railway's dashboard (next step), not into GitHub.

### 3. Deploy on Railway (keeps it running 24/7)
- Go to **railway.app** in your phone browser → sign in with GitHub
- **New Project → Deploy from GitHub repo** → select `insta-reel-bot`
- Once it's created, go to your service → **Variables** tab, add:
  - `TG_BOT_TOKEN` = your BotFather token
  - `IG_USERNAME` = your Instagram username
  - `IG_PASSWORD` = your Instagram password
- Go to **Settings** → under **Deploy**, make sure the start command uses the
  `Procfile` worker (`python bot.py`) — Railway auto-detects this
- Deploy. Railway will install `requirements.txt` and start the bot automatically.

From now on:
- Any time you edit code on GitHub, Railway **auto-redeploys** — no manual steps
- The bot keeps running continuously, even with your phone off, since it's in the cloud
- Open Telegram anytime and send `/post` to your bot to upload a reel

### 4. First login note
Instagram may challenge a brand-new automated login (email/SMS code) the very first time.
If `instagrapi` throws a challenge error on first deploy, check Railway's **Logs** tab —
it'll tell you what verification step Instagram wants. After the first successful login,
the bot saves a session file so it won't need to log in again each run.

---

## Files in this project

| File | Purpose |
|---|---|
| `bot.py` | Main bot logic |
| `requirements.txt` | Python dependencies |
| `Procfile` | Tells Railway how to run the bot |
| `.env.example` | Template showing which secrets are needed |
| `.gitignore` | Keeps secrets and temp files out of GitHub |
