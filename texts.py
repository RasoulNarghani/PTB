# =============================================
# texts.py - تمامی متن‌های ربات
# =============================================

from config import TON_WALLET, TRC20_WALLET, CARD_NAME, CARD_NUMBER


# ==========================================
# متن‌های عمومی
# ==========================================

JOIN_TEXT = """
با عرض پوزش از شما کاربر گرامی🙏
برای استفاده از ربات، باید در کانال
<b>Persian Tunnel 🦁🛡</b>
عضو شوید.

عضویت شما در کانال، فقط به این منظور است که اخبار، بروزرسانی‌ها و آپدیت‌های مرتبط را از دست ندهید.

برای عضویت در کانال، و یا بررسی عضویت،
روی دکمه‌های کلیک کنید.👇
"""

WELCOME_TEXT = """
سلام ✋
به ربات🤖 <b>پرشین تانل🦁🛡</b> خوش آمدید. 🌹


لطفاً برای خرید اشتراک 🛍
مشاهده امکانات ✨
و مدیریت حساب کاربری 👤
از دکمه‌های ربات استفاده کنید. 👇
"""

FEATURES_TEXT = """
یک اشتراک، برای همه دستگاه ها. 📱💻🖥
تمامی سرویس ها بدون
محدودیت تعداد کاربر 👤
و بدون محدودیت زمانی میباشند. ⏱️


<b>لیست سرورها و کشورها:</b>
آلمان🇩🇪، فنلاند🇫🇮، ترکیه🇹🇷، امارات🇦🇪، آمریکا🇺🇸


تمامی سرویس ها به صورت همزمان به ۵ کشور دنیا با آیپی ثابت (STATIC-IP) دسترسی دارند. ✅
مجهز به سیستم مانیتورینگ 24 ساعته سرورها. 📊


اگه شما هم به سرور از کشور خاصی نیاز دارید اعلام کنید بدون هزینه، اضافه میکنیم. 👍
"""

SUPPORT_TEXT = """
پیام خود را برای پشتیبانی ارسال کنید. 📩

شما می‌توانید:
• متن 📝
• تصویر 🌄
• ویدیو 🎥
ارسال کنید.
"""

UNKNOWN_COMMAND_TEXT = """
دستور نامشخص! ❓
لطفاً از دکمه‌های ربات استفاده کنید. 👇
"""

NOT_MEMBER_TEXT = """
⛔️ شما هنوز عضو کانال نیستید!
لطفاً ابتدا در کانال عضو شوید و سپس دوباره امتحان کنید.
"""

ERROR_TEXT = """
⚠️ خطایی رخ داد. لطفاً دوباره تلاش کنید.
"""


# ==========================================
# توابع متن پشتیبانی
# ==========================================

def user_support_text(ticket_id: str, admin_ticket_message: str) -> str:
    return f"""
📩 <b>پیام پشتیبانی (پیام ادمین)</b>
🎫 شماره تیکت: <code>{ticket_id}</code>

💬 متن پیام:
{admin_ticket_message}
"""


def admin_support_text(full_name: str, username: str, user_id: int,
                       ticket_id: str, ticket_message: str) -> str:
    username_text = f"@{username}" if username else "-"
    return f"""
📩 <b>پیام پشتیبانی</b> 🎫
🎫 شماره تیکت: <code>{ticket_id}</code>

👤 {full_name}
🆔 {username_text} 🔢 <code>{user_id}</code>

💬 متن پیام:
{ticket_message}
"""

TICKET_CLOSED_TEXT = """
🔒 تیکت بسته شد.
برای ارسال پیام جدید، مجدداً از بخش پشتیبانی اقدام کنید.
"""

TICKET_CLOSED_ADMIN_TEXT = """
🔒 تیکت توسط کاربر بسته شد.
"""


# ==========================================
# متن‌های مرتبط با بخش خرید
# ==========================================

