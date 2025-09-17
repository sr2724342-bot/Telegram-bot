import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    PicklePersistence
)
import yt_dlp as youtube_dl

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = "7331909026:AAGTVa_11W3sZvxDp4oIlOOaoe83nHUkxMw"  # Replace with your bot token
MAX_FILE_SIZE = 50  # MB (Telegram's limit for bots)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message."""
    await update.message.reply_text(
        "🎵 YouTube Audio Downloader Bot\n\n"
        "Send me any YouTube link and I'll extract the audio for you!\n\n"
        f"Max file size: {MAX_FILE_SIZE}MB (about 30 minutes of audio)\n"
        "For best results, use videos under 15 minutes."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    await update.message.reply_text(
        "How to use this bot:\n\n"
        "1. Send any YouTube URL (video or playlist)\n"
        "2. Wait while I process it\n"
        "3. Receive the audio file\n\n"
        "Commands:\n"
        "/start - Show welcome message\n"
        "/help - Show this help message"
    )

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download and send YouTube audio."""
    url = update.message.text.strip()
    
    # Validate URL
    if not any(domain in url for domain in ['youtube.com', 'youtu.be']):
        await update.message.reply_text("⚠️ Please send a valid YouTube URL.")
        return
    
    try:
        # Create downloads directory if needed
        os.makedirs('downloads', exist_ok=True)
        
        # Send initial message
        msg = await update.message.reply_text("⏳ Starting download...")
        
        # Configure download options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,  # Skip playlists by default
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Get video info first to check duration
            info = ydl.extract_info(url, download=False)
            duration = info.get('duration', 0)
            
            # Warn about long videos
            if duration > 1800:  # 30 minutes
                await msg.edit_text(
                    "⚠️ This video is quite long (>30 min).\n"
                    "The resulting file might be too large for Telegram.\n"
                    "Still want to proceed? (yes/no)"
                )
                context.user_data['pending_url'] = url
                return
            
            # Start download
            await msg.edit_text("⏳ Downloading audio...")
            info = ydl.extract_info(url, download=True)
            audio_filename = f"downloads/{info['id']}.mp3"
            
            # Verify download
            if not os.path.exists(audio_filename):
                raise Exception("Downloaded file not found")
            
            # Check file size
            file_size = os.path.getsize(audio_filename) / (1024 * 1024)  # MB
            if file_size > MAX_FILE_SIZE:
                await msg.edit_text(f"❌ File too large (max {MAX_FILE_SIZE}MB). Try a shorter video.")
                os.remove(audio_filename)
                return
            
            # Upload to Telegram
            await msg.edit_text("⬆️ Uploading to Telegram...")
            try:
                with open(audio_filename, 'rb') as audio_file:
                    await context.bot.send_audio(
                        chat_id=update.effective_chat.id,
                        audio=audio_file,
                        caption=f"🎧 {info.get('title', 'Audio')}",
                        read_timeout=60,
                        write_timeout=60
                    )
                await msg.delete()  # Remove progress message
            except Exception as upload_error:
                await msg.edit_text(f"❌ Upload failed: {str(upload_error)}")
                logger.error(f"Upload error: {upload_error}")
            
            # Clean up
            try:
                os.remove(audio_filename)
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        error_msg = "❌ An error occurred. Please try again later."
        try:
            await msg.edit_text(error_msg)
        except:
            await update.message.reply_text(error_msg)

def main():
    """Start the bot."""
    # Configure persistence to store user data
    persistence = PicklePersistence(filepath='bot_data.pickle')
    
    # Create application with optimized timeouts
    application = Application.builder() \
        .token(TOKEN) \
        .read_timeout(60) \
        .write_timeout(60) \
        .pool_timeout(60) \
        .get_updates_read_timeout(60) \
        .persistence(persistence) \
        .build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Handle text messages that aren't commands
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        download_audio
    ))

    # Run bot
    logger.info("Bot is running and ready to accept commands...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()