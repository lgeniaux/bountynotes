from fastapi.testclient import TestClient

import app.api.routers.ask as ask_router
from app.main import app


class FakeAskResponse:
    answer = "Grounded answer"
    citations = [
        {
            "source_id": 7,
            "chunk_id": "7-0",
            "title": "Stored XSS note",
            "snippet": "Relevant citation",
            "score": 0.82,
            "source_type": "manual",
            "summary": "Short summary",
            "techs": ["Angular"],
            "tags": ["xss"],
            "cwes": ["CWE-79"],
            "cves": [],
            "start_offset": 0,
            "end_offset": 16,
        }
    ]


def test_ask_endpoint_returns_grounded_answer_and_citations(monkeypatch) -> None:
    def fake_ask_sources(query: str, filters, limit: int):
        assert query == "How is the XSS exploited?"
        assert filters is not None
        assert filters.source_id == 7
        assert filters.tags == ["xss"]
        assert filters.cwes == ["CWE-79"]
        assert filters.cves == []
        assert limit == 3
        return FakeAskResponse()

    monkeypatch.setattr(ask_router, "ask_sources", fake_ask_sources)

    with TestClient(app) as client:
        response = client.post(
            "/ask",
            json={
                "query": "How is the XSS exploited?",
                "filters": {
                    "source_id": 7,
                    "tags": ["xss"],
                    "cwes": ["CWE-79"],
                    "cves": [],
                },
                "limit": 3,
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Grounded answer"
    assert payload["citations"][0]["chunk_id"] == "7-0"
    assert payload["citations"][0]["tags"] == ["xss"]


def test_ask_endpoint_returns_empty_answer_when_retrieval_is_empty(monkeypatch) -> None:
    class EmptyAskResponse:
        answer = None
        citations = []

    def fake_ask_sources(query: str, filters, limit: int):
        assert query == "What is this source about?"
        assert filters is None
        assert limit == 5
        return EmptyAskResponse()

    monkeypatch.setattr(ask_router, "ask_sources", fake_ask_sources)

    with TestClient(app) as client:
        response = client.post(
            "/ask",
            json={
                "query": "What is this source about?",
            },
        )

    assert response.status_code == 200
    assert response.json() == {"answer": None, "citations": []}
