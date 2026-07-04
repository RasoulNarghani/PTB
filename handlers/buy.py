# =============================================
# handlers/buy.py
# هندلر بخش خرید اشتراک
# =============================================

import json
import logging
import os
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

from config import PLANS, ADMIN_ID, CARD_NUMBER
from keyboards import (
    plans_keyboard, random_username_keyboard, renew_keyboard,
    wallets_keyboard, receipt_review_keyboard, subscription_keyboard,
    resend_receipt_keyboard, go_back_keyboard
)
from texts import (
    PLANS_TEXT, INVALID_ID_TEXT, QRCODE_TEXT,
    VALID_RECEIPT_TEXT, VIDEO_RECEIPT_TEXT, INVALID_RECEIPT_TEXT,
    ADMIN_SEND_REASON_TEXT,
    user_new_text, user_renew_text, user_taken_id_text, user_order_details_text,
    user_send_receipt_text, user_send_card_text,
    admin_newsub_receipt_text, admin_newsub_approve_text,
    admin_renewsub_receipt_text, user_send_newsub_text,
    user_send_renewsub_text, user_reject_receipt_text,
)
from services.user import is_valid_username, generate_order_id, get_full_name
from services.subscription import (
    fetch_subscription_info, validate_subscription_link,
    calculate_prices, format_subscription_list
)
from services.points import process_new_buy
import database as db

logger = logging.getLogger(__name__)


async def show_plans(query_or_update, context: ContextTypes.DEFAULT_TYPE, from_message=False):
    """نمایش پلن‌های خرید"""
    if from_message:
        msg = query_or_update.effective_message
        db.clear_state(query_or_update.effective_user.id)
        await msg.reply_text(
            PLANS_TEXT,
            reply_markup=plans_keyboard(PLANS),
            parse_mode="HTML"
        )
    else:
        query = query_or_update
        db.clear_state(query.from_user.id)
        await query.message.edit_text(
            PLANS_TEXT,
            reply_markup=plans_keyboard(PLANS),
            parse_mode="HTML"
        )


