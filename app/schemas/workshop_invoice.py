"""SGD billing contracts, separate from captured source totals."""
from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, Field, field_serializer, model_validator

from app.schemas.workshop import _WorkshopSchema, Reference, Description, Money, DataOrigin


class InvoiceParty(_WorkshopSchema):
    name: Reference
    address: Description


class InvoiceSupplier(InvoiceParty):
    gst_status: Literal["registered", "not_registered"]
    gst_registration_number: Reference | None = None

    @model_validator(mode="after")
    def registration(self):
        if (self.gst_status == "registered") != (self.gst_registration_number is not None):
            raise ValueError("Registered suppliers need a GST number; non-registered suppliers must omit it")
        return self


class InvoiceRequest(_WorkshopSchema):
    supplier: InvoiceSupplier
    customer: InvoiceParty
    invoice_date: date
    pricing_basis: Literal["inclusive", "exclusive"]
    discount: Money = 0

    @field_serializer("discount", when_used="json")
    def serialize_discount(self, value) -> str:
        return format(value, ".2f")


class InvoiceIssueRequest(_WorkshopSchema):
    invoice: InvoiceRequest
    acknowledged: bool = Field(strict=True)

    @model_validator(mode="after")
    def acknowledge_issuance(self):
        if not self.acknowledged:
            raise ValueError("Explicit invoice issuance acknowledgement is required")
        return self


class InvoiceLine(_WorkshopSchema):
    description: Description
    amount: Money

    @field_serializer("amount", when_used="json")
    def serialize_amount(self, value) -> str:
        return format(value, ".2f")


class InvoicePreview(_WorkshopSchema):
    job_id: UUID
    revision_id: UUID
    data_origin: DataOrigin
    job_reference: Reference
    vehicle_reference: Reference | None
    request: InvoiceRequest
    lines: list[InvoiceLine]
    subtotal: Money
    net: Money
    gst: Money
    total: Money
    gst_rate: Literal["9%", "not_applicable"]
    calculation_version: Literal["sgd-invoice-v1"] = "sgd-invoice-v1"

    @field_serializer("subtotal", "net", "gst", "total", when_used="json")
    def serialize_money(self, value) -> str:
        return format(value, ".2f")


class InvoiceResponse(_WorkshopSchema):
    id: UUID
    number: Reference
    preview: InvoicePreview
    issued_by: Reference
    issued_at: AwareDatetime
    checksum: str


class InvoiceSettingsResponse(_WorkshopSchema):
    real_invoices_enabled: bool
    supplier: InvoiceSupplier | None
