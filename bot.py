#!/usr/bin/env python3
# =============================================
# bot.py - فایل اصلی ربات Persian Tunnel
# =============================================

import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from database import DB_PATH

from config import BOT_TOKEN, ADMIN_ID
from database import init_db
from keyboards import (
    BUTTON_BUY_SUB,
    BUTTON_FEATURES,
    BUTTON_PROFILE,
    BUTTON_SUPPORT
)
from callbacks import *

# Handlers
from handlers.start import (
    start_handler, check_join_callback,
    features_handler, go_back_callback
)
from handlers.buy import (
    buy_handler, plan_selected_callback, renew_selected_callback,
    add_newsub_callback, random_username_callback,
    show_qrcode_callback, send_receipt_callback,
    approve_receipt_callback, reject_receipt_callback,
    resend_receipt_callback,
    handle_username_input, handle_receipt_input, handle_admin_reply
)
from handlers.support import (
    support_handler, reply_user_callback, reply_admin_callback,
    close_ticket_callback, handle_support_message, handle_admin_support_reply
)
from handlers.profile import (
    profile_handler, my_accounts_callback, view_sub_callback,
    req_disable_callback, confirm_disable_callback, cancel_disable_callback,
    done_disable_callback,
    req_active_callback, confirm_active_callback, cancel_active_callback,
    done_active_callback,
    revoke_sub_callback, confirm_revoke_callback, cancel_revoke_callback,
    delete_sub_callback, confirm_delete_callback, cancel_delete_callback,
    add_account_callback, handle_add_account,
    my_points_callback, invite_banner_callback,
    convert_points_callback, convert_points_selected_callback,
    convert_all_points_callback,
    handle_admin_revoke_and_gift_reply
)
from handlers.subtest_handler import (
    request_subtest_callback, receive_subtest_callback,
    check_expired_subtests, handle_admin_subtest_reset
)
from handlers.admin import (
    price_command, user_command, message_command,
    channel_command,
    admin_send_now_callback, admin_cancel_callback, admin_add_buttons_callback,
    handle_admin_broadcast, handle_channel_message
)

# تنظیمات لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# غیرفعال کردن لاگ‌های اضافی
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

async def send_db_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return  # فقط ادمین اجازه داره
    try:
        with open(DB_PATH, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename="persian_tunnel.db"
            )
    except Exception as e:
        await update.message.reply_text(f"خطا در ارسال فایل: {e}")