async def buy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه خرید اشتراک (reply keyboard)"""
    await show_plans(update, context, from_message=True)


async def plan_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر انتخاب پلن"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    volume = int(query.data.replace("plan_", ""))
    price = PLANS.get(volume)
    if not price:
        await query.answer("پلن نامعتبر!", show_alert=True)
        return

    # بررسی اشتراک‌های قبلی
    existing_subs = db.get_user_active_subscriptions(user.id)

    db.set_state(user.id, "buy_plan", json.dumps({
        "volume": volume,
        "price": price
    }))

    if existing_subs:
        # کاربر اشتراک داشت - نمایش لیست برای تمدید
        db.set_state(user.id, "buy_renew", json.dumps({
            "volume": volume,
            "price": price
        }))
        await query.message.edit_text(
            user_renew_text(volume),
            reply_markup=renew_keyboard(existing_subs),
            parse_mode="HTML"
        )
    else:
        # اشتراک جدید - درخواست نام کاربری
        db.set_state(user.id, "buy_username", json.dumps({
            "volume": volume,
            "price": price,
            "order_type": "new"
        }))
        await query.message.edit_text(
            user_new_text(volume),
            reply_markup=random_username_keyboard(),
            parse_mode="HTML"
        )


async def renew_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر انتخاب اشتراک برای تمدید"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    sub_username = query.data.replace("renew_", "")
    state_data = db.get_state(user.id)

    if not state_data:
        await query.answer("خطا! لطفاً دوباره تلاش کنید.", show_alert=True)
        return

    data = json.loads(state_data.get("data", "{}"))
    volume = data.get("volume")
    price = data.get("price")

    # ذخیره اطلاعات سفارش
    db.set_state(user.id, "buy_payment", json.dumps({
        "volume": volume,
        "price": price,
        "order_type": "renew",
        "sub_username": sub_username
    }))

    # نمایش جزئیات سفارش
    prices_db = db.get_prices()
    crypto_prices = calculate_prices(price, prices_db)

    await query.message.edit_text(
        user_order_details_text(
            sub_username, volume, price,
            crypto_prices["usdt"], crypto_prices["gram"], crypto_prices["trx"]
        ),
        reply_markup=wallets_keyboard(),
        parse_mode="HTML"
    )


async def add_newsub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه افزودن اشتراک جدید (از صفحه تمدید)"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    state_data = db.get_state(user.id)
    if not state_data:
        await query.answer("خطا!", show_alert=True)
        return

    data = json.loads(state_data.get("data", "{}"))
    volume = data.get("volume")
    price = data.get("price")

    db.set_state(user.id, "buy_username", json.dumps({
        "volume": volume,
        "price": price,
        "order_type": "new"
    }))

    await query.message.edit_text(
        user_new_text(volume),
        reply_markup=random_username_keyboard(),
        parse_mode="HTML"
    )


async def random_username_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه نام کاربری رندوم"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    import random
    import string
    random_name = "PT_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))

    state_data = db.get_state(user.id)
    if not state_data:
        return

    data = json.loads(state_data.get("data", "{}"))
    volume = data.get("volume")
    price = data.get("price")

    # ذخیره نام کاربری رندوم
    db.set_state(user.id, "buy_payment", json.dumps({
        "volume": volume,
        "price": price,
        "order_type": "new",
        "sub_username": random_name + "_[رندوم]"
    }))

    prices_db = db.get_prices()
    crypto_prices = calculate_prices(price, prices_db)

    display_name = f"{random_name} (رندوم - ادمین انتخاب میکند)"

    await query.message.edit_text(
        user_order_details_text(
            display_name, volume, price,
            crypto_prices["usdt"], crypto_prices["gram"], crypto_prices["trx"]
        ),
        reply_markup=wallets_keyboard(),
        parse_mode="HTML"
    )


async def handle_username_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    پردازش ورودی نام کاربری
    Returns: True اگر پیام مربوط به نام کاربری بود
    """
    user = update.effective_user
    message = update.effective_message
    state_data = db.get_state(user.id)

    if not state_data or state_data.get("state") != "buy_username":
        return False

    if not message.text:
        return False

    # بررسی آپشن مخفی شماره کارت
    if message.text.strip() == "شماره کارت":
        await message.reply_text(
            user_send_card_text(),
            parse_mode="HTML"
        )
        return True

    username = message.text.strip()
    data = json.loads(state_data.get("data", "{}"))
    volume = data.get("volume")
    price = data.get("price")

    # اعتبارسنجی نام کاربری
    if not is_valid_username(username):
        await message.reply_text(
            INVALID_ID_TEXT,
            reply_markup=random_username_keyboard(),
            parse_mode="HTML"
        )
        return True

    # بررسی تکراری بودن
    if db.username_exists(username):
        await message.reply_text(
            user_taken_id_text(username),
            reply_markup=random_username_keyboard(),
            parse_mode="HTML"
        )
        return True

    # ذخیره و نمایش جزئیات
    db.set_state(user.id, "buy_payment", json.dumps({
        "volume": volume,
        "price": price,
        "order_type": "new",
        "sub_username": username
    }))

    prices_db = db.get_prices()
    crypto_prices = calculate_prices(price, prices_db)

    await message.reply_text(
        user_order_details_text(
            username, volume, price,
            crypto_prices["usdt"], crypto_prices["gram"], crypto_prices["trx"]
        ),
        reply_markup=wallets_keyboard(),
        parse_mode="HTML"
    )
    return True