PLANS_TEXT = """
تمامی سرویس‌ها بدون محدودیت کاربر👤 و بدون محدودیت زمانی⏱️ می‌باشد.

<b>قیمت واحد (هر گیگابایت):</b>
<blockquote>20 گیگابایت = هر گیگابایت 12,000 تومان</blockquote>
<blockquote>50 گیگابایت = هر گیگابایت 10,000 تومان</blockquote>
<blockquote>100 گیگابایت = هر گیگابایت 9,000 تومان</blockquote>
<blockquote>200 گیگابایت = هر گیگابایت 8,000 تومان</blockquote>
<blockquote>500 گیگابایت = هر گیگابایت 7,000 تومان</blockquote>
<blockquote>1,000 گیگابایت = هر گیگابایت 6,000 تومان</blockquote>

لطفاً حجم مورد نظر خود را انتخاب کنید. 👇
"""


def user_renew_text(sub_total_volume: int) -> str:
    return f"""
📦 حجم انتخابی شما: <b>{sub_total_volume} GB</b>

جهت شارژ اشتراک، لطفاً یکی از اشتراک‌های خود را انتخاب کنید. 👇

و یا اگر قصد خرید اشتراک جدید دارید، روی دکمه <b>افزودن اشتراک جدید</b> کلیک کنید.
"""


def user_new_text(sub_total_volume: int) -> str:
    return f"""
📦 حجم انتخابی شما: <b>{sub_total_volume} GB</b>

نام‌کاربری اشتراک خود را ارسال کنید. ✨

کاراکترهای مجاز برای انتخاب نام کاربری:
• فقط حروف انگلیسی 🔠🔡
• فقط اعداد انگلیسی 🔢
• فقط  <code>. - _</code>
• بدون فاصله

می‌توانید با زدن دکمه زیر از این مرحله عبور کنید.
"""


INVALID_ID_TEXT = """
❌ نام‌کاربری مجاز نیست.

کاراکترهای مجاز برای انتخاب نام کاربری:
• فقط حروف انگلیسی 🔠🔡
• فقط اعداد انگلیسی 🔢
• فقط  <code>. - _</code>
• بدون فاصله

<b>مثال:</b>
<blockquote>PersianSub
PersianSub123
Persian.Sub
Persian-Sub
Persian_Sub</blockquote>
"""


def user_taken_id_text(sub_username: str) -> str:
    return f"""
با عرض پوزش، نام کاربری <b>{sub_username}</b> متعلق به شخص دیگریست.
لطفاً نام‌کاربری دیگری انتخاب کنید.

اما اگر این نام کاربری متعلق به شماست، از بخش:
<blockquote>حساب کاربری من 👤
⬇️
افزودن اشتراک ➕</blockquote>
لینک اشتراک خود را برای ما ارسال کنید.
"""


def user_order_details_text(sub_username: str, sub_total_volume: int,
                             price_toman: int, price_usdt: float,
                             price_gram: float, price_trx: float) -> str:
    return f"""
📋 <b>جزییات اشتراک شما:</b>
🆔 نام‌کاربری:   <b>{sub_username}</b>
🔋 حجم:   <b>{sub_total_volume} GB</b>

💰 مبلغ:   <b>{price_toman:,} تومان</b>

💲 معادل:   <b>{price_usdt} USDT</b>
💎 معادل:   <b>{price_gram} Gram (ex TON)</b>
🔴 معادل:   <b>{price_trx} TRX</b>


🪙 <b>آدرس ولت‌ها:</b>
TON (USDT coin, Gram coin):
<code>{TON_WALLET}</code>

TRC20 (USDT coin, TRX coin):
<code>{TRC20_WALLET}</code>


پس از پرداخت، روی دکمه زیر کلیک کنید. 👇
"""


QRCODE_TEXT = "📷 بارکد (QR) آدرس ولت‌های شبکه TON و TRC20 👇"


def user_send_card_text() -> str:
    return f"""
💳 <b>اطلاعات کارت:</b>

نام:
<b>{CARD_NAME}</b>

شماره کارت:
<code>{CARD_NUMBER}</code>
"""


