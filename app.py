import os
import asyncio
from textwrap import dedent

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
BOT_TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")  # e.g. https://magnus-bot.onrender.com
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "magnus-secret")
WEBHOOK_PATH = f"/tg/{WEBHOOK_SECRET}"
PORT = int(os.getenv("PORT", "8000"))

if not BOT_TOKEN or not PUBLIC_BASE_URL:
    raise RuntimeError("BOT_TOKEN and PUBLIC_BASE_URL must be set as environment variables.")

# ===========================
# BOT + DISPATCHER (HTML mode)
# ===========================
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
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
    "celebrate": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjM3YzA5MGQ2M2ZkMDk0M2I5NTRmOWQxM2EwYWFkZjFjYTcxY2Y5MiZjdD1n/26gslU06gXJ5a9aYs/giphy.gif"
}

# ===========================
# Features & Earnings (HTML)
# ===========================
MAGNUS_UNIQUE = dedent("""\
▫ <b>Magnus offers thousands of digital products</b> you can access anytime.<br>
▫ Some products are usable <i>immediately</i>, others need deeper study — <b>you choose</b>.<br>
▫ Some skills take <i>minutes</i>, others <i>months</i> — <b>your pace, your path</b>.<br>
▫ Learn <b>multiple</b> skills to increase your income.<br>
▫ The <b>more skills</b> you learn and the <b>more time</b> you work, the <b>more you earn</b>.<br>
▫ Become a <b>digital retailer</b> and earn <b>millions monthly</b> (no referrals required).<br>
▫ Withdraw via <b>PayPal</b>, <b>USDT</b>, or a <b>local bank account</b>.<br>
▫ <b>100% refundable</b> entry fee — can be recovered within <b>5 days</b> of joining.
""")

MAGNUS_EMP_EARNINGS = dedent("""\
<b>Earnings for Magnus Employees</b><br><br>
① Gain Valuable Skills<br>
② Get Trained<br>
③ Get Employed<br>
④ Start Making Money<br><br>
• Every <b>30 minutes</b> of work: <b>₦2,499</b><br>
• 1 hour  = <b>₦4,999.8</b><br>
• 2 hours = <b>₦9,999.6</b><br>
• 3 hours = <b>₦14,999.4</b><br><br>
⭐ Work <b>6 hours daily</b> → <b>₦29,998.8/day</b>, <b>₦209,991.6/week</b>, <b>₦899,964/30 days</b><br><br>
<b>Pro tip:</b> Learn <b>two skills</b> and multitask to <b>double your income</b>:<br>
• 1 day:  ₦59,997.6<br>
• 2 days: ₦119,995.2<br>
• 3 days: ₦179,992.8<br>
• 4 days: ₦239,990.4<br><br>
⚡ You can also become a <b>digital retailer</b> and earn <b>millions monthly</b> — <i>no referrals needed</i>.
""")

