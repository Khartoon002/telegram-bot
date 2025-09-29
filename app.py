import os
from textwrap import dedent

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command

from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

# ===========================
# ENV VARS
# ===========================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # set in host dashboard
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")  # e.g. https://magnus-bot.onrender.com
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "magnus-secret")  # any random string
WEBHOOK_PATH = f"/tg/{WEBHOOK_SECRET}"  # final webhook URL = PUBLIC_BASE_URL + WEBHOOK_PATH
PORT = int(os.getenv("PORT", "8000"))   # Render sets PORT automatically

if not BOT_TOKEN or not PUBLIC_BASE_URL:
    raise RuntimeError("BOT_TOKEN and PUBLIC_BASE_URL must be set as environment variables.")

# ===========================
# BOT + DISPATCHER
# ===========================
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()

# ===========================
# CONTENT
# ===========================
IMAGES = {
    "what_is": "https://magnuswebsite.site/img/magnus_resell.jpg",
    "features": "https://magnuswebsite.site/img/magnus_wealth.jpg",
    "register": "https://magnuswebsite.site/img/magnus_register.jpg",
}

PAYMENT_DETAILS = {
    "NG": dedent("""\
        🇳🇬 *Nigeria — Bank Transfer*
        • Account Name: REPLACE_ME_ACCOUNT_NAME
        • Bank: REPLACE_ME_BANK
        • Account No: REPLACE_ME_ACCOUNT_NUMBER

        *Fees (One-time):*
        • Magnus Business: ₦28,500
        • Magnus Pro: ₦17,500
        • Magnus Lite: ₦11,500

        After payment, send proof here to activate your access.
    """),
    "GH": dedent("""\
        🇬🇭 *Ghana — Mobile Money*
        • Name: REPLACE_ME_MOMO_NAME
        • Network: REPLACE_ME_NETWORK
        • MoMo Number: REPLACE_ME_MOMO_NUMBER

        *Equivalent Fees:* confirm current rate
        • Business ≈ NGN 28,500
        • Pro ≈ NGN 17,500
        • Lite ≈ NGN 11,500

        Send proof of payment here to proceed.
    """),
    "KE": dedent("""\
        🇰🇪 *Kenya — M-Pesa*
        • Name: REPLACE_ME_MPESA_NAME
        • Till/PayBill: REPLACE_ME_MPESA_TILL
        • Number: REPLACE_ME_MPESA_NUMBER

        *Equivalent Fees:* confirm current rate
        • Business ≈ NGN 28,500
        • Pro ≈ NGN 17,500
        • Lite ≈ NGN 11,500

        Send proof of payment here to proceed.
    """),
    "ZA": dedent("""\
        🇿🇦 *South Africa — EFT*
        • Account Name: REPLACE_ME_ACCOUNT_NAME
        • Bank: REPLACE_ME_BANK
        • Account No: REPLACE_ME_ACCOUNT_NUMBER

        *Equivalent Fees:* confirm current rate
        • Business ≈ NGN 28,500
        • Pro ≈ NGN 17,500
        • Lite ≈ NGN 11,500

        Send proof of payment here to proceed.
    """),
    "INTL": dedent("""\
        🌍 *International — USD / Wise / PayPal*
        • Method: REPLACE_ME_METHOD (e.g., Wise/PayPal)
        • Handle/Email: REPLACE_ME_EMAIL_OR_HANDLE

        *Guide (edit to official USD pricing):*
        • Business: $35
        • Pro: $25
        • Lite: $18

        After payment, reply with your receipt to activate access.
    """),
}

HELP_LINK = "Reply here and we’ll assist you."  # or a URL

SECTION_TEXT = {
    "what_is": dedent("""\
        *MAGNUS — Your Shortcut to Digital Wealth*

        MAGNUS is a digital marketplace that helps you learn in-demand skills and access powerful digital products (trading tools, signals, analytics, courses).
        Use them for personal growth *or* resell for profit. With flexible entry plans, instant earning routes, and global job offers, MAGNUS makes it simple to *learn, earn, and grow*.
    """),
    "features": dedent("""\
        *What You Get in MAGNUS (Earning Features + Legitimacy)*

        • Trading Tools — stay ahead in the markets
        • Signals & Analytics — make smarter moves
        • Hot Courses — learn skills in minutes, not months
        • Resale Rights — earn while others are still learning

        *Entry Plans*
        • *MAGNUS BUSINESS* — ₦28,500
          Unlimited products • Full resale rights • Create & sell your own • Instant job opportunity after skill acquisition
          Commissions: Direct ₦17,100 | Indirect ₦1,300

        • *MAGNUS PRO* — ₦17,500
          Limited access • Low resale rights • Learn for growth
          Earn via PR entry data up to ₦985 every 2 minutes (when available)
          Commissions: Direct ₦11,500 | Indirect ₦650

        • *MAGNUS LITE* — ₦11,500
          1 product • No resale rights
          Earn via referrals + data entry jobs up to ₦985 every 2 minutes (when available)
          Commissions: Direct ₦7,500 | Indirect ₦350

        *Earnings Potential*
        • Profit ₦5,000+ per sale
        • Company handles ads & logistics
        • Free resale setup manual (1–72hrs sales cycle)
        • Multiple income streams: Skills + Resale + Commissions + Global Jobs

        *Jobs & Skills Advantage (Business tier)*
        • High-demand skills + employment
        • ₦5,000/hour global pay → 6 hrs/day = ₦30,000/day = ₦900,000/month

        *Why MAGNUS?*
        Affordable entry • In-demand products • Multiple ways to earn • Freedom to learn, use, or resell • We handle the hard part so you enjoy the results.
    """),
    "register": dedent("""\
        *How to Register (Simple Steps)*

        1) Choose your entry plan: *Business*, *Pro*, or *Lite*.
        2) Tap *Register Now*, pick your country, and pay to the displayed account.
        3) Send your receipt here in chat.
        4) Get activated and start using products, learning skills, and earning.

        *Tip:* Start now. The sooner you begin, the faster you unlock skills, resale rights, and job routes.
    """),
}

