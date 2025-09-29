import os
import asyncio
from textwrap import dedent
from datetime import timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode, ChatAction
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command

from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

# ===========================
# ENV VARS (Render/Railway)
# ===========================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # set in host dashboard
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")  # e.g. https://magnus-bot.onrender.com
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "magnus-secret")
WEBHOOK_PATH = f"/tg/{WEBHOOK_SECRET}"
PORT = int(os.getenv("PORT", "8000"))

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
# Content: IMAGES / ANIMS
# ===========================
IMAGES = {
    "what_is": "https://magnuswebsite.site/img/magnus_resell.jpg",
    "features": "https://magnuswebsite.site/img/magnus_wealth.jpg",
    "register": "https://magnuswebsite.site/img/magnus_register.jpg",
}
ANIMS = {
    # optional celebratory animation (replace with your own hosted .gif/.mp4 if you like)
    "celebrate": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjM3YzA5MGQ2M2ZkMDk0M2I5NTRmOWQxM2EwYWFkZjFjYTcxY2Y5MiZjdD1n/26gslU06gXJ5a9aYs/giphy.gif"
}

# ===========================
# Features & Earnings (new)
# ===========================
MAGNUS_UNIQUE = dedent("""\
▫ *Magnus offers thousands of digital products* you can access anytime.  
▫ Some products are usable *immediately*, others need deeper study—*you choose*.  
▫ Some skills take *minutes*, others *months*—*your pace, your path*.  
▫ Learn *multiple* skills to increase your income.  
▫ The *more skills* you learn and the *more time* you work, the *more you earn*.  
▫ Become a *digital retailer* and earn *millions monthly* (no referrals required).  
▫ Withdraw via *PayPal*, *USDT*, or *local bank account*.  
▫ *100% refundable* entry fee—can be recovered within *5 days* of joining.
""")

MAGNUS_EMP_EARNINGS = dedent("""\
*Earnings for Magnus Employees*

① Gain Valuable Skills  
② Get Trained  
③ Get Employed  
④ Start Making Money

• Every *30 minutes* of work: *₦2,499*  
• 1 hour  = *₦4,999.8*  
• 2 hours = *₦9,999.6*  
• 3 hours = *₦14,999.4*

⭐ Work *6 hours daily* → *₦29,998.8/day*, *₦209,991.6/week*, *₦899,964/30 days*

*Pro tip:* Learn *two skills* and multitask to *double your income*:  
• 1 day:  ₦59,997.6  
• 2 days: ₦119,995.2  
• 3 days: ₦179,992.8  
• 4 days: ₦239,990.4

⚡ You can also become a *digital retailer* and earn *millions monthly*—*no referrals needed*.
""")

# ===========================
# Section Texts
# ===========================
SECTION_TEXT = {
    "what_is": dedent("""\
        *MAGNUS — Your Shortcut to Digital Freedom*

        MAGNUS is a digital marketplace for *in-demand skills* and *powerful products*
        (trading tools, signals, analytics, courses). Use them for *personal growth* or
        *resell for profit*. With flexible plans, instant earning routes, and global job
        offers, MAGNUS helps you *learn, earn, and grow*.
        
        {}
    """).format(MAGNUS_UNIQUE),

    "features": dedent("""\
        *What You Get (Earning Features + Legitimacy)*

        • Trading Tools — stay ahead in the markets  
        • Signals & Analytics — make smarter moves  
        • Hot Courses — learn skills in minutes, not months  
        • Resale Rights — earn while others are still learning

        *Entry Plans*
        • *MAGNUS BUSINESS* — ₦28,500  
          Unlimited products • Full resale rights • Create & sell your own • Instant job after skills  
          Commissions: Direct ₦17,100 | Indirect ₦1,300

        • *MAGNUS PRO* — ₦17,500  
          Limited access • Low resale rights • Learn for growth  
          Earn via PR entry data up to ₦985 every 2 minutes (when available)  
          Commissions: Direct ₦11,500 | Indirect ₦650

        • *MAGNUS LITE* — ₦11,500  
          1 product • No resale rights  
          Earn via referrals + data entry up to ₦985 every 2 minutes (when available)  
          Commissions: Direct ₦7,500 | Indirect ₦350

        *Earnings Potential*
        • Profit ₦5,000+ per sale  
        • Company handles ads & logistics  
        • Free resale setup manual (1–72hrs sales cycle)  
        • Multiple streams: Skills + Resale + Commissions + Global Jobs

        {}
    """).format(MAGNUS_EMP_EARNINGS),

    "register": dedent("""\
        *How to Register (Simple Steps)*

        1) Choose your entry plan: *Business*, *Pro*, or *Lite*.  
        2) Tap *Register Now*, pick your country, and pay to the displayed account.  
        3) Send your receipt here in chat.  
        4) Get activated and start learning, using products, and earning.

        *Tip:* Start now. The sooner you begin, the faster you unlock skills, resale rights, and job routes.
    """),
}

