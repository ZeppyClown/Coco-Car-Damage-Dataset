"""Payment entries against issued invoices."""
from datetime import date
from typing import Annotated, Literal

from pydantic import Field, model_validator

from app.schemas.workshop import SignedMoney, _WorkshopSchema


class PaymentRequest(_WorkshopSchema):
    """Money received (positive) or refunded (negative). Entries are added, never edited."""
    amount: SignedMoney
    method: Literal["cash", "nets", "paynow", "bank", "other"]
    paid_on: date
    note: Annotated[str, Field(max_length=500)] = ""

    @model_validator(mode="after")
    def not_zero(self):
        if self.amount == 0:
            raise ValueError("A payment or refund needs an amount")
        return self
