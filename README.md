import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor

# Replace with your token
API_TOKEN = '8157929380:AAEPKj5uBvzPRBQDviPvnZ_Js4f3wdUCM-A'

# Logging setup
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ------------------- MAIN MENU -------------------
def main_menu():
    buttons = [
        [InlineKeyboardButton("📂 PDF Tools", callback_data="pdf_tools")],
        [InlineKeyboardButton("🔲 QR Generator", callback_data="qr_generator")],
        [InlineKeyboardButton("📹 YouTube Download", callback_data="youtube_dl")],
        [InlineKeyboardButton("💳 Pay via UPI", callback_data="upi_payment")],
        [InlineKeyboardButton("📞 Contact Us", callback_data="contact")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ------------------- START / HELP -------------------
@dp.message_handler(commands=['start', 'help'])
async def start_handler(message: types.Message):
    await message.answer(
        "🤖 *Telegram Bot Directory by Sachin Rawat*\n\n"
        "Choose a category below to explore useful bots:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ------------------- PDF TOOLS -------------------
@dp.callback_query_handler(lambda c: c.data == 'pdf_tools')
async def pdf_tools_handler(callback_query: types.CallbackQuery):
    text = (
        "📂 *PDF Tools:*\n\n"
        "1. [@mrpadaibot](https://t.me/mrpadaibot) – PDF Tool\n"
        "2. [@MSStudy_bot](https://t.me/MSStudy_bot) – PDF Tools by SR"
    )
    await bot.send_message(callback_query.from_user.id, text, parse_mode="Markdown")
    await bot.answer_callback_query(callback_query.id)

# ------------------- QR GENERATOR -------------------
@dp.callback_query_handler(lambda c: c.data == 'qr_generator')
async def qr_generator_handler(callback_query: types.CallbackQuery):
    text = (
        "🔲 *QR Generator:*\n\n"
        "1. [@SRawarbot](https://t.me/SRawarbot) – QR Code Generator"
    )
    await bot.send_message(callback_query.from_user.id, text, parse_mode="Markdown")
    await bot.answer_callback_query(callback_query.id)

# ------------------- YOUTUBE DOWNLOAD -------------------
@dp.callback_query_handler(lambda c: c.data == 'youtube_dl')
async def youtube_dl_handler(callback_query: types.CallbackQuery):
    text = (
        "📹 *YouTube Download Bots:*\n\n"
        "1. [@srvideoytbot](https://t.me/srvideoytbot) – YT Saver\n"
        "2. [@YTSABERBot](https://t.me/YTSABERBot) – YT Downloader"
    )
    await bot.send_message(callback_query.from_user.id, text, parse_mode="Markdown")
    await bot.answer_callback_query(callback_query.id)

# ------------------- CONTACT -------------------
@dp.callback_query_handler(lambda c: c.data == 'contact')
async def contact_handler(callback_query: types.CallbackQuery):
    text = (
        "📞 *Contact Us:*\n\n"
        "📸 Instagram: [@sachinrawt_](https://www.instagram.com/sachinrawt_/?__pwa=1)\n"
        "✉️ Email: thorbeast946@gmail.com"
    )
    await bot.send_message(callback_query.from_user.id, text, parse_mode="Markdown")
    await bot.answer_callback_query(callback_query.id)

# ------------------- UPI PAYMENT -------------------
@dp.callback_query_handler(lambda c: c.data == 'upi_payment')
async def upi_payment_handler(callback_query: types.CallbackQuery):
    upi_text = (
        "💳 *Support via UPI Payment*\n\n"
        "📥 UPI ID: `6264926275@ybl`\n"
        "📸 Scan the QR below or use UPI ID to pay.\n\n"
        "*After payment, submit proof by clicking the button below.*"
    )
    await bot.send_message(callback_query.from_user.id, upi_text, parse_mode="Markdown")

    # Send QR code if available
    try:
        with open("upi_qr.png", "rb") as photo:
            await bot.send_photo(callback_query.from_user.id, photo)
    except FileNotFoundError:
        await bot.send_message(callback_query.from_user.id, "⚠️ QR image not found. Please contact admin.")

    # Send proof button
    proof_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("📤 Send Payment Proof", url="https://t.me/sachinrawt_")
    )
    await bot.send_message(callback_query.from_user.id, "⬇️ Tap below to send payment proof:", reply_markup=proof_button)
    await bot.answer_callback_query(callback_query.id)

# ------------------- RUN BOT -------------------
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
