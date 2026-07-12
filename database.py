# =============================================
# database.py - مدیریت دیتابیس SQLite
# =============================================

import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

import os
DB_PATH = "/data/persian_tunnel.db"


@contextmanager
def get_db():
    """Context manager برای اتصال به دیتابیس"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def init_db():
    """ایجاد جداول دیتابیس"""
    with get_db() as conn:
        cursor = conn.cursor()
    ensure_subtest_allowed_column()
        # جدول کاربران
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                invited_by INTEGER,
                join_date TEXT DEFAULT (datetime('now')),
                is_active INTEGER DEFAULT 1
            )
        """)

        # جدول اشتراک‌ها
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sub_username TEXT NOT NULL,
                sub_link TEXT NOT NULL,
                sub_type TEXT DEFAULT 'normal',  -- normal, gift, test
                sub_status TEXT DEFAULT 'active',
                sub_total_volume REAL DEFAULT 0,
                sub_used_volume REAL DEFAULT 0,
                sub_remain_volume REAL DEFAULT 0,
                sub_created_at TEXT,
                sub_added_at TEXT DEFAULT (datetime('now')),
                is_deleted INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # جدول سفارش‌ها
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                sub_username TEXT NOT NULL,
                sub_total_volume INTEGER NOT NULL,
                order_type TEXT DEFAULT 'new',  -- new, renew
                status TEXT DEFAULT 'pending',   -- pending, approved, rejected
                receipt_file_id TEXT,
                receipt_type TEXT,               -- photo, text, video
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # جدول امتیازات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                total_points INTEGER DEFAULT 0,
                unused_points INTEGER DEFAULT 0,
                invite_points INTEGER DEFAULT 0,
                buy_points INTEGER DEFAULT 0,
                friend_buy_points INTEGER DEFAULT 0,
                total_buy_gb REAL DEFAULT 0,
                friend_buy_gb REAL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # جدول تیکت‌های پشتیبانی
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'open',  -- open, closed
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # جدول اشتراک‌های تست
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subtest_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                subtest_username TEXT NOT NULL,
                subtest_link TEXT NOT NULL,
                subtest_number INTEGER NOT NULL,
                assigned_at TEXT DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                is_expired INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # جدول قیمت‌ها
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency TEXT UNIQUE NOT NULL,
                price INTEGER NOT NULL,
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)

        # درج قیمت‌های پیش‌فرض
        from config import DEFAULT_USDT_PRICE, DEFAULT_GRAM_PRICE, DEFAULT_TRX_PRICE
        default_prices = [
            ("usdt", DEFAULT_USDT_PRICE),
            ("gram", DEFAULT_GRAM_PRICE),
            ("trx", DEFAULT_TRX_PRICE),
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO prices (currency, price) VALUES (?, ?)
        """, default_prices)

        # جدول تنظیمات bot state
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_states (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                data TEXT,
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)

        logger.info("Database initialized successfully.")


# ==========================================
# توابع کاربران
# ==========================================

def get_user(user_id: int) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def add_user(user_id: int, first_name: str, last_name: str = None,
             username: str = None, invited_by: int = None):
    with get_db() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO users (user_id, first_name, last_name, username, invited_by)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, first_name, last_name, username, invited_by))
        # اگر کاربر جدید بود، جدول امتیازات هم ایجاد میشه
        conn.execute("""
            INSERT OR IGNORE INTO points (user_id) VALUES (?)
        """, (user_id,))


def update_user(user_id: int, first_name: str, last_name: str = None, username: str = None):
    with get_db() as conn:
        conn.execute("""
            UPDATE users SET first_name=?, last_name=?, username=?
            WHERE user_id=?
        """, (first_name, last_name, username, user_id))


def get_all_users() -> List[Dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM users ORDER BY join_date DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_invited_users(inviter_id: int) -> List[Dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM users WHERE invited_by = ?", (inviter_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_inviter(user_id: int) -> Optional[Dict]:
    with get_db() as conn:
        user = conn.execute("SELECT invited_by FROM users WHERE user_id=?", (user_id,)).fetchone()
        if user and user["invited_by"]:
            row = conn.execute("SELECT * FROM users WHERE user_id=?", (user["invited_by"],)).fetchone()
            return dict(row) if row else None
        return None


# ==========================================
# توابع اشتراک‌ها
# ==========================================

def get_user_subscriptions(user_id: int, include_test: bool = True) -> List[Dict]:
    """دریافت اشتراک‌های کاربر (بدون اشتراک‌های حذف شده)"""
    with get_db() as conn:
        if include_test:
            rows = conn.execute("""
                SELECT * FROM subscriptions
                WHERE user_id = ? AND is_deleted = 0
                ORDER BY sub_added_at DESC
            """, (user_id,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM subscriptions
                WHERE user_id = ? AND is_deleted = 0 AND sub_type != 'test'
                ORDER BY sub_added_at DESC
            """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


def get_subscription_by_username(sub_username: str) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM subscriptions WHERE sub_username = ? AND is_deleted = 0",
            (sub_username,)
        ).fetchone()
        return dict(row) if row else None


