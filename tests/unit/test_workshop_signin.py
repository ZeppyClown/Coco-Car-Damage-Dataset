"""Sign-in page and cookie sessions; all logins are fictional."""
from pydantic import SecretStr
import pytest

from app.core.config import settings
from app.core.workshop_auth import SESSION_COOKIE, hash_password
from tests.conftest import TEST_OPERATOR, TEST_PASSWORD

API = "/api/v1/workshop"


@pytest.fixture
def browser(client, monkeypatch):
    """A browser with no saved password: it must use the sign-in page."""
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    client.auth = None
    return client


def sign_in(browser, username, password):
    return browser.post(API + "/login", data={"username": username, "password": password}, follow_redirects=False)


def test_page_sends_strangers_to_sign_in_without_a_popup(browser):
    response = browser.get("/workshop", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == "/workshop/login"
    assert "www-authenticate" not in response.headers
    page = browser.get("/workshop/login")
    assert page.status_code == 200 and 'name="password"' in page.text and API + "/login" in page.text
    assert "{{" not in page.text
    assert browser.get(API + "/jobs").status_code == 401


def test_sign_in_sets_a_private_cookie_and_sign_out_clears_it(browser):
    response = sign_in(browser, TEST_OPERATOR, TEST_PASSWORD)
    assert response.status_code == 303 and response.headers["location"] == "/workshop"
    cookie = response.headers["set-cookie"]
    assert SESSION_COOKIE in cookie and "HttpOnly" in cookie and "samesite=strict" in cookie.lower()
    assert TEST_PASSWORD not in cookie
    assert browser.get("/workshop").status_code == 200
    assert browser.get(API + "/users").json()["me"] == TEST_OPERATOR
    out = browser.post(API + "/logout", follow_redirects=False)
    assert out.status_code == 303 and "error=out" in out.headers["location"]
    assert browser.get(API + "/jobs").status_code == 401
    assert "signed out" in browser.get("/workshop/login?error=out").text


def test_wrong_password_shows_a_message_and_counts_towards_lockout(browser):
    response = sign_in(browser, TEST_OPERATOR, "not the fictional password")
    assert response.status_code == 303 and response.headers["location"] == "/workshop/login?error=wrong"
    assert "set-cookie" not in response.headers
    assert "not right" in browser.get(response.headers["location"]).text
    for _ in range(10):
        response = sign_in(browser, TEST_OPERATOR, "not the fictional password")
    assert response.headers["location"].endswith("error=locked")
    assert sign_in(browser, TEST_OPERATOR, TEST_PASSWORD).headers["location"].endswith("error=locked")


def test_message_is_never_copied_from_the_address(browser):
    assert "<script>" not in browser.get("/workshop/login?error=<script>alert(1)</script>").text


def test_forged_or_altered_cookies_are_refused(browser):
    sign_in(browser, TEST_OPERATOR, TEST_PASSWORD)
    good = browser.cookies[SESSION_COOKIE]
    name, expires, signature = good.split(".")
    for forged in [f"{name}.{int(expires) + 999}.{signature}", f"{name}.{expires}.{'0' * 64}", "garbage", "a.b.c.d"]:
        browser.cookies.set(SESSION_COOKIE, forged)
        assert browser.get(API + "/jobs").status_code == 401, forged


def test_changing_the_owner_password_ends_old_sessions(browser, monkeypatch):
    sign_in(browser, TEST_OPERATOR, TEST_PASSWORD)
    monkeypatch.setattr(settings, "WORKSHOP_AUTH_PASSWORD_HASH", SecretStr(hash_password("Another fictional owner password")))
    assert browser.get(API + "/jobs").status_code == 401


def test_staff_session_ends_when_switched_off(client, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    assert client.post(API + "/users", json={"username": "fictional-staff", "password": "staff fictional 2026", "role": "staff"}).status_code == 201
    client.auth = None
    sign_in(client, "fictional-staff", "staff fictional 2026")
    assert client.get(API + "/users").json() == {"me": "fictional-staff", "role": "staff", "users": []}
    client.cookies.clear()
    client.auth = (TEST_OPERATOR, TEST_PASSWORD)
    assert client.post(API + "/users/fictional-staff/active", json={"active": False}).status_code == 200
    client.auth = None
    sign_in(client, "fictional-staff", "staff fictional 2026")
    assert client.get(API + "/jobs").status_code == 401


def test_sign_in_from_another_site_is_refused(browser):
    response = browser.post(API + "/login", data={"username": TEST_OPERATOR, "password": TEST_PASSWORD},
                            headers={"Origin": "https://example.invalid"}, follow_redirects=False)
    assert response.status_code == 403 and "set-cookie" not in response.headers
