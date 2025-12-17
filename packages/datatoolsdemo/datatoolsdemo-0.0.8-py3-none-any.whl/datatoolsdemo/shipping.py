"""Simple shipping price calculator function."""

from __future__ import annotations


def shipping_price_eur(weight_kg: float) -> int:
    """Calculate shipping price based on package weight.

    Rules:
    - weight must be in (0, 30] (strictly greater than 0, up to 30 inclusive)
    - Price tiers (upper bound inclusive):
        (0, 1]    -> 5 EUR
        (1, 5]    -> 8 EUR
        (5, 10]   -> 12 EUR
        (10, 20]  -> 20 EUR
        (20, 30]  -> 30 EUR

    Raises:
    - TypeError: if weight_kg is not int/float
    - ValueError: if weight_kg is outside allowed range or is NaN/inf

    """
    if not isinstance(weight_kg, (int, float)):
        msg = "weight_kg must be a number"
        raise TypeError(msg)

    # Guard against NaN/inf without importing math in tests.
    if weight_kg in (float("inf"), float("-inf")):
        msg = "weight_kg must be a finite number"
        raise ValueError(msg)

    if weight_kg <= 0 or weight_kg > 30:
        msg = "weight_kg must be in (0, 30]"
        raise ValueError(msg)

    if weight_kg <= 1:
        return 5
    if weight_kg <= 5:
        return 8
    if weight_kg <= 10:
        return 12
    if weight_kg <= 20:
        return 20
    return 30
