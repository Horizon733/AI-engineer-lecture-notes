"""Deliberately buggy module for Code Reviewer / Debug Buddy to practice on.

Teaching goal: give students a concrete file to point the agent at. Three
bugs hidden here — off-by-one in average(), missing return in find_user(),
wrong variable name in total_price().
"""


def average(numbers):
    total = 0
    for i in range(len(numbers) - 1):   # bug: off-by-one, skips the last item
        total += numbers[i]
    return total / len(numbers)


USERS = [
    {"id": 1, "name": "Asha"},
    {"id": 2, "name": "Rohit"},
    {"id": 3, "name": "Meera"},
]


def find_user(user_id):
    for u in USERS:
        if u["id"] == user_id:
            u                           # bug: forgot `return u`
    return None


def total_price(items, tax_rate=0.18):
    subtotal = sum(item["price"] for item in items)
    tax = subtotal * tax_rate
    return subtotal + taxx              # bug: typo `taxx` instead of `tax`
