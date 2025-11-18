from dataclasses import dataclass
from typing import Protocol

from app.clients.openai_embeddings_client import get_openai_embeddings_client
from app.clients.qdrant_client import QdrantPoint, get_qdrant_client
from app.services.chunking_service import TextChunk


@dataclass
class IndexedChunk:
    chunk_id: str
    text: str
    start_offset: int
    end_offset: int


class IndexableSource(Protocol):
    id: int | None
    title: str | None
    source_type: str
    summary: str | None
    techs: list[str]
    tags: list[str]
    cwes: list[str]
    cves: list[str]


class EmbeddingsClient(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class VectorStoreClient(Protocol):
    def ensure_collection(self) -> None: ...

    def upsert_points(self, points: list[QdrantPoint]) -> None: ...


def index_source_chunks(
    source: IndexableSource,
    chunks: list[TextChunk],
    embeddings_client: EmbeddingsClient | None = None,
    qdrant_client: VectorStoreClient | None = None,
) -> list[IndexedChunk]:
    if source.id is None:
        raise ValueError("Source must have an id before indexing")
    if not chunks:
        raise ValueError("Source must have at least one chunk before indexing")

    resolved_embeddings_client = embeddings_client or get_openai_embeddings_client()
    resolved_qdrant_client = qdrant_client or get_qdrant_client()

    vectors = resolved_embeddings_client.embed_texts([chunk.text for chunk in chunks])
    if len(vectors) != len(chunks):
        raise ValueError("Embeddings count does not match chunk count")

    indexed_chunks = [
        IndexedChunk(
            chunk_id=build_chunk_id(source.id, chunk.index),
            text=chunk.text,
            start_offset=chunk.start_offset,
            end_offset=chunk.end_offset,
        )
        for chunk in chunks
    ]

    points = [
        QdrantPoint(
            point_id=indexed_chunk.chunk_id,
            vector=vectors[index],
            payload={
                "chunk_id": indexed_chunk.chunk_id,
                "source_id": source.id,
                "title": source.title,
                "source_type": source.source_type,
                "summary": source.summary,
                "techs": source.techs,
                "tags": source.tags,
                "cwes": source.cwes,
                "cves": source.cves,
                "text": indexed_chunk.text,
                "start_offset": indexed_chunk.start_offset,
                "end_offset": indexed_chunk.end_offset,
            },
        )
        for index, indexed_chunk in enumerate(indexed_chunks)
    ]

    # Create-on-write keeps the MVP setup simple while the collection contract is still evolving.
    resolved_qdrant_client.ensure_collection()
    resolved_qdrant_client.upsert_points(points)

    return indexed_chunks


def build_chunk_id(source_id: int, chunk_index: int) -> str:
    return f"{source_id}-{chunk_index}"
