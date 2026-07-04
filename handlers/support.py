# =============================================
# handlers/support.py
# هندلر بخش پشتیبانی
# =============================================

import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_ID
from keyboards import support_reply_keyboard, user_reply_keyboard, go_back_keyboard
from texts import (
    SUPPORT_TEXT, TICKET_CLOSED_TEXT, TICKET_CLOSED_ADMIN_TEXT,
    user_support_text, admin_support_text
)
from services.user import generate_ticket_id, get_full_name
import database as db

logger = logging.getLogger(__name__)


async def support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه پشتیبانی"""
    user = update.effective_user
    message = update.effective_message

    db.set_state(user.id, "support_waiting", None)

    await message.reply_text(
        SUPPORT_TEXT,
        parse_mode="HTML"
    )


async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    پردازش پیام پشتیبانی کاربر
    Returns: True اگر پیام مربوط به پشتیبانی بود
    """
    user = update.effective_user
    message = update.effective_message
    state_data = db.get_state(user.id)

    if not state_data or state_data.get("state") != "support_waiting":
        return False

    # ایجاد تیکت
    ticket_id = generate_ticket_id()
    db.create_ticket(ticket_id, user.id)
    db.set_state(user.id, "support_open", ticket_id)

    full_name = get_full_name(user)
    username = user.username

    # تشخیص نوع پیام
    ticket_message = ""
    if message.text:
        ticket_message = message.text
    elif message.caption:
        ticket_message = message.caption
    else:
        ticket_message = "[محتوای غیر متنی]"

    # ارسال پیام ادمین
    admin_text = admin_support_text(
        full_name, username, user.id, ticket_id, ticket_message
    )

    if message.text:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            reply_markup=support_reply_keyboard(ticket_id),
            parse_mode="HTML"
        )
    elif message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=admin_text,
            reply_markup=support_reply_keyboard(ticket_id),
            parse_mode="HTML"
        )
    elif message.video:
        await context.bot.send_video(
            chat_id=ADMIN_ID,
            video=message.video.file_id,
            caption=admin_text,
            reply_markup=support_reply_keyboard(ticket_id),
            parse_mode="HTML"
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            reply_markup=support_reply_keyboard(ticket_id),
            parse_mode="HTML"
        )
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=user.id,
            message_id=message.message_id
        )

    await message.reply_text(
        "✅ پیام شما برای پشتیبانی ارسال شد. منتظر پاسخ باشید."
    )
    return True


async def reply_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه پاسخ به کاربر (ادمین)"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    ticket_id = query.data.replace("reply_user_", "")
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        await query.answer("تیکت یافت نشد!", show_alert=True)
        return

    # ذخیره state ادمین
    db.set_state(ADMIN_ID, "support_reply_to_user", ticket_id)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"✏️ پیام خود را با <b>ریپلای</b> روی این پیام ارسال کنید.\n🎫 تیکت: <code>{ticket_id}</code>",
        parse_mode="HTML"
    )


async def reply_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه پاسخ به ادمین (کاربر)"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    ticket_id = query.data.replace("reply_admin_", "")

    ticket = db.get_ticket(ticket_id)
    if not ticket or ticket["status"] == "closed":
        await query.answer("این تیکت بسته شده است.", show_alert=True)
        return

    db.set_state(user.id, "support_waiting", ticket_id)
    await context.bot.send_message(
        chat_id=user.id,
        text="✏️ پیام خود را ارسال کنید:"
    )


async def close_ticket_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر بستن تیکت"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    ticket_id = query.data.replace("close_ticket_", "")

    ticket = db.get_ticket(ticket_id)
    if not ticket:
        await query.answer("تیکت یافت نشد!", show_alert=True)
        return

    db.close_ticket(ticket_id)
    db.clear_state(ticket["user_id"])

    await query.message.edit_reply_markup(reply_markup=None)

    if user.id == ADMIN_ID:
        # ادمین تیکت رو بست
        await query.answer("✅ تیکت بسته شد.")
        await context.bot.send_message(
            chat_id=ticket["user_id"],
            text=TICKET_CLOSED_TEXT,
            parse_mode="HTML"
        )
    else:
        # کاربر تیکت رو بست
        await query.answer("✅ تیکت بسته شد.")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"{TICKET_CLOSED_ADMIN_TEXT}\n🎫 شماره تیکت: <code>{ticket_id}</code>",
            parse_mode="HTML"
        )


async def handle_admin_support_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    پردازش پاسخ ادمین به تیکت
    """
    user = update.effective_user
    message = update.effective_message

    if user.id != ADMIN_ID:
        return False

    state_data = db.get_state(ADMIN_ID)
    if not state_data or state_data.get("state") != "support_reply_to_user":
        return False

    ticket_id = state_data.get("data", "")
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        return False

    target_user_id = ticket["user_id"]

    admin_message = ""
    if message.reply_to_message and message.reply_to_message.text:
        # ادمین با ریپلای پاسخ داد
        admin_message = message.text or message.caption or ""
    elif message.text:
        admin_message = message.text
    else:
        return False

    # ارسال پاسخ به کاربر
    await context.bot.send_message(
        chat_id=target_user_id,
        text=user_support_text(ticket_id, admin_message),
        reply_markup=user_reply_keyboard(ticket_id),
        parse_mode="HTML"
    )

    db.clear_state(ADMIN_ID)
    await message.reply_text(f"✅ پاسخ به کاربر ارسال شد.")
    return True
