"""Synthetic buggy code used only as inert lesson data."""


def discounted_total(subtotal_cents: int, discount_percent: int) -> int:
    if subtotal_cents < 0:
        raise ValueError("subtotal must be non-negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount must be between 0 and 100")
    return subtotal_cents - (subtotal_cents * discount_percent // 100)
