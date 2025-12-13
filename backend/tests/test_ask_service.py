from dataclasses import dataclass
from typing import Any

from app.schemas.ask import AskFilters
from app.services.ask_service import ask_sources, build_qdrant_filters


class FakeEmbeddingsClient:
    def __init__(self, vectors: list[list[float]]) -> None:
        self._vectors = vectors
        self.recorded_texts: list[str] = []

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.recorded_texts = texts
        return self._vectors


@dataclass
class FakeSearchResult:
    score: float
    payload: dict[str, Any]


class FakeQdrantClient:
    def __init__(self, results: list[FakeSearchResult]) -> None:
        self._results = results
        self.recorded_vector: list[float] | None = None
        self.recorded_filters: Any = None
        self.recorded_limit: int | None = None

    def search(self, query_vector: list[float], filters: Any = None, limit: int = 5) -> list[Any]:
        self.recorded_vector = query_vector
        self.recorded_filters = filters
        self.recorded_limit = limit
        return self._results


class FakeAnswerClient:
    def __init__(self, answer: str) -> None:
        self._answer = answer
        self.recorded_system_prompt: str | None = None
        self.recorded_user_prompt: str | None = None

    def complete_text(self, system_prompt: str, user_prompt: str) -> str:
        self.recorded_system_prompt = system_prompt
        self.recorded_user_prompt = user_prompt
        return self._answer


def test_ask_sources_returns_citations_from_qdrant_hits() -> None:
    embeddings_client = FakeEmbeddingsClient([[0.1, 0.2]])
    answer_client = FakeAnswerClient("Grounded answer")
    qdrant_client = FakeQdrantClient(
        [
            FakeSearchResult(
                score=0.82,
                payload={
                    "source_id": 4,
                    "chunk_id": "4-0",
                    "title": "Write-up",
                    "text": "Relevant snippet",
                    "source_type": "manual",
                    "summary": "Short summary",
                    "techs": ["FastAPI"],
                    "tags": ["xss"],
                    "cwes": ["CWE-79"],
                    "cves": [],
                    "start_offset": 0,
                    "end_offset": 16,
                },
            )
        ]
    )

    response = ask_sources(
        query="how is xss exploited?",
        filters=AskFilters(tags=["xss"], cwes=["CWE-79"]),
        limit=3,
        embeddings_client=embeddings_client,
        qdrant_client=qdrant_client,
        answer_client=answer_client,
    )

    assert response.answer == "Grounded answer"
    assert embeddings_client.recorded_texts == ["how is xss exploited?"]
    assert qdrant_client.recorded_vector == [0.1, 0.2]
    assert qdrant_client.recorded_limit == 3
    assert answer_client.recorded_user_prompt is not None
    assert "Relevant snippet" in answer_client.recorded_user_prompt
    assert response.citations[0].source_id == 4
    assert response.citations[0].chunk_id == "4-0"
    assert response.citations[0].tags == ["xss"]
    assert response.citations[0].score == 0.82


def test_build_qdrant_filters_maps_api_filters() -> None:
    filters = build_qdrant_filters(
        AskFilters(source_id=7, tags=["idor"], cwes=["CWE-639"], cves=[])
    )

    assert filters is not None
    assert filters.source_id == 7
    assert filters.tags == ["idor"]
    assert filters.cwes == ["CWE-639"]
    assert filters.cves is None


def test_ask_sources_rejects_incomplete_qdrant_payload() -> None:
    embeddings_client = FakeEmbeddingsClient([[0.1, 0.2]])
    qdrant_client = FakeQdrantClient([FakeSearchResult(score=0.5, payload={"source_id": 1})])

    try:
        ask_sources(
            query="test",
            embeddings_client=embeddings_client,
            qdrant_client=qdrant_client,
        )
    except ValueError as exc:
        assert str(exc) == "Qdrant result payload is missing required citation fields"
        return

    raise AssertionError("Expected invalid qdrant payload to raise ValueError")


def test_ask_sources_skips_answer_generation_without_citations() -> None:
    embeddings_client = FakeEmbeddingsClient([[0.1, 0.2]])
    answer_client = FakeAnswerClient("unused")
    qdrant_client = FakeQdrantClient([])

    response = ask_sources(
        query="test",
        embeddings_client=embeddings_client,
        qdrant_client=qdrant_client,
        answer_client=answer_client,
    )

    assert response.answer is None
    assert response.citations == []
    assert answer_client.recorded_user_prompt is None


def test_ask_sources_filters_out_orphaned_qdrant_hits() -> None:
    embeddings_client = FakeEmbeddingsClient([[0.1, 0.2]])
    answer_client = FakeAnswerClient("Grounded answer")
    qdrant_client = FakeQdrantClient(
        [
            # Qdrant can still have the chunk even if the source dropped out of the ready set.
            FakeSearchResult(
                score=0.82,
                payload={
                    "source_id": 4,
                    "chunk_id": "4-0",
                    "title": "Stale source",
                    "text": "Stale snippet",
                },
            ),
            # Only ready sources should survive this filter.
            FakeSearchResult(
                score=0.91,
                payload={
                    "source_id": 7,
                    "chunk_id": "7-0",
                    "title": "Live source",
                    "text": "Fresh snippet",
                },
            ),
        ]
    )

    response = ask_sources(
        query="test",
        ready_source_ids={7},
        embeddings_client=embeddings_client,
        qdrant_client=qdrant_client,
        answer_client=answer_client,
    )

    assert len(response.citations) == 1
    assert response.citations[0].source_id == 7
    assert "Fresh snippet" in (answer_client.recorded_user_prompt or "")
