"""The owner login from the server settings plus staff logins kept in the database; authenticate before parsing request bodies.
Browsers sign in once on the sign-in page and then carry a signed cookie; scripts may still send a username and password."""
import base64
import binascii
import hmac
from hashlib import scrypt, sha256
from collections import deque
from secrets import compare_digest, token_bytes
from threading import BoundedSemaphore
from time import monotonic, time
from urllib.parse import urlsplit

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.db.models import WorkshopUser
from app.db.session import SessionLocal, get_db


BASIC = HTTPBasic(auto_error=False, realm="Workshop")
HASH_PREFIX = "scrypt$16384$8$5"


STAFF_PASSWORD_LENGTH = 10
# Wrong passwords: after 10 in 5 minutes from one address, or for one login name, further tries wait. Counting by name
# matters because the address comes from a header the visitor can fake behind some hosts. Kept in memory; resets on restart.
MAX_FAILURES, FAILURE_WINDOW = 10, 300
FAILURES: dict[str, deque] = {}
# One password check holds 16 MB; allow two at once so a burst of guesses queues instead of exhausting a 512 MB server.
CHECKS = BoundedSemaphore(2)
# No WWW-Authenticate header is ever sent, so browsers show the sign-in page instead of their own password pop-up.
SESSION_COOKIE, SESSION_SECONDS = "workshop_session", 12 * 3600
LOGIN_PAGE = "/workshop/login"


def hash_password(password: str, minimum: int = 16) -> str:
    if not minimum <= len(password) <= 1024 or not password.isascii() or not password.isprintable():
        raise ValueError(f"Use {minimum}–1024 printable ASCII password characters")
    salt = token_bytes(16)
    digest = scrypt(password.encode(), salt=salt, n=16384, r=8, p=5, dklen=32, maxmem=32*1024*1024)
    return HASH_PREFIX + "$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()


def _parse_hash(encoded: str) -> tuple[bytes, bytes]:
    if len(encoded) > 200 or not encoded.startswith(HASH_PREFIX + "$"):
        raise ValueError("Unsupported password hash")
    salt_text, digest_text = encoded[len(HASH_PREFIX)+1:].split("$")
    salt = base64.b64decode(salt_text, altchars=b"-_", validate=True)
    digest = base64.b64decode(digest_text, altchars=b"-_", validate=True)
    if len(salt) != 16 or len(digest) != 32:
        raise ValueError("Invalid password hash size")
    return salt, digest


def valid_username(username: str) -> bool:
    return bool(username.strip()) and username == username.strip() and len(username) <= 50 and username.isascii() \
        and username.isprintable() and ":" not in username


def _origin(value: str):
    parsed = urlsplit(value)
    if (parsed.scheme not in {"http", "https"} or not parsed.hostname
            or not parsed.hostname.isascii() or any(c.isspace() for c in parsed.hostname)
            or parsed.username is not None or parsed.password is not None
            or parsed.path not in {"", "/"} or parsed.query or parsed.fragment or parsed.port == 0):
        raise ValueError("Origin must contain only scheme, host and optional port")
    return parsed.scheme, parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80)


def _configuration():
    try:
        username = settings.WORKSHOP_AUTH_USERNAME or ""
        if not username.strip() or username != username.strip() or len(username) > 200 or not username.isascii() or not username.isprintable() or ":" in username:
            raise ValueError("Invalid account name")
        configured_origin = _origin(settings.WORKSHOP_ORIGIN or "")
        if configured_origin[0] != "https" and configured_origin[1] not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Non-loopback origins require HTTPS")
        salt, digest = _parse_hash(settings.WORKSHOP_AUTH_PASSWORD_HASH.get_secret_value())
        return username, salt, digest, configured_origin
    except (ValueError, AttributeError, binascii.Error):
        raise HTTPException(status_code=503, detail="Workshop account/origin is not configured correctly") from None


