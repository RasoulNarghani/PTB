# =============================================
# keyboard.py - تمامی کیبوردها و دکمه‌ها
# =============================================

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    CopyTextButton
)
from config import *
from callbacks import *


# ==========================================
# متن دکمه‌ها
# ==========================================

BUTTON_JOIN_CHANNEL = "عضویت در Persian Tunnel 🦁🛡"
BUTTON_JOIN_CHECK = "بررسی عضویت ☑️"

BUTTON_BUY_SUB = "خرید اشتراک 🛍"
BUTTON_FEATURES = "مشاهده امکانات ✨"
BUTTON_PROFILE = "حساب کاربری من 👤"
BUTTON_SUPPORT = "پشتیبانی 🎫"

BUTTON_GO_BACK = "برگشت به عقب 🔙"

BUTTON_MY_ACCOUNTS = "اشتراک‌های من 🆔"
BUTTON_MY_POINTS = "امتیازات من 🪄"

BUTTON_ADD_NEWSUB = "افزودن اشتراک جدید ➕"
BUTTON_ADD_ACCOUNT = "افزودن اشتراک ➕"
BUTTON_RANDOM_USERNAME = "نام کاربری رندوم 🔀"

BUTTON_GO_BUY = "رفتن به صفحه خرید 🛍"
BUTTON_REQ_SUBTEST = "درخواست اشتراک تست 💡"
BUTTON_RECEIVE_SUBTEST = "دریافت اشتراک تست 💡"

BUTTON_COPY_TON = "کپی آدرس ولت TON"
BUTTON_COPY_TRC20 = "کپی آدرس ولت TRC20"
BUTTON_SHOW_WALLETS = "نمایش QR آدرس ولت‌ها 📷"

BUTTON_CARD_NUMBER = "شماره کارت 💳"

BUTTON_SEND_RECEIPT = "ارسال رسید 🌄📝"
BUTTON_RESEND_RECEIPT = "ارسال مجدد رسید 🔁"

BUTTON_COPY_SUB = "کپی لینک اشتراک"
BUTTON_OPEN_SUB = "باز کردن لینک اشتراک 🔗"
BUTTON_TUTORIAL_LINK = "آموزش افزودن اشتراک به برنامه‌ها"

BUTTON_ACTIVE_SUB = "فعال کردن اشتراک ✅"
BUTTON_DISABLE_SUB = "غیرفعال کردن اشتراک ❌"
BUTTON_REVOKE_SUB = "تغییر لینک اشتراک 🔄"
BUTTON_DELETE_SUB = "حذف اشتراک 🗑"

BUTTON_CONVERT_POINTS = "تبدیل امتیاز به اشتراک 🔄"
BUTTON_ALL_CONVERT = "تبدیل همه امتیازها به اشتراک 🔄"

BUTTON_INVITE_BANNER = "دریافت بنر دعوت 🎁"

BUTTON_REPLY_USER = "پاسخ 💬"
BUTTON_REPLY_ADMIN = "پاسخ به ادمین 💬"
BUTTON_CLOSE_TICKET = "بستن تیکت 🔒"

BUTTON_DONE = "انجام شد ✅"


# ==========================================
# کیبورد پایین صفحه (Reply Keyboard)
# ==========================================

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """کیبورد اصلی پایین صفحه"""
    keyboard = [
        [BUTTON_FEATURES, BUTTON_BUY_SUB],
        [BUTTON_PROFILE, BUTTON_SUPPORT]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )


# ==========================================
# Inline Keyboards
# ==========================================

