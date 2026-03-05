import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, CommandHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN3")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a YouTube link.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("🎧 MP3", callback_data="mp3"),
            InlineKeyboardButton("🎬 MP4", callback_data="mp4")
        ]
    ]

    await update.message.reply_text(
        "Choose format:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")

    try:

        if query.data == "mp3":

            await query.edit_message_text("Downloading MP3...")

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "song.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            await query.message.reply_audio(audio=open("song.mp3", "rb"))

            os.remove("song.mp3")


        elif query.data == "mp4":

            await query.edit_message_text("Downloading MP4...")

            ydl_opts = {
                "format": "best[height<=720]",
                "outtmpl": "video.%(ext)s",
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

            await query.message.reply_video(video=open(file, "rb"))

            os.remove(file)

    except Exception as e:
        await query.message.reply_text("Error occurred. Try another video.")

app = ApplicationBuilder().token(TOKEN).read_timeout(600).write_timeout(600).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
