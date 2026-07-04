# =============================================
# subtest.py - اشتراک‌های تست
# =============================================

SUBTEST_ACCOUNTS = [
    {
        "number": 1,
        "username": "PT_SubTest1",
        "link": "https://de.3erveronline.com/sub/djMsNzMyOCwxNzgxNjM4MjA5f476ddde09",
    },
    {
        "number": 2,
        "username": "PT_SubTest2",
        "link": "https://de.3erveronline.com/sub/djMsNzMyOSwxNzgxNjM4MjA52fb8a08921",
    },
    {
        "number": 3,
        "username": "PT_SubTest3",
        "link": "https://de.3erveronline.com/sub/djMsNzMzMCwxNzgxNjM4MjA5150a0ba03c",
    },
    {
        "number": 4,
        "username": "PT_SubTest4",
        "link": "https://de.3erveronline.com/sub/djMsNzMzMSwxNzgxNjM4MjA5a9b0c02d85",
    },
    {
        "number": 5,
        "username": "PT_SubTest5",
        "link": "https://de.3erveronline.com/sub/djMsNzMzMiwxNzgxNjM4MjA5e077d9ce34",
    },
    {
        "number": 6,
        "username": "PT_SubTest6",
        "link": "https://de.3erveronline.com/sub/djMsNzMzMywxNzgxNjM4MjA5eb5d283776",
    },
    {
        "number": 7,
        "username": "PT_SubTest7",
        "link": "https://de.3erveronline.com/sub/djMsNzMzNCwxNzgxNjM4MjA51f71b1e0aa",
    },
    {
        "number": 8,
        "username": "PT_SubTest8",
        "link": "https://de.3erveronline.com/sub/djMsNzMzNSwxNzgxNjM4MjA598fb6144e8",
    },
    {
        "number": 9,
        "username": "PT_SubTest9",
        "link": "https://de.3erveronline.com/sub/djMsNzMzNiwxNzgxNjM4MjA5be6248a072",
    },
    {
        "number": 10,
        "username": "PT_SubTest10",
        "link": "https://de.3erveronline.com/sub/djMsNzMzNywxNzgxNjM4MjA5bfd735e5c9",
    },
]


def get_subtest_by_number(number: int) -> dict | None:
    for account in SUBTEST_ACCOUNTS:
        if account["number"] == number:
            return account
    return None


def get_available_subtest(assigned_numbers: list) -> dict | None:
    """
    دریافت یک اشتراک تست رندوم که هنوز اختصاص داده نشده
    """
    import random
    available = [
        acc for acc in SUBTEST_ACCOUNTS
        if acc["number"] not in assigned_numbers
    ]
    if not available:
        return None
    return random.choice(available)