def _check_request(request: Request):
    if not settings.WORKSHOP_ENABLED:
        raise HTTPException(status_code=404, detail="The workshop app is switched off")
    configuration = _configuration()
    expected = configuration[3]
    try:
        if _origin(f"{request.url.scheme}://{request.url.netloc}") != expected:
            raise ValueError("Wrong host")
        if "origin" in request.headers and _origin(request.headers["origin"]) != expected:
            raise ValueError("Cross-origin request")
        if request.headers.get("sec-fetch-site", "") not in {"", "none", "same-origin"}:
            raise ValueError("Cross-site browser request")
    except ValueError:
        raise HTTPException(status_code=403, detail="Workshop request origin is not permitted") from None
    return configuration


def _staff_login(app, username: str) -> tuple[bytes, bytes, str] | None:
    """Salt, digest and role of an active staff login, or None. Uses the same database session source as the routes."""
    override = app.dependency_overrides.get(get_db) if app is not None else None
    db = override() if override else SessionLocal()
    try:
        user = db.get(WorkshopUser, username)
        if user is None or not user.active:
            return None
        return (*_parse_hash(user.password_hash), user.role)
    except ValueError:
        return None
    finally:
        if not override:
            db.close()


def _failures(key: str) -> deque:
    """Recent wrong-password times for one address or name, with old ones dropped."""
    if len(FAILURES) > 10_000:  # made-up names would otherwise grow this without limit
        for stale in [name for name, times in FAILURES.items() if not times or monotonic() - times[-1] > FAILURE_WINDOW]:
            del FAILURES[stale]
    recent = FAILURES.setdefault(key, deque())
    while recent and monotonic() - recent[0] > FAILURE_WINDOW:
        recent.popleft()
    return recent


def _verify(credentials, configuration, app=None, address: str = ""):
    """Return (login name, role). The owner login comes from the server settings; other names are looked up as staff."""
    username, salt, expected, _ = configuration
    password = credentials.password if credentials else ""
    if not credentials or len(password) > 1024:
        raise HTTPException(status_code=401, detail="Workshop authentication required")
    counters = [_failures("address:" + address), _failures("name:" + credentials.username.lower()[:200])]
    if any(len(recent) >= MAX_FAILURES for recent in counters):
        raise HTTPException(status_code=429, detail="Too many wrong passwords. Wait five minutes and try again.",
                            headers={"Retry-After": str(FAILURE_WINDOW)})
    role = "owner"
    if not compare_digest(credentials.username.encode(), username.encode()):
        staff = _staff_login(app, credentials.username) if valid_username(credentials.username) else None
        # An unknown name still costs one password check, so names cannot be found by timing.
        salt, expected, role = staff or (salt, b"", "staff")
    with CHECKS:
        candidate = scrypt(password.encode(), salt=salt, n=16384, r=8, p=5, dklen=32, maxmem=32*1024*1024)
    if not compare_digest(candidate, expected):
        for recent in counters:
            recent.append(monotonic())
        raise HTTPException(status_code=401, detail="Workshop authentication required")
    return credentials.username, role


def _session_key(app, username: str, configuration) -> tuple[bytes, str] | None:
    """Signing key and role for a login. The key changes when that login's password (or the owner's) changes, which ends its sessions."""
    owner, _, owner_digest, _ = configuration
    if username == owner:
        return sha256(b"workshop-session\0" + owner_digest).digest(), "owner"
    staff = _staff_login(app, username) if valid_username(username) else None
    if staff is None:
        return None
    return sha256(b"workshop-session\0" + owner_digest + b"\0" + staff[1]).digest(), staff[2]


def _signature(key: bytes, name: str, expires: str) -> str:
    return hmac.new(key, f"{name}\n{expires}".encode(), sha256).hexdigest()


def session_token(app, username: str, configuration) -> str:
    key, _ = _session_key(app, username, configuration)
    name, expires = base64.urlsafe_b64encode(username.encode()).decode(), str(int(time()) + SESSION_SECONDS)
    return f"{name}.{expires}.{_signature(key, name, expires)}"


