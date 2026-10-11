"""Evaluator denominators/failures are checked; mocked scores are not outcomes."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.evaluate_workshop import Label, Prediction, evaluate, read_jsonl


FIXTURES = Path(__file__).parents[1] / "fixtures/workshop"


def fixtures():
    return read_jsonl(FIXTURES / "evaluation-labels.jsonl", Label), read_jsonl(FIXTURES / "evaluation-mocked-predictions.jsonl", Prediction)


def test_authored_imperfect_fixture_exact_denominators_and_failures():
    labels, predictions = fixtures()
    report = evaluate(labels, predictions, prediction_kind="mocked")
    assert report["is_company_outcome"] is False and report["prediction_kind"] == "mocked"
    group = report["by_origin"]["synthetic_demo"]
    assert group["cases"] == 3 and group["failed_cases"] == {"timeout": 1}
    identity = group["by_category"]["identity"]
    assert (identity["resolved"], identity["correct"], identity["incorrect"], identity["missing_prediction"]) == (5,2,1,2)
    amounts = group["by_category"]["amount"]
    assert (amounts["resolved"], amounts["correct"], amounts["incorrect"], amounts["values_proposed_for_unknown"]) == (2,1,1,2)
    assert group["by_category"]["description"]["values_proposed_for_unknown"] == 1
    assert group["by_category"]["literal"]["values_proposed_for_unknown"] == 0, "Empty raw text is absent, not fabricated"
    assert group["by_category"]["date"]["resolved_value_accuracy"] is None
    assert group["cancelled_values_excluded"] == 2 and group["missing_items"] == 2
    assert group["critical_errors"] == {"identity": 3, "amount": 1, "description": 1, "cancellation": 2}
    serialized = json.dumps(report)
    assert "Fictional WRONG Person" not in serialized and "fictional-clean" not in serialized


def test_supplied_perfect_values_do_not_turn_unknowns_or_cancelled_values_into_accuracy():
    labels, _ = fixtures()
    predictions = [{"case_id": row.case_id, "record": row.record.model_dump(mode="json")} for row in labels]
    group = evaluate(labels, predictions, prediction_kind="manual")["by_origin"]["synthetic_demo"]
    assert group["failed_cases"] == {} and group["critical_errors"] == dict.fromkeys(("identity", "amount", "description", "cancellation"), 0)
    assert group["by_category"]["amount"]["resolved"] == 2
    assert group["by_category"]["amount"]["unknown_expected"] == 13
    assert group["by_category"]["amount"]["values_proposed_for_unknown"] == 0
    assert group["by_category"]["literal"]["resolved"] == 8
    assert group["cancelled_values_excluded"] == 2


def test_missing_row_and_extra_row_are_explicit_and_missing_unknown_is_not_observed():
    labels, _ = fixtures()
    label = labels[1]
    empty = {"case_id": label.case_id, "record": {"data_origin": "synthetic_demo"}}
    group = evaluate([label], [empty], prediction_kind="mocked")["by_origin"]["synthetic_demo"]
    assert group["missing_items"] == 1 and group["by_category"]["amount"]["unknown_not_observed"] == 1
    record = label.record.model_dump(mode="json")
    record["items"].append({"description": "Extra invented row", "description_state": "proposed"})
    group = evaluate([label], [{"case_id": label.case_id, "record": record}], prediction_kind="mocked")["by_origin"]["synthetic_demo"]
    assert group["unexpected_items"] == 1


def test_zero_canonical_decimal_and_unknown_amount_are_different():
    labels, _ = fixtures()
    label = labels[0].model_dump(mode="json")
    label["record"]["items"][0]["amount"] = "0.00"
    predicted = deepcopy(label["record"])
    predicted["items"][0].update(amount="0", amount_state="proposed")
    group = evaluate([label], [{"case_id": label["case_id"], "record": predicted}], prediction_kind="mocked")["by_origin"]["synthetic_demo"]
    assert group["by_category"]["amount"]["correct"] == 2
    predicted["items"][0].update(amount=None, amount_state="missing")
    group = evaluate([label], [{"case_id": label["case_id"], "record": predicted}], prediction_kind="mocked")["by_origin"]["synthetic_demo"]
    assert group["by_category"]["amount"]["missing_prediction"] == 1


def test_declared_private_origin_kept_separate_from_synthetic_metrics():
    labels, _ = fixtures()
    private = labels[0].model_dump(mode="json")
    private.update(case_id="fictional-private-boundary", label_source="independent_company_review", source_note="Fictional test of a private-origin boundary, not real company labels.")
    private["record"]["data_origin"] = "private_source"
    combined = [labels[0], private]
    predictions = [{"case_id": row.case_id, "record": row.record.model_dump(mode="json")} for row in (Label.model_validate(item) for item in combined)]
    report = evaluate(combined, predictions, prediction_kind="manual")
    assert {key: value["cases"] for key, value in report["by_origin"].items()} == {"synthetic_demo":1, "private_source":1}
    assert report["is_company_outcome"] is False


@pytest.mark.parametrize("change", ["empty", "missing_prediction", "unlabelled_prediction", "duplicate_label", "duplicate_prediction", "proposed_label", "wrong_origin", "no_resolved_fields", "invalid_kind", "wrong_label_source", "both_result_and_failure"])
def test_incomplete_or_unreliable_inputs_fail(change):
    labels, predictions = fixtures()
    labels = [row.model_dump(mode="json") for row in labels]
    predictions = [row.model_dump(mode="json") for row in predictions]
    kind = "mocked"
    if change == "empty": labels, predictions = [], []
    if change == "missing_prediction": predictions.pop()
    if change == "unlabelled_prediction": predictions.append({"case_id":"unlabelled", "failure":"timeout"})
    if change == "duplicate_label": labels.append(labels[0])
    if change == "duplicate_prediction": predictions.append(predictions[0])
    if change == "proposed_label": labels[0]["record"]["field_states"]["job_reference"] = "proposed"
    if change == "wrong_origin": predictions[0]["record"]["data_origin"] = "private_source"
    if change == "no_resolved_fields":
        labels = [{**labels[0], "record":{"data_origin":"synthetic_demo"}}]
        predictions = [{"case_id":labels[0]["case_id"], "record":{"data_origin":"synthetic_demo"}}]
    if change == "invalid_kind": kind = "unspecified"
    if change == "wrong_label_source": labels[0]["label_source"] = "independent_company_review"
    if change == "both_result_and_failure": predictions[0]["failure"] = "timeout"
    with pytest.raises(ValueError):
        evaluate(labels, predictions, prediction_kind=kind)


def test_cli_report_and_sanitized_invalid_label_error(tmp_path):
    command = [sys.executable, "-m", "scripts.evaluate_workshop", "--labels", str(FIXTURES / "evaluation-labels.jsonl"),
               "--predictions", str(FIXTURES / "evaluation-mocked-predictions.jsonl"), "--prediction-kind", "mocked"]
    good = subprocess.run(command, capture_output=True, text=True)
    assert good.returncode == 0 and json.loads(good.stdout)["by_origin"]["synthetic_demo"]["cases"] == 3
    path = tmp_path / "invalid.jsonl"
    path.write_text('{"PRIVATE LABEL VALUE":"invalid"}\n')
    command[4] = str(path)
    bad = subprocess.run(command, capture_output=True, text=True)
    assert bad.returncode == 2 and bad.stdout == "" and "PRIVATE LABEL VALUE" not in bad.stderr