def add_subscription(user_id: int, sub_username: str, sub_link: str,
                     sub_type: str = "normal", sub_total_volume: float = 0,
                     sub_used_volume: float = 0, sub_created_at: str = None) -> int:
    with get_db() as conn:
        remain = max(0, sub_total_volume - sub_used_volume)
        cursor = conn.execute("""
            INSERT INTO subscriptions
            (user_id, sub_username, sub_link, sub_type, sub_total_volume,
             sub_used_volume, sub_remain_volume, sub_created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, sub_username, sub_link, sub_type, sub_total_volume,
              sub_used_volume, remain, sub_created_at))
        return cursor.lastrowid


def update_subscription_link(sub_username: str, new_link: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE subscriptions SET sub_link=? WHERE sub_username=? AND is_deleted=0",
            (new_link, sub_username)
        )


def update_subscription_status(sub_username: str, status: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE subscriptions SET sub_status=? WHERE sub_username=? AND is_deleted=0",
            (status, sub_username)
        )


def update_subscription_volumes(sub_username: str, total: float, used: float):
    with get_db() as conn:
        remain = max(0, total - used)
        conn.execute("""
            UPDATE subscriptions
            SET sub_total_volume=?, sub_used_volume=?, sub_remain_volume=?
            WHERE sub_username=? AND is_deleted=0
        """, (total, used, remain, sub_username))


def soft_delete_subscription(sub_username: str, user_id: int):
    """حذف نرم اشتراک (از پروفایل حذف می‌شود ولی نام کاربری آزاد نمی‌شود)"""
    with get_db() as conn:
        conn.execute(
            "UPDATE subscriptions SET is_deleted=1 WHERE sub_username=? AND user_id=?",
            (sub_username, user_id)
        )


def username_exists(sub_username: str) -> bool:
    """بررسی وجود نام کاربری اشتراک"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM subscriptions WHERE sub_username=? AND is_deleted=0",
            (sub_username,)
        ).fetchone()
        return row is not None


def get_user_active_subscriptions(user_id: int) -> List[Dict]:
    """اشتراک‌های فعال (برای تمدید - بدون اشتراک تست)"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM subscriptions
            WHERE user_id=? AND is_deleted=0 AND sub_type != 'test'
            ORDER BY sub_added_at DESC
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


# ==========================================
# توابع سفارش‌ها
# ==========================================

def create_order(order_id: str, user_id: int, sub_username: str,
                 sub_total_volume: int, order_type: str = "new") -> str:
    with get_db() as conn:
        conn.execute("""
            INSERT INTO orders (order_id, user_id, sub_username, sub_total_volume, order_type)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, user_id, sub_username, sub_total_volume, order_type))
    return order_id


def get_order(order_id: str) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM orders WHERE order_id=?", (order_id,)
        ).fetchone()
        return dict(row) if row else None


def update_order_receipt(order_id: str, receipt_file_id: str, receipt_type: str):
    with get_db() as conn:
        conn.execute("""
            UPDATE orders SET receipt_file_id=?, receipt_type=?, updated_at=datetime('now')
            WHERE order_id=?
        """, (receipt_file_id, receipt_type, order_id))


def update_order_status(order_id: str, status: str):
    with get_db() as conn:
        conn.execute("""
            UPDATE orders SET status=?, updated_at=datetime('now') WHERE order_id=?
        """, (status, order_id))


# ==========================================
# توابع امتیازات
# ==========================================

