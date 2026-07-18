# =============================================
# handlers/admin.py
# هندلرهای دستورات ادمین
# =============================================

import logging
import os
import sqlite3
import shutil

from datetime import datetime
from database import DB_PATH

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import ADMIN_ID, CHANNEL_ID
from keyboards import admin_message_channel_keyboard, admin_user_panel_keyboard
from texts import (
    ADMIN_MESSAGE_CHANNEL, ADMIN_URL_BUTTON,
    admin_price_text, admin_user_list_text, admin_user_detail_text,
    admin_message_confirm_text, admin_message_sent_text
)
import database as db

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ==========================================
# دستور /price
# ==========================================

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت قیمت ارزها"""
    if not is_admin(update.effective_user.id):
        return

    args = context.args

    if not args:
        # نمایش قیمت‌های فعلی
        prices = db.get_prices()
        await update.message.reply_text(
            admin_price_text(prices),
            parse_mode="HTML"
        )
        return

    if len(args) < 2:
        await update.message.reply_text(
            "📌 نحوه استفاده:\n"
            "/price usdt 175000\n"
            "/price trx 57000\n"
            "/price gram 297000\n"
            "/price not 70"
        )
        return

    currency = args[0].lower()
    if currency not in ["usdt", "trx", "gram", "not"]:
        await update.message.reply_text("❌ ارز نامعتبر! (usdt, trx, gram, not)")
        return

    try:
        price = int(args[1])
    except ValueError:
        await update.message.reply_text("❌ قیمت باید عدد صحیح باشد!")
        return

    db.update_price(currency, price)

    currency_names = {
        "usdt": "USDT (تتر)",
        "trx": "TRX (ترون)",
        "gram": "Gram (گرام)",
        "not": "NOT (ناتکوین)"
    }

    await update.message.reply_text(
        f"✅ قیمت {currency_names.get(currency, currency)} به "
        f"<b>{price:,} تومان</b> بروزرسانی شد.",
        parse_mode="HTML"
    )


# ==========================================
# دستور /user
# ==========================================

async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کاربران"""
    if not is_admin(update.effective_user.id):
        return

    args = context.args

    if not args:
        await update.message.reply_text(
            "📌 نحوه استفاده:\n"
            "/user all - لیست همه کاربران\n"
            "/user 123456789 - جزئیات کاربر"
        )
        return

    if args[0] == "all":
        users = db.get_all_users()
        text = admin_user_list_text(users)
        # ارسال پیام‌های تقسیم شده (Telegram limit: 4096 chars)
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode="HTML")
        return

    try:
        user_id = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ آیدی عددی نامعتبر!")
        return

    user_data = db.get_user(user_id)
    if not user_data:
        await update.message.reply_text(f"❌ کاربر با آیدی {user_id} یافت نشد!")
        return

    subscriptions = db.get_user_subscriptions(user_id)
    invites = db.get_invited_users(user_id)
    inviter = db.get_inviter(user_id)

    text = admin_user_detail_text(user_data, subscriptions, invites, inviter)
    await update.message.reply_text(
        text, parse_mode="HTML",
        reply_markup=admin_user_panel_keyboard(user_id)
    )


# ==========================================
# دستور /message
# ==========================================

