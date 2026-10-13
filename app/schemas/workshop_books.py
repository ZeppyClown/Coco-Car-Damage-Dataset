"""Payments, expenses and the workshop's own details."""
from datetime import date
from typing import Annotated, Literal

from pydantic import Field, model_validator

from app.schemas.workshop import Money, Reference, Description, SignedMoney, _WorkshopSchema


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


ExpenseCategory = Literal["parts", "paint", "subcontract", "wages", "rent", "utilities", "tools", "other"]


class ExpenseRequest(_WorkshopSchema):
    """Money paid out (positive) or a supplier refund/correction (negative). Entries are added, never edited."""
    spent_on: date
    supplier: Reference
    category: ExpenseCategory
    description: Annotated[str, Field(max_length=500)] = ""
    supplier_invoice: Annotated[str, Field(max_length=200)] = ""
    job_reference: Annotated[str, Field(max_length=200)] = ""
    amount: SignedMoney
    gst: Money = 0

    @model_validator(mode="after")
    def sensible(self):
        if self.amount == 0:
            raise ValueError("An expense needs an amount")
        if self.gst > abs(self.amount):
            raise ValueError("GST cannot be more than the amount paid")
        return self


class CompanyRequest(_WorkshopSchema):
    """The workshop's own details. Leave the GST number empty if the workshop is not GST-registered."""
    name: Reference
    address: Description
    gst_registration_number: Reference | None = None
    phone: Annotated[str, Field(max_length=200)] = ""


class UserRequest(_WorkshopSchema):
    username: Annotated[str, Field(min_length=1, max_length=50)]
    password: Annotated[str, Field(min_length=1, max_length=1024)]
    role: Literal["owner", "staff"] = "staff"


class UserSwitch(_WorkshopSchema):
    active: bool = Field(strict=True)