def get_points(user_id: int) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM points WHERE user_id=?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def add_points(user_id: int, amount: int, point_type: str = "other",
               buy_gb: float = 0):
    """
    point_type: invite, buy, friend_buy, other
    """
    with get_db() as conn:
        if point_type == "invite":
            conn.execute("""
                UPDATE points
                SET total_points=total_points+?,
                    unused_points=unused_points+?,
                    invite_points=invite_points+?
                WHERE user_id=?
            """, (amount, amount, amount, user_id))
        elif point_type == "buy":
            conn.execute("""
                UPDATE points
                SET total_points=total_points+?,
                    unused_points=unused_points+?,
                    buy_points=buy_points+?,
                    total_buy_gb=total_buy_gb+?
                WHERE user_id=?
            """, (amount, amount, amount, buy_gb, user_id))
        elif point_type == "friend_buy":
            conn.execute("""
                UPDATE points
                SET total_points=total_points+?,
                    unused_points=unused_points+?,
                    friend_buy_points=friend_buy_points+?,
                    friend_buy_gb=friend_buy_gb+?
                WHERE user_id=?
            """, (amount, amount, amount, buy_gb, user_id))
        else:
            conn.execute("""
                UPDATE points
                SET total_points=total_points+?,
                    unused_points=unused_points+?
                WHERE user_id=?
            """, (amount, amount, user_id))


def deduct_points(user_id: int, amount: int):
    """کسر امتیازات استفاده شده"""
    with get_db() as conn:
        conn.execute("""
            UPDATE points SET unused_points=MAX(0, unused_points-?) WHERE user_id=?
        """, (amount, user_id))


def has_bought_before(user_id: int) -> bool:
    """بررسی آیا کاربر قبلاً خرید داشته"""
    with get_db() as conn:
        row = conn.execute("""
            SELECT id FROM orders WHERE user_id=? AND status='approved'
        """, (user_id,)).fetchone()
        return row is not None


# ==========================================
# توابع تیکت‌های پشتیبانی
# ==========================================

def create_ticket(ticket_id: str, user_id: int) -> str:
    with get_db() as conn:
        conn.execute("""
            INSERT INTO tickets (ticket_id, user_id) VALUES (?, ?)
        """, (ticket_id, user_id))
    return ticket_id


def get_ticket(ticket_id: str) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM tickets WHERE ticket_id=?", (ticket_id,)
        ).fetchone()
        return dict(row) if row else None


def close_ticket(ticket_id: str):
    with get_db() as conn:
        conn.execute("""
            UPDATE tickets SET status='closed', updated_at=datetime('now')
            WHERE ticket_id=?
        """, (ticket_id,))


def get_open_ticket_by_user(user_id: int) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("""
            SELECT * FROM tickets WHERE user_id=? AND status='open'
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,)).fetchone()
        return dict(row) if row else None


# ==========================================
# توابع اشتراک تست
# ==========================================

def get_user_subtest(user_id: int) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM subtest_assignments WHERE user_id=?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def assign_subtest(user_id: int, subtest_username: str, subtest_link: str,
                   subtest_number: int, expires_at: str):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO subtest_assignments
            (user_id, subtest_username, subtest_link, subtest_number, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, subtest_username, subtest_link, subtest_number, expires_at))


def get_assigned_subtest_numbers() -> List[int]:
    """دریافت شماره اشتراک‌های تستی که الان در حال استفاده هستند (منقضی نشده)"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT subtest_number FROM subtest_assignments
            WHERE is_expired=0
        """).fetchall()
        return [r["subtest_number"] for r in rows]


def get_expired_subtests() -> List[Dict]:
    """اشتراک‌های تستی که منقضی شده‌اند"""
    with get_db() as conn:
        now = datetime.now().isoformat()
        rows = conn.execute("""
            SELECT sa.*, u.first_name, u.last_name, u.username
            FROM subtest_assignments sa
            JOIN users u ON sa.user_id = u.user_id
            WHERE sa.expires_at <= ? AND sa.is_expired = 0
        """, (now,)).fetchall()
        return [dict(r) for r in rows]


def mark_subtest_expired(user_id: int):
    with get_db() as conn:
        conn.execute(
            "UPDATE subtest_assignments SET is_expired=1 WHERE user_id=?",
            (user_id,)
        )


def update_subtest_link(subtest_number: int, new_link: str):
    with get_db() as conn:
        conn.execute("""
            UPDATE subtest_assignments SET subtest_link=?, is_expired=0
            WHERE subtest_number=?
        """, (new_link, subtest_number))
        # همچنین لینک اشتراک توی جدول subscriptions هم آپدیت بشه
        username = f"PT_SubTest{subtest_number}"
        conn.execute("""
            UPDATE subscriptions SET sub_link=?
            WHERE sub_username=?
        """, (new_link, username))


def get_plan_price_from_order(order_id: str):
    """دریافت قیمت از config بر اساس حجم سفارش"""
    order = get_order(order_id)
    if not order:
        return None
    from config import get_plan_price
    return get_plan_price(order["sub_total_volume"])


# ==========================================
# توابع قیمت‌ها
# ==========================================

def get_prices() -> Dict[str, Any]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM prices").fetchall()
        return {r["currency"]: {"price": r["price"], "updated_at": r["updated_at"]} for r in rows}


def update_price(currency: str, price: int):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO prices (currency, price, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(currency) DO UPDATE SET price=?, updated_at=datetime('now')
        """, (currency, price, price))