def user_send_receipt_text(sub_username: str, sub_total_volume: int,
                            price_toman: int) -> str:
    return f"""
📋 <b>جزئیات اشتراک شما:</b>
🆔 نام کاربری: <b>{sub_username}</b>
🔋 حجم اشتراک: <b>{sub_total_volume} GB</b>
💰 مبلغ: <b>{price_toman:,} تومان</b>

رسید پرداخت را ارسال کنید. 📩
• تصویر یا متن رسید تراکنش 🌄📝
"""


INVALID_RECEIPT_TEXT = """
❌ فرمت رسید ارسالی شما، نامعتبر است.
فقط تصویر، یا متن رسید تراکنش را ارسال کنید. 🌄📝
"""

VALID_RECEIPT_TEXT = """
✅ رسید شما برای ادمین ارسال شد.
لطفاً منتظر پاسخ از سوی ادمین باشید.
"""

VIDEO_RECEIPT_TEXT = """
✅ ویدیوی شما برای ادمین ارسال شد.

معمولاً رسیدهایی که ارسال می‌شود
یا متن فیش واریزی است 📝
یا عکس و اسکرین‌شات فیش واریزی 🌄

حالا چرا شما برای رسید، ویدیو فرستادید!
نمیدونم!!! 🤔

حالا منتظر می‌مونیم ببینیم ادمین چه نظری داره!
"""


def admin_newsub_receipt_text(sub_order_id: str, full_name: str, username: str,
                               user_id: int, sub_username: str,
                               sub_total_volume: int) -> str:
    username_text = f"@{username}" if username else "-"
    return f"""
🧾 <b>رسید سفارش اشتراک جدید</b>

🧾 شماره سفارش: <code>{sub_order_id}</code>

👤 نام: {full_name}
🆔 نام کاربری: {username_text}
🔢 آیدی عددی: <code>{user_id}</code>

🆔 نام کاربری اشتراک: <code>{sub_username}</code>
🔋 حجم اشتراک: {sub_total_volume} GB
"""


def admin_newsub_approve_text(order_id: str, full_name: str, username: str,
                               user_id: int, volume: int,
                               sub_username: str) -> str:
    username_text = f"@{username}" if username else "-"
    return f"""
✅ <b>رسید سفارش اشتراک جدید تایید شد.</b>

🧾 شماره سفارش: <code>{order_id}</code>

👤 نام: {full_name}
🆔 نام کاربری: {username_text}
🔢 آیدی عددی: <code>{user_id}</code>

🆔 نام کاربری اشتراک: <code>{sub_username}</code>
🔋 حجم اشتراک: {volume} GB

لطفاً با <b>ریپلای</b> روی همین پیام لینک اشتراک را ارسال کنید. 👇
"""


def user_send_newsub_text(sub_username: str, sub_total_volume: int) -> str:
    return f"""
🎉 <b>خرید شما تایید شد.</b> ✅

👤 نام‌کاربری: <b>{sub_username}</b>
🔋 حجم اشتراک: <b>{sub_total_volume} GB</b>
"""


def admin_renewsub_receipt_text(order_id: str, full_name: str, username: str,
                                 user_id: int, sub_username: str,
                                 volume: int) -> str:
    username_text = f"@{username}" if username else "-"
    return f"""
🧾 <b>رسید سفارش شارژ اشتراک</b>

🧾 شماره سفارش: <code>{order_id}</code>

👤 نام: {full_name}
🆔 نام کاربری: {username_text}
🔢 آیدی عددی: <code>{user_id}</code>

🆔 نام کاربری اشتراک: <code>{sub_username}</code>
🔋 حجم اشتراک: {volume} GB
"""


def user_send_renewsub_text(sub_username: str, sub_total_volume: int) -> str:
    return f"""
✅ <b>اشتراک شما شارژ شد.</b>
قبل از استفاده آپدیت کانفیگ بزنید. 🔄

👤 نام‌کاربری: <b>{sub_username}</b>
🔋 حجم اشتراک: <b>{sub_total_volume} GB</b>
"""


ADMIN_SEND_REASON_TEXT = """
❓ دلیل رد تایید رسید را با <b>ریپلای</b> روی همین پیام ارسال کنید:
"""


