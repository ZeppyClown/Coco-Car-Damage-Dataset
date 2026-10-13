"""The owner login from the server settings plus staff logins kept in the database; authenticate before parsing request bodies."""
import base64
import binascii
from hashlib import scrypt
from collections import deque
from secrets import compare_digest, token_bytes
from time import monotonic
from urllib.parse import urlsplit

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.db.models import WorkshopUser
from app.db.session import SessionLocal, get_db


BASIC = HTTPBasic(auto_error=False, realm="Workshop")
HASH_PREFIX = "scrypt$16384$8$5"


STAFF_PASSWORD_LENGTH = 10
# Wrong passwords from one address: after 10 in 5 minutes that address waits. Kept in memory, so it resets on restart.
MAX_FAILURES, FAILURE_WINDOW = 10, 300
FAILURES: dict[str, deque] = {}
CHALLENGE = {"WWW-Authenticate": 'Basic realm="Workshop"'}


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


def _verify(credentials, configuration, app=None, address: str = ""):
    """Return (login name, role). The owner login comes from the server settings; other names are looked up as staff."""
    username, salt, expected, _ = configuration
    password = credentials.password if credentials else ""
    if not credentials or len(password) > 1024:
        raise HTTPException(status_code=401, detail="Workshop authentication required", headers=CHALLENGE)
    recent = FAILURES.setdefault(address, deque())
    while recent and monotonic() - recent[0] > FAILURE_WINDOW:
        recent.popleft()
    if len(recent) >= MAX_FAILURES:
        raise HTTPException(status_code=429, detail="Too many wrong passwords. Wait five minutes and try again.",
                            headers={"Retry-After": str(FAILURE_WINDOW)})
    role = "owner"
    if not compare_digest(credentials.username.encode(), username.encode()):
        staff = _staff_login(app, credentials.username) if valid_username(credentials.username) else None
        # An unknown name still costs one password check, so names cannot be found by timing.
        salt, expected, role = staff or (salt, b"", "staff")
    candidate = scrypt(password.encode(), salt=salt, n=16384, r=8, p=5, dklen=32, maxmem=32*1024*1024)
    if not compare_digest(candidate, expected):
        recent.append(monotonic())
        raise HTTPException(status_code=401, detail="Workshop authentication required", headers=CHALLENGE)
    return credentials.username, role


class WorkshopAccessMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        prefix = f"/api/{settings.API_VERSION}/workshop"
        path = scope.get("path", "").rstrip("/")
        if scope["type"] != "http" or not (path == "/workshop" or path == prefix or path.startswith(prefix + "/")):
            if scope["type"] == "http" and settings.WORKSHOP_ONLY and path != "/health" and not path.startswith("/static/"):
                response = RedirectResponse("/workshop") if path == "" else JSONResponse(status_code=404, content={"detail": "Not found"})
                return await response(scope, receive, send)
            return await self.app(scope, receive, send)
        try:
            request = Request(scope)
            configuration = _check_request(request)
            if len(request.headers.get("authorization", "")) > 4096:
                raise HTTPException(status_code=401, detail="Workshop authentication required", headers=CHALLENGE)
            credentials = await BASIC(request)
            username, role = await run_in_threadpool(_verify, credentials, configuration, scope.get("app"),
                                                     request.client.host if request.client else "")
            scope.setdefault("state", {}).update(workshop_user=username, workshop_role=role)
        except HTTPException as error:
            response = JSONResponse(status_code=error.status_code, content={"detail":error.detail},
                                    headers={**(error.headers or {}), "Cache-Control":"no-store"})
            return await response(scope, receive, send)
        async def private_send(message):
            if message["type"] == "http.response.start":
                message["headers"] = [(key, value) for key, value in message.get("headers", []) if key.lower() != b"cache-control"]
                message["headers"].append((b"cache-control", b"no-store"))
            await send(message)
        await self.app(scope, receive, private_send)
