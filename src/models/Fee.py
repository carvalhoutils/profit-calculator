from decimal import Decimal

from pydantic import BaseModel


class Fee(BaseModel):
    id: str
    name: str
    amount: Decimal