def user_reject_receipt_text(reason_reject: str) -> str:
    return f"""
❌ <b>رسید ارسالی شما تایید نشد.</b>

<b>دلیل رد تایید:</b>
{reason_reject}

برای ارسال مجدد رسید پرداختی، روی دکمه زیر کلیک کنید. 👇
"""


# ==========================================
# متن‌های مرتبط با حساب کاربری
# ==========================================

def user_profile_text(full_name: str, username: str, subscriptions: str,
                       invites: int, total_points: int,
                       unused_points: int) -> str:
    username_text = f"@{username}" if username else "-"
    return f"""
👤 <b>حساب کاربری شما:</b>
نام: {full_name}
نام‌کاربری: {username_text}


📶 <b>اشتراک‌های شما:</b>
{subscriptions}

👥 دعوت شدگان: <b>{invites} نفر</b>
🎉 کل امتیازات: <b>{total_points} امتیاز</b>
🎁 امتیازات استفاده نشده: <b>{unused_points} امتیاز</b>
"""


NO_ACCOUNT_TEXT = "⚠️ شما هنوز هیچ اشتراکی ثبت نکرده‌اید!"

MY_ACCOUNTS_TEXT = "برای مدیریت، روی نام اشتراک مد نظر کلیک کنید. 👇"

ADD_ACCOUNT_TEXT = "🔗 لینک اشتراک خود را ارسال کنید:"

UNKNOWN_LINK_TEXT = """
⚠️ لینک اشتراک معتبر نیست.

لطفاً لینک اشتراک خود را که به شکل زیر است ارسال کنید:
<blockquote>https://de.3erveronline.com/sub/xxx</blockquote>
"""

ERROR_ADDING_TEXT = "❌ خطا در افزودن اشتراک. لطفاً دوباره تلاش کنید."


def user_added_account_text(sub_username: str, sub_total_volume: float,
                             sub_remain_volume: float) -> str:
    return f"""
✅ <b>اکانت با موفقیت اضافه شد.</b>

🆔 {sub_username}
🔋 {sub_total_volume:.2f} GB / {sub_remain_volume:.2f} GB
"""


def user_sub_info_text(sub_username: str, sub_id: int, sub_status: str,
                        sub_created_at: str, sub_age: str,
                        sub_total_volume: float, sub_used_volume: float,
                        sub_remain_volume: float) -> str:
    status_text = "Active ✅" if sub_status == "active" else "Disable ❌"
    return f"""
📋 <b>جزییات اشتراک شما:</b>

🆔 نام‌کاربری: <b>{sub_username}</b>
🔢 آیدی اشتراک: {sub_id}
✅ وضعیت: {status_text}

🔋 <b>حجم اشتراک</b>
• کل: {sub_total_volume:.2f} GB
• مصرف شده: {sub_used_volume:.2f} GB
• مانده: {sub_remain_volume:.2f} GB

📅 تاریخ و ساعت ساخت اشتراک: {sub_created_at}
🚼 عمر اشتراک شما: {sub_age}
"""


# --- غیرفعال سازی ---
def user_req_disable_sub_text(sub_username: str) -> str:
    return f"""
❌ با ارسال این درخواست، اشتراک شما غیرفعال خواهد شد.

با غیرفعال سازی، اشتراک شما خاموش خواهد شد.
و تا فعال سازی مجدد نمی‌توانید از اشتراک خود استفاده کنید.

آیا می‌خواهید اشتراک را غیرفعال کنید؟
🆔 {sub_username}
"""


CANCELLED_DISABLE_SUB_TEXT = "درخواست غیرفعال سازی اشتراک لغو شد."


def user_disable_sub_text(sub_username: str) -> str:
    return f"""
✅ درخواست شما برای غیرفعال سازی اشتراک ارسال شد.
🆔 نام کاربری اشتراک: {sub_username}

بعد از غیرفعال سازی اشتراک، به شما اطلاع خواهیم داد.
"""


