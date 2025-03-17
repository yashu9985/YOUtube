import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

# Replace this with your actual bot token from BotFather
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Function to start the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Send me a YouTube link, and I'll fetch the download options for you!")

# Function to handle YouTube links
def handle_message(update: Update, context: CallbackContext) -> None:
    url = update.message.text

    # Validate if it's a YouTube link
    if "youtube.com" in url or "youtu.be" in url:
        update.message.reply_text("Fetching video details...")

        # Extract available formats
        ydl_opts = {
            "quiet": True,
            "noprogress": True,
            "simulate": True,
            "format": "best",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                formats = info.get("formats", [])
                
                keyboard = []
                for fmt in formats:
                    fmt_id = fmt.get("format_id")
                    ext = fmt.get("ext")
                    res = fmt.get("height", "Unknown")
                    
                    if ext in ["mp4", "webm"] and res != "Unknown":
                        keyboard.append([InlineKeyboardButton(f"{res}p ({ext})", callback_data=f"video|{url}|{fmt_id}")])
                
                keyboard.append([InlineKeyboardButton("Audio (MP3)", callback_data=f"audio|{url}")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text("Choose your format:", reply_markup=reply_markup)
            
            except Exception as e:
                update.message.reply_text("Failed to fetch video details. Please try another link.")
    else:
        update.message.reply_text("Please send a valid YouTube link.")

# Function to handle button clicks
def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = query.data.split("|")
    option, url = data[0], data[1]

    if option == "video":
        fmt_id = data[2]
        file_path = download_video(url, fmt_id)
    elif option == "audio":
        file_path = download_audio(url)

    if file_path:
        query.message.reply_document(document=open(file_path, "rb"))
        os.remove(file_path)  # Delete after sending
    else:
        query.message.reply_text("Download failed. Try again.")

# Function to download video
def download_video(url, fmt_id):
    ydl_opts = {
        "format": fmt_id,
        "outtmpl": "downloads/video.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return "downloads/video.mp4"
        except Exception as e:
            return None

# Function to download audio
def download_audio(url):
    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": "downloads/audio.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return "downloads/audio.mp3"
        except Exception as e:
            return None

# Main function to run the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(button_callback))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
