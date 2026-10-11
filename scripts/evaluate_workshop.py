"""Compare supplied draft predictions with separate labels; no model/network calls."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Literal, get_args

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from app.schemas.workshop import WorkshopDraft, ReviewField, Reference, Description


CATEGORIES = {
    "identity": {"job_reference", "customer_reference", "vehicle_reference", "make", "model"},
    "amount": {"currency", "written_total", "written_adjustment", "written_grand_total", "item_amount"},
    "description": {"diagram_notes", "item_description"},
    "date": {"quotation_date", "date_in", "date_out"},
    "literal": {"raw"},
    "cancellation": {"cancelled"},
}


class _EvaluationRow(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    case_id: Reference


class Label(_EvaluationRow):
    labeler: Reference
    label_source: Literal["synthetic_authored", "independent_company_review"]
    source_note: Description
    record: WorkshopDraft

    @model_validator(mode="after")
    def label_boundary(self):
        expected_source = "synthetic_authored" if self.record.data_origin == "synthetic_demo" else "independent_company_review"
        if self.label_source != expected_source:
            raise ValueError("Label source must match record origin")
        if any(self.record.field_state(name) == "proposed" for name in get_args(ReviewField)) or any(
            state == "proposed" for item in self.record.items if not item.cancelled
            for state in (item.description_state, item.amount_state)
        ):
            raise ValueError("Expected labels must resolve or explicitly mark uncertainty, never be proposed")
        return self


class Prediction(_EvaluationRow):
    record: WorkshopDraft | None = None
    failure: Literal["timeout", "provider_error", "invalid_response", "disabled"] | None = None

    @model_validator(mode="after")
    def one_result(self):
        if (self.record is None) == (self.failure is None):
            raise ValueError("Supply one prediction record or explicit failure")
        return self


def read_jsonl(path: Path, row_type):
    rows = []
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                rows.append(row_type.model_validate_json(line))
            except ValidationError:
                raise ValueError(f"Invalid {row_type.__name__.lower()} at line {number}") from None
    return rows


def _stats():
    return {"resolved": 0, "correct": 0, "incorrect": 0, "missing_prediction": 0,
            "unknown_expected": 0, "unknown_kept": 0, "values_proposed_for_unknown": 0, "unknown_not_observed": 0}


def _compare(stats, expected, actual, resolved, failed):
    if resolved:
        stats["resolved"] += 1
        if failed or actual is None:
            stats["missing_prediction"] += 1
        elif actual == expected:
            stats["correct"] += 1
        else:
            stats["incorrect"] += 1
    else:
        stats["unknown_expected"] += 1
        stats["unknown_not_observed" if failed else "unknown_kept" if actual is None else "values_proposed_for_unknown"] += 1


def evaluate(labels, predictions, *, prediction_kind: Literal["mocked", "live_model", "manual"]):
    labels = [Label.model_validate(row) for row in labels]
    predictions = [Prediction.model_validate(row) for row in predictions]
    if prediction_kind not in {"mocked", "live_model", "manual"}:
        raise ValueError("Explicit prediction kind is required")
    if not labels:
        raise ValueError("Nonempty expected labels are required")
    expected_ids = {row.case_id for row in labels}
    predicted = {row.case_id: row for row in predictions}
    if len(expected_ids) != len(labels) or len(predicted) != len(predictions):
        raise ValueError("Duplicate case IDs")
    if set(predicted) != expected_ids:
        raise ValueError("Every prediction needs a label and every label needs a prediction or explicit failure")
    groups = {}
    for label in labels:
        prediction = predicted[label.case_id]
        expected, actual = label.record, prediction.record
        if actual is not None and actual.data_origin != expected.data_origin:
            raise ValueError("Prediction and label origins differ")
        group = groups.setdefault(expected.data_origin, {
            "cases": 0, "failed_cases": {}, "by_category": {name: _stats() for name in CATEGORIES},
            "missing_items": 0, "unexpected_items": 0, "cancelled_values_excluded": 0,
        })
        group["cases"] += 1
        if prediction.failure:
            group["failed_cases"][prediction.failure] = group["failed_cases"].get(prediction.failure, 0) + 1
        expected_json = expected.model_dump(mode="json")
        actual_json = actual.model_dump(mode="json") if actual is not None else {}
        def compare(category, value, candidate, resolved, not_observed=False):
            _compare(group["by_category"][category], value, candidate, resolved, actual is None or not_observed)
        for name in get_args(ReviewField):
            category = next(key for key, names in CATEGORIES.items() if name in names)
            compare(category, expected_json[name], actual_json.get(name), expected.field_state(name) == "confirmed")
        for name in ("date_note_raw", "diagram_notes_raw", "written_totals_raw"):
            compare("literal", expected_json[name], actual_json.get(name) or None, bool(expected_json[name]))
        predicted_items = actual_json.get("items", [])
        group["missing_items"] += max(0, len(expected.items) - len(predicted_items))
        group["unexpected_items"] += max(0, len(predicted_items) - len(expected.items))
        for index, item in enumerate(expected.items):
            missing_row = index >= len(predicted_items)
            candidate = predicted_items[index] if not missing_row else {}
            compare("cancellation", item.cancelled, candidate.get("cancelled"), True, missing_row)
            for raw in ("description_raw", "amount_raw"):
                compare("literal", getattr(item, raw), candidate.get(raw) or None, bool(getattr(item, raw)), missing_row)
            if item.cancelled:
                group["cancelled_values_excluded"] += 2
                continue
            compare("description", expected_json["items"][index]["description"], candidate.get("description"), item.description_state == "confirmed", missing_row)
            compare("amount", expected_json["items"][index]["amount"], candidate.get("amount"), item.amount_state == "confirmed", missing_row)
    for group in groups.values():
        for stats in group["by_category"].values():
            stats["resolved_value_accuracy"] = stats["correct"] / stats["resolved"] if stats["resolved"] else None
        group["critical_errors"] = {
            name: stats["incorrect"] + stats["missing_prediction"]
            for name, stats in group["by_category"].items() if name in {"identity", "amount", "description", "cancellation"}
        }
    if not any(stats["resolved"] for group in groups.values() for stats in group["by_category"].values()):
        raise ValueError("Labels contain no resolved fields")
    return {
        "report_version": "workshop-field-comparison-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
        "prediction_kind": prediction_kind, "is_company_outcome": False,
        "metric": "Exact canonical resolved-value comparison; unknown/cancelled values have separate denominators",
        "label_provenance": "Supplied by the label file; independence/authority not verified by this evaluator",
        "excluded_metadata": ["record_stage", "data_origin", "source_document_id", "manual_provenance", "ai_provenance", "review states"],
        "item_alignment": "Original row order; extra/missing rows reported, no fuzzy matching",
        "by_origin": groups,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--prediction-kind", choices=("mocked", "live_model", "manual"), required=True)
    args = parser.parse_args()
    try:
        report = evaluate(read_jsonl(args.labels, Label), read_jsonl(args.predictions, Prediction), prediction_kind=args.prediction_kind)
    except (ValueError, OSError):
        parser.exit(2, "Evaluation failed: check file access, schemas, matching case IDs and resolved labels. No report generated.\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
