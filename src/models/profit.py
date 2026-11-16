from decimal import Decimal

from pydantic import BaseModel, Field

from src.models.fee import Fee
from src.utils.uuid import generate_uuid


class Profit(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    price_cost: Decimal
    price_sale: Decimal
    after_fees: Decimal
    profit: Decimal

    fees: list[Fee] = Field(default_factory=list)
