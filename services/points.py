# =============================================
# services/points.py
# سرویس مدیریت امتیازات
# =============================================

import logging
from typing import Optional
from config import (
    POINTS_PER_INVITE, POINTS_PER_FIRST_BUY,
    POINTS_PER_GB, MIN_POINTS_FOR_GIFT, POINTS_PER_GB_GIFT,
    BOT_LINK
)
import database as db

logger = logging.getLogger(__name__)


def get_invite_link(user_id: int) -> str:
    """ساخت لینک دعوت کاربر"""
    return f"https://t.me/{BOT_LINK.split('/')[-1]}?start=ref_{user_id}"


async def process_new_buy(buyer_id: int, volume_gb: int, context) -> None:
    """
    پردازش خرید جدید و اعطای امتیاز:
    - به خریدار
    - به کسی که خریدار رو دعوت کرده
    """
    buyer = db.get_user(buyer_id)
    if not buyer:
        return

    buyer_points = db.get_points(buyer_id)
    is_first_buy = not db.has_bought_before(buyer_id)

    # امتیاز خریدار
    total_earn = 0
    reason = f"خرید {volume_gb} گیگابایت"

    if is_first_buy:
        total_earn += POINTS_PER_FIRST_BUY

    volume_points = volume_gb * POINTS_PER_GB
    total_earn += volume_points

    db.add_points(buyer_id, total_earn, "buy", buy_gb=volume_gb)

    # ارسال پیام امتیاز به خریدار
    updated_points = db.get_points(buyer_id)
    if updated_points and total_earn > 0:
        from texts import user_receive_point_text
        try:
            await context.bot.send_message(
                chat_id=buyer_id,
                text=user_receive_point_text(
                    total_earn,
                    reason,
                    updated_points["total_points"],
                    updated_points["unused_points"]
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error sending points message to buyer {buyer_id}: {e}")

    # امتیاز به دعوت‌کننده
    inviter = db.get_inviter(buyer_id)
    if inviter:
        inviter_id = inviter["user_id"]

        inviter_earn = 0
        inviter_reason = f"خرید دوست شما ({volume_gb} گیگابایت)"

        if is_first_buy:
            # اولین خرید دوست = 100 امتیاز
            db.add_points(inviter_id, POINTS_PER_FIRST_BUY, "friend_buy")
            inviter_earn += POINTS_PER_FIRST_BUY

        # امتیاز حجم خرید دوست
        friend_vol_points = volume_gb * POINTS_PER_GB
        db.add_points(inviter_id, friend_vol_points, "friend_buy", buy_gb=volume_gb)
        inviter_earn += friend_vol_points

        updated_inviter = db.get_points(inviter_id)
        if updated_inviter and inviter_earn > 0:
            from texts import user_receive_point_text
            try:
                await context.bot.send_message(
                    chat_id=inviter_id,
                    text=user_receive_point_text(
                        inviter_earn,
                        inviter_reason,
                        updated_inviter["total_points"],
                        updated_inviter["unused_points"]
                    ),
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Error sending points message to inviter {inviter_id}: {e}")


async def process_invite(inviter_id: int, new_user_id: int, context) -> None:
    """اعطای امتیاز دعوت به دعوت‌کننده"""
    db.add_points(inviter_id, POINTS_PER_INVITE, "invite")
    updated = db.get_points(inviter_id)

    if updated:
        from texts import user_receive_point_text
        try:
            await context.bot.send_message(
                chat_id=inviter_id,
                text=user_receive_point_text(
                    POINTS_PER_INVITE,
                    "دعوت دوست",
                    updated["total_points"],
                    updated["unused_points"]
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error sending invite points to {inviter_id}: {e}")


def calculate_gift_volume(points_to_spend: int) -> float:
    """محاسبه حجم هدیه از تعداد امتیاز"""
    return round(points_to_spend / POINTS_PER_GB_GIFT, 2)


def build_gift_username(telegram_username: str, user_id: int) -> str:
    """ساخت نام کاربری اشتراک هدیه"""
    if telegram_username:
        return f"{telegram_username}_Gift"
    else:
        return f"User{user_id}_Gift"
