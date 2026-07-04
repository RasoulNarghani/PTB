# =============================================
# config.py - تنظیمات اصلی ربات
# =============================================

# Bot
BOT_TOKEN = "8953535498:AAE4AKtrTcteACickymwFWlPA3_xIGbhGJI"
BOT_NAME = "Persian Tunnel Bot"
BOT_USERNAME = "PersianTunnelBot"
BOT_LINK = "https://t.me/PersianTunnelBot"

# Admin
ADMIN_ID = 8868259762
ADMIN_NAME = "Persian Tunnel Admin"
ADMIN_USERNAME = "PersianTunnelAdmin"

# Channel
CHANNEL_ID = -1001962788029
CHANNEL_NAME = "Persian Tunnel"
CHANNEL_USERNAME = "@PersianTunnel"
CHANNEL_LINK = "https://t.me/PersianTunnel"
JOIN_CHANNEL_LINK = "https://t.me/+3eLq9fkwII1mNzNk"

# Links
TUTORIAL_LINK = "https://t.me/PersianTunnel/277"
BASE_SUB_LINK = "https://de.3erveronline.com/sub/"

# Wallets
TON_WALLET = "UQBvOv6VPoXi0NYrlqHyQAM33AdkkPZAIuCxyuyWbYtUSboY"
TRC20_WALLET = "TPK3ty9AT2SpS4ZN1rdm2QNiXc5wpzGdim"

# Bank Card
CARD_NAME = "رسول نرقانی"
CARD_NUMBER = "6219-8614-2475-2532"

# Prices (پیش‌فرض - از دیتابیس خوانده می‌شود)
DEFAULT_USDT_PRICE = 174000
DEFAULT_GRAM_PRICE = 300000
DEFAULT__PRICE = 277790000
DEFAULT_TRX_PRICE = 52900

# Plans - حجم: قیمت به تومان
PLANS = {20: 240000, 50: 500000, 100: 900000, 200: 1600000, 500: 3500000, 1000: 6000000}


def get_plan_price(volume: int) -> int | None:
    """دریافت قیمت پلن بر اساس حجم"""
    return PLANS.get(volume)


def format_price(amount: int) -> str:
    """فرمت قیمت با جداکننده سه‌رقمی"""
    return f"{amount:,}"


# Points System
POINTS_PER_INVITE = 100
POINTS_PER_FIRST_BUY = 100
POINTS_PER_GB = 10
MIN_POINTS_FOR_GIFT = 10000
POINTS_PER_GB_GIFT = 1000  # هر 1000 امتیاز = 1 گیگابایت هدیه

# Subtest
SUBTEST_VOLUME_MB = 200
SUBTEST_DURATION_HOURS = 24

# Base subscription URL
BASE_SUB_URL = "https://de.3erveronline.com/sub/"
