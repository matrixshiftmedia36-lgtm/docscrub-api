import io

from fastapi.testclient import TestClient
from pypdf import PdfReader, PdfWriter

from main import app

client = TestClient(app)


def valid_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_metadata({"/Author": "Test author"})
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def submit(headers=None):
    return client.post(
        "/api/v1/clean-pdf",
        files={"file": ("test.pdf", valid_pdf(), "application/pdf")},
        headers=headers or {},
    )


def test_health_remains_public(monkeypatch):
    monkeypatch.delenv("RAPIDAPI_PROXY_SECRET", raising=False)
    assert client.get("/").status_code == 200


def test_missing_configuration_is_fail_closed(monkeypatch):
    monkeypatch.delenv("RAPIDAPI_PROXY_SECRET", raising=False)
    assert submit({"X-RapidAPI-Proxy-Secret": "test-value"}).status_code == 503


def test_direct_and_wrong_secret_rejected(monkeypatch):
    monkeypatch.setenv("RAPIDAPI_PROXY_SECRET", "good-value")
    assert submit().status_code == 403
    assert submit({"X-RapidAPI-Proxy-Secret": "wrong-value"}).status_code == 403


def test_valid_proxy_secret_can_clean_pdf(monkeypatch):
    monkeypatch.setenv("RAPIDAPI_PROXY_SECRET", "good-value")
    response = submit({"X-RapidAPI-Proxy-Secret": "good-value"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    result = PdfReader(io.BytesIO(response.content))
    assert len(result.pages) == 1
    assert result.metadata.get("/Author") is None


def test_preflight_not_blocked(monkeypatch):
    monkeypatch.setenv("RAPIDAPI_PROXY_SECRET", "good-value")
    response = client.options(
        "/api/v1/clean-pdf",
        headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
    )
    assert response.status_code == 200