def join_channel_keyboard(join_channel_link: str) -> InlineKeyboardMarkup:
    """دکمه‌های عضویت و بررسی عضویت"""
    keyboard = [
        [
            InlineKeyboardButton(
                BUTTON_JOIN_CHANNEL,
                url=join_channel_link
            )
        ],
        [
            InlineKeyboardButton(
                BUTTON_JOIN_CHECK,
                callback_data=CHECK_JOIN
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def features_keyboard() -> InlineKeyboardMarkup:
    """دکمه‌های صفحه امکانات"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_GO_BUY, callback_data=GO_BUY)
        ],
        [
            InlineKeyboardButton(BUTTON_REQ_SUBTEST, callback_data=REQUEST_SUBTEST)
        ],
        [
            InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def go_buy_keyboard() -> InlineKeyboardMarkup:
    """دکمه رفتن به صفحه خرید"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_GO_BUY, callback_data=GO_BUY)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def go_back_keyboard() -> InlineKeyboardMarkup:
    """دکمه برگشت به عقب"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def support_reply_keyboard(ticket_id: str) -> InlineKeyboardMarkup:
    """دکمه‌های پشتیبانی برای ادمین"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_REPLY_USER, callback_data=f"reply_user_{ticket_id}")
        ],
        [
            InlineKeyboardButton(BUTTON_CLOSE_TICKET, callback_data=f"{CLOSE_TICKET_PREFIX}{ticket_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def user_reply_keyboard(ticket_id: str) -> InlineKeyboardMarkup:
    """دکمه‌های پشتیبانی برای کاربر"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_REPLY_ADMIN, callback_data=f"reply_admin_{ticket_id}")
        ],
        [
            InlineKeyboardButton(BUTTON_CLOSE_TICKET, callback_data=f"{CLOSE_TICKET_PREFIX}{ticket_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def plans_keyboard(plans: dict) -> InlineKeyboardMarkup:
    """دکمه‌های پلن‌های خرید"""
    keyboard = []
    for volume, price in plans.items():
        formatted_price = f"{price:,}"
        keyboard.append([
            InlineKeyboardButton(
                f"📦 {volume} گیگابایت = {formatted_price} تومان",
                callback_data=f"{PLAN_PREFIX}{volume}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(BUTTON_REQ_SUBTEST, callback_data=REQUEST_SUBTEST)
    ])
    keyboard.append([
        InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
    ])
    return InlineKeyboardMarkup(keyboard)


def random_username_keyboard() -> InlineKeyboardMarkup:
    """دکمه انتخاب نام کاربری رندوم"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_RANDOM_USERNAME, callback_data=RANDOM_USERNAME)
        ],
        [
            InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def renew_keyboard(accounts: list) -> InlineKeyboardMarkup:
    """دکمه‌های اشتراک‌ها برای تمدید"""
    keyboard = []
    row = []
    for account in accounts:
        username = account.get("sub_username", "")
        row.append(
            InlineKeyboardButton(
                f"🆔 {username}",
                callback_data=f"{RENEW_PREFIX}{username}"
            )
        )
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(BUTTON_ADD_NEWSUB, callback_data=ADD_NEWSUB)
    ])
    keyboard.append([
        InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
    ])
    return InlineKeyboardMarkup(keyboard)


def wallets_keyboard() -> InlineKeyboardMarkup:
    """دکمه‌های ولت‌ها و ارسال رسید"""
    keyboard = [
        [
            InlineKeyboardButton(
                BUTTON_COPY_TON,
                copy_text=CopyTextButton(TON_WALLET)
            )
        ],
        [
            InlineKeyboardButton(
                BUTTON_COPY_TRC20,
                copy_text=CopyTextButton(TRC20_WALLET)
            )
        ],
        [
            InlineKeyboardButton(BUTTON_SHOW_WALLETS, callback_data=SHOW_QRCODE)
        ],
        [
            InlineKeyboardButton(BUTTON_SEND_RECEIPT, callback_data=SEND_RECEIPT)
        ],
        [
            InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def receipt_review_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """دکمه‌های تایید و رد رسید برای ادمین"""
    keyboard = [
        [
            InlineKeyboardButton("تایید ✅", callback_data=f"{APPROVE_RECEIPT_PREFIX}{order_id}"),
            InlineKeyboardButton("رد ❌", callback_data=f"{REJECT_RECEIPT_PREFIX}{order_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def resend_receipt_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """دکمه ارسال مجدد رسید"""
    keyboard = [
        [
            InlineKeyboardButton(
                BUTTON_RESEND_RECEIPT,
                callback_data=f"{RESEND_RECEIPT_PREFIX}{order_id}"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def subscription_keyboard(link: str) -> InlineKeyboardMarkup:
    """دکمه‌های مشاهده اشتراک"""
    keyboard = [
        [
            InlineKeyboardButton(
                BUTTON_COPY_SUB,
                copy_text=CopyTextButton(link)
            )
        ],
        [
            InlineKeyboardButton(BUTTON_OPEN_SUB, url=link)
        ],
        [
            InlineKeyboardButton(BUTTON_TUTORIAL_LINK, url=TUTORIAL_LINK)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def profile_keyboard() -> InlineKeyboardMarkup:
    """دکمه‌های پروفایل"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_MY_ACCOUNTS, callback_data=MY_ACCOUNTS),
            InlineKeyboardButton(BUTTON_MY_POINTS, callback_data=MY_POINTS)
        ],
        [
            InlineKeyboardButton(BUTTON_ADD_ACCOUNT, callback_data=ADD_ACCOUNT)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def my_accounts_keyboard(accounts: list) -> InlineKeyboardMarkup:
    """دکمه‌های لیست اشتراک‌های کاربر"""
    keyboard = []
    row = []
    for account in accounts:
        username = account.get("sub_username", "")
        row.append(
            InlineKeyboardButton(
                f"🆔 {username}",
                callback_data=f"{VIEW_SUB_PREFIX}{username}"
            )
        )
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
    ])
    return InlineKeyboardMarkup(keyboard)


def subscription_manage_keyboard(link: str, username: str, is_active: bool = True) -> InlineKeyboardMarkup:
    """دکمه‌های مدیریت اشتراک"""
    toggle_btn = (
        InlineKeyboardButton(BUTTON_DISABLE_SUB, callback_data=f"req_disable_{username}")
        if is_active else
        InlineKeyboardButton(BUTTON_ACTIVE_SUB, callback_data=f"req_active_{username}")
    )
    keyboard = [
        [
            InlineKeyboardButton(
                BUTTON_COPY_SUB,
                copy_text=CopyTextButton(link)
            )
        ],
        [
            InlineKeyboardButton(BUTTON_OPEN_SUB, url=link)
        ],
        [toggle_btn],
        [
            InlineKeyboardButton(BUTTON_REVOKE_SUB, callback_data=f"{REVOKE_SUB_PREFIX}{username}"),
            InlineKeyboardButton(BUTTON_DELETE_SUB, callback_data=f"{DELETE_SUB_PREFIX}{username}")
        ],
        [
            InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def yes_no_keyboard(action: str) -> InlineKeyboardMarkup:
    """دکمه‌های بله و خیر"""
    keyboard = [
        [
            InlineKeyboardButton("خیر ❌", callback_data=f"{CANCEL_PREFIX}{action}"),
            InlineKeyboardButton("بله ✅", callback_data=f"{CONFIRM_PREFIX}{action}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def done_keyboard(action: str) -> InlineKeyboardMarkup:
    """دکمه انجام شد"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_DONE, callback_data=f"{DONE_PREFIX}{action}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def points_keyboard() -> InlineKeyboardMarkup:
    """دکمه‌های صفحه امتیازات"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_INVITE_BANNER, callback_data=INVITE_BANNER)
        ],
        [
            InlineKeyboardButton(BUTTON_CONVERT_POINTS, callback_data=CONVERT_POINTS)
        ],
        [
            InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def low_points_keyboard() -> InlineKeyboardMarkup:
    """دکمه‌های صفحه کم بودن امتیاز"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_INVITE_BANNER, callback_data=INVITE_BANNER)
        ],
        [
            InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def convert_points_keyboard(unused_points: int) -> InlineKeyboardMarkup:
    """دکمه‌های تبدیل امتیاز به اشتراک"""
    keyboard = []

    # دکمه‌های پایه
    keyboard.append([
        InlineKeyboardButton(
            "کسر ۱۰,۰۰۰ امتیاز = دریافت ۱۰ گیگابایت 🎁",
            callback_data=f"{CONVERT_POINTS_PREFIX}10000"
        )
    ])

    if unused_points >= 15000:
        keyboard.append([
            InlineKeyboardButton(
                "کسر ۱۵,۰۰۰ امتیاز = دریافت ۱۵ گیگابایت 🎁",
                callback_data=f"{CONVERT_POINTS_PREFIX}15000"
            )
        ])

    if unused_points >= 20000:
        keyboard.append([
            InlineKeyboardButton(
                "کسر ۲۰,۰۰۰ امتیاز = دریافت ۲۰ گیگابایت 🎁",
                callback_data=f"{CONVERT_POINTS_PREFIX}20000"
            )
        ])

    # حجم کل قابل تبدیل
    total_gb = round(unused_points / POINTS_PER_GB_GIFT, 2)
    keyboard.append([
        InlineKeyboardButton(
            f"کسر همه امتیازها = دریافت {total_gb} گیگابایت 🎁",
            callback_data=CONVERT_ALL_POINTS
        )
    ])

    keyboard.append([
        InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
    ])
    return InlineKeyboardMarkup(keyboard)


def receive_subtest_keyboard() -> InlineKeyboardMarkup:
    """دکمه دریافت اشتراک تست"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTON_RECEIVE_SUBTEST, callback_data=RECEIVE_SUBTEST)
        ],
        [
            InlineKeyboardButton(BUTTON_GO_BACK, callback_data=GO_BACK)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_message_channel_keyboard() -> InlineKeyboardMarkup:
    """دکمه‌های ارسال پیام در کانال توسط ادمین"""
    keyboard = [
        [
            InlineKeyboardButton("افزودن دکمه URL ➕", callback_data=ADMIN_ADD_BUTTONS)
        ],
        [
            InlineKeyboardButton("ارسال الان 📤", callback_data=ADMIN_SEND_NOW)
        ],
        [
            InlineKeyboardButton("انصراف ❌", callback_data=ADMIN_CANCEL)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)




def admin_user_panel_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ ارسال پیام", callback_data=f"adminp_msg_{user_id}")],
        [InlineKeyboardButton("🏆 امتیازات", callback_data=f"adminp_points_{user_id}")],
        [InlineKeyboardButton("👤 دعوت شده توسط", callback_data=f"adminp_setinviter_{user_id}")],
        [InlineKeyboardButton("👥 دعوت‌شدگان", callback_data=f"adminp_setinvited_{user_id}")],
        [InlineKeyboardButton("📦 اشتراک‌های کاربر", callback_data=f"adminp_subs_{user_id}")],
        [InlineKeyboardButton("⏱ اشتراک تست", callback_data=f"adminp_subtest_{user_id}")],
    ])
