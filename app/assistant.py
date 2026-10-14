"""The manual assistant (the Flask app in `car mechanic assistant/`) served at /assistant. WorkshopAccessMiddleware puts it
behind the workshop sign-in. It is loaded on first use, so a workshop that never opens it does not pay for Chroma's memory."""
import sys
import warnings
from pathlib import Path
from threading import Lock

from starlette.concurrency import run_in_threadpool
from starlette.responses import HTMLResponse, JSONResponse

from app.core.config import settings

ASSISTANT_DIR = Path(__file__).resolve().parents[1] / "car mechanic assistant"
NOT_CONFIGURED = "The AI assistant is not configured yet. The owner needs to add GEMINI_API_KEY in the host's settings."
NOT_READY = "The AI assistant is still preparing its library. This takes about two minutes after the app starts. Try again shortly."
_lock = Lock()
_loaded = {}


def _config():
    with _lock:
        if "config" not in _loaded:
            sys.path.insert(0, str(ASSISTANT_DIR))
            from src.config import Config
            _loaded["config"] = Config
    return _loaded["config"]


def _flask():
    with _lock:
        if "wsgi" not in _loaded:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)  # ponytail: starlette's WSGI bridge; a2wsgi if it is removed
                from starlette.middleware.wsgi import WSGIMiddleware
            from web_app import create_app
            _loaded["wsgi"] = WSGIMiddleware(create_app())
    return _loaded["wsgi"]


def _message(scope, text: str):
    if scope["method"] == "GET":
        page = (f'<!doctype html><meta charset="utf-8"><title>AI assistant</title><body style="font-family:sans-serif;max-width:40rem;'
                f'margin:3rem auto"><h1>AI assistant</h1><p>{text}</p><p><a href="/workshop">Back to the workshop</a></p>')
        return HTMLResponse(page, status_code=503)
    return JSONResponse({"error": text}, status_code=503)


async def assistant_app(scope, receive, send):
    if scope["type"] != "http" or not settings.AI_TOOLS_ENABLED:
        return await JSONResponse({"detail": "Not found"}, status_code=404)(scope, receive, send)
    config = _config()
    if not config.GOOGLE_API_KEY:
        return await _message(scope, NOT_CONFIGURED)(scope, receive, send)
    if not (config.CHROMA_PERSIST_DIR / "corpus.json").exists():  # written only when a build finishes
        return await _message(scope, NOT_READY)(scope, receive, send)
    await (await run_in_threadpool(_flask))(scope, receive, send)
