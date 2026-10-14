"""The manual assistant and the parts/vehicle tools on a hosted copy: signed-in owner/staff only. Fictional logins and answers."""
import sys
from types import SimpleNamespace

import pytest

from app import assistant as assistant_mount
from app.core.config import settings
from tests.conftest import TEST_OPERATOR, TEST_PASSWORD

sys.path.insert(0, str(assistant_mount.ASSISTANT_DIR))
from web_app import create_app  # noqa: E402

AI_PAGES = ["/assistant/", "/static/index.html"]
AI_APIS = [("post", "/assistant/query"), ("post", "/api/v1/query"), ("post", "/api/v1/parts/identify"),
           ("post", "/api/v1/valuation/estimate"), ("post", "/api/v1/paint-code/lookup"),
           ("get", "/api/v1/specifications/1HGCM82633A004352"), ("post", "/api/v1/diagnostics/troubleshoot")]


class FictionalAssistant:
    def query(self, text):
        return {"response": "Fictional answer to: " + text, "sources": [], "metadata": {}}


@pytest.fixture
def hosted(client, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    monkeypatch.setattr(settings, "WORKSHOP_ONLY", True)
    monkeypatch.setattr(settings, "AI_TOOLS_ENABLED", True)
    (tmp_path / "corpus.json").write_text("{}")
    from starlette.middleware.wsgi import WSGIMiddleware
    monkeypatch.setitem(assistant_mount._loaded, "config", SimpleNamespace(GOOGLE_API_KEY="fictional-key", CHROMA_PERSIST_DIR=tmp_path))
    monkeypatch.setitem(assistant_mount._loaded, "wsgi", WSGIMiddleware(
        create_app(assistant=FictionalAssistant(), feedback_path=tmp_path / "feedback.sqlite")))
    client.auth = None
    return client


def test_strangers_are_sent_to_sign_in_or_refused(hosted):
    for path in AI_PAGES + ["/assistant"]:
        response = hosted.get(path, follow_redirects=False)
        assert response.status_code == 303 and response.headers["location"] == "/workshop/login", path
    for method, path in AI_APIS:
        response = hosted.get(path) if method == "get" else hosted.post(path, json={})
        assert response.status_code == 401, path
    assert hosted.get("/docs").status_code == 404  # everything else stays hidden


def test_signed_in_staff_can_use_the_assistant_and_tools(hosted):
    response = hosted.post("/api/v1/workshop/login", data={"username": TEST_OPERATOR, "password": TEST_PASSWORD}, follow_redirects=False)
    assert response.status_code == 303
    workshop = hosted.get("/workshop").text
    assert 'href="/assistant/"' in workshop and 'href="/static/index.html"' in workshop
    # The page uses relative links; the router sends /assistant on to /assistant/.
    assert hosted.get("/assistant", follow_redirects=False).headers["location"].endswith("/assistant/")
    page = hosted.get("/assistant/")
    assert page.status_code == 200 and "fetch('query'" in page.text and "/assistant/static/style.css" in page.text
    assert hosted.get("/assistant/static/style.css").status_code == 200
    origin = {"origin": "http://127.0.0.1", "sec-fetch-site": "same-origin"}
    answer = hosted.post("/assistant/query", json={"query": "Fictional rattle"}, headers=origin)
    assert answer.status_code == 200 and answer.json()["response"] == "Fictional answer to: Fictional rattle"
    assert hosted.post("/assistant/feedback", json={"query_id": answer.json()["query_id"], "rating": "useful"}, headers=origin).json() == {"success": True}
    assert hosted.post("/assistant/query", json={"query": "x"}, headers={"origin": "https://elsewhere.example"}).status_code == 403
    assert hosted.get("/static/index.html").status_code == 200
    assert hosted.post("/api/v1/query", data={"text": "Find brake pads for 2015 Honda Civic"}, headers=origin).status_code == 200


def test_scripts_can_use_the_tools_with_a_password(hosted):
    hosted.auth = (TEST_OPERATOR, TEST_PASSWORD)
    assert hosted.post("/assistant/query", json={"query": "Fictional squeal"}).status_code == 200


def test_assistant_without_a_key_says_so(hosted, monkeypatch, tmp_path):
    monkeypatch.setitem(assistant_mount._loaded, "config", SimpleNamespace(GOOGLE_API_KEY=None, CHROMA_PERSIST_DIR=tmp_path))
    hosted.auth = (TEST_OPERATOR, TEST_PASSWORD)
    page = hosted.get("/assistant/")
    assert page.status_code == 503 and "not configured yet" in page.text and "GEMINI_API_KEY" in page.text
    assert "not configured yet" in hosted.post("/assistant/query", json={"query": "x"}).json()["error"]


def test_assistant_before_its_library_is_built_says_so(hosted, monkeypatch, tmp_path):
    monkeypatch.setitem(assistant_mount._loaded, "config", SimpleNamespace(GOOGLE_API_KEY="fictional-key", CHROMA_PERSIST_DIR=tmp_path / "missing"))
    hosted.auth = (TEST_OPERATOR, TEST_PASSWORD)
    assert "still preparing" in hosted.get("/assistant/").text


def test_switched_off_tools_stay_hidden_with_no_links(hosted, monkeypatch):
    monkeypatch.setattr(settings, "AI_TOOLS_ENABLED", False)
    hosted.auth = (TEST_OPERATOR, TEST_PASSWORD)
    assert [hosted.get(path).status_code for path in AI_PAGES] == [404, 404]
    assert hosted.post("/api/v1/query", json={}).status_code == 404
    assert "/assistant/" not in hosted.get("/workshop").text
