from typing import List
from decimal import Decimal

from pydantic import BaseModel

from src.models.Fee import Fee


class Profit(BaseModel):
    id: str
    price_cost: Decimal
    price_sale: Decimal
    after_fees: Decimal
    profit: Decimal

    fees: List[Fee] = []
