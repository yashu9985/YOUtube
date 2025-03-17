import os
import asyncio
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Replace with your BotFather token
BOT_TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Start Command
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    welcome_text = "🎥 **Welcome to YT Video Downloader Bot!**\n\n" \
                   "📥 Send me a **YouTube link**, and I will provide you with download options!"
    await message.reply(welcome_text)

# Process YouTube Link
@dp.message_handler(lambda message: message.text.startswith("http"))
async def process_youtube_link(message: types.Message):
    url = message.text
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Add format selection buttons
    keyboard.add(
        InlineKeyboardButton("📺 MP4 (720p)", callback_data=f"mp4_720p|{url}"),
        InlineKeyboardButton("📺 MP4 (360p)", callback_data=f"mp4_360p|{url}"),
        InlineKeyboardButton("🎵 MP3 (Audio)", callback_data=f"mp3|{url}")
    )
    
    await message.reply("🔽 **Select download format:**", reply_markup=keyboard)

# Callback Query Handler for Download
@dp.callback_query_handler(lambda call: call.data.startswith("mp4") or call.data.startswith("mp3"))
async def download_video(call: types.CallbackQuery):
    format_type, url = call.data.split("|")
    
    await call.message.edit_text("⏳ **Downloading... Please wait!**")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True
    }
    
    # Change format options based on selection
    if format_type == "mp4_720p":
        ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
    elif format_type == "mp4_360p":
        ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best'
    elif format_type == "mp3":
        ydl_opts['format'] = 'bestaudio'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Find the downloaded file
        for file in os.listdir():
            if file.startswith("downloaded_video"):
                file_path = file
                break

        # Send the downloaded file
        with open(file_path, "rb") as video_file:
            if format_type == "mp3":
                await call.message.answer_document(video_file, caption="🎵 Here is your MP3 file!")
            else:
                await call.message.answer_video(video_file, caption="🎬 Here is your video!")
        
        # Clean up
        os.remove(file_path)
    except Exception as e:
        await call.message.answer(f"⚠️ **Error:** {str(e)}")
    
    await call.message.edit_text("✅ **Download completed!**")

# Run the bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