async def message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام به کاربران"""
    if not is_admin(update.effective_user.id):
        return

    args = context.args

    if not args:
        await update.message.reply_text(
            "📌 نحوه استفاده:\n"
            "/message all - ارسال به همه\n"
            "/message 123456789 - ارسال به یک نفر\n"
            "/message 123 456 789 - ارسال به چند نفر"
        )
        return

    if args[0] == "all":
        target = "همه کاربران"
        db.set_state(ADMIN_ID, "admin_message_all", "all")
    else:
        try:
            user_ids = [int(a) for a in args]
            target = ", ".join(str(uid) for uid in user_ids)
            import json
            db.set_state(ADMIN_ID, "admin_message_users", json.dumps(user_ids))
        except ValueError:
            await update.message.reply_text("❌ آیدی‌های عددی نامعتبر!")
            return

    sent = await update.message.reply_text(
        admin_message_confirm_text(target),
        parse_mode="HTML"
    )
    context.bot_data[f"admin_msg_confirm_{sent.message_id}"] = True


async def handle_admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """پردازش پیام برادکست ادمین"""
    user = update.effective_user
    message = update.effective_message

    if user.id != ADMIN_ID:
        return False

    state_data = db.get_state(ADMIN_ID)
    if not state_data:
        return False

    state = state_data.get("state", "")
    if not state.startswith("admin_message"):
        return False

    if not message.reply_to_message:
        return False

    replied_id = message.reply_to_message.message_id
    if f"admin_msg_confirm_{replied_id}" not in context.bot_data:
        return False

    context.bot_data.pop(f"admin_msg_confirm_{replied_id}", None)

    if state == "admin_message_all":
        users = db.get_all_users()
        target_ids = [u["user_id"] for u in users]
    else:
        import json
        target_ids = json.loads(state_data.get("data", "[]"))

    sent_count = 0
    for uid in target_ids:
        try:
            if message.text:
                await context.bot.send_message(
                    chat_id=uid,
                    text=message.text,
                    parse_mode="HTML"
                )
            elif message.photo:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=message.photo[-1].file_id,
                    caption=message.caption or ""
                )
            elif message.video:
                await context.bot.send_video(
                    chat_id=uid,
                    video=message.video.file_id,
                    caption=message.caption or ""
                )
            elif message.document:
                await context.bot.send_document(
                    chat_id=uid,
                    document=message.document.file_id,
                    caption=message.caption or ""
                )
            else:
                await context.bot.forward_message(
                    chat_id=uid,
                    from_chat_id=user.id,
                    message_id=message.message_id
                )
            sent_count += 1
        except Exception as e:
            logger.error(f"Error broadcasting to {uid}: {e}")

    db.clear_state(ADMIN_ID)
    await message.reply_text(admin_message_sent_text(sent_count), parse_mode="HTML")
    return True


# ==========================================
# دستور /channel
# ==========================================

async def channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام به کانال"""
    if not is_admin(update.effective_user.id):
        return

    sent = await update.message.reply_text(
        ADMIN_MESSAGE_CHANNEL,
        parse_mode="HTML"
    )
    db.set_state(ADMIN_ID, "admin_channel_waiting", None)
    context.bot_data["channel_waiting_msg"] = sent.message_id


async def handle_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """پردازش پیام کانال"""
    user = update.effective_user
    message = update.effective_message

    if user.id != ADMIN_ID:
        return False

    state_data = db.get_state(ADMIN_ID)
    if not state_data:
        return False

    state = state_data.get("state", "")

    if state == "admin_channel_waiting":
        if not message.reply_to_message:
            return False

        # ذخیره محتوای پیام
        db.set_state(ADMIN_ID, "admin_channel_review", None)

        import json
        msg_info = {
            "text": message.text or "",
            "caption": message.caption or "",
            "photo": message.photo[-1].file_id if message.photo else None,
            "video": message.video.file_id if message.video else None,
            "document": message.document.file_id if message.document else None,
            "type": (
                "photo" if message.photo else
                "video" if message.video else
                "document" if message.document else
                "text"
            )
        }
        context.bot_data["pending_channel_msg"] = msg_info

        # نمایش پیش‌نمایش + دکمه‌ها
        await _send_channel_preview(context.bot, ADMIN_ID, msg_info, None)
        return True

    if state == "admin_channel_url_waiting":
        if not message.reply_to_message:
            return False

        # پارس دکمه‌های URL
        buttons = parse_url_buttons(message.text or "")
        if not buttons:
            await message.reply_text("❌ فرمت دکمه‌ها نامعتبر است!")
            return True

        msg_info = context.bot_data.get("pending_channel_msg", {})
        context.bot_data["pending_channel_buttons"] = buttons
        db.set_state(ADMIN_ID, "admin_channel_review", None)

        # نمایش پیش‌نمایش با دکمه‌ها
        await _send_channel_preview(context.bot, ADMIN_ID, msg_info, buttons)
        return True

    return False


