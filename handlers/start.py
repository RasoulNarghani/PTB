# =============================================
# handlers/start.py
# هندلر استارت و منوی اصلی
# =============================================

import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import JOIN_CHANNEL_LINK, BOT_LINK
from keyboards import (
    join_channel_keyboard, main_menu_keyboard,
    features_keyboard, go_back_keyboard
)
from texts import (
    JOIN_TEXT, WELCOME_TEXT, FEATURES_TEXT,
    NOT_MEMBER_TEXT, UNKNOWN_COMMAND_TEXT
)
from services.user import ensure_user, get_full_name, check_channel_membership
from services.points import get_invite_link, process_invite
import database as db

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دستور /start"""
    user = update.effective_user
    message = update.effective_message

    # دریافت پارامتر ارجاع
    args = context.args
    referred_by = None
    if args and args[0].startswith("ref_"):
        try:
            referred_by = int(args[0].split("_")[1])
            if referred_by == user.id:
                referred_by = None
        except (ValueError, IndexError):
            referred_by = None

    # بررسی کاربر جدید
    existing_user = db.get_user(user.id)
    is_new_user = existing_user is None

    # ثبت یا بروزرسانی کاربر
    ensure_user(user)

    # اگر کاربر جدید بود و از طریق لینک دعوت اومده
    if is_new_user and referred_by and db.get_user(referred_by):
        # ذخیره دعوت‌کننده
        with db.get_db() as conn:
            conn.execute(
                "UPDATE users SET invited_by=? WHERE user_id=?",
                (referred_by, user.id)
            )
        # اعطای امتیاز دعوت
        await process_invite(referred_by, user.id, context)

    # بررسی عضویت در کانال
    is_member = await check_channel_membership(context.bot, user.id)

    if not is_member:
        await message.reply_text(
            JOIN_TEXT,
            reply_markup=join_channel_keyboard(JOIN_CHANNEL_LINK),
            parse_mode="HTML"
        )
        return

    # ارسال خوش‌آمدگویی
    await message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )


async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بررسی عضویت با کلیک روی دکمه"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    is_member = await check_channel_membership(context.bot, user.id)

    if not is_member:
        await query.answer(NOT_MEMBER_TEXT, show_alert=True)
        return

    # کاربر عضو شد
    ensure_user(user)
    await query.message.edit_text(
        WELCOME_TEXT,
        reply_markup=None,
        parse_mode="HTML"
    )
    await context.bot.send_message(
        chat_id=user.id,
        text=WELCOME_TEXT,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )


async def features_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه مشاهده امکانات"""
    message = update.effective_message
    await message.reply_text(
        FEATURES_TEXT,
        reply_markup=features_keyboard(),
        parse_mode="HTML"
    )


async def go_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر دکمه برگشت به عقب
    بر اساس state کاربر، به صفحه قبلی برمیگرده
    """
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    state_data = db.get_state(user.id)

    if not state_data or not state_data.get("state"):
        # برگشت به منوی اصلی
        await query.message.edit_text(
            WELCOME_TEXT,
            reply_markup=None,
            parse_mode="HTML"
        )
        return

    state = state_data["state"]

    # انتقال به صفحه قبلی بر اساس state
    if state in ["buy_username", "buy_payment", "buy_renew"]:
        # برگشت به صفحه پلن‌ها
        from handlers.buy import show_plans
        await show_plans(query, context)
    elif state in ["profile_accounts", "profile_sub_detail"]:
        # برگشت به پروفایل
        from handlers.profile import show_profile
        await show_profile(query, context, edit=True)
    elif state in ["profile_points", "profile_add"]:
        # برگشت به پروفایل
        from handlers.profile import show_profile
        await show_profile(query, context, edit=True)
    elif state == "sub_manage":
        # برگشت به لیست اشتراک‌ها
        from handlers.profile import show_my_accounts
        await show_my_accounts(query, context)
    elif state in ["disable_confirm", "active_confirm", "revoke_confirm", "delete_confirm"]:
        # برگشت به مدیریت اشتراک
        import json
        data = json.loads(state_data.get("data", "{}"))
        sub_username = data.get("sub_username", "")
        from handlers.profile import show_sub_detail
        await show_sub_detail(query, context, sub_username)
    else:
        # پیش‌فرض: برگشت به پروفایل
        from handlers.profile import show_profile
        await show_profile(query, context, edit=True)
