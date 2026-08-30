import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    filters,
)
from instagrapi import Client

# ---------- Config (set these as environment variables, not in code) ----------
TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
IG_USERNAME = os.environ["IG_USERNAME"]
IG_PASSWORD = os.environ["IG_PASSWORD"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

VIDEO, CAPTION, THUMBNAIL = range(3)

SESSION_FILE = "ig_session.json"

# ---------- Instagram client with persistent session ----------
cl = Client()

def ig_login():
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(IG_USERNAME, IG_PASSWORD)
            cl.get_timeline_feed()  # verify session still valid
            logger.info("Logged into Instagram using saved session.")
            return
        except Exception as e:
            logger.warning(f"Saved session invalid, logging in fresh: {e}")

    cl.login(IG_USERNAME, IG_PASSWORD)
    cl.dump_settings(SESSION_FILE)
    logger.info("Logged into Instagram fresh and saved session.")


# ---------- Telegram handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me the reel video you want to post (as a video file, not a document)."
    )
    return VIDEO


async def get_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    if not video:
        await update.message.reply_text("That doesn't look like a video. Please send a video file.")
        return VIDEO

    file = await video.get_file()
    path = f"downloads/{update.effective_user.id}_reel.mp4"
    os.makedirs("downloads", exist_ok=True)
    await file.download_to_drive(path)

    context.user_data["video"] = path
    await update.message.reply_text("Got the video. Now send the caption text.")
    return CAPTION


async def get_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["caption"] = update.message.text
    await update.message.reply_text(
        "Now send a thumbnail image, or type /skip to auto-generate one from the video."
    )
    return THUMBNAIL


async def get_thumbnail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"downloads/{update.effective_user.id}_thumb.jpg"
    await file.download_to_drive(path)
    return await do_upload(update, context, path)


async def skip_thumbnail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await do_upload(update, context, None)


async def do_upload(update: Update, context: ContextTypes.DEFAULT_TYPE, thumb_path):
    video_path = context.user_data["video"]
    caption = context.user_data["caption"]

    await update.message.reply_text("Uploading to Instagram, please wait...")

    try:
        if thumb_path:
            cl.clip_upload(video_path, caption, thumbnail=thumb_path)
        else:
            cl.clip_upload(video_path, caption)
        await update.message.reply_text("✅ Reel posted successfully!")
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        await update.message.reply_text(f"❌ Upload failed: {e}")
    finally:
        # cleanup local files
        for p in [video_path, thumb_path]:
            if p and os.path.exists(p):
                os.remove(p)
        context.user_data.clear()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


def main():
    ig_login()

    app = ApplicationBuilder().token(TG_BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("post", start)],
        states={
            VIDEO: [MessageHandler(filters.VIDEO, get_video)],
            CAPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_caption)],
            THUMBNAIL: [
                MessageHandler(filters.PHOTO, get_thumbnail),
                CommandHandler("skip", skip_thumbnail),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    logger.info("Bot started. Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
