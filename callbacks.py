# =============================================
# callbacks.py - تمامی callback data ها
# =============================================

# --- Navigation ---
GO_BACK = "go_back"
GO_BUY = "go_buy"

# --- Channel ---
CHECK_JOIN = "check_join"

# --- Features ---
REQUEST_SUBTEST = "request_subtest"
RECEIVE_SUBTEST = "receive_subtest"

# --- Buy / Order ---
ADD_NEWSUB = "add_newsub"
RANDOM_USERNAME = "random_username"
SHOW_QRCODE = "show_qrcode"
SEND_RECEIPT = "send_receipt"

# Pattern prefixes (برای callback هایی که پارامتر دارن)
PLAN_PREFIX = "plan_"           # plan_20, plan_50, ...
RENEW_PREFIX = "renew_"         # renew_username
APPROVE_RECEIPT_PREFIX = "approve_receipt_"   # approve_receipt_ORDER_ID
REJECT_RECEIPT_PREFIX = "reject_receipt_"     # reject_receipt_ORDER_ID
RESEND_RECEIPT_PREFIX = "resend_receipt_"     # resend_receipt_ORDER_ID

# --- Profile ---
MY_ACCOUNTS = "my_accounts"
MY_POINTS = "my_points"
ADD_ACCOUNT = "add_account"

# --- Subscription Management ---
ACTIVE_SUB = "active_sub"
DISABLE_SUB = "disable_sub"

# Pattern prefixes for subscription
VIEW_SUB_PREFIX = "view_sub_"           # view_sub_username
REVOKE_SUB_PREFIX = "revoke_sub_"       # revoke_sub_username
DELETE_SUB_PREFIX = "delete_sub_"       # delete_sub_username
CONFIRM_PREFIX = "confirm_"             # confirm_action
CANCEL_PREFIX = "cancel_"              # cancel_action

# Confirm actions
CONFIRM_DISABLE = "disable"
CONFIRM_ACTIVE = "active"
CONFIRM_REVOKE = "revoke"
CONFIRM_DELETE = "delete"

# Done actions
DONE_PREFIX = "done_"                   # done_action
DONE_DISABLE = "done_disable"
DONE_ACTIVE = "done_active"

# --- Points ---
INVITE_BANNER = "invite_banner"
CONVERT_POINTS = "convert_points"
CONVERT_POINTS_PREFIX = "convert_pts_"  # convert_pts_10000
CONVERT_ALL_POINTS = "convert_all_points"

# --- Support ---
REPLY_USER = "reply_user"
REPLY_ADMIN = "reply_admin"
CLOSE_TICKET = "close_ticket"
CLOSE_TICKET_PREFIX = "close_ticket_"   # close_ticket_TICKET_ID

# --- Admin Channel ---
ADMIN_SEND_NOW = "admin_send_now"
ADMIN_CANCEL = "admin_cancel"
ADMIN_ADD_BUTTONS = "admin_add_buttons"
# --- Admin User Panel ---
ADMIN_PANEL_PREFIX = "adminp_"   # adminp_ACTION_USERID

# --- Admin Subscription ---
ADMIN_DONE_PREFIX = "admin_done_"       # admin_done_TYPE_ID