async def _send_channel_preview(bot, admin_id: int, msg_info: dict, buttons: list):
    """نمایش پیش‌نمایش پیام کانال"""
    # ساخت کیبورد
    keyboard_rows = []
    if buttons:
        for row in buttons:
            keyboard_rows.append([
                InlineKeyboardButton(btn["text"], url=btn["url"])
                for btn in row
            ])

    # اضافه کردن دکمه‌های ادمین
    keyboard_rows.append([
        InlineKeyboardButton("ارسال الان 📤", callback_data="admin_send_now"),
        InlineKeyboardButton("انصراف ❌", callback_data="admin_cancel")
    ])
    if not buttons:
        keyboard_rows.insert(0, [
            InlineKeyboardButton("افزودن دکمه URL ➕", callback_data="admin_add_buttons")
        ])

    reply_markup = InlineKeyboardMarkup(keyboard_rows)

    msg_type = msg_info.get("type", "text")

    if msg_type == "photo":
        await bot.send_photo(
            chat_id=admin_id,
            photo=msg_info["photo"],
            caption=msg_info.get("caption", ""),
            reply_markup=reply_markup
        )
    elif msg_type == "video":
        await bot.send_video(
            chat_id=admin_id,
            video=msg_info["video"],
            caption=msg_info.get("caption", ""),
            reply_markup=reply_markup
        )
    else:
        await bot.send_message(
            chat_id=admin_id,
            text=msg_info.get("text", ""),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


async def admin_send_now_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام به کانال"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    msg_info = context.bot_data.get("pending_channel_msg", {})
    buttons = context.bot_data.get("pending_channel_buttons", [])

    # ساخت کیبورد کانال
    keyboard_rows = []
    for row in buttons:
        keyboard_rows.append([
            InlineKeyboardButton(btn["text"], url=btn["url"])
            for btn in row
        ])
    reply_markup = InlineKeyboardMarkup(keyboard_rows) if keyboard_rows else None

    msg_type = msg_info.get("type", "text")

    try:
        if msg_type == "photo":
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=msg_info["photo"],
                caption=msg_info.get("caption", ""),
                reply_markup=reply_markup
            )
        elif msg_type == "video":
            await context.bot.send_video(
                chat_id=CHANNEL_ID,
                video=msg_info["video"],
                caption=msg_info.get("caption", ""),
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=msg_info.get("text", ""),
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        await query.message.edit_reply_markup(reply_markup=None)
        await query.answer("✅ پیام در کانال ارسال شد!")

    except Exception as e:
        logger.error(f"Error sending to channel: {e}")
        await query.answer(f"❌ خطا: {str(e)}", show_alert=True)

    # پاکسازی
    context.bot_data.pop("pending_channel_msg", None)
    context.bot_data.pop("pending_channel_buttons", None)
    db.clear_state(ADMIN_ID)


async def admin_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انصراف از ارسال پیام کانال"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    context.bot_data.pop("pending_channel_msg", None)
    context.bot_data.pop("pending_channel_buttons", None)
    db.clear_state(ADMIN_ID)

    await query.message.delete()
    await query.answer("❌ عملیات لغو شد.")


async def admin_add_buttons_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه افزودن دکمه‌های URL"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    db.set_state(ADMIN_ID, "admin_channel_url_waiting", None)
    await query.message.delete()

    sent = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=ADMIN_URL_BUTTON,
        parse_mode="HTML"
    )
    context.bot_data["url_button_msg"] = sent.message_id


def parse_url_buttons(text: str) -> list:
    """
    پارس دکمه‌های URL از متن ادمین
    فرمت: Button text - http://url | Button text 2 - http://url2
           Button text 3 - http://url3
    """
    rows = []
    lines = text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        row = []
        buttons_raw = line.split("|")
        for btn_raw in buttons_raw[:3]:  # حداکثر 3 دکمه در یک ردیف
            btn_raw = btn_raw.strip()
            parts = btn_raw.split(" - ")
            if len(parts) >= 2:
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                if btn_text and btn_url.startswith("http"):
                    row.append({"text": btn_text, "url": btn_url})

        if row:
            rows.append(row)

    return rows



import json as _json

ADMINP_PROMPTS = {
    "msg": "✉️ متن پیامی که می‌خوای برای این کاربر ارسال بشه رو بفرست:",
    "points": "🏆 به این فرمت ریپلای کن:\nfield مقدار\nمثال: unused_points 500\n(فیلدها: total_points, unused_points, invite_points, buy_points)",
    "setinviter": "👤 آیدی عددی کسی که این کاربر توسط اون دعوت شده رو بفرست:",
    "setinvited": "👥 یک یا چند آیدی عددی (با فاصله) از کسانی که این کاربر دعوتشون کرده رو بفرست:",
    "subs": "📦 یکی از این حالت‌ها رو بفرست:\nadd USERNAME LINK\nedit USERNAME NEW_LINK\ndelete USERNAME",
    "subtest": "⏱ یکی از این‌ها رو بفرست:\nallow - مجاز به دریافت اشتراک تست\nblock - غیرمجاز کردن\nusedmark - ثبت دستی اینکه قبلا گرفته\nreset - آزاد کردن دوباره امکان دریافت",
}

async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return

    _, action, target_id = query.data.split("_", 2)
    target_id = int(target_id)

    sent = await query.message.reply_text(ADMINP_PROMPTS[action])
    db.set_state(ADMIN_ID, f"adminp_{action}", _json.dumps({"target": target_id}))
    context.bot_data[f"adminp_wait_{sent.message_id}"] = True


