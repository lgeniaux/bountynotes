from dataclasses import dataclass
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings


class QdrantClientError(Exception):
    pass


class QdrantClientNotConfiguredError(QdrantClientError):
    pass


class QdrantUpstreamError(QdrantClientError):
    pass


@dataclass
class QdrantPoint:
    point_id: str | int
    vector: list[float]
    payload: dict[str, Any]


@dataclass
class QdrantSearchFilters:
    source_id: int | None = None
    tags: list[str] | None = None
    cwes: list[str] | None = None
    cves: list[str] | None = None


class QdrantVectorStoreClient:
    def __init__(
        self,
        url: str | None,
        collection_name: str | None,
        vector_size: int | None,
    ) -> None:
        self._url = url
        self._collection_name = collection_name
        self._vector_size = vector_size

    def ensure_collection(self) -> None:
        client = self._build_client()
        collection_name = self._get_collection_name()
        vector_size = self._get_vector_size()

        try:
            collections = client.get_collections().collections
            if any(collection.name == collection_name for collection in collections):
                return

            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
        except Exception as exc:
            raise QdrantUpstreamError("Qdrant collection setup failed") from exc

    def upsert_points(self, points: list[QdrantPoint]) -> None:
        if not points:
            return

        client = self._build_client()
        collection_name = self._get_collection_name()

        try:
            client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(id=point.point_id, vector=point.vector, payload=point.payload)
                    for point in points
                ],
            )
        except Exception as exc:
            raise QdrantUpstreamError("Qdrant upsert failed") from exc

    def search(
        self,
        query_vector: list[float],
        filters: QdrantSearchFilters | None = None,
        limit: int = 5,
    ) -> list[Any]:
        client = self._build_client()
        collection_name = self._get_collection_name()

        try:
            return client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=self._build_filter(filters),
                limit=limit,
                with_payload=True,
            )
        except Exception as exc:
            raise QdrantUpstreamError("Qdrant search failed") from exc

    def _build_client(self) -> QdrantClient:
        if not self._url:
            raise QdrantClientNotConfiguredError("QDRANT_URL is not configured")

        return QdrantClient(url=self._url)

    def _get_collection_name(self) -> str:
        if not self._collection_name:
            raise QdrantClientNotConfiguredError("QDRANT_COLLECTION_NAME is not configured")

        return self._collection_name

    def _get_vector_size(self) -> int:
        if self._vector_size is None:
            raise QdrantClientNotConfiguredError("QDRANT_VECTOR_SIZE is not configured")

        return self._vector_size

    def _build_filter(self, filters: QdrantSearchFilters | None) -> Filter | None:
        if filters is None:
            return None

        conditions: list[Any] = []
        if filters.source_id is not None:
            conditions.append(
                FieldCondition(key="source_id", match=MatchValue(value=filters.source_id))
            )
        if filters.tags:
            conditions.append(FieldCondition(key="tags", match=MatchAny(any=filters.tags)))
        if filters.cwes:
            conditions.append(FieldCondition(key="cwes", match=MatchAny(any=filters.cwes)))
        if filters.cves:
            conditions.append(FieldCondition(key="cves", match=MatchAny(any=filters.cves)))

        if not conditions:
            return None

        return Filter(must=conditions)


def get_qdrant_client() -> QdrantVectorStoreClient:
    return QdrantVectorStoreClient(
        url=settings.qdrant_url,
        collection_name=settings.qdrant_collection_name,
        vector_size=settings.qdrant_vector_size,
    )
