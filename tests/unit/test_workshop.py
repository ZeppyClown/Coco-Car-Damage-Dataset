"""Fictional contract checks; no workshop/provider/database evidence is implied."""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.workshop import (
    WorkshopDraft, WorkshopItem, WorkshopReviewedDraft, WorkshopReviewedRevision,
)


EXAMPLES = json.loads(
    (Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text()
)["examples"]


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda example: example["id"])
def test_fictional_drafts_and_review_gates(example):
    draft = WorkshopDraft.model_validate(example["record"])
    assert draft.data_origin == "synthetic_demo"
    if example["reviewable"]:
        reviewed = WorkshopReviewedDraft.model_validate(draft.model_dump())
        assert reviewed.record_stage == draft.record_stage
    else:
        with pytest.raises(ValidationError):
            WorkshopReviewedDraft.model_validate(draft.model_dump())


def test_money_round_trip_null_and_zero_are_distinct():
    record = WorkshopReviewedDraft.model_validate(EXAMPLES[0]["record"])
    encoded = record.model_dump_json()
    assert json.loads(encoded)["items"][0]["amount"] == "25.10"
    assert WorkshopReviewedDraft.model_validate_json(encoded).items[0].amount == Decimal("25.10")
    assert WorkshopItem().amount is None
    zero = WorkshopItem(amount="0", amount_state="confirmed")
    assert zero.amount == Decimal("0")
    assert json.loads(zero.model_dump_json())["amount"] == "0.00"


@pytest.mark.parametrize("amount", [True, 12.3, "NaN", "Infinity", "-1", "1.001", "$12", "1,234", "10000000000"])
def test_invalid_item_amount_rejected(amount):
    with pytest.raises(ValidationError):
        WorkshopItem(amount=amount, amount_state="proposed")


@pytest.mark.parametrize("values", [
    {"amount": "1.00"},
    {"amount_state": "confirmed"},
    {"description": "A value labelled missing"},
    {"description_state": "proposed"},
])
def test_inconsistent_item_states_rejected(values):
    with pytest.raises(ValidationError):
        WorkshopItem(**values)


def test_provisional_scalar_values_and_unknown_dates():
    record = WorkshopDraft(data_origin="synthetic_demo", job_reference="DEMO-NEW", date_note_raw="Friday")
    assert record.field_state("job_reference") == "proposed"
    assert record.field_state("date_out") == "missing"
    assert record.date_out is None
    with pytest.raises(ValidationError):
        WorkshopDraft(data_origin="synthetic_demo", date_out="Friday")


@pytest.mark.parametrize("changes", [
    {"record_stage": "unknown"},
    {"job_reference": None, "field_states": {}},
    {"manual_provenance": None},
    {"currency": None, "field_states": {"job_reference": "confirmed", "customer_reference": "confirmed", "vehicle_reference": "confirmed"}},
    {"field_states": {"job_reference": "proposed"}},
    {"items": []},
    {"items": [{"description": "Not reviewed", "description_state": "proposed"}]},
    {"items": [{"description": "Confirmed", "description_state": "confirmed", "amount_raw": "??", "amount_state": "unclear"}]},
    {"items": [{"description": "Cancelled", "description_state": "confirmed", "cancelled": True}]},
])
def test_review_cannot_promote_unresolved_record(changes):
    data = deepcopy(EXAMPLES[0]["record"])
    data.update(changes)
    with pytest.raises(ValidationError):
        WorkshopReviewedDraft.model_validate(data)


def test_cancelled_values_preserved_but_do_not_supply_reviewed_work():
    data = deepcopy(EXAMPLES[0]["record"])
    data["items"].append({"amount_raw": "80 crossed out", "amount": "80", "amount_state": "proposed", "cancelled": True})
    record = WorkshopReviewedDraft.model_validate(data)
    assert record.items[1].cancelled and record.items[1].amount == Decimal("80")
    assert record.items[0].amount == Decimal("25.10")


def test_literal_notes_and_same_name_jobs_remain_separate():
    bilingual = WorkshopDraft.model_validate(EXAMPLES[3]["record"])
    assert bilingual.diagram_notes is None
    assert "车门" in bilingual.diagram_notes_raw
    assert "示例" in bilingual.model_dump_json()
    left = WorkshopReviewedDraft.model_validate(EXAMPLES[0]["record"])
    right = WorkshopReviewedDraft.model_validate(EXAMPLES[4]["record"])
    assert left.customer_reference == right.customer_reference
    assert left.job_reference != right.job_reference
    assert left.vehicle_reference != right.vehicle_reference


@pytest.mark.parametrize("values", [
    {"data_origin": "company_production"},
    {"record_stage": "paid"},
    {"items": [{"description_raw": "x" * 10001}]},
    {"items": [{}] * 51},
    {"field_states": {"invented_field": "confirmed"}},
    {"field_states": {"job_reference": "confirmed"}},
    {"job_reference": "DEMO", "field_states": {"job_reference": "missing"}},
    {"currency": "sgd"},
    {"job_reference": "   "},
    {"invoice_paid": True},
])
def test_invalid_extra_and_oversized_input_rejected(values):
    data = {"data_origin": "synthetic_demo", **values}
    with pytest.raises(ValidationError):
        WorkshopDraft.model_validate(data)


def test_reviewed_revision_requires_real_metadata_shape():
    data = {
        "job_id": "00000000-0000-4000-8000-000000000001",
        "version": 1,
        "record": EXAMPLES[0]["record"],
        "reviewer": "Fictional demo reviewer",
        "reviewed_at": "2026-10-11T12:00:00+08:00",
    }
    revision = WorkshopReviewedRevision.model_validate(data)
    assert revision.record.record_stage == "quote"
    for field, value in [("reviewer", " "), ("version", True), ("version", 0), ("reviewed_at", "2026-10-11T12:00:00")]:
        with pytest.raises(ValidationError):
            WorkshopReviewedRevision.model_validate({**data, field: value})


def test_written_adjustment_is_literal_not_an_inferred_tax_rule():
    record = WorkshopDraft(data_origin="synthetic_demo", written_adjustment="-2.50", written_totals_raw="Fictional discount note")
    assert json.loads(record.model_dump_json())["written_adjustment"] == "-2.50"
    assert record.field_state("written_adjustment") == "proposed"
    assert record.written_grand_total is None


def test_money_boundary_and_linked_source_review():
    data = deepcopy(EXAMPLES[0]["record"])
    data["manual_provenance"] = None
    data["source_document_id"] = "00000000-0000-4000-8000-000000000002"
    data["items"][0]["amount"] = "9999999999.99"
    reviewed = WorkshopReviewedDraft.model_validate(data)
    assert reviewed.source_document_id is not None
    assert reviewed.items[0].amount == Decimal("9999999999.99")
    for value in ("-10000000000", "10000000000"):
        with pytest.raises(ValidationError):
            WorkshopDraft(data_origin="synthetic_demo", written_adjustment=value)


def test_mutated_item_is_revalidated_and_raw_text_preserved():
    item = WorkshopItem(description_raw="  Literal note\n", description="Confirmed", description_state="confirmed")
    assert item.description_raw == "  Literal note\n"
    item.amount = Decimal("-1")
    item.amount_state = "confirmed"
    with pytest.raises(ValidationError):
        WorkshopDraft(data_origin="synthetic_demo", items=[item])
