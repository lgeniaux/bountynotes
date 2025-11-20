from dataclasses import dataclass, field

from app.clients.qdrant_client import QdrantPoint
from app.services.chunking_service import TextChunk
from app.services.indexing_service import build_chunk_id, build_point_id, index_source_chunks


@dataclass
class FakeSource:
    id: int | None
    title: str | None = None
    source_type: str = "manual"
    summary: str | None = None
    techs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    cwes: list[str] = field(default_factory=list)
    cves: list[str] = field(default_factory=list)


class FakeEmbeddingsClient:
    def __init__(self, vectors: list[list[float]]) -> None:
        self._vectors = vectors
        self.recorded_texts: list[str] = []

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.recorded_texts = texts
        return self._vectors


class FakeQdrantClient:
    def __init__(self) -> None:
        self.ensure_collection_calls = 0
        self.upserted_points: list[QdrantPoint] = []

    def ensure_collection(self) -> None:
        self.ensure_collection_calls += 1

    def upsert_points(self, points: list[QdrantPoint]) -> None:
        self.upserted_points = points


def test_index_source_chunks_builds_expected_payloads() -> None:
    source = FakeSource(
        id=7,
        title="Write-up",
        source_type="manual",
        summary="summary",
        techs=["FastAPI"],
        tags=["xss"],
        cwes=["CWE-79"],
        cves=["CVE-2024-12345"],
    )
    chunks = [
        TextChunk(index=0, text="chunk one", start_offset=0, end_offset=9),
        TextChunk(index=1, text="chunk two", start_offset=10, end_offset=19),
    ]
    embeddings_client = FakeEmbeddingsClient(vectors=[[0.1, 0.2], [0.3, 0.4]])
    qdrant_client = FakeQdrantClient()

    indexed_chunks = index_source_chunks(
        source,
        chunks,
        embeddings_client=embeddings_client,
        qdrant_client=qdrant_client,
    )

    assert embeddings_client.recorded_texts == ["chunk one", "chunk two"]
    assert qdrant_client.ensure_collection_calls == 1
    assert len(qdrant_client.upserted_points) == 2
    assert indexed_chunks[0].chunk_id == "7-0"
    assert qdrant_client.upserted_points[0].point_id == build_point_id(7, 0, 0)
    assert qdrant_client.upserted_points[0].payload["source_id"] == 7
    assert qdrant_client.upserted_points[0].payload["tags"] == ["xss"]
    assert qdrant_client.upserted_points[0].payload["text"] == "chunk one"


def test_index_source_chunks_rejects_missing_source_id() -> None:
    source = FakeSource(id=None)

    try:
        index_source_chunks(
            source, [TextChunk(index=0, text="chunk", start_offset=0, end_offset=5)]
        )
    except ValueError as exc:
        assert str(exc) == "Source must have an id before indexing"
        return

    raise AssertionError("Expected missing source id to raise ValueError")


def test_build_chunk_id_is_stable() -> None:
    assert build_chunk_id(12, 3) == "12-3"


def test_build_point_id_is_stable() -> None:
    assert build_point_id(12, 240, 3) == 12030240
