# =============================================
# services/subscription.py
# سرویس مدیریت اشتراک‌ها و ارتباط با API
# =============================================

import aiohttp
import logging
from typing import Optional, Dict, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

BYTES_TO_GB = 1024 ** 3  # 1073741824


def bytes_to_gb(value: int) -> float:
    """تبدیل بایت به گیگابایت با ۲ رقم اعشار"""
    if not value:
        return 0.0
    return round(value / BYTES_TO_GB, 2)


async def fetch_subscription_info(link: str) -> Optional[Dict]:
    """
    دریافت اطلاعات اشتراک از API
    لینک اشتراک + /info
    """
    info_url = link.rstrip("/") + "/info"
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(info_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return parse_subscription_data(data)
                else:
                    logger.warning(f"Subscription info returned {resp.status} for {info_url}")
                    return None
    except Exception as e:
        logger.error(f"Error fetching subscription info from {info_url}: {e}")
        return None


def parse_subscription_data(data: dict) -> Dict:
    """
    پارس کردن داده‌های API اشتراک
    """
    total_bytes = data.get("data_limit", 0) or 0
    used_bytes = data.get("used_traffic", 0) or 0

    total_gb = bytes_to_gb(total_bytes)
    used_gb = bytes_to_gb(used_bytes)
    remain_gb = max(0.0, round(total_gb - used_gb, 2))

    username = data.get("username", "")
    status = data.get("status", "active")
    created_at_raw = data.get("created_at", "")
    sub_id = data.get("id", 0)

    # تبدیل تاریخ به شمسی
    created_at_jalali, created_time = convert_to_jalali(created_at_raw)
    sub_age = calculate_age(created_at_raw)

    return {
        "sub_id": sub_id,
        "sub_username": username,
        "sub_status": status,
        "sub_total_volume": total_gb,
        "sub_used_volume": used_gb,
        "sub_remain_volume": remain_gb,
        "sub_created_at": f"{created_at_jalali} | {created_time}",
        "sub_age": sub_age,
    }


def convert_to_jalali(iso_date: str) -> Tuple[str, str]:
    """
    تبدیل تاریخ میلادی به شمسی
    """
    if not iso_date:
        return "نامشخص", "نامشخص"
    try:
        # پارس تاریخ ISO
        if iso_date.endswith("Z"):
            iso_date = iso_date[:-1] + "+00:00"
        dt = datetime.fromisoformat(iso_date)
        # تبدیل به تهران (UTC+3:30)
        from datetime import timedelta
        tehran_offset = timedelta(hours=3, minutes=30)
        dt_tehran = dt.replace(tzinfo=timezone.utc).astimezone(
            timezone(tehran_offset)
        )
        time_str = dt_tehran.strftime("%H:%M")

        # تبدیل به شمسی (بدون کتابخانه خارجی)
        jalali_date = gregorian_to_jalali(
            dt_tehran.year, dt_tehran.month, dt_tehran.day
        )
        return f"{jalali_date[0]}/{jalali_date[1]:02d}/{jalali_date[2]:02d}", time_str
    except Exception as e:
        logger.error(f"Date conversion error: {e}")
        return iso_date[:10] if iso_date else "نامشخص", ""


def calculate_age(iso_date: str) -> str:
    """محاسبه سن اشتراک"""
    if not iso_date:
        return "نامشخص"
    try:
        if iso_date.endswith("Z"):
            iso_date = iso_date[:-1] + "+00:00"
        created = datetime.fromisoformat(iso_date).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - created

        total_days = delta.days
        if total_days >= 365:
            years = total_days // 365
            months = (total_days % 365) // 30
            return f"{years} سال و {months} ماه"
        elif total_days >= 30:
            months = total_days // 30
            days = total_days % 30
            return f"{months} ماه و {days} روز"
        else:
            return f"{total_days} روز"
    except Exception:
        return "نامشخص"


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> Tuple[int, int, int]:
    """تبدیل تاریخ میلادی به شمسی"""
    g_d_no = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
    for i in range(gm - 1):
        g_d_no += [31, 28 + (1 if gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0) else 0),
                   31, 30, 31, 30, 31, 31, 30, 31, 30, 31][i]
    g_d_no += gd - 1

    j_d_no = g_d_no - 79

    j_np = j_d_no // 12053
    j_d_no %= 12053

    jy = 979 + 33 * j_np + 4 * (j_d_no // 1461)
    j_d_no %= 1461

    if j_d_no >= 366:
        jy += (j_d_no - 1) // 365
        j_d_no = (j_d_no - 1) % 365

    j_mi = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    for i in range(11):
        j_d = j_mi[i]
        if j_d_no >= j_d:
            j_d_no -= j_d
        else:
            break
        i += 1
    jm = i + 1
    jd = j_d_no + 1
    return jy, jm, jd


def validate_subscription_link(link: str) -> bool:
    """بررسی اعتبار لینک اشتراک"""
    from config import BASE_SUB_URL
    return link.startswith(BASE_SUB_URL)


def calculate_prices(price_toman: int, prices_db: dict) -> dict:
    """محاسبه قیمت به ارزهای مختلف"""
    usdt_price = prices_db.get("usdt", {}).get("price", 174000)
    gram_price = prices_db.get("gram", {}).get("price", 300000)
    trx_price = prices_db.get("trx", {}).get("price", 52900)

    return {
        "usdt": round(price_toman / usdt_price, 2),
        "gram": round(price_toman / gram_price, 2),
        "trx": round(price_toman / trx_price, 2),
    }


def format_subscription_list(subscriptions: list, include_test_active: bool = True) -> str:
    """
    فرمت‌بندی لیست اشتراک‌ها برای نمایش در پروفایل
    """
    if not subscriptions:
        return ""

    lines = []
    for sub in subscriptions:
        sub_type = sub.get("sub_type", "normal")
        username = sub.get("sub_username", "")
        total = sub.get("sub_total_volume", 0) or 0
        remain = sub.get("sub_remain_volume", 0) or 0
        status = sub.get("sub_status", "active")

        # نوع اشتراک
        if sub_type == "gift":
            emoji = "🎁"
        elif sub_type == "test":
            emoji = "⏱"
        else:
            emoji = "🆔"

        # حجم
        battery = "🔋" if remain > 0 else "🪫"
        volume_text = f"{battery} {remain:.2f}GB / {total:.2f}GB"

        # وضعیت
        status_text = "Status: Active ✅" if status == "active" else "Status: Disable ❌"

        lines.append(f"{emoji} {username} {volume_text}\n{status_text}")

    return "\n\n".join(lines)
