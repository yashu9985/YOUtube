import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from pytube import YouTube
from moviepy.editor import VideoFileClip

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = "8032740300:AAGhHzbHcY6aCi3hAKiqz7lgr3b34Iu5CGc"

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a YouTube link to download the video or audio.")

# Handle YouTube link
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("Please send a valid YouTube link.")
        return

    keyboard = [
        [InlineKeyboardButton("MP3", callback_data=f"mp3_{url}")],
        [InlineKeyboardButton("MP4", callback_data=f"mp4_{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose format:", reply_markup=reply_markup)

# Handle button callbacks
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    format_type, url = data.split("_", 1)

    try:
        yt = YouTube(url)
        if format_type == "mp3":
            await query.edit_message_text("Downloading audio...")
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_file = audio_stream.download(output_path="downloads", filename="audio")
            mp3_file = audio_file.replace(".mp4", ".mp3")
            os.rename(audio_file, mp3_file)
            await query.edit_message_text("Uploading audio...")
            await context.bot.send_audio(chat_id=query.message.chat_id, audio=open(mp3_file, "rb"))
            os.remove(mp3_file)
        elif format_type == "mp4":
            await query.edit_message_text("Downloading video...")
            video_stream = yt.streams.get_highest_resolution()
            video_file = video_stream.download(output_path="downloads")
            await query.edit_message_text("Uploading video...")
            await context.bot.send_video(chat_id=query.message.chat_id, video=open(video_file, "rb"))
            os.remove(video_file)
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.edit_message_text("Something went wrong. Please try again.")

# Main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    # Create downloads directory if it doesn't exist
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    main()