async def universal_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر یکپارچه پیام‌های متنی
    اولویت‌بندی:
    1. دکمه‌های Reply Keyboard
    2. State-based handlers
    """
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    text = message.text or ""

    # --- دکمه‌های منوی اصلی ---
    if text == BUTTON_BUY_SUB:
        await buy_handler(update, context)
        return

    if text == BUTTON_FEATURES:
        await features_handler(update, context)
        return

    if text == BUTTON_PROFILE:
        await profile_handler(update, context)
        return

    if text == BUTTON_SUPPORT:
        await support_handler(update, context)
        return

    # آپشن مخفی شماره کارت
    if text.strip() == "شماره کارت":
        from texts import user_send_card_text
        await message.reply_text(user_send_card_text(), parse_mode="HTML")
        return

    # --- پردازش بر اساس state ---

    # ادمین: پاسخ به کاربران
    if user.id == ADMIN_ID:
        if await handle_admin_reply(update, context):
            return
        if await handle_admin_support_reply(update, context):
            return
        if await handle_admin_broadcast(update, context):
            return
        if await handle_channel_message(update, context):
            return
        if await handle_admin_subtest_reset(update, context):
            return
        if await handle_admin_revoke_and_gift_reply(update, context):
            return

    # کاربر: نام کاربری خرید
    if await handle_username_input(update, context):
        return

    # کاربر: رسید پرداخت
    if await handle_receipt_input(update, context):
        return

    # کاربر: افزودن اشتراک
    if await handle_add_account(update, context):
        return

    # کاربر: پیام پشتیبانی
    if await handle_support_message(update, context):
        return


async def post_init(application: Application):
    """اجرا شده بعد از راه‌اندازی"""
    logger.info("Bot started successfully!")
    try:
        await application.bot.send_message(
            chat_id=ADMIN_ID,
            text="🤖 ربات روشن شد. ✅"
        )
    except Exception:
        pass


def main():
    """تابع اصلی راه‌اندازی ربات"""
    # اولیه‌سازی دیتابیس
    init_db()
    logger.info("Database initialized.")

    # ساخت Application
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ==========================================
    # Command Handlers
    # ==========================================
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("user", user_command))
    application.add_handler(CommandHandler("message", message_command))
    application.add_handler(CommandHandler("channel", channel_command))
    application.add_handler(CommandHandler("getdb", send_db_backup))

    # ==========================================
    # Callback Query Handlers
    # ==========================================

    # --- Channel Join ---
    application.add_handler(CallbackQueryHandler(check_join_callback, pattern=f"^{CHECK_JOIN}$"))

    # --- Navigation ---
    application.add_handler(CallbackQueryHandler(go_back_callback, pattern=f"^{GO_BACK}$"))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: buy_handler(u, c) if u.callback_query.message.text else None,
        pattern=f"^{GO_BUY}$"
    ))

    # --- Buy ---
    application.add_handler(CallbackQueryHandler(plan_selected_callback, pattern=r"^plan_\d+$"))
    application.add_handler(CallbackQueryHandler(renew_selected_callback, pattern=r"^renew_.+$"))
    application.add_handler(CallbackQueryHandler(add_newsub_callback, pattern=f"^{ADD_NEWSUB}$"))
    application.add_handler(CallbackQueryHandler(random_username_callback, pattern=f"^{RANDOM_USERNAME}$"))
    application.add_handler(CallbackQueryHandler(show_qrcode_callback, pattern=f"^{SHOW_QRCODE}$"))
    application.add_handler(CallbackQueryHandler(send_receipt_callback, pattern=f"^{SEND_RECEIPT}$"))
    application.add_handler(CallbackQueryHandler(approve_receipt_callback, pattern=r"^approve_receipt_.+$"))
    application.add_handler(CallbackQueryHandler(reject_receipt_callback, pattern=r"^reject_receipt_.+$"))
    application.add_handler(CallbackQueryHandler(resend_receipt_callback, pattern=r"^resend_receipt_.+$"))

    # --- Features / SubTest ---
    application.add_handler(CallbackQueryHandler(request_subtest_callback, pattern=f"^{REQUEST_SUBTEST}$"))
    application.add_handler(CallbackQueryHandler(receive_subtest_callback, pattern=f"^{RECEIVE_SUBTEST}$"))

    # --- Profile ---
    application.add_handler(CallbackQueryHandler(my_accounts_callback, pattern=f"^{MY_ACCOUNTS}$"))
    application.add_handler(CallbackQueryHandler(my_points_callback, pattern=f"^{MY_POINTS}$"))
    application.add_handler(CallbackQueryHandler(add_account_callback, pattern=f"^{ADD_ACCOUNT}$"))
    application.add_handler(CallbackQueryHandler(view_sub_callback, pattern=r"^view_sub_.+$"))

    # --- Subscription Management ---
    application.add_handler(CallbackQueryHandler(req_disable_callback, pattern=r"^req_disable_.+$"))
    application.add_handler(CallbackQueryHandler(confirm_disable_callback, pattern=r"^confirm_disable_.+$"))
    application.add_handler(CallbackQueryHandler(cancel_disable_callback, pattern=r"^cancel_disable_.+$"))
    application.add_handler(CallbackQueryHandler(done_disable_callback, pattern=r"^done_disable_.+$"))

    application.add_handler(CallbackQueryHandler(req_active_callback, pattern=r"^req_active_.+$"))
    application.add_handler(CallbackQueryHandler(confirm_active_callback, pattern=r"^confirm_active_.+$"))
    application.add_handler(CallbackQueryHandler(cancel_active_callback, pattern=r"^cancel_active_.+$"))
    application.add_handler(CallbackQueryHandler(done_active_callback, pattern=r"^done_active_.+$"))

    application.add_handler(CallbackQueryHandler(revoke_sub_callback, pattern=r"^revoke_sub_.+$"))
    application.add_handler(CallbackQueryHandler(confirm_revoke_callback, pattern=r"^confirm_revoke_.+$"))
    application.add_handler(CallbackQueryHandler(cancel_revoke_callback, pattern=r"^cancel_revoke_.+$"))

    application.add_handler(CallbackQueryHandler(delete_sub_callback, pattern=r"^delete_sub_.+$"))
    application.add_handler(CallbackQueryHandler(confirm_delete_callback, pattern=r"^confirm_delete_.+$"))
    application.add_handler(CallbackQueryHandler(cancel_delete_callback, pattern=r"^cancel_delete_.+$"))

    # --- Points ---
    application.add_handler(CallbackQueryHandler(invite_banner_callback, pattern=f"^{INVITE_BANNER}$"))
    application.add_handler(CallbackQueryHandler(convert_points_callback, pattern=f"^{CONVERT_POINTS}$"))
    application.add_handler(CallbackQueryHandler(convert_points_selected_callback, pattern=r"^convert_pts_\d+$"))
    application.add_handler(CallbackQueryHandler(convert_all_points_callback, pattern=f"^{CONVERT_ALL_POINTS}$"))

    # --- Support ---
    application.add_handler(CallbackQueryHandler(reply_user_callback, pattern=r"^reply_user_.+$"))
    application.add_handler(CallbackQueryHandler(reply_admin_callback, pattern=r"^reply_admin_.+$"))
    application.add_handler(CallbackQueryHandler(close_ticket_callback, pattern=r"^close_ticket_.+$"))

    # --- Admin Channel ---
    application.add_handler(CallbackQueryHandler(admin_send_now_callback, pattern=f"^{ADMIN_SEND_NOW}$"))
    application.add_handler(CallbackQueryHandler(admin_cancel_callback, pattern=f"^{ADMIN_CANCEL}$"))
    application.add_handler(CallbackQueryHandler(admin_add_buttons_callback, pattern=f"^{ADMIN_ADD_BUTTONS}$"))

    # --- GO_BUY callback ---
    async def go_buy_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        from handlers.buy import show_plans
        await show_plans(query, context)

    application.add_handler(CallbackQueryHandler(go_buy_cb, pattern=f"^{GO_BUY}$"))

    # ==========================================
    # Message Handler (یکپارچه)
    # ==========================================
    application.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VIDEO_NOTE | filters.Document.ALL,
        universal_message_handler
    ))

    # ==========================================
    # Job Queue - بررسی اشتراک‌های تست منقضی شده
    # ==========================================
    job_queue = application.job_queue
    job_queue.run_repeating(
        check_expired_subtests,
        interval=1800,  # هر 30 دقیقه
        first=60        # اولین اجرا 60 ثانیه بعد از شروع
    )

    # ==========================================
    # راه‌اندازی
    # ==========================================
    logger.info("Starting Persian Tunnel Bot...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