# ===========================
# Section Texts (HTML)
# ===========================
SECTION_TEXT = {
    "what_is": dedent(f"""\
<b>MAGNUS — Your Shortcut to Digital Freedom</b><br><br>
MAGNUS is a digital marketplace for <b>in-demand skills</b> and <b>powerful products</b>
(trading tools, signals, analytics, courses). Use them for <i>personal growth</i> or
<i>resell for profit</i>. With flexible plans, instant earning routes, and global job
offers, MAGNUS helps you <b>learn, earn, and grow</b>.<br><br>
{MAGNUS_UNIQUE}
"""),

    "features": dedent(f"""\
<b>What You Get (Earning Features + Legitimacy)</b><br><br>
• Trading Tools — stay ahead in the markets<br>
• Signals &amp; Analytics — make smarter moves<br>
• Hot Courses — learn skills in minutes, not months<br>
• Resale Rights — earn while others are still learning<br><br>

<b>Entry Plans</b><br>
• <b>MAGNUS BUSINESS</b> — ₦28,500<br>
&nbsp;&nbsp;Unlimited products • Full resale rights • Create &amp; sell your own • Instant job after skills<br>
&nbsp;&nbsp;Commissions: Direct ₦17,100 | Indirect ₦1,300<br><br>

• <b>MAGNUS PRO</b> — ₦17,500<br>
&nbsp;&nbsp;Limited access • Low resale rights • Learn for growth<br>
&nbsp;&nbsp;Earn via PR entry data up to ₦985 every 2 minutes (when available)<br>
&nbsp;&nbsp;Commissions: Direct ₦11,500 | Indirect ₦650<br><br>

• <b>MAGNUS LITE</b> — ₦11,500<br>
&nbsp;&nbsp;1 product • No resale rights<br>
&nbsp;&nbsp;Earn via referrals + data entry up to ₦985 every 2 minutes (when available)<br>
&nbsp;&nbsp;Commissions: Direct ₦7,500 | Indirect ₦350<br><br>

<b>Earnings Potential</b><br>
• Profit ₦5,000+ per sale<br>
• Company handles ads &amp; logistics<br>
• Free resale setup manual (1–72hrs sales cycle)<br>
• Multiple streams: Skills + Resale + Commissions + Global Jobs<br><br>
{MAGNUS_EMP_EARNINGS}
"""),

    "register": dedent("""\
<b>How to Register (Simple Steps)</b><br><br>
1) Choose your entry plan: <b>Business</b>, <b>Pro</b>, or <b>Lite</b>.<br>
2) Tap <b>Register Now</b>, pick your country, and pay to the displayed account.<br>
3) Send your receipt here in chat.<br>
4) Get activated and start learning, using products, and earning.<br><br>
<i>Tip: Start now. The sooner you begin, the faster you unlock skills, resale rights, and job routes.</i>
"""),
}