def admin_request_disable_sub_text(full_name: str, username: str,
                                    user_id: int, sub_username: str) -> str:
    username_text = f"@{username}" if username else "-"
    return f"""
🔴 <b>درخواست غیرفعال سازی اشتراک</b>

<b>اطلاعات کاربر:</b>
👤 {full_name}
🆔 {username_text} 🔢 <code>{user_id}</code>

🆔 {sub_username}

پس از غیرفعال سازی روی دکمه انجام شد کلیک کنید.
"""


def user_disabled_sub_text(sub_username: str) -> str:
    return f"""
❌ <b>اشتراک غیرفعال شد.</b>

🆔 نام کاربری اشتراک: {sub_username}
"""


# --- فعال سازی ---
def user_req_active_sub_text(sub_username: str) -> str:
    return f"""
✅ با ارسال این درخواست، اشتراک شما مجدداً فعال خواهد شد.

با فعال سازی مجدد، اشتراک شما روشن خواهد شد.
و می‌توانید از اشتراک خود استفاده کنید.

آیا می‌خواهید اشتراک را مجدداً فعال کنید؟
🆔 {sub_username}
"""


CANCELLED_ACTIVE_SUB_TEXT = "درخواست فعال سازی اشتراک لغو شد."


def user_active_sub_text(sub_username: str) -> str:
    return f"""
✅ درخواست شما برای فعال سازی مجدد اشتراک ارسال شد.
🆔 نام کاربری اشتراک: {sub_username}

بعد از فعال سازی اشتراک، به شما اطلاع خواهیم داد.
"""


def admin_request_active_sub_text(full_name: str, username: str,
                                   user_id: int, sub_username: str) -> str:
    username_text = f"@{username}" if username else "-"
    return f"""
🟢 <b>درخواست فعال سازی اشتراک</b>

<b>اطلاعات کاربر:</b>
👤 {full_name}
🆔 {username_text} 🔢 <code>{user_id}</code>

🆔 {sub_username}

پس از فعال سازی روی دکمه انجام شد کلیک کنید.
"""


def user_actived_sub_text(sub_username: str) -> str:
    return f"""
✅ <b>اشتراک مجدداً فعال شد.</b>

🆔 نام کاربری اشتراک: {sub_username}
"""


# --- تغییر لینک ---
def user_req_revoke_sub_text(sub_username: str) -> str:
    return f"""
🔄 با ارسال این درخواست، لینک اشتراک شما تغییر خواهد کرد.
لینک اشتراک شما باطل و لینک جدید، برای شما ارسال و جایگزین لینک قدیمی خواهد شد. ♻️

آیا می‌خواهید لینک اشتراک را تغییر دهید؟
🆔 {sub_username}
"""


CANCELLED_REVOKE_SUB_TEXT = "درخواست تغییر لینک اشتراک لغو شد."


def user_revoke_sub_text(sub_username: str) -> str:
    return f"""
✅ درخواست شما برای تغییر لینک اشتراک ارسال شد.
🆔 نام کاربری اشتراک: {sub_username}

بعد از تغییر، لینک اشتراک جدید برای شما ارسال خواهد شد. 📩
"""


def admin_request_revoke_sub_text(full_name: str, username: str,
                                   user_id: int, sub_username: str) -> str:
    username_text = f"@{username}" if username else "-"
    return f"""
🔄 <b>درخواست تغییر لینک اشتراک</b>

<b>اطلاعات کاربر:</b>
👤 {full_name}
🆔 {username_text} 🔢 <code>{user_id}</code>

🆔 {sub_username}

بعد از تغییر، لینک اشتراک جدید را با <b>ریپلای</b> روی این پیام ارسال کنید.
"""


def user_revoked_sub_text(sub_username: str) -> str:
    return f"""
✅ <b>لینک اشتراک تغییر کرد.</b>

🆔 نام کاربری اشتراک: {sub_username}
"""


# --- حذف اشتراک ---
def user_req_delete_sub_text(sub_username: str) -> str:
    return f"""
🗑 با زدن تایید، اشتراک از حساب کاربری شما حذف خواهد شد.

آیا می‌خواهید اشتراک را از حساب کاربری خود حذف کنید؟
🆔 {sub_username}
"""


