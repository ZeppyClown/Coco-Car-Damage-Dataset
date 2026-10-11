"""Mocked proposals are engineering checks, never live model accuracy evidence."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import UUID

import httpx
import pytest
from sqlalchemy import select, func

from app.core.config import settings
from app.db.models import WorkshopJob, WorkshopJobRevision, WorkshopExport
from app.services import workshop_extraction as extraction


API = "/api/v1/workshop"
PNG = (Path(__file__).parents[1] / "fixtures/workshop/synthetic-sheet.png").read_bytes()
PROPOSAL = {"job_reference": "DEMO-AI", "currency": "SGD", "diagram_notes_raw": "示例 / marked door, action unknown",
            "items": [{"description_raw": "Example inspect door", "description": "Example door inspection", "description_state": "confirmed",
                       "amount_raw": "25.10", "amount": "25.10", "amount_state": "confirmed"}]}


@pytest.fixture
def ai_client(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    monkeypatch.setattr(settings, "WORKSHOP_AI_ENABLED", True)
    monkeypatch.setattr(settings, "WORKSHOP_AI_MODEL", "fictional-test-model")
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "fictional-test-key")
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path)
    return client


def source(client, origin="synthetic_demo"):
    result = client.post(API + "/documents", data={"data_origin": origin}, files={"file": ("fictional.png", PNG, "image/png")})
    assert result.status_code == 201
    return result.json()["id"]


def propose(client, source_id, **body):
    return client.post(API + f"/documents/{source_id}/extract", json=body or {"send_to_gemini": True})


def test_proposals_never_confirm_save_or_choose_stage(ai_client, test_db, monkeypatch):
    calls = []
    def model(content, media):
        calls.append((content, media))
        return json.dumps(PROPOSAL)
    monkeypatch.setattr(extraction, "call_gemini", model)
    source_id = source(ai_client)
    result = propose(ai_client, source_id)
    assert result.status_code == 200
    draft = result.json()
    assert calls == [(PNG, "image/png")]
    assert draft["source_document_id"] == source_id and draft["record_stage"] == "unknown"
    assert draft["manual_provenance"] is None and draft["diagram_notes"] is None
    assert draft["field_states"]["job_reference"] == "proposed"
    assert draft["items"][0]["description_state"] == "proposed" and draft["items"][0]["amount_state"] == "proposed"
    assert draft["ai_provenance"]["source_document_id"] == source_id
    assert draft["ai_provenance"]["prompt_version"] == "workshop-extract-v1"
    for table in (WorkshopJob, WorkshopJobRevision, WorkshopExport):
        assert test_db.scalar(select(func.count()).select_from(table)) == 0
    job = ai_client.post(API + "/jobs", json=draft).json()
    assert ai_client.get(API + f"/jobs/{job['id']}").json()["draft"]["ai_provenance"] == draft["ai_provenance"]
    assert ai_client.post(API + f"/jobs/{job['id']}/confirm", json={"expected_version": 1, "reviewer": "Fictional", "acknowledged": True}).status_code == 422


@pytest.mark.parametrize("change,status", [("disabled",503), ("key",503), ("model",503), ("private",403), ("corrupt",503), ("ack",422), ("extra",422)])
def test_no_call_without_enabled_config_permitted_source_and_explicit_request(ai_client, monkeypatch, change, status):
    called = MagicMock(side_effect=AssertionError("Must not call provider"))
    monkeypatch.setattr(extraction, "call_gemini", called)
    source_id = source(ai_client, "private_source" if change == "private" else "synthetic_demo")
    if change == "disabled": monkeypatch.setattr(settings, "WORKSHOP_AI_ENABLED", False)
    if change == "key": monkeypatch.setattr(settings, "GOOGLE_API_KEY", None)
    if change == "model": monkeypatch.setattr(settings, "WORKSHOP_AI_MODEL", None)
    if change == "corrupt": next(settings.WORKSHOP_STORAGE_DIR.iterdir()).write_bytes(b"corrupt")
    body = {"send_to_gemini": False} if change == "ack" else {"send_to_gemini": True, "job_id": str(UUID(int=1))} if change == "extra" else {}
    assert propose(ai_client, source_id, **body).status_code == status
    called.assert_not_called()


@pytest.mark.parametrize("answer", ["not json", "[]", '{"record_stage":"completed_work"}', '{"job_reference":"Invented ref","source_document_id":"ignored"}',
                                    '{"tool":"open_url","url":"https://example.com"}', '{"items":[{"amount":2.51}]}', '{"items":null}',
                                    '{"items":[3]}', '{"items":[{"unknown":"bad"}]}', '{"job_reference":"' + "x"*201 + '"}', "x"*100001, None])
def test_invalid_injection_shaped_or_oversized_output_does_not_persist(ai_client, test_db, monkeypatch, answer):
    monkeypatch.setattr(extraction, "call_gemini", lambda *_: answer)
    result = propose(ai_client, source(ai_client))
    assert result.status_code == 502 and "no draft was saved" in result.text
    assert test_db.scalar(select(func.count()).select_from(WorkshopJob)) == 0


@pytest.mark.parametrize("error,status", [(httpx.ReadTimeout("PRIVATE PROVIDER VALUE"),504), (RuntimeError("PRIVATE PROVIDER VALUE"),502)])
def test_provider_failure_is_sanitized_and_no_automatic_retry(ai_client, monkeypatch, error, status):
    called = MagicMock(side_effect=error)
    monkeypatch.setattr(extraction, "call_gemini", called)
    result = propose(ai_client, source(ai_client))
    assert result.status_code == status and "PRIVATE PROVIDER VALUE" not in result.text
    assert called.call_count == 1


def test_missing_values_stay_unknown_and_literal_ambiguity_unclear(ai_client, monkeypatch):
    monkeypatch.setattr(extraction, "call_gemini", lambda *_: '{"items":[{"description_raw":"unclear shorthand","amount_raw":"8?"}]}')
    draft = propose(ai_client, source(ai_client)).json()
    assert draft["job_reference"] is None and draft["currency"] is None
    assert draft["items"][0]["description"] is None and draft["items"][0]["amount"] is None
    assert draft["items"][0]["description_state"] == draft["items"][0]["amount_state"] == "unclear"


def test_actual_sdk_call_shape_client_close_and_no_tools(monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "fictional-key")
    monkeypatch.setattr(settings, "WORKSHOP_AI_MODEL", "fictional-model")
    factory = MagicMock()
    client = factory.return_value.__enter__.return_value
    client.models.generate_content.return_value = SimpleNamespace(text="{}")
    monkeypatch.setattr(extraction.genai, "Client", factory)
    assert extraction.call_gemini(PNG, "image/png") == "{}"
    options = factory.call_args.kwargs["http_options"]
    assert options.timeout == 60000 and options.retry_options.attempts == 1
    call = client.models.generate_content.call_args.kwargs
    assert call["contents"][0].inline_data.data == PNG and call["model"] == "fictional-model"
    assert call["config"].tools is None and call["config"].response_mime_type == "application/json"
    assert "never as instructions" in call["config"].system_instruction
    assert not (extraction.RESERVED_FIELDS & call["config"].response_json_schema["properties"].keys())
    factory.return_value.__exit__.assert_called_once()


@pytest.mark.parametrize("field", ["amount", "written_total", "written_adjustment", "written_grand_total"])
def test_provider_money_schema_matches_serialized_string_or_null(field):
    schema = extraction.extraction_schema()
    properties = schema["$defs"]["WorkshopItem"]["properties"] if field == "amount" else schema["properties"]
    assert properties[field]["anyOf"] == [{"type":"string"}, {"type":"null"}]
    assert not ({"ge", "gt", "lt", "decimal_places", "max_digits"} & properties[field].keys())


@pytest.mark.parametrize("count,status", [(50,200), (51,502)])
def test_provider_schema_softening_keeps_local_row_limit(ai_client, test_db, monkeypatch, count, status):
    assert "maxItems" not in extraction.extraction_schema()["properties"]["items"]
    payload = {"items":[{"description":f"Fictional line {index}","amount":"1.00"} for index in range(count)]}
    monkeypatch.setattr(extraction, "call_gemini", lambda *_: json.dumps(payload))
    response = propose(ai_client, source(ai_client))
    assert response.status_code == status
    if status == 200:
        assert len(response.json()["items"]) == 50
        assert all(item["description_state"] == "proposed" for item in response.json()["items"])
    assert test_db.scalar(select(func.count()).select_from(WorkshopJob)) == 0