# ===========================
# Payments (NG updated)
# ===========================
PAYMENT_DETAILS = {
    "NG": dedent("""\
        🇳🇬 *Nigeria — Bank Transfer (No OPay)*

        • *Bank:* Moniepoint MFB  
        • *Account Number:* `6054080105`  
        • *Account Name:* *SPINO CLINTON UCHENNA*

        🔔 *OPay payments are NOT allowed.* Please use *bank transfer* only.

        *One-time Fees:*  
        • Magnus Business: ₦28,500  
        • Magnus Pro: ₦17,500  
        • Magnus Lite: ₦11,500

        *Perks for Paying *Now**:*  
        • ⚡ *Priority Activation* — jump the queue  
        • 🎁 *Starter Toolkit* — quick-start guides + templates  
        • 🛡️ *5-Day Entry Fee Safety* — recoverable on terms stated  
        • 💼 *Fast-Track Jobs* (Business tier) — early slot access

        After payment, *send your receipt here* for instant processing.
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
# Helper: Typing “animation”
# ===========================
async def human_typing(chat_id: int, seconds: float = 1.2):
    await bot.send_chat_action(chat_id, ChatAction.TYPING)
    await asyncio.sleep(seconds)

# ===========================
# Countdown Engine (edits msg)
# ===========================
async def start_countdown(chat_id: int, message_id: int, total_seconds: int = 300):
    """
    Edits the same message with a ticking countdown (every 10s).
    Telegram rate limits apply; 10s steps are friendly.
    """
    step = 10
    remain = total_seconds
    while remain > 0:
        m, s = divmod(remain, 60)
        timer = f"{m:01d}:{s:02d}"
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=dedent(f"""\
                    ⏳ *Secure your perks by completing payment now*

                    • *Priority Activation* — jump the queue  
                    • *Starter Toolkit* — guides & templates  
                    • *5-Day Entry Fee Safety*  
                    • *Fast-Track Jobs* (Business tier)

                    *Nigeria — Pay via Bank Transfer (No OPay)*  
                    *Bank:* Moniepoint MFB  
                    *Acct:* `6054080105`  
                    *Name:* *SPINO CLINTON UCHENNA*

                    Time left to lock perks: *{timer}*
                    _After transfer, send your receipt here for instant processing._
                """),
                reply_markup=kb_back_menu()
            )
        except Exception:
            # If message was changed by user actions or edited too fast, ignore.
            pass
        await asyncio.sleep(step)
        remain -= step

    # Final nudge
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=dedent("""\
                ✅ *Timer ended.*

                You can still complete payment to join MAGNUS — but *priority perks* may no longer apply.
                
                *Nigeria — Bank Transfer (No OPay)*  
                *Bank:* Moniepoint MFB  
                *Acct:* `6054080105`  
                *Name:* *SPINO CLINTON UCHENNA*

                _Send your receipt here to activate your access._
            """),
            reply_markup=kb_back_menu()
        )
        # Optional little celebration animation when they reply with proof (handled manually by you),
        # but we can pre-warm with a friendly animation here:
        await bot.send_animation(chat_id, ANIMS["celebrate"])
    except Exception:
        pass

# ===========================
# Handlers
# ===========================
@dp.message(CommandStart())
async def on_start(message: types.Message):
    await human_typing(message.chat.id, 1.0)
    text = dedent(f"""\
        *Welcome to MAGNUS!*
        This bot will guide you through:
        • What MAGNUS is
        • Earning Features + Legitimacy
        • How to Register (with your country’s payment details)

        👉 Tap the Telegram *Start* button to begin, then choose an option below.
        Need help? Reply here and we’ll assist you.
    """)
    await message.answer(text, reply_markup=kb_main_menu())

@dp.message(Command("menu"))
async def on_menu(message: types.Message):
    await message.answer("Choose a section:", reply_markup=kb_main_menu())

async def show_section(chat_id: int, key: str):
    await human_typing(chat_id, 0.8)
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

        await human_typing(chat_id, 0.8)
        sent = await bot.send_message(chat_id, details, reply_markup=kb_back_menu())

        # Special behavior for Nigeria: start visible countdown + perks lock-in
        if code == "NG":
            # Kick off countdown in background (doesn't block webhook loop)
            asyncio.create_task(start_countdown(chat_id, sent.message_id, total_seconds=300))

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