def _session(app, token: str, configuration):
    """(login name, role) for a valid, unexpired cookie whose login is still active, else None."""
    try:
        name, expires, signature = token.split(".")
        if len(token) > 400 or int(expires) < time():
            return None
        username = base64.urlsafe_b64decode(name.encode()).decode()
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return None
    found = _session_key(app, username, configuration)
    if found is None or not compare_digest(_signature(found[0], name, expires), signature):
        return None
    return username, found[1]


login_router = APIRouter(include_in_schema=False)


@login_router.post(f"/api/{settings.API_VERSION}/workshop/login")
async def sign_in(request: Request, username: str = Form("", max_length=200), password: str = Form("", max_length=1024)):
    """The sign-in page posts here; the middleware has already checked the request comes from the workshop page."""
    configuration = _configuration()
    try:
        username, _ = await run_in_threadpool(_verify, HTTPBasicCredentials(username=username, password=password),
                                              configuration, request.app, request.client.host if request.client else "")
    except HTTPException as error:
        return RedirectResponse(LOGIN_PAGE + ("?error=locked" if error.status_code == 429 else "?error=wrong"), status_code=303)
    token = await run_in_threadpool(session_token, request.app, username, configuration)
    response = RedirectResponse("/workshop", status_code=303)
    response.set_cookie(SESSION_COOKIE, token, max_age=SESSION_SECONDS, path="/", httponly=True, samesite="strict",
                        secure=configuration[3][0] == "https")
    return response


@login_router.post(f"/api/{settings.API_VERSION}/workshop/logout")
def sign_out():
    # ponytail: the cookie is removed from this browser only; a copied cookie stays valid until it expires (12 hours)
    # or that login's password changes. Keep a server-side list of sessions if that matters.
    response = RedirectResponse(LOGIN_PAGE + "?error=out", status_code=303)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


class WorkshopAccessMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        prefix = f"/api/{settings.API_VERSION}/workshop"
        path = scope.get("path", "").rstrip("/")
        if scope["type"] != "http" or not (path in {"/workshop", LOGIN_PAGE} or path == prefix or path.startswith(prefix + "/")):
            if scope["type"] == "http" and settings.WORKSHOP_ONLY and path != "/health" and not path.startswith("/static/workshop"):
                response = RedirectResponse("/workshop") if path == "" else JSONResponse(status_code=404, content={"detail": "Not found"})
                return await response(scope, receive, send)
            return await self.app(scope, receive, send)
        async def private_send(message):
            if message["type"] == "http.response.start":
                message["headers"] = [(key, value) for key, value in message.get("headers", []) if key.lower() != b"cache-control"]
                message["headers"].append((b"cache-control", b"no-store"))
            await send(message)
        try:
            request = Request(scope)
            configuration = _check_request(request)
            if path in {LOGIN_PAGE, prefix + "/login", prefix + "/logout"}:
                return await self.app(scope, receive, private_send)
            signed_in = await run_in_threadpool(_session, scope.get("app"), request.cookies.get(SESSION_COOKIE, ""), configuration)
            if signed_in is None:
                if len(request.headers.get("authorization", "")) > 4096:
                    raise HTTPException(status_code=401, detail="Workshop authentication required")
                credentials = await BASIC(request)
                if credentials is None and path == "/workshop":
                    return await RedirectResponse(LOGIN_PAGE, status_code=303, headers={"Cache-Control": "no-store"})(scope, receive, send)
                signed_in = await run_in_threadpool(_verify, credentials, configuration, scope.get("app"),
                                                    request.client.host if request.client else "")
            username, role = signed_in
            scope.setdefault("state", {}).update(workshop_user=username, workshop_role=role)
        except HTTPException as error:
            response = JSONResponse(status_code=error.status_code, content={"detail":error.detail},
                                    headers={**{key: value for key, value in (error.headers or {}).items()
                                                if key.lower() != "www-authenticate"}, "Cache-Control":"no-store"})
            return await response(scope, receive, send)
        await self.app(scope, receive, private_send)
