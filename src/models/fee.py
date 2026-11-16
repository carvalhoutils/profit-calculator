from decimal import Decimal

from pydantic import BaseModel

from src.utils.uuid import generate_uuid


class Fee(BaseModel):
    id: str = generate_uuid()
    name: str
    amount: Decimal