# ===========================
# Keyboards
# ===========================
def kb_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 What is MAGNUS", callback_data="sec:what_is")],
        [InlineKeyboardButton(text="💹 Earning Features + Legitimacy", callback_data="sec:features")],
        [InlineKeyboardButton(text="📝 How to Register", callback_data="sec:register")],
    ])

def kb_register() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Register Now", callback_data="register")],
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back:menu")],
    ])

def kb_countries() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇳🇬 Nigeria", callback_data="country:NG"),
            InlineKeyboardButton(text="🇬🇭 Ghana", callback_data="country:GH"),
        ],
        [
            InlineKeyboardButton(text="🇰🇪 Kenya", callback_data="country:KE"),
            InlineKeyboardButton(text="🇿🇦 South Africa", callback_data="country:ZA"),
        ],
        [InlineKeyboardButton(text="🌍 International (USD)", callback_data="country:INTL")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back:menu")],
    ])

def kb_back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back:menu")]
    ])

# ===========================
# Handlers
# ===========================
@dp.message(CommandStart())
async def on_start(message: types.Message):
    text = dedent(f"""\
        *Welcome to MAGNUS!*
        This bot will guide you through:
        • What MAGNUS is
        • Earning Features + Legitimacy
        • How to Register (with your country’s payment details)

        👉 Tap the Telegram *Start* button to begin, then choose an option below.
        Need help? {HELP_LINK}
    """)
    await message.answer(text, reply_markup=kb_main_menu())

@dp.message(Command("menu"))
async def on_menu(message: types.Message):
    await message.answer("Choose a section:", reply_markup=kb_main_menu())

async def show_section(chat_id: int, key: str):
    caption = SECTION_TEXT[key] + "\n\n" + "_Tap the button below to proceed._"
    photo_url = IMAGES.get(key, IMAGES["what_is"])
    await bot.send_photo(
        chat_id=chat_id,
        photo=photo_url,
        caption=caption,
        reply_markup=kb_register()
    )

@dp.callback_query(F.data.func(lambda d: d is not None and (
    d.startswith("sec:") or d == "register" or d.startswith("country:") or d.startswith("back:")
)))
async def on_cb(callback: CallbackQuery):
    data = callback.data or ""
    chat_id = callback.message.chat.id
    await callback.answer()

    if data.startswith("sec:"):
        key = data.split("sec:")[1]
        if key in SECTION_TEXT:
            await show_section(chat_id, key)
        else:
            await bot.send_message(chat_id, "Unknown section.", reply_markup=kb_main_menu())

    elif data == "register":
        await bot.send_message(chat_id, "Select your country to see payment details:", reply_markup=kb_countries())

    elif data.startswith("country:"):
        code = data.split("country:")[1]
        details = PAYMENT_DETAILS.get(code)
        if not details:
            await bot.send_message(chat_id, "Payment details not available yet. Please choose another country.", reply_markup=kb_countries())
            return
        await bot.send_message(chat_id, details, reply_markup=kb_back_menu())

    elif data.startswith("back:"):
        await bot.send_message(chat_id, "Back to menu. Choose a section:", reply_markup=kb_main_menu())

# ===========================
# Web server (aiohttp) + webhook
# ===========================
async def on_startup(app: web.Application):
    await bot.set_webhook(
        url=PUBLIC_BASE_URL + WEBHOOK_PATH,
        drop_pending_updates=True,
    )

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()

def build_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Route only the webhook path to aiogram
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=None).register(app, path=WEBHOOK_PATH)

    # Optional health check
    async def health(_):
        return web.Response(text="OK")
    app.router.add_get("/", health)

    return app

if __name__ == "__main__":
    web.run_app(build_app(), port=PORT)
