import logging
import asyncio
import os
import html
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yt_dlp import YoutubeDL

# Replace this with your bot token
BOT_TOKEN = "8176958632:AAFmYZauRe5OfYTqcq7kFrV-GUjvt9bjnDY"

# Bot setup
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# Command handler
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("🎬 Send me a YouTube video link to download the video file only.")

# Handle YouTube link
@dp.message(F.text.startswith("http"))
async def handle_youtube_link(message: Message):
    url = message.text.strip()
    msg = await message.reply("🔄 Downloading video... Please wait.")

    try:
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        ydl_opts = {
            'format': 'mp4',
            'outtmpl': 'downloads/video.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video_file = None
        for ext in ['mp4', 'mkv', 'webm']:
            path = f'downloads/video.{ext}'
            if os.path.exists(path):
                video_file = FSInputFile(path)
                break

        if video_file is None:
            raise Exception("Downloaded video file not found.")

        await bot.send_video(chat_id=message.chat.id, video=video_file, caption="✅ Here is your downloaded video.")
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Failed to download video.\n\n<code>{html.escape(str(e))}</code>")

    finally:
        # Clean up
        for file in os.listdir("downloads"):
            os.remove(os.path.join("downloads", file))

# Run bot
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