CANCELLED_DELETE_SUB_TEXT = "درخواست حذف اشتراک لغو شد."


def user_deleted_sub_text(sub_username: str) -> str:
    return f"""
✅ <b>اشتراک حذف شد.</b>
🆔 نام کاربری اشتراک: {sub_username}

در صورت پشیمانی از حذف، می‌توانید از بخش افزودن اکانت، و ارسال لینک اشتراک،
اشتراک حذف شده را به حساب کاربری خود برگردانید.
"""


# ==========================================
# متن‌های مرتبط با امتیازات
# ==========================================

def user_points_list_text(invites: int, invite_points: int,
                           total_buy: float, total_buy_points: int,
                           total_buy_friends: float, total_buy_friends_points: int,
                           total_points: int, unused_points: int) -> str:
    return f"""
شما می‌توانید با دعوت دوست، خرید خودتان و دوستانتان، از ما امتیاز دریافت کنید. 🎁

<blockquote>• دعوت دوست = 100 امتیاز
• اولین خرید شما یا دوست شما = 100 امتیاز
• هر گیگابایت خرید شما = 10 امتیاز
• هر گیگابایت خرید دوست شما = 10 امتیاز</blockquote>

🔸 در نهایت در ازای هر 1,000 امتیاز، از ما 1 گیگابایت اشتراک هدیه دریافت کنید. 🎁
🔻 حداقل امتیاز مورد نیاز برای دریافت اشتراک هدیه:
<b>10,000 امتیاز (10 گیگابایت)</b>


📈 <b>امتیازات من</b>
امتیازات به دست آمده از دعوت:
🎉 <b>{invite_points} امتیاز</b> • {invites} نفر

امتیازات به دست آمده از خرید:
🪅 <b>{total_buy_points} امتیاز</b> از خرید شما • {total_buy:.1f} گیگابایت
🎊 <b>{total_buy_friends_points} امتیاز</b> از خرید دوستان • {total_buy_friends:.1f} گیگابایت


مجموع امتیازات شما:
🎁 <b>{total_points} امتیاز</b>
امتیازات استفاده نشده شما:
🪄 <b>{unused_points} امتیاز</b>
"""


def user_invite_text(invite_link: str) -> str:
    return f"""
🚀 <b>Persian Tunnel</b> 🚀

⚡ اتصال پایدار و پرسرعت
🌐 مولتی لوکیشن
✅ آی‌پی ثابت
🌍 مناسب برای تمامی اپراتورها
📱 قابل استفاده در تمامی سیستم‌عامل‌ها و برنامه‌ها
🔄 پشتیبانی و بروزرسانی مداوم

🎁 با دعوت دوستان خود امتیاز دریافت کنید.
هر دعوت = 100 امتیاز
هر 10,000 امتیاز = 10 گیگ هدیه

👇
{invite_link}
"""


def user_low_points_text(unused_points: int) -> str:
    return f"""
با عرض پوزش، مجموع امتیازات شما از حداقل امتیاز مورد نیاز برای دریافت اشتراک هدیه کمتر می‌باشد. ❌

🎉 مجموع امتیازات استفاده نشده شما: <b>{unused_points} امتیاز</b>
🔻 حداقل امتیاز مورد نیاز: <b>10,000 امتیاز</b>
"""


def user_convert_points_text(unused_points: int) -> str:
    return f"""
🪄 <b>تبدیل امتیاز به اشتراک</b>

🎉 مجموع امتیازات استفاده نشده شما: <b>{unused_points} امتیاز</b>

لطفاً حجم مورد نظر خود را انتخاب کنید. 👇
"""


REQ_SUBGIFT_TEXT = """
✅ درخواست دریافت اشتراک هدیه شما، برای ادمین ارسال شد.

به‌زودی لینک اشتراک هدیه، برای شما ارسال خواهد شد.
"""


