"""Draft/review contracts; no persistence or automatic extraction is implied."""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal, get_args
from uuid import UUID

from pydantic import (
    AwareDatetime, BaseModel, BeforeValidator, ConfigDict, Field,
    StringConstraints, field_serializer, model_validator,
)


FieldState = Literal["missing", "unclear", "proposed", "confirmed"]
RecordStage = Literal["unknown", "quote", "approved_scope", "completed_work"]
DataOrigin = Literal["synthetic_demo", "private_source"]
ReviewField = Literal[
    "job_reference", "customer_reference", "vehicle_reference", "make", "model",
    "quotation_date", "date_in", "date_out", "currency", "diagram_notes",
    "written_total", "written_adjustment", "written_grand_total",
]
Reference = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Description = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
RawNote = Annotated[str, Field(max_length=10000)]
Currency = Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]


def _decimal_input(value):
    # Floats may already have lost precision before Decimal sees them.
    if isinstance(value, (float, bool)):
        raise ValueError("Amounts require decimal strings, Decimal values or whole integers")
    return value


SignedMoney = Annotated[
    Decimal, BeforeValidator(_decimal_input),
    Field(
        max_digits=12, decimal_places=2, allow_inf_nan=False,
        gt=Decimal("-10000000000"), lt=Decimal("10000000000"),
    ),
]
Money = Annotated[SignedMoney, Field(ge=0)]


def _validate_state(name, value, state):
    if state == "missing" and value is not None:
        raise ValueError(f"{name}: a missing field cannot have a value")
    if state in {"proposed", "confirmed"} and value is None:
        raise ValueError(f"{name}: {state} requires a value")


class _WorkshopSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")


class WorkshopItem(_WorkshopSchema):
    description_raw: RawNote = ""
    description: Description | None = None
    description_state: FieldState = "missing"
    amount_raw: Annotated[str, Field(max_length=200)] = ""
    amount: Money | None = None
    amount_state: FieldState = "missing"
    cancelled: bool = False

    @model_validator(mode="after")
    def consistent_states(self):
        _validate_state("description", self.description, self.description_state)
        _validate_state("amount", self.amount, self.amount_state)
        return self

    @field_serializer("amount", when_used="json")
    def serialize_amount(self, value):
        return None if value is None else format(value, ".2f")


class WorkshopDraft(_WorkshopSchema):
    data_origin: DataOrigin
    source_document_id: UUID | None = None
    manual_provenance: Description | None = None
    record_stage: RecordStage = "unknown"
    job_reference: Reference | None = None
    customer_reference: Reference | None = None
    vehicle_reference: Reference | None = None
    make: Reference | None = None
    model: Reference | None = None
    quotation_date: date | None = None
    date_in: date | None = None
    date_out: date | None = None
    date_note_raw: RawNote = ""
    currency: Currency | None = None
    items: list[WorkshopItem] = Field(default_factory=list, max_length=50)
    diagram_notes_raw: RawNote = ""
    diagram_notes: Description | None = None
    written_totals_raw: RawNote = ""
    written_total: Money | None = None
    written_adjustment: SignedMoney | None = None
    written_grand_total: Money | None = None
    field_states: dict[ReviewField, FieldState] = Field(default_factory=dict)

    def field_state(self, name: ReviewField) -> FieldState:
        # Supplied values remain provisional unless their status is explicit.
        return self.field_states.get(name, "missing" if getattr(self, name) is None else "proposed")

    @model_validator(mode="after")
    def consistent_states(self):
        for name, state in self.field_states.items():
            _validate_state(name, getattr(self, name), state)
        return self

    @field_serializer("written_total", "written_adjustment", "written_grand_total", when_used="json")
    def serialize_money(self, value):
        return None if value is None else format(value, ".2f")


class WorkshopReviewedDraft(WorkshopDraft):
    """Validation gate; database snapshot immutability is a later service feature."""

    @model_validator(mode="after")
    def ready_for_reviewed_record(self):
        if self.record_stage == "unknown":
            raise ValueError("Review requires an explicit record stage")
        if self.job_reference is None:
            raise ValueError("Review requires a job reference")
        if self.source_document_id is None and self.manual_provenance is None:
            raise ValueError("Review requires a source document or manual provenance")
        for name in get_args(ReviewField):
            state = self.field_state(name)
            if state in {"unclear", "proposed"}:
                raise ValueError(f"Review requires resolving {name}")
        active = [item for item in self.items if not item.cancelled]
        if not active:
            raise ValueError("Review requires at least one active item")
        for item in active:
            if item.description_state != "confirmed":
                raise ValueError("Review requires confirmed active item descriptions")
            if item.amount_state in {"unclear", "proposed"}:
                raise ValueError("Review requires resolving active item amounts")
        has_amount = any(item.amount is not None for item in active) or any(
            getattr(self, name) is not None
            for name in ("written_total", "written_adjustment", "written_grand_total")
        )
        if has_amount and self.currency is None:
            raise ValueError("Review requires an explicit currency when amounts are supplied")
        return self


class WorkshopReviewedRevision(_WorkshopSchema):
    job_id: UUID
    version: int = Field(ge=1, strict=True)
    record: WorkshopReviewedDraft
    reviewer: Reference
    reviewed_at: AwareDatetime


class WorkshopDraftUpdate(_WorkshopSchema):
    expected_version: int = Field(ge=1, strict=True)
    draft: WorkshopDraft


class WorkshopJobResponse(_WorkshopSchema):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    draft: WorkshopDraft
    draft_version: int
    created_at: datetime
    updated_at: datetime


class WorkshopDocumentResponse(_WorkshopSchema):
    id: UUID
    media_type: str
    byte_size: int
    data_origin: DataOrigin
    duplicate: bool
