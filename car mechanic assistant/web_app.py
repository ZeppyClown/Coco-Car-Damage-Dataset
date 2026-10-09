"""Local workshop UI. Shared deployment requires an authenticated HTTPS proxy."""
import io
import json
import logging
import os
from pathlib import Path
import sqlite3
from threading import Lock
from uuid import uuid4
from flask import Flask, jsonify, render_template, request
from PIL import Image, UnidentifiedImageError
from src.rag_system import MechanicAssistant

logger = logging.getLogger(__name__)


def create_app(assistant=None, feedback_path=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    state = {"assistant": assistant}
    query_lock = Lock()
    evidence = Path(feedback_path or os.getenv("FEEDBACK_DB", str(Path(__file__).parent / "runtime" / "feedback.sqlite")))
    evidence.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(evidence) as db:
        db.execute("CREATE TABLE IF NOT EXISTS queries (id TEXT PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, sources TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS feedback (query_id TEXT PRIMARY KEY REFERENCES queries(id), created_at TEXT DEFAULT CURRENT_TIMESTAMP, rating TEXT NOT NULL, comment TEXT NOT NULL)")

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/query")
    def query():
        image_data = None
        if request.files:
            user_query = request.form.get("query", "").strip()
            image_data = request.files.get("image")
            if image_data is None:
                return jsonify(error="Expected an image upload"), 400
            image_data = image_data.read()
            try:
                with Image.open(io.BytesIO(image_data)) as image:
                    image.verify()
            except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
                return jsonify(error="Invalid image"), 400
        else:
            payload = request.get_json(silent=True)
            if not isinstance(payload, dict) or not isinstance(payload.get("query"), str):
                return jsonify(error="Expected a JSON query string"), 400
            user_query = payload["query"].strip()
        if not user_query or len(user_query) > 4000:
            return jsonify(error="Enter a question from 1 to 4000 characters"), 400
        try:
            with query_lock:
                if state["assistant"] is None:
                    state["assistant"] = MechanicAssistant()
                assistant = state["assistant"]
                result = assistant.query_with_image(user_query, image_data) if image_data else assistant.query(user_query)
            identifier = uuid4().hex
            with sqlite3.connect(evidence) as db:
                db.execute("INSERT INTO queries(id, sources) VALUES (?, ?)",
                           (identifier, json.dumps({"query": user_query, "response": result.get("response"),
                             "sources": result.get("sources", []), "metadata": result.get("metadata", {})}, ensure_ascii=False)))
            return jsonify(**result, query_id=identifier)
        except Exception as exc:
            logger.error("query_failed: %s", type(exc).__name__)
            return jsonify(error="Assistant unavailable; check the configured model and index"), 503

    @app.post("/feedback")
    def feedback():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or payload.get("rating") not in {"useful", "partly_useful", "not_useful"}:
            return jsonify(error="Choose a valid feedback rating"), 400
        identifier, comment = payload.get("query_id"), payload.get("comment", "")
        if not isinstance(identifier, str) or not isinstance(comment, str) or len(comment) > 1000:
            return jsonify(error="Invalid query ID or comment"), 400
        with sqlite3.connect(evidence) as db:
            if db.execute("SELECT id FROM queries WHERE id = ?", (identifier,)).fetchone() is None:
                return jsonify(error="Query not found"), 404
            db.execute("INSERT INTO feedback(query_id, rating, comment) VALUES (?, ?, ?) "
                       "ON CONFLICT(query_id) DO UPDATE SET rating=excluded.rating, comment=excluded.comment",
                       (identifier, payload["rating"], comment))
        return jsonify(success=True)

    @app.get("/health")
    def health():
        return jsonify(status="healthy", assistant="initialised" if state["assistant"] else "not_initialised")

    @app.after_request
    def headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=int(os.environ.get("PORT", 8080)), debug=False)
