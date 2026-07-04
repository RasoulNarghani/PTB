# =============================================
# services/user.py
# سرویس مدیریت کاربران
# =============================================

import logging
from telegram import Bot
from config import CHANNEL_ID
import database as db

logger = logging.getLogger(__name__)


async def check_channel_membership(bot: Bot, user_id: int) -> bool:
    """بررسی عضویت کاربر در کانال"""
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking membership for {user_id}: {e}")
        return False


def ensure_user(user) -> None:
    """ثبت یا بروزرسانی کاربر در دیتابیس"""
    db.add_user(
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username
    )
    db.update_user(
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username
    )


def get_full_name(user) -> str:
    """دریافت نام کامل کاربر"""
    parts = [user.first_name or "", user.last_name or ""]
    return " ".join(p for p in parts if p).strip() or "بی‌نام"


import re


def is_valid_username(username: str) -> bool:
    """بررسی اعتبار نام کاربری اشتراک"""
    pattern = r'^[a-zA-Z0-9._\-]+$'
    return bool(re.match(pattern, username)) and len(username) >= 2


import uuid


def generate_order_id() -> str:
    """تولید شناسه یکتا برای سفارش"""
    return str(uuid.uuid4())[:8].upper()


def generate_ticket_id() -> str:
    """تولید شناسه یکتا برای تیکت"""
    return str(uuid.uuid4())[:6].upper()
