# =============================================
# handlers/subtest_handler.py
# هندلر بخش اشتراک تست
# =============================================

import logging
from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_ID, SUBTEST_DURATION_HOURS
from keyboards import (
    receive_subtest_keyboard, go_back_keyboard,
    go_buy_keyboard, subscription_keyboard
)
from texts import (
    SUBTEST_TEXT, RECEIVED_SUBTEST_TEXT, REJECT_RECEIVE_SUBTEST_TEXT,
    NO_SUBTEST_AVAILABLE_TEXT,
    user_send_subtest_text, user_timeout_subtest_text, admin_reset_subtest_text
)
from services.subscription import fetch_subscription_info
from services.user import get_full_name
from subtest import get_available_subtest, SUBTEST_ACCOUNTS
import database as db

logger = logging.getLogger(__name__)


async def request_subtest_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر درخواست اشتراک تست"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    await query.message.edit_text(
        SUBTEST_TEXT,
        reply_markup=receive_subtest_keyboard(),
        parse_mode="HTML"
    )


async def receive_subtest_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دریافت اشتراک تست"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    # بررسی آیا قبلاً اشتراک تست گرفته
    existing_test = db.get_user_subtest(user.id)
    if existing_test:
        await query.message.edit_text(
            RECEIVED_SUBTEST_TEXT,
            reply_markup=go_back_keyboard(),
            parse_mode="HTML"
        )
        return

    # بررسی آیا اشتراک عادی یا هدیه دارد
    subs = db.get_user_active_subscriptions(user.id)
    if subs:
        await query.message.edit_text(
            REJECT_RECEIVE_SUBTEST_TEXT,
            reply_markup=go_back_keyboard(),
            parse_mode="HTML"
        )
        return

    # یافتن اشتراک تست آزاد
    assigned_numbers = db.get_assigned_subtest_numbers()
    available = get_available_subtest(assigned_numbers)

    if not available:
        await query.message.edit_text(
            NO_SUBTEST_AVAILABLE_TEXT,
            reply_markup=go_back_keyboard(),
            parse_mode="HTML"
        )
        return

    # اختصاص اشتراک تست
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(hours=SUBTEST_DURATION_HOURS)).isoformat()

    db.assign_subtest(
        user_id=user.id,
        subtest_username=available["username"],
        subtest_link=available["link"],
        subtest_number=available["number"],
        expires_at=expires_at
    )

    # ذخیره در جدول اشتراک‌ها
    info = await fetch_subscription_info(available["link"])
    total_vol = info["sub_total_volume"] if info else 0.2
    used_vol = info["sub_used_volume"] if info else 0

    db.add_subscription(
        user_id=user.id,
        sub_username=available["username"],
        sub_link=available["link"],
        sub_type="test",
        sub_total_volume=total_vol,
        sub_used_volume=used_vol,
        sub_created_at=info["sub_created_at"] if info else now.isoformat()
    )

    await query.message.edit_text(
        user_send_subtest_text(available["number"]),
        reply_markup=subscription_keyboard(available["link"]),
        parse_mode="HTML"
    )


async def check_expired_subtests(context: ContextTypes.DEFAULT_TYPE):
    """
    Job برای بررسی اشتراک‌های تست منقضی شده
    هر 30 دقیقه اجرا می‌شود
    """
    expired = db.get_expired_subtests()

    for test in expired:
        user_id = test["user_id"]
        subtest_number = test["subtest_number"]
        subtest_link = test["subtest_link"]

        # دریافت اطلاعات آخرین حجم
        info = await fetch_subscription_info(subtest_link)
        total_vol = info["sub_total_volume"] if info else 0.2
        used_vol = info["sub_used_volume"] if info else 0

        # علامت‌گذاری به عنوان منقضی
        db.mark_subtest_expired(user_id)

        # حذف کامل اشتراک تست از نمایش (هم پروفایل، هم اشتراک‌های من)
        db.soft_delete_subscription(test["subtest_username"], user_id)

        # اطلاع رسانی به کاربر
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=user_timeout_subtest_text(total_vol, used_vol),
                reply_markup=go_buy_keyboard(),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error notifying user {user_id} about subtest expiry: {e}")

        # اطلاع رسانی به ادمین
        full_name = f"{test.get('first_name', '')} {test.get('last_name', '')}".strip()
        username = test.get("username")

        try:
            sent = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_reset_subtest_text(
                    full_name, username, user_id,
                    subtest_number, total_vol, used_vol
                ),
                parse_mode="HTML"
            )
            context.bot_data[f"subtest_reset_{sent.message_id}"] = {
                "subtest_number": subtest_number,
                "old_link": subtest_link
            }
        except Exception as e:
            logger.error(f"Error notifying admin about subtest {subtest_number}: {e}")


async def handle_admin_subtest_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """پردازش ریپلای ادمین برای ریست لینک اشتراک تست"""
    user = update.effective_user
    message = update.effective_message

    if user.id != ADMIN_ID:
        return False

    if not message.reply_to_message:
        return False

    replied_id = message.reply_to_message.message_id
    reset_key = f"subtest_reset_{replied_id}"

    if reset_key not in context.bot_data:
        return False

    reset_data = context.bot_data.pop(reset_key)
    subtest_number = reset_data["subtest_number"]

    new_link = message.text.strip() if message.text else ""

    from services.subscription import validate_subscription_link
    if not validate_subscription_link(new_link):
        await message.reply_text("⚠️ لینک معتبر نیست!")
        context.bot_data[reset_key] = reset_data
        return True

    # بروزرسانی لینک در دیتابیس
    db.update_subtest_link(subtest_number, new_link)
    await message.reply_text(f"✅ لینک اشتراک تست شماره {subtest_number} بروزرسانی شد.")
    return True