# ==========================================
# توابع Bot State
# ==========================================

def set_state(user_id: int, state: str, data: str = None):
    import json
    with get_db() as conn:
        conn.execute("""
            INSERT INTO bot_states (user_id, state, data, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET state=?, data=?, updated_at=datetime('now')
        """, (user_id, state, data, state, data))


def get_state(user_id: int) -> Optional[Dict]:
    import json
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM bot_states WHERE user_id=?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def clear_state(user_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM bot_states WHERE user_id=?", (user_id,))



# ==========================================
# توابع پنل مدیریت کاربر (ادمین)
# ==========================================

def ensure_subtest_allowed_column():
    """اضافه کردن ستون subtest_allowed در صورت نبود (یکبار در init_db صدا زده میشه)"""
    with get_db() as conn:
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "subtest_allowed" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN subtest_allowed INTEGER DEFAULT 1")

def is_subtest_allowed(user_id: int) -> bool:
    with get_db() as conn:
        row = conn.execute("SELECT subtest_allowed FROM users WHERE user_id=?", (user_id,)).fetchone()
        return row["subtest_allowed"] != 0 if row else True

def set_subtest_allowed(user_id: int, allowed: bool):
    with get_db() as conn:
        conn.execute("UPDATE users SET subtest_allowed=? WHERE user_id=?", (1 if allowed else 0, user_id))

def force_mark_subtest_used(user_id: int):
    """ثبت دستی اینکه کاربر قبلا اشتراک تست گرفته (بدون تخصیص واقعی)"""
    import datetime
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM subtest_assignments WHERE user_id=?", (user_id,)).fetchone()
        if existing:
            return
        past = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn.execute("""
            INSERT INTO subtest_assignments
            (user_id, subtest_username, subtest_link, subtest_number, expires_at, is_expired)
            VALUES (?, 'manual', 'manual', 0, ?, 1)
        """, (user_id, past))

def clear_subtest_usage(user_id: int):
    """آزاد کردن دوباره‌ی امکان دریافت اشتراک تست"""
    with get_db() as conn:
        conn.execute("DELETE FROM subtest_assignments WHERE user_id=?", (user_id,))

def set_points_field(user_id: int, field: str, value):
    """ویرایش یکی از فیلدهای جدول points"""
    allowed_fields = {"total_points", "unused_points", "invite_points", "buy_points"}
    if field not in allowed_fields:
        raise ValueError("فیلد نامعتبر")
    with get_db() as conn:
        conn.execute(f"UPDATE points SET {field}=? WHERE user_id=?", (value, user_id))

def set_inviter(user_id: int, inviter_id: int):
    with get_db() as conn:
        conn.execute("UPDATE users SET invited_by=? WHERE user_id=?", (inviter_id, user_id))

def set_invited_by_bulk(inviter_id: int, invited_ids: list):
    """چند کاربر رو بصورت یکجا 'دعوت‌شده توسط' این کاربر ثبت می‌کنه"""
    with get_db() as conn:
        for uid in invited_ids:
            conn.execute("UPDATE users SET invited_by=? WHERE user_id=?", (inviter_id, uid))