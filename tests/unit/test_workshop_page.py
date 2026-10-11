from app.core.config import settings


def test_workshop_page_gate_assets_and_no_static_html_bypass(client, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", False)
    assert client.get("/workshop").status_code == 404
    assert client.get("/static/workshop.html").status_code == 404
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    page = client.get("/workshop")
    assert page.status_code == 200 and page.headers["cache-control"] == "no-store"
    assert 'id="draft-form"' in page.text
    assert 'content="/api/v1/workshop"' in page.text and "{{workshop_api}}" not in page.text
    assert client.get("/static/workshop.js").status_code == 200
    assert client.get("/static/workshop.css").status_code == 200
    assert client.get("/").status_code == 200