async def show_qrcode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش QR کدهای ولت‌ها"""
    query = update.callback_query
    await query.answer()

    assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

    qr_files = [
        ("qr_ton_wallet.jpg", "TON"),
        ("qr_trx_wallet.jpg", "TRC20"),
    ]

    media_group = []
    for i, (filename, label) in enumerate(qr_files):
        filepath = os.path.join(assets_path, filename)
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                caption = QRCODE_TEXT if i == 0 else label
                media_group.append(InputMediaPhoto(f.read(), caption=caption if i == 0 else ""))

    if media_group:
        await context.bot.send_media_group(
            chat_id=query.from_user.id,
            media=media_group
        )
    else:
        await query.answer("فایل‌های QR یافت نشد. لطفاً با پشتیبانی تماس بگیرید.", show_alert=True)


async def send_receipt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه ارسال رسید"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    state_data = db.get_state(user.id)
    if not state_data:
        return

    data = json.loads(state_data.get("data", "{}"))
    volume = data.get("volume")
    price = data.get("price")
    sub_username = data.get("sub_username", "")

    db.set_state(user.id, "buy_receipt", json.dumps(data))

    await context.bot.send_message(
        chat_id=user.id,
        text=user_send_receipt_text(sub_username, volume, price),
        parse_mode="HTML"
    )


async def handle_receipt_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """پردازش رسید ارسال شده توسط کاربر"""
    user = update.effective_user
    message = update.effective_message
    state_data = db.get_state(user.id)

    if not state_data or state_data.get("state") != "buy_receipt":
        return False

    data = json.loads(state_data.get("data", "{}"))
    volume = data.get("volume")
    price = data.get("price")
    sub_username = data.get("sub_username", "")
    order_type = data.get("order_type", "new")

    # تشخیص نوع رسید
    receipt_type = None
    receipt_file_id = None
    is_video = False

    if message.photo:
        receipt_type = "photo"
        receipt_file_id = message.photo[-1].file_id
    elif message.text:
        receipt_type = "text"
        receipt_file_id = message.text
    elif message.video or message.video_note:
        receipt_type = "video"
        is_video = True
        if message.video:
            receipt_file_id = message.video.file_id
        else:
            receipt_file_id = message.video_note.file_id
    else:
        await message.reply_text(
            INVALID_RECEIPT_TEXT,
            parse_mode="HTML"
        )
        return True

    # ایجاد سفارش
    order_id = generate_order_id()
    db.create_order(order_id, user.id, sub_username, volume, order_type)
    db.update_order_receipt(order_id, receipt_file_id, receipt_type)

    # پیام تایید به کاربر
    if is_video:
        await message.reply_text(VIDEO_RECEIPT_TEXT, parse_mode="HTML")
    else:
        await message.reply_text(VALID_RECEIPT_TEXT, parse_mode="HTML")

    # ارسال به ادمین
    full_name = get_full_name(user)
    username = user.username

    if order_type == "new":
        admin_text = admin_newsub_receipt_text(
            order_id, full_name, username, user.id, sub_username, volume
        )
    else:
        admin_text = admin_renewsub_receipt_text(
            order_id, full_name, username, user.id, sub_username, volume
        )

    # ارسال رسید به ادمین
    if receipt_type == "photo":
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=receipt_file_id,
            caption=admin_text,
            reply_markup=receipt_review_keyboard(order_id),
            parse_mode="HTML"
        )
    elif receipt_type == "video":
        await context.bot.send_video(
            chat_id=ADMIN_ID,
            video=receipt_file_id,
            caption=admin_text,
            reply_markup=receipt_review_keyboard(order_id),
            parse_mode="HTML"
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text + f"\n\n📝 رسید:\n{receipt_file_id}",
            reply_markup=receipt_review_keyboard(order_id),
            parse_mode="HTML"
        )

    db.set_state(user.id, "waiting_approval", json.dumps({
        **data,
        "order_id": order_id
    }))
    return True


async def approve_receipt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر تایید رسید توسط ادمین"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("شما مجاز به این عملیات نیستید!", show_alert=True)
        return

    order_id = query.data.replace("approve_receipt_", "")
    order = db.get_order(order_id)

    if not order:
        await query.answer("سفارش یافت نشد!", show_alert=True)
        return

    db.update_order_status(order_id, "approved")
    user_db = db.get_user(order["user_id"])
    full_name = f"{user_db['first_name'] or ''} {user_db['last_name'] or ''}".strip()

    if order["order_type"] == "new":
        # ادمین باید لینک اشتراک ارسال کنه
        approve_text = admin_newsub_approve_text(
            order_id, full_name, user_db.get("username"),
            order["user_id"], order["sub_total_volume"],
            order["sub_username"]
        )
        sent_msg = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=approve_text,
            parse_mode="HTML"
        )
        # ذخیره message_id برای reply detection
        context.bot_data[f"approve_msg_{sent_msg.message_id}"] = {
            "order_id": order_id,
            "user_id": order["user_id"],
            "sub_username": order["sub_username"],
            "volume": order["sub_total_volume"],
            "type": "new"
        }
        await query.message.edit_reply_markup(reply_markup=None)

    else:
        # تمدید - لینک از قبل موجوده
        sub = db.get_subscription_by_username(order["sub_username"])
        sub_link = sub["sub_link"] if sub else ""

        await context.bot.send_message(
            chat_id=order["user_id"],
            text=user_send_renewsub_text(
                order["sub_username"], order["sub_total_volume"]
            ),
            reply_markup=subscription_keyboard(sub_link) if sub_link else None,
            parse_mode="HTML"
        )
        # اعطای امتیاز
        await process_new_buy(order["user_id"], order["sub_total_volume"], context)
        await query.message.edit_reply_markup(reply_markup=None)
        await query.answer("✅ سفارش تمدید تایید و به کاربر اطلاع داده شد.")


async def reject_receipt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر رد رسید توسط ادمین"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("شما مجاز به این عملیات نیستید!", show_alert=True)
        return

    order_id = query.data.replace("reject_receipt_", "")
    db.update_order_status(order_id, "rejected")

    # درخواست دلیل رد از ادمین
    sent_msg = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=ADMIN_SEND_REASON_TEXT,
        parse_mode="HTML"
    )
    context.bot_data[f"reject_reason_{sent_msg.message_id}"] = {
        "order_id": order_id
    }
    await query.message.edit_reply_markup(reply_markup=None)


async def resend_receipt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر ارسال مجدد رسید"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    order_id = query.data.replace("resend_receipt_", "")
    order = db.get_order(order_id)

    if not order:
        return

    db.set_state(user.id, "buy_receipt", json.dumps({
        "volume": order["sub_total_volume"],
        "price": db.get_plan_price_from_order(order_id) or 0,
        "order_type": order["order_type"],
        "sub_username": order["sub_username"]
    }))

    await query.message.edit_text(
        user_send_receipt_text(
            order["sub_username"],
            order["sub_total_volume"],
            0
        ),
        parse_mode="HTML"
    )


async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    پردازش ریپلای ادمین - چه لینک اشتراک، چه دلیل رد
    Returns: True اگر پیام توسط این هندلر پردازش شد
    """
    user = update.effective_user
    message = update.effective_message

    if user.id != ADMIN_ID:
        return False

    if not message.reply_to_message:
        return False

    replied_msg_id = message.reply_to_message.message_id

    # بررسی تایید سفارش جدید
    approve_key = f"approve_msg_{replied_msg_id}"
    if approve_key in context.bot_data:
        order_data = context.bot_data.pop(approve_key)
        order_id = order_data["order_id"]
        user_id = order_data["user_id"]
        sub_username = order_data["sub_username"]
        volume = order_data["volume"]

        sub_link = message.text.strip() if message.text else ""

        if not sub_link or not validate_subscription_link(sub_link):
            await message.reply_text("⚠️ لینک اشتراک معتبر نیست!")
            # ذخیره مجدد برای retry
            context.bot_data[approve_key] = order_data
            return True

        # دریافت اطلاعات اشتراک از API
        sub_info = await fetch_subscription_info(sub_link)
        if not sub_info:
            await message.reply_text("⚠️ خطا در خواندن اطلاعات اشتراک! لینک را بررسی کنید.")
            context.bot_data[approve_key] = order_data
            return True

        # ثبت اشتراک در دیتابیس
        user_db = db.get_user(user_id)
        is_first = not db.has_bought_before(user_id)

        db.add_subscription(
            user_id=user_id,
            sub_username=sub_username if not sub_username.endswith("[رندوم]") else sub_info["sub_username"],
            sub_link=sub_link,
            sub_type="normal",
            sub_total_volume=sub_info["sub_total_volume"],
            sub_used_volume=sub_info["sub_used_volume"],
            sub_created_at=sub_info["sub_created_at"]
        )

        # ارسال لینک به کاربر
        await context.bot.send_message(
            chat_id=user_id,
            text=user_send_newsub_text(sub_username, volume),
            reply_markup=subscription_keyboard(sub_link),
            parse_mode="HTML"
        )

        # اعطای امتیاز
        await process_new_buy(user_id, volume, context)

        await message.reply_text(f"✅ اشتراک {sub_username} به کاربر ارسال شد.")
        return True

    # بررسی دلیل رد
    reject_key = f"reject_reason_{replied_msg_id}"
    if reject_key in context.bot_data:
        order_data = context.bot_data.pop(reject_key)
        order_id = order_data["order_id"]

        order = db.get_order(order_id)
        if not order:
            return True

        reason = message.text.strip() if message.text else "توضیح داده نشد."

        # ارسال به کاربر
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=user_reject_receipt_text(reason),
            reply_markup=resend_receipt_keyboard(order_id),
            parse_mode="HTML"
        )
        await message.reply_text("✅ دلیل رد به کاربر ارسال شد.")
        return True

    return False
