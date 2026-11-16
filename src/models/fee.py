from decimal import Decimal

from pydantic import BaseModel, Field

from src.utils.uuid import generate_uuid


class Fee(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    amount: Decimal