def admin_request_create_subgift_text(full_name: str, username: str,
                                       user_id: int, volume_gift: float) -> str:
    username_text = f"@{username}" if username else "-"
    return f"""
🎁 <b>درخواست تبدیل امتیاز به اشتراک</b>

<b>اطلاعات کاربر:</b>
👤 {full_name}
🆔 {username_text} 🔢 <code>{user_id}</code>

حجم اشتراک هدیه: <b>{volume_gift} GB</b>

بعد از ساخت اشتراک هدیه، لینک اشتراک را با <b>ریپلای</b> روی این پیام ارسال کنید.
"""


def user_subgift_text(sub_username: str, sub_total_volume: float) -> str:
    return f"""
🎁 <b>اطلاعات اشتراک هدیه شما:</b>

🆔 نام‌کاربری: {sub_username}
🔋 حجم اشتراک: {sub_total_volume} GB
"""


def user_receive_point_text(receive_point: int, reason_point: str,
                             total_points: int, unused_points: int) -> str:
    return f"""
🎉 <b>تبریک!</b>
شما <b>{receive_point} امتیاز</b> بابت {reason_point} دریافت کردید.

مجموع امتیازات شما: <b>{total_points} امتیاز</b>
امتیازات استفاده نشده: <b>{unused_points} امتیاز</b>
"""


# ==========================================
# متن‌های مرتبط با اشتراک تست
# ==========================================

SUBTEST_TEXT = """
شما می‌توانید برای اطمینان از کیفیت و سرعت سرویس‌های ما، اشتراک تست دریافت کنید. ✨

<blockquote>حجم اشتراک تست: 200 مگابایت
مدت زمان استفاده: 24 ساعت</blockquote>

برای ارسال درخواست کانفیگ تست، روی دکمه زیر کلیک کنید. 👇
"""

RECEIVED_SUBTEST_TEXT = """
با عرض پوزش، هر کاربر فقط یک بار مجاز به دریافت اشتراک تست می‌باشد.
و شما قبلاً اشتراک تست دریافت کرده‌اید.
"""

REJECT_RECEIVE_SUBTEST_TEXT = """
متأسفانه شما مجاز به دریافت اشتراک تست نیستید.

کاربرانی که اشتراک عادی یا هدیه دارند، مجاز به دریافت اشتراک تست نیستند.
"""

NO_SUBTEST_AVAILABLE_TEXT = """
⚠️ در حال حاضر اشتراک تست در دسترس نیست.
لطفاً بعداً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.
"""


def user_send_subtest_text(subtest_number: int) -> str:
    return f"""
✅ <b>اطلاعات اشتراک تست شما</b>

🔢 شماره اشتراک: <b>{subtest_number}</b>
🔋 حجم اشتراک: <b>200 MB</b>
⏱️ زمان استفاده: <b>24 ساعت</b>
"""


def user_timeout_subtest_text(sub_total_volume: float, sub_used_volume: float) -> str:
    return f"""
⌛️ <b>زمان استفاده از اشتراک تست به پایان رسید.</b>

🔋 حجم استفاده شده شما: <b>{sub_used_volume:.2f} GB / {sub_total_volume:.2f} GB</b>

برای خرید اشتراک کامل روی دکمه زیر کلیک کنید. 👇
"""


def admin_reset_subtest_text(full_name: str, username: str, user_id: int,
                              subtest_number: int, sub_total_volume: float,
                              sub_used_volume: float) -> str:
    username_text = f"@{username}" if username else "-"
    return f"""
⌛️ <b>پایان زمان استفاده از اشتراک تست</b>

<b>اطلاعات کاربر:</b>
👤 {full_name}
🆔 {username_text} 🔢 <code>{user_id}</code>

<b>اطلاعات اشتراک تست:</b>
🔢 {subtest_number}
🔋 {sub_used_volume:.2f} GB / {sub_total_volume:.2f} GB

بعد از تغییر، لینک اشتراک جدید را با <b>ریپلای</b> روی این پیام ارسال کنید.
"""


# ==========================================
# متن‌های ادمین
# ==========================================

