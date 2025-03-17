from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, CallbackQueryHandler, ContextTypes
)

TOKEN = "YOUR_BOT_TOKEN"

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a YouTube link!")

# Handle YouTube Links
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "youtube.com" in text or "youtu.be" in text:
        keyboard = [
            [InlineKeyboardButton("MP4", callback_data=f"mp4_{text}"),
             InlineKeyboardButton("MP3", callback_data=f"mp3_{text}")],
            [InlineKeyboardButton("Select Resolution", callback_data=f"res_{text}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose download option:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Please send a valid YouTube link.")

# Handle Button Clicks
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_", 1)

    if data[0] == "mp4":
        await query.message.reply_text(f"Downloading MP4: {data[1]}")
    elif data[0] == "mp3":
        await query.message.reply_text(f"Downloading MP3: {data[1]}")
    elif data[0] == "res":
        keyboard = [
            [InlineKeyboardButton("1080p", callback_data=f"1080p_{data[1]}"),
             InlineKeyboardButton("720p", callback_data=f"720p_{data[1]}")],
            [InlineKeyboardButton("480p", callback_data=f"480p_{data[1]}"),
             InlineKeyboardButton("360p", callback_data=f"360p_{data[1]}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Choose resolution:", reply_markup=reply_markup)

# Run the Bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_callback))

app.run_polling()