async def handle_admin_panel_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    message = update.effective_message
    if user.id != ADMIN_ID or not message.reply_to_message:
        return False

    replied_id = message.reply_to_message.message_id
    if f"adminp_wait_{replied_id}" not in context.bot_data:
        return False

    state_data = db.get_state(ADMIN_ID) or {}
    state = state_data.get("state", "")
    if not state.startswith("adminp_"):
        return False

    action = state.replace("adminp_", "")
    payload = _json.loads(state_data.get("data") or "{}")
    target_id = payload.get("target")
    text = (message.text or "").strip()

    try:
        if action == "msg":
            await context.bot.send_message(chat_id=target_id, text=text, parse_mode="HTML")
            await message.reply_text("✅ پیام ارسال شد.")

        elif action == "points":
            field, value = text.split()
            db.set_points_field(target_id, field, int(value))
            await message.reply_text("✅ امتیاز بروزرسانی شد.")

        elif action == "setinviter":
            db.set_inviter(target_id, int(text))
            await message.reply_text("✅ دعوت‌کننده ثبت شد.")

        elif action == "setinvited":
            ids = [int(x) for x in text.split()]
            db.set_invited_by_bulk(target_id, ids)
            await message.reply_text(f"✅ {len(ids)} کاربر به عنوان دعوت‌شده ثبت شدند.")

        elif action == "subs":
            parts = text.split()
            cmd = parts[0].lower()
            if cmd == "add":
                _, username, link = parts
                db.add_subscription(target_id, username, link, sub_type="gift")
            elif cmd == "edit":
                _, username, link = parts
                db.update_subscription_link(username, link)
            elif cmd == "delete":
                _, username = parts
                db.soft_delete_subscription(username, target_id)
            await message.reply_text("✅ انجام شد.")

        elif action == "subtest":
            cmd = text.lower()
            if cmd == "allow":
                db.set_subtest_allowed(target_id, True)
            elif cmd == "block":
                db.set_subtest_allowed(target_id, False)
            elif cmd == "usedmark":
                db.force_mark_subtest_used(target_id)
            elif cmd == "reset":
                db.clear_subtest_usage(target_id)
            await message.reply_text("✅ انجام شد.")

    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

    context.bot_data.pop(f"adminp_wait_{replied_id}", None)
    db.clear_state(ADMIN_ID)
    return True



# دیتابیس
RESTORE_TMP_PATH = "/tmp/restore_upload.db"

async def restoredb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text(
        "📤 فایل بکاپ دیتابیس (.db) رو به عنوان Document ارسال کن.\n"
        "⚠️ این کار دیتابیس فعلی رو جایگزین می‌کنه."
    )
    db.set_state(ADMIN_ID, "adminp_restoredb_wait_file", None)


async def handle_restoredb_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """پردازش فایل آپلودشده برای ریستور"""
    user = update.effective_user
    message = update.effective_message

    if user.id != ADMIN_ID:
        return False

    state_data = db.get_state(ADMIN_ID)
    if not state_data or state_data.get("state") != "adminp_restoredb_wait_file":
        return False

    if not message.document:
        return False

    # دانلود فایل
    tg_file = await context.bot.get_file(message.document.file_id)
    await tg_file.download_to_drive(RESTORE_TMP_PATH)

    # اعتبارسنجی فایل sqlite
    try:
        test_conn = sqlite3.connect(RESTORE_TMP_PATH)
        tables = [r[0] for r in test_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        test_conn.close()
        if "users" not in tables:
            raise ValueError("جدول users پیدا نشد")
    except Exception as e:
        await message.reply_text(f"❌ فایل معتبر نیست: {e}")
        os.remove(RESTORE_TMP_PATH)
        db.clear_state(ADMIN_ID)
        return True

    # نمایش تایید نهایی
    sent = await message.reply_text(
        "⚠️ آیا مطمئنی می‌خوای دیتابیس فعلی رو با این فایل جایگزین کنی؟\n"
        "قبلش یه نسخه از دیتابیس فعلی safety-backup میشه.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ بله، جایگزین کن", callback_data="admindb_confirm_restore"),
            InlineKeyboardButton("❌ انصراف", callback_data="admindb_cancel_restore"),
        ]])
    )
    db.clear_state(ADMIN_ID)
    return True


async def admindb_confirm_restore_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return

    try:
        # safety backup از دیتابیس فعلی
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safety_path = f"{DB_PATH}.before_restore_{ts}"
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, safety_path)

        # جایگزینی
        shutil.move(RESTORE_TMP_PATH, DB_PATH)

        # بروزرسانی ساختار جداول جدید (اگه بکاپ قدیمی، ستون‌های جدید رو نداشته باشه)
        db.init_db()

        await query.message.edit_text(
            f"✅ دیتابیس با موفقیت جایگزین شد.\n"
            f"🛡 نسخه‌ی قبلی به عنوان safety-backup ذخیره شد: {safety_path}"
        )
    except Exception as e:
        await query.message.edit_text(f"❌ خطا در جایگزینی: {e}")


async def admindb_cancel_restore_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return
    if os.path.exists(RESTORE_TMP_PATH):
        os.remove(RESTORE_TMP_PATH)
    await query.message.edit_text("❌ ریستور لغو شد.")