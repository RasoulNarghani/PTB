# =============================================
# handlers/profile.py
# هندلر بخش حساب کاربری
# =============================================

import json
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_ID, BASE_SUB_URL
from keyboards import (
    profile_keyboard, my_accounts_keyboard, subscription_manage_keyboard,
    points_keyboard, low_points_keyboard, convert_points_keyboard,
    go_back_keyboard, yes_no_keyboard, done_keyboard, subscription_keyboard
)
from texts import (
    NO_ACCOUNT_TEXT, MY_ACCOUNTS_TEXT, ADD_ACCOUNT_TEXT,
    UNKNOWN_LINK_TEXT, ERROR_ADDING_TEXT, CANCELLED_DISABLE_SUB_TEXT,
    CANCELLED_ACTIVE_SUB_TEXT, CANCELLED_REVOKE_SUB_TEXT, CANCELLED_DELETE_SUB_TEXT,
    REQ_SUBGIFT_TEXT,
    user_profile_text, user_added_account_text, user_sub_info_text,
    user_req_disable_sub_text, user_disable_sub_text, user_disabled_sub_text,
    user_req_active_sub_text, user_active_sub_text, user_actived_sub_text,
    user_req_revoke_sub_text, user_revoke_sub_text, user_revoked_sub_text,
    user_req_delete_sub_text, user_deleted_sub_text,
    user_points_list_text, user_low_points_text, user_convert_points_text,
    user_invite_text, user_subgift_text,
    admin_request_disable_sub_text, admin_request_active_sub_text,
    admin_request_revoke_sub_text, admin_request_create_subgift_text,
)
from services.user import get_full_name
from services.subscription import (
    fetch_subscription_info, validate_subscription_link,
    format_subscription_list
)
from services.points import (
    get_invite_link, calculate_gift_volume, build_gift_username
)
import database as db

logger = logging.getLogger(__name__)


