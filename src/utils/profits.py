from decimal import Decimal
from typing import Iterable

from src.models.fee import Fee


def calculate_profits(
    price_sale: Decimal,
    price_cost: Decimal,
    fees: Iterable[Fee],
) -> tuple[Decimal, Decimal]:
    after_fees = price_sale - sum((fee.amount for fee in fees), Decimal("0"))
    profit = after_fees - price_cost
    return after_fees, profit
