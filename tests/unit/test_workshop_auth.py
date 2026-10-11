"""Access/attribution boundaries; all credentials and records are fictional."""
import asyncio
import json
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.security import HTTPBasicCredentials
from pydantic import SecretStr
import pytest

from app.core.config import settings
from app.core.workshop_auth import WorkshopAccessMiddleware, hash_password, _configuration, _verify
from app.api.v1.workshop import require_workshop_enabled

API = "/api/v1/workshop"
PASSWORD = "Fictional tests only password 2026"
EXAMPLE = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())["examples"][0]["record"]


@pytest.fixture
def auth_client(client, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    return client


@pytest.mark.parametrize("path", ["/workshop", "/workshop/", API+"/jobs", API+"/documents/"+str(uuid4())+"/preview", API+"/exports/"+str(uuid4())+"/download"])
def test_protected_surfaces_challenge_before_lookup(auth_client, path):
    response = auth_client.get(path, auth=None)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == 'Basic realm="Workshop"'
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("header", ["Basic !!!", "Basic dXNlcg==", "Bearer fictional", "Basic " + "A"*4096], ids=["invalid-base64","missing-colon","wrong-scheme","oversized"])
def test_malformed_or_wrong_credentials_never_expose_data(auth_client, header):
    response = auth_client.get(API+"/jobs", auth=None, headers={"Authorization":header})
    assert response.status_code == 401 and "www-authenticate" in response.headers
    assert PASSWORD not in response.text


def test_correct_credentials_private_response_and_html_escaping(auth_client, monkeypatch):
    assert auth_client.get(API+"/jobs").status_code == 200
    schema = auth_client.get("/openapi.json", auth=None).json()
    assert schema["components"]["securitySchemes"]["HTTPBasic"] == {"type":"http", "scheme":"basic"}
    assert {"HTTPBasic":[]} in schema["paths"][API+"/jobs"]["post"]["security"]
    username = 'fictional-<operator>"'
    monkeypatch.setattr(settings, "WORKSHOP_AUTH_USERNAME", username)
    page = auth_client.get("/workshop", auth=(username, PASSWORD))
    assert page.status_code == 200 and page.headers["cache-control"] == "no-store"
    assert 'fictional-&lt;operator&gt;&quot;' in page.text and 'readonly' in page.text
    assert auth_client.get("/workshop", auth=(username, "wrong fictional password")).status_code == 401
    assert auth_client.get("/workshop", auth=("other fictional operator", PASSWORD)).status_code == 401
    assert auth_client.get("/static/workshop.html", auth=None).status_code == 404


@pytest.mark.parametrize("headers", [{"Origin":"https://example.invalid"}, {"Origin":"null"}, {"Origin":"http://127.0.0.1:80@evil.invalid"}, {"Sec-Fetch-Site":"cross-site"}, {"Sec-Fetch-Site":"same-site"}, {"Host":"localhost"}, {"Host":"127.0.0.1:bad"}])
def test_cross_origin_requests_rejected_before_body(auth_client, headers):
    response = auth_client.post(API+"/documents", content=b"unparseable body", headers={**headers,"Content-Type":"multipart/form-data"})
    assert response.status_code == 403 and response.headers["cache-control"] == "no-store"


def test_same_origin_browser_and_cli_are_supported(auth_client):
    response = auth_client.get(API+"/jobs", headers={"Origin":"http://127.0.0.1:80", "Sec-Fetch-Site":"same-origin"})
    assert response.status_code == 200
    assert auth_client.get(API+"/jobs").status_code == 200


def test_unauthenticated_upload_does_not_read_any_body(auth_client):
    async def run():
        messages = []
        async def receive():
            raise AssertionError("Unauthenticated body must not be read")
        async def downstream(*args):
            raise AssertionError("Unauthenticated request must not reach parser/router")
        async def send(message):
            messages.append(message)
        scope = {"type":"http", "method":"POST", "path":API+"/documents", "scheme":"http", "server":("127.0.0.1",80), "headers":[(b"host",b"127.0.0.1"),(b"content-type",b"multipart/form-data")], "query_string":b""}
        await WorkshopAccessMiddleware(downstream)(scope, receive, send)
        assert messages[0]["status"] == 401
    asyncio.run(run())
    assert auth_client.post(API+"/documents", auth=None, content=b"invalid multipart", headers={"Content-Type":"multipart/form-data"}).status_code == 401


@pytest.mark.parametrize("name,value", [("WORKSHOP_AUTH_USERNAME",None), ("WORKSHOP_AUTH_USERNAME","name:password"), ("WORKSHOP_AUTH_PASSWORD_HASH",None), ("WORKSHOP_AUTH_PASSWORD_HASH",SecretStr("scrypt$2$8$1$bad$bad")), ("WORKSHOP_AUTH_PASSWORD_HASH",SecretStr("scrypt$16384$8$5$bad$bad")), ("WORKSHOP_ORIGIN",None), ("WORKSHOP_ORIGIN","http://example.invalid"), ("WORKSHOP_ORIGIN","http://127.0.0.1/path"), ("WORKSHOP_ORIGIN","http://@127.0.0.1"), ("WORKSHOP_ORIGIN","http://127.0.0.1:0")])
def test_missing_invalid_configuration_fails_closed(auth_client, monkeypatch, name, value):
    monkeypatch.setattr(settings, name, value)
    response = auth_client.get("/workshop")
    assert response.status_code == 503 and "not configured" in response.text
    assert PASSWORD not in response.text


def test_salted_hash_and_length_validation(auth_client, monkeypatch):
    encoded = hash_password(PASSWORD)
    assert encoded != hash_password(PASSWORD) and PASSWORD not in encoded
    monkeypatch.setattr(settings, "WORKSHOP_AUTH_PASSWORD_HASH", SecretStr(encoded))
    assert _verify(HTTPBasicCredentials(username="fictional-test-operator", password=PASSWORD), _configuration()) == "fictional-test-operator"
    for invalid in ("short", "x"*1025, "long password with newline\n", "密码"*16):
        with pytest.raises(ValueError):
            hash_password(invalid)


def test_disabled_and_missing_boundary_fail_closed(auth_client, monkeypatch):
    request = Request({"type":"http", "headers":[], "state":{}})
    with pytest.raises(HTTPException) as error:
        require_workshop_enabled(request)
    assert error.value.status_code == 503
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", False)
    assert auth_client.get("/workshop", auth=None).status_code == 404
    assert auth_client.post(API+"/documents", auth=None, content=b"invalid").status_code == 404
    assert auth_client.get("/health", auth=None).status_code == 200


def test_client_cannot_choose_authenticated_reviewer(auth_client):
    job = auth_client.post(API+"/jobs", json=EXAMPLE).json()
    body = {"expected_version":1,"reviewer":"Impersonated fictional person","acknowledged":True}
    response = auth_client.post(API+f"/jobs/{job['id']}/confirm", json=body)
    assert response.status_code == 200
    review = response.json()
    assert review["reviewer"] == "fictional-test-operator" and review["reviewer_identity"] == "authenticated"
    assert auth_client.post(API+f"/jobs/{job['id']}/confirm", json={**body,"reviewer_identity":"authenticated"}).status_code == 422
    assert auth_client.post(API+f"/jobs/{job['id']}/confirm", json=body).json() == review


def test_password_setup_prints_hash_only_and_rejects_mismatch(monkeypatch, capsys):
    from scripts import workshop_password
    answers = iter([PASSWORD, PASSWORD])
    monkeypatch.setattr(workshop_password, "getpass", lambda prompt: next(answers))
    workshop_password.main()
    output = capsys.readouterr().out
    assert output.startswith("scrypt$16384$8$5$") and PASSWORD not in output
    answers = iter([PASSWORD, "Different fictional password"])
    with pytest.raises(SystemExit, match="Passwords differ"):
        workshop_password.main()
    assert capsys.readouterr().out == ""


def test_unexpected_failure_does_not_cache_or_log_secret_values(auth_client, monkeypatch, capsys, caplog):
    def fail(*args):
        raise RuntimeError(PASSWORD)
    monkeypatch.setattr("app.api.v1.workshop.create_job", fail)
    response = auth_client.post(API+"/jobs", json=EXAMPLE)
    assert response.status_code == 500 and response.headers["cache-control"] == "no-store"
    assert PASSWORD not in response.text + caplog.text + capsys.readouterr().out