ADMIN_MESSAGE_CHANNEL = """
📢 پیامی که می‌خواهید در کانال قرار دهید را با <b>ریپلای</b> روی همین پیام برای من ارسال کنید.
این پیام می‌تواند هر چیزی باشد - متن، عکس، ویدیو، حتی یک استیکر.
"""

ADMIN_URL_BUTTON = """
📎 فهرستی از دکمه‌های URL برای پیام را برای من ارسال کنید.
لطفاً از این فرمت استفاده کنید:

<code>Button text 1 - http://www.example.com/ | Button text 2 - http://www.example2.com/
Button text 3 - http://www.example3.com/</code>

از جداکننده <code>|</code> برای اضافه کردن حداکثر سه دکمه در یک ردیف استفاده کنید.

برای بازگشت، <b>Cancel</b> را انتخاب کنید.
"""


def admin_price_text(prices: dict) -> str:
    lines = ["💱 <b>قیمت ارزها:</b>\n"]
    currency_names = {
        "usdt": "USDT (تتر)",
        "gram": "Gram (گرام)",
        "trx": "TRX (ترون)"
    }
    for currency, info in prices.items():
        name = currency_names.get(currency, currency.upper())
        price = f"{info['price']:,}"
        updated = info["updated_at"][:16].replace("T", " ")
        lines.append(f"• {name}: <b>{price} تومان</b>\n  🕐 آخرین بروزرسانی: {updated}")
    return "\n\n".join(lines)


def admin_user_list_text(users: list) -> str:
    if not users:
        return "هیچ کاربری یافت نشد."
    lines = [f"👥 <b>لیست کاربران ({len(users)} نفر):</b>\n"]
    for u in users:
        full_name = f"{u['first_name'] or ''} {u['last_name'] or ''}".strip()
        username_text = f"@{u['username']}" if u.get("username") else "-"
        lines.append(f"👤 {full_name}\n🆔 {username_text} • <code>{u['user_id']}</code>")
    return "\n\n".join(lines)


def admin_user_detail_text(user: dict, subscriptions: list, invites: list,
                            inviter: dict = None) -> str:
    full_name = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip()
    username_text = f"@{user['username']}" if user.get("username") else "-"

    subs_text = ""
    for sub in subscriptions:
        battery = "🔋" if sub["sub_remain_volume"] > 0 else "🪫"
        status = "✅" if sub["sub_status"] == "active" else "❌"
        subs_text += f"\n{battery} {sub['sub_username']} {sub['sub_remain_volume']:.2f}/{sub['sub_total_volume']:.2f} GB {status}"

    invites_text = ""
    for inv in invites[:5]:
        inv_name = f"{inv['first_name'] or ''} {inv['last_name'] or ''}".strip()
        invites_text += f"\n  👤 {inv_name}"
    if len(invites) > 5:
        invites_text += f"\n  و {len(invites)-5} نفر دیگر..."

    inviter_text = ""
    if inviter:
        inv_name = f"{inviter['first_name'] or ''} {inviter['last_name'] or ''}".strip()
        inv_username = f"@{inviter['username']}" if inviter.get("username") else "-"
        inviter_text = f"\n\n👆 دعوت شده توسط: {inv_name} ({inv_username})"

    return f"""
👤 <b>اطلاعات کاربر:</b>
نام: {full_name}
🆔 {username_text} • <code>{user['user_id']}</code>
📅 تاریخ عضویت: {user['join_date'][:10]}

📶 <b>اشتراک‌ها:</b>{subs_text if subs_text else chr(10) + "  ندارد"}

👥 <b>دعوت شدگان ({len(invites)} نفر):</b>{invites_text if invites_text else chr(10) + "  ندارد"}{inviter_text}
"""


def admin_message_confirm_text(target: str) -> str:
    return f"""
📨 شما می‌خواهید به <b>{target}</b> پیام ارسال کنید.

پیام خود را با <b>ریپلای</b> روی همین پیام ارسال کنید.
"""


def admin_message_sent_text(count: int) -> str:
    return f"✅ پیام به <b>{count} کاربر</b> ارسال شد."