# ===========================
# Payments (HTML; NG updated)
# ===========================
PAYMENT_DETAILS = {
    "NG": dedent("""\
🇳🇬 <b>Nigeria — Bank Transfer (No OPay)</b><br><br>
• <b>Bank:</b> Moniepoint MFB<br>
• <b>Account Number:</b> <code>6054080105</code><br>
• <b>Account Name:</b> <b>SPINO CLINTON UCHENNA</b><br><br>
🔔 <b>OPay payments are NOT allowed.</b> Please use <b>bank transfer</b> only.<br><br>
<b>One-time Fees:</b><br>
• Magnus Business: ₦28,500<br>
• Magnus Pro: ₦17,500<br>
• Magnus Lite: ₦11,500<br><br>
<b>Perks for Paying Now:</b><br>
• ⚡ <b>Priority Activation</b> — jump the queue<br>
• 🎁 <b>Starter Toolkit</b> — guides &amp; templates<br>
• 🛡️ <b>5-Day Entry Fee Safety</b> — recoverable on stated terms<br>
• 💼 <b>Fast-Track Jobs</b> (Business tier) — early slot access<br><br>
After payment, <b>send your receipt here</b> for instant processing.
"""),
    "GH": dedent("""\
🇬🇭 <b>Ghana — Mobile Money</b><br>
• Name: REPLACE_ME_MOMO_NAME<br>
• Network: REPLACE_ME_NETWORK<br>
• MoMo Number: REPLACE_ME_MOMO_NUMBER<br><br>
<b>Equivalent Fees:</b> confirm current rate<br>
• Business ≈ NGN 28,500<br>
• Pro ≈ NGN 17,500<br>
• Lite ≈ NGN 11,500<br><br>
Send proof of payment here to proceed.
"""),
    "KE": dedent("""\
🇰🇪 <b>Kenya — M-Pesa</b><br>
• Name: REPLACE_ME_MPESA_NAME<br>
• Till/PayBill: REPLACE_ME_MPESA_TILL<br>
• Number: REPLACE_ME_MPESA_NUMBER<br><br>
<b>Equivalent Fees:</b> confirm current rate<br>
• Business ≈ NGN 28,500<br>
• Pro ≈ NGN 17,500<br>
• Lite ≈ NGN 11,500<br><br>
Send proof of payment here to proceed.
"""),
    "ZA": dedent("""\
🇿🇦 <b>South Africa — EFT</b><br>
• Account Name: REPLACE_ME_ACCOUNT_NAME<br>
• Bank: REPLACE_ME_BANK<br>
• Account No: REPLACE_ME_ACCOUNT_NUMBER<br><br>
<b>Equivalent Fees:</b> confirm current rate<br>
• Business ≈ NGN 28,500<br>
• Pro ≈ NGN 17,500<br>
• Lite ≈ NGN 11,500<br><br>
Send proof of payment here to proceed.
"""),
    "INTL": dedent("""\
🌍 <b>International — USD / Wise / PayPal</b><br>
• Method: REPLACE_ME_METHOD (e.g., Wise/PayPal)<br>
• Handle/Email: REPLACE_ME_EMAIL_OR_HANDLE<br><br>
<b>Guide (edit to official USD pricing):</b><br>
• Business: $35<br>
• Pro: $25<br>
• Lite: $18<br><br>
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
⏳ <b>Secure your perks by completing payment now</b><br><br>
• <b>Priority Activation</b> — jump the queue<br>
• <b>Starter Toolkit</b> — guides &amp; templates<br>
• <b>5-Day Entry Fee Safety</b><br>
• <b>Fast-Track Jobs</b> (Business tier)<br><br>
<b>Nigeria — Pay via Bank Transfer (No OPay)</b><br>
<b>Bank:</b> Moniepoint MFB<br>
<b>Acct:</b> <code>6054080105</code><br>
<b>Name:</b> <b>SPINO CLINTON UCHENNA</b><br><br>
Time left to lock perks: <b>{timer}</b><br>
<i>After transfer, send your receipt here for instant processing.</i>
"""),
                reply_markup=kb_back_menu()
            )
        except Exception:
            pass
        await asyncio.sleep(step)
        remain -= step

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=dedent("""\
✅ <b>Timer ended.</b><br><br>
You can still complete payment to join MAGNUS — but <b>priority perks</b> may no longer apply.<br><br>
<b>Nigeria — Bank Transfer (No OPay)</b><br>
<b>Bank:</b> Moniepoint MFB<br>
<b>Acct:</b> <code>6054080105</code><br>
<b>Name:</b> <b>SPINO CLINTON UCHENNA</b><br><br>
<i>Send your receipt here to activate your access.</i>
"""),
            reply_markup=kb_back_menu()
        )
        await bot.send_animation(chat_id, ANIMS["celebrate"])
    except Exception:
        pass

# ===========================
# Handlers
# ===========================
@dp.message(CommandStart())
async def on_start(message: types.Message):
    await human_typing(message.chat.id, 1.0)
    text = dedent("""\
<b>Welcome to MAGNUS!</b><br>
This bot will guide you through:<br>
• What MAGNUS is<br>
• Earning Features + Legitimacy<br>
• How to Register (with your country’s payment details)<br><br>
👉 Tap the Telegram <b>Start</b> button to begin, then choose an option below.<br>
Need help? Reply here and we’ll assist you.
""")
    await message.answer(text, reply_markup=kb_main_menu())

@dp.message(Command("menu"))
async def on_menu(message: types.Message):
    await message.answer("Choose a section:", reply_markup=kb_main_menu())

async def show_section(chat_id: int, key: str):
    await human_typing(chat_id, 0.8)
    caption = SECTION_TEXT[key] + "<br><i>Tap the button below to proceed.</i>"
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

        if code == "NG":
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
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=None).register(app, path=WEBHOOK_PATH)
    async def health(_): return web.Response(text="OK")
    app.router.add_get("/", health)
    return app

if __name__ == "__main__":
    web.run_app(build_app(), port=PORT)