async def show_profile(query_or_update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    """نمایش پروفایل کاربر"""
    if edit and hasattr(query_or_update, 'from_user'):
        user = query_or_update.from_user
        msg = query_or_update.message
    else:
        user = query_or_update.effective_user
        msg = query_or_update.effective_message
        edit = False

    # بروزرسانی اطلاعات اشتراک‌ها
    subscriptions = db.get_user_subscriptions(user.id)
    for sub in subscriptions:
        if sub["sub_type"] == "test":
            # بررسی انقضای اشتراک تست
            test_info = db.get_user_subtest(user.id)
            if test_info and test_info.get("is_expired"):
                continue
        # بروزرسانی از API
        info = await fetch_subscription_info(sub["sub_link"])
        if info:
            db.update_subscription_volumes(
                sub["sub_username"],
                info["sub_total_volume"],
                info["sub_used_volume"]
            )

    # دریافت اطلاعات بروز شده
    subscriptions = db.get_user_subscriptions(user.id, include_test=False)
    points_data = db.get_points(user.id) or {}
    invited_users = db.get_invited_users(user.id)

    subs_text = format_subscription_list(subscriptions) if subscriptions else NO_ACCOUNT_TEXT

    full_name = get_full_name(user)
    text = user_profile_text(
        full_name,
        user.username,
        subs_text,
        len(invited_users),
        points_data.get("total_points", 0),
        points_data.get("unused_points", 0)
    )

    db.set_state(user.id, "profile", None)

    if edit:
        await msg.edit_text(text, reply_markup=profile_keyboard(), parse_mode="HTML")
    else:
        await msg.reply_text(text, reply_markup=profile_keyboard(), parse_mode="HTML")


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه حساب کاربری من"""
    await show_profile(update, context)


# بروزرسانی اشتراک‌ها (اشتراک تست هیچ‌وقت توی این لیست نشون داده نمی‌شه)
    subscriptions = db.get_user_subscriptions(user.id)
    final_subs = [s for s in subscriptions if s["sub_type"] != "test"]

    # فیلتر اشتراک تست منقضی شده
    final_subs = []
    for sub in subscriptions:
        if sub["sub_type"] == "test":
            test_info = db.get_user_subtest(user.id)
            if test_info and not test_info.get("is_expired"):
                final_subs.append(sub)
        else:
            final_subs.append(sub)

    if not final_subs:
        await query.message.edit_text(
            NO_ACCOUNT_TEXT,
            reply_markup=go_back_keyboard(),
            parse_mode="HTML"
        )
        db.set_state(user.id, "profile_accounts", None)
        return

    db.set_state(user.id, "profile_accounts", None)
    await query.message.edit_text(
        MY_ACCOUNTS_TEXT,
        reply_markup=my_accounts_keyboard(final_subs),
        parse_mode="HTML"
    )


async def my_accounts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه اشتراک‌های من"""
    query = update.callback_query
    await query.answer()
    await show_my_accounts(query, context)


async def show_sub_detail(query, context: ContextTypes.DEFAULT_TYPE, sub_username: str):
    """نمایش جزئیات اشتراک"""
    user = query.from_user
    sub = db.get_subscription_by_username(sub_username)

    if not sub:
        await query.answer("اشتراک یافت نشد!", show_alert=True)
        return

    # بروزرسانی از API
    info = await fetch_subscription_info(sub["sub_link"])
    if info:
        db.update_subscription_volumes(
            sub_username,
            info["sub_total_volume"],
            info["sub_used_volume"]
        )
        sub = db.get_subscription_by_username(sub_username)

    is_active = sub["sub_status"] == "active"

    text = user_sub_info_text(
        sub_username=sub["sub_username"],
        sub_id=sub["id"],
        sub_status=sub["sub_status"],
        sub_created_at=sub.get("sub_created_at", "نامشخص"),
        sub_age=info["sub_age"] if info else "نامشخص",
        sub_total_volume=sub["sub_total_volume"],
        sub_used_volume=sub["sub_used_volume"],
        sub_remain_volume=sub["sub_remain_volume"]
    )

    db.set_state(user.id, "sub_manage", json.dumps({"sub_username": sub_username}))

    await query.message.edit_text(
        text,
        reply_markup=subscription_manage_keyboard(sub["sub_link"], sub_username, is_active),
        parse_mode="HTML"
    )


async def view_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر کلیک روی اشتراک در لیست"""
    query = update.callback_query
    await query.answer()
    sub_username = query.data.replace("view_sub_", "")
    await show_sub_detail(query, context, sub_username)


# ===== غیرفعال سازی =====
async def req_disable_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("req_disable_", "")

    db.set_state(user.id, "disable_confirm", json.dumps({"sub_username": sub_username}))
    await query.message.edit_text(
        user_req_disable_sub_text(sub_username),
        reply_markup=yes_no_keyboard(f"disable_{sub_username}"),
        parse_mode="HTML"
    )


async def confirm_disable_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("confirm_disable_", "")

    await query.message.edit_text(
        user_disable_sub_text(sub_username),
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )

    full_name = get_full_name(user)
    sent = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_request_disable_sub_text(full_name, user.username, user.id, sub_username),
        reply_markup=done_keyboard(f"disable_{user.id}_{sub_username}"),
        parse_mode="HTML"
    )
    db.set_state(user.id, "waiting_disable", json.dumps({"sub_username": sub_username}))


async def cancel_disable_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("cancel_disable_", "")

    await query.message.edit_text(
        CANCELLED_DISABLE_SUB_TEXT,
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )
    db.set_state(user.id, "sub_manage", json.dumps({"sub_username": sub_username}))


async def done_disable_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    parts = query.data.replace("done_disable_", "").split("_", 1)
    user_id = int(parts[0])
    sub_username = parts[1] if len(parts) > 1 else ""

    db.update_subscription_status(sub_username, "disabled")
    db.clear_state(user_id)

    await context.bot.send_message(
        chat_id=user_id,
        text=user_disabled_sub_text(sub_username),
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )
    await query.message.edit_reply_markup(reply_markup=None)
    await query.answer("✅ اشتراک غیرفعال شد.")


# ===== فعال سازی =====
async def req_active_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("req_active_", "")

    db.set_state(user.id, "active_confirm", json.dumps({"sub_username": sub_username}))
    await query.message.edit_text(
        user_req_active_sub_text(sub_username),
        reply_markup=yes_no_keyboard(f"active_{sub_username}"),
        parse_mode="HTML"
    )


async def confirm_active_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("confirm_active_", "")

    await query.message.edit_text(
        user_active_sub_text(sub_username),
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )

    full_name = get_full_name(user)
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_request_active_sub_text(full_name, user.username, user.id, sub_username),
        reply_markup=done_keyboard(f"active_{user.id}_{sub_username}"),
        parse_mode="HTML"
    )
    db.set_state(user.id, "waiting_active", json.dumps({"sub_username": sub_username}))


async def cancel_active_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("cancel_active_", "")

    await query.message.edit_text(
        CANCELLED_ACTIVE_SUB_TEXT,
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )
    db.set_state(user.id, "sub_manage", json.dumps({"sub_username": sub_username}))


async def done_active_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    parts = query.data.replace("done_active_", "").split("_", 1)
    user_id = int(parts[0])
    sub_username = parts[1] if len(parts) > 1 else ""

    db.update_subscription_status(sub_username, "active")
    db.clear_state(user_id)

    await context.bot.send_message(
        chat_id=user_id,
        text=user_actived_sub_text(sub_username),
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )
    await query.message.edit_reply_markup(reply_markup=None)
    await query.answer("✅ اشتراک فعال شد.")


# ===== تغییر لینک اشتراک =====
async def revoke_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("revoke_sub_", "")

    db.set_state(user.id, "revoke_confirm", json.dumps({"sub_username": sub_username}))
    await query.message.edit_text(
        user_req_revoke_sub_text(sub_username),
        reply_markup=yes_no_keyboard(f"revoke_{sub_username}"),
        parse_mode="HTML"
    )


async def confirm_revoke_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("confirm_revoke_", "")

    await query.message.edit_text(
        user_revoke_sub_text(sub_username),
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )

    full_name = get_full_name(user)
    sent = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_request_revoke_sub_text(full_name, user.username, user.id, sub_username),
        parse_mode="HTML"
    )
    context.bot_data[f"revoke_msg_{sent.message_id}"] = {
        "user_id": user.id,
        "sub_username": sub_username
    }
    db.set_state(user.id, "waiting_revoke", json.dumps({"sub_username": sub_username}))


async def cancel_revoke_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("cancel_revoke_", "")

    await query.message.edit_text(
        CANCELLED_REVOKE_SUB_TEXT,
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )
    db.set_state(user.id, "sub_manage", json.dumps({"sub_username": sub_username}))


# ===== حذف اشتراک =====
async def delete_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("delete_sub_", "")

    db.set_state(user.id, "delete_confirm", json.dumps({"sub_username": sub_username}))
    await query.message.edit_text(
        user_req_delete_sub_text(sub_username),
        reply_markup=yes_no_keyboard(f"delete_{sub_username}"),
        parse_mode="HTML"
    )


async def confirm_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("confirm_delete_", "")

    db.soft_delete_subscription(sub_username, user.id)
    db.set_state(user.id, "profile", None)

    await query.message.edit_text(
        user_deleted_sub_text(sub_username),
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )


async def cancel_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    sub_username = query.data.replace("cancel_delete_", "")

    await query.message.edit_text(
        CANCELLED_DELETE_SUB_TEXT,
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )
    db.set_state(user.id, "sub_manage", json.dumps({"sub_username": sub_username}))


# ===== افزودن اشتراک =====
async def add_account_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    db.set_state(user.id, "add_account", None)
    await query.message.edit_text(
        ADD_ACCOUNT_TEXT,
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )


async def handle_add_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """پردازش لینک اشتراک برای افزودن"""
    user = update.effective_user
    message = update.effective_message
    state_data = db.get_state(user.id)

    if not state_data or state_data.get("state") != "add_account":
        return False

    if not message.text:
        return False

    link = message.text.strip()

    if not validate_subscription_link(link):
        await message.reply_text(
            UNKNOWN_LINK_TEXT,
            reply_markup=go_back_keyboard(),
            parse_mode="HTML"
        )
        return True

    # دریافت اطلاعات از API
    info = await fetch_subscription_info(link)
    if not info:
        await message.reply_text(
            ERROR_ADDING_TEXT,
            reply_markup=go_back_keyboard(),
            parse_mode="HTML"
        )
        return True

    # بررسی اینکه اشتراک قبلاً اضافه شده یا نه
    existing = db.get_subscription_by_username(info["sub_username"])
    if existing and existing["user_id"] != user.id:
        from texts import user_taken_id_text
        await message.reply_text(
            user_taken_id_text(info["sub_username"]),
            parse_mode="HTML"
        )
        return True

    if existing and existing["user_id"] == user.id:
        # بروزرسانی لینک
        db.update_subscription_link(info["sub_username"], link)
        await message.reply_text(
            user_added_account_text(
                info["sub_username"],
                info["sub_total_volume"],
                info["sub_remain_volume"]
            ),
            parse_mode="HTML"
        )
    else:
        # افزودن جدید
        db.add_subscription(
            user_id=user.id,
            sub_username=info["sub_username"],
            sub_link=link,
            sub_type="normal",
            sub_total_volume=info["sub_total_volume"],
            sub_used_volume=info["sub_used_volume"],
            sub_created_at=info["sub_created_at"]
        )
        await message.reply_text(
            user_added_account_text(
                info["sub_username"],
                info["sub_total_volume"],
                info["sub_remain_volume"]
            ),
            parse_mode="HTML"
        )

    db.clear_state(user.id)
    return True


# ===== امتیازات =====
async def my_points_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    points = db.get_points(user.id) or {}
    invited = db.get_invited_users(user.id)

    db.set_state(user.id, "profile_points", None)
    await query.message.edit_text(
        user_points_list_text(
            invites=len(invited),
            invite_points=points.get("invite_points", 0),
            total_buy=points.get("total_buy_gb", 0),
            total_buy_points=points.get("buy_points", 0),
            total_buy_friends=points.get("friend_buy_gb", 0),
            total_buy_friends_points=points.get("friend_buy_points", 0),
            total_points=points.get("total_points", 0),
            unused_points=points.get("unused_points", 0)
        ),
        reply_markup=points_keyboard(),
        parse_mode="HTML"
    )


async def invite_banner_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    invite_link = get_invite_link(user.id)
    invite_text = user_invite_text(invite_link)

    assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    banner_path = os.path.join(assets_path, "invite_banner.jpg")

    if os.path.exists(banner_path):
        with open(banner_path, "rb") as f:
            await context.bot.send_photo(
                chat_id=user.id,
                photo=f.read(),
                caption=invite_text,
                parse_mode="HTML"
            )
    else:
        await context.bot.send_message(
            chat_id=user.id,
            text=invite_text,
            parse_mode="HTML"
        )


async def convert_points_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    points = db.get_points(user.id) or {}
    unused = points.get("unused_points", 0)

    from config import MIN_POINTS_FOR_GIFT
    if unused < MIN_POINTS_FOR_GIFT:
        await query.message.edit_text(
            user_low_points_text(unused),
            reply_markup=low_points_keyboard(),
            parse_mode="HTML"
        )
        return

    db.set_state(user.id, "convert_points", None)
    await query.message.edit_text(
        user_convert_points_text(unused),
        reply_markup=convert_points_keyboard(unused),
        parse_mode="HTML"
    )


async def convert_points_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    points_to_spend = int(query.data.replace("convert_pts_", ""))
    gift_volume = calculate_gift_volume(points_to_spend)

    await _send_gift_request(query, context, user, points_to_spend, gift_volume)


async def convert_all_points_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    points = db.get_points(user.id) or {}
    unused = points.get("unused_points", 0)
    gift_volume = calculate_gift_volume(unused)

    await _send_gift_request(query, context, user, unused, gift_volume)


async def _send_gift_request(query, context, user, points_to_spend: int, gift_volume: float):
    """ارسال درخواست هدیه به ادمین"""
    full_name = get_full_name(user)

    await query.message.edit_text(
        REQ_SUBGIFT_TEXT,
        reply_markup=go_back_keyboard(),
        parse_mode="HTML"
    )

    # کسر امتیاز
    db.deduct_points(user.id, points_to_spend)

    # ارسال به ادمین
    sent = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_request_create_subgift_text(
            full_name, user.username, user.id, gift_volume
        ),
        parse_mode="HTML"
    )
    context.bot_data[f"gift_msg_{sent.message_id}"] = {
        "user_id": user.id,
        "gift_volume": gift_volume,
        "points_spent": points_to_spend
    }


async def handle_admin_revoke_and_gift_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """پردازش ریپلای ادمین برای تغییر لینک و هدیه"""
    user = update.effective_user
    message = update.effective_message

    if user.id != ADMIN_ID:
        return False

    if not message.reply_to_message:
        return False

    replied_id = message.reply_to_message.message_id

    # بررسی تغییر لینک اشتراک
    revoke_key = f"revoke_msg_{replied_id}"
    if revoke_key in context.bot_data:
        revoke_data = context.bot_data.pop(revoke_key)
        target_user_id = revoke_data["user_id"]
        sub_username = revoke_data["sub_username"]

        new_link = message.text.strip() if message.text else ""
        if not validate_subscription_link(new_link):
            await message.reply_text("⚠️ لینک معتبر نیست!")
            context.bot_data[revoke_key] = revoke_data
            return True

        db.update_subscription_link(sub_username, new_link)
        sub = db.get_subscription_by_username(sub_username)
        db.clear_state(target_user_id)

        await context.bot.send_message(
            chat_id=target_user_id,
            text=user_revoked_sub_text(sub_username),
            reply_markup=subscription_keyboard(new_link),
            parse_mode="HTML"
        )
        await message.reply_text("✅ لینک اشتراک تغییر کرد و به کاربر ارسال شد.")
        return True

    # بررسی هدیه
    gift_key = f"gift_msg_{replied_id}"
    if gift_key in context.bot_data:
        gift_data = context.bot_data.pop(gift_key)
        target_user_id = gift_data["user_id"]
        gift_volume = gift_data["gift_volume"]

        gift_link = message.text.strip() if message.text else ""
        if not validate_subscription_link(gift_link):
            await message.reply_text("⚠️ لینک معتبر نیست!")
            context.bot_data[gift_key] = gift_data
            return True

        # دریافت اطلاعات اشتراک هدیه
        info = await fetch_subscription_info(gift_link)
        if not info:
            await message.reply_text("⚠️ خطا در خواندن اطلاعات لینک!")
            context.bot_data[gift_key] = gift_data
            return True

        target_user = db.get_user(target_user_id)
        gift_username = build_gift_username(
            target_user.get("username", ""), target_user_id
        )

        # بررسی اشتراک هدیه قبلی
        existing_gift = db.get_subscription_by_username(gift_username)
        if existing_gift:
            # شارژ اشتراک هدیه موجود
            db.update_subscription_link(gift_username, gift_link)
            db.update_subscription_volumes(
                gift_username, info["sub_total_volume"], info["sub_used_volume"]
            )
        else:
            # ساخت اشتراک هدیه جدید
            db.add_subscription(
                user_id=target_user_id,
                sub_username=gift_username,
                sub_link=gift_link,
                sub_type="gift",
                sub_total_volume=info["sub_total_volume"],
                sub_used_volume=info["sub_used_volume"],
                sub_created_at=info["sub_created_at"]
            )

        await context.bot.send_message(
            chat_id=target_user_id,
            text=user_subgift_text(gift_username, gift_volume),
            reply_markup=subscription_keyboard(gift_link),
            parse_mode="HTML"
        )
        await message.reply_text(f"✅ اشتراک هدیه {gift_username} به کاربر ارسال شد.")
        return True

    return False
