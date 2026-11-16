from typing import List
from decimal import Decimal

from pydantic import BaseModel

from src.models.Fee import Fee
from src.utils.uuid import generate_uuid


class Profit(BaseModel):
    id: str = generate_uuid()
    price_cost: Decimal
    price_sale: Decimal
    after_fees: Decimal
    profit: Decimal

    fees: List[Fee] = []
