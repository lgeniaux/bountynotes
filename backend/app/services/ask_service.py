from dataclasses import dataclass
from typing import Any, Protocol

from app.clients.deepseek_client import get_deepseek_chat_client
from app.clients.openai_embeddings_client import get_openai_embeddings_client
from app.clients.qdrant_client import QdrantSearchFilters, get_qdrant_client
from app.schemas.ask import AskFilters, AskResponse, CitationRead

ANSWER_SYSTEM_PROMPT = (
    "Answer the user's security question using only the provided citations. "
    "Be concise, factual, and do not invent facts that are not grounded in the citations."
)


@dataclass
class SearchHit:
    score: float
    payload: dict[str, Any]


class AskEmbeddingsClient(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class AskVectorStoreClient(Protocol):
    def search(
        self,
        query_vector: list[float],
        filters: QdrantSearchFilters | None = None,
        limit: int = 5,
    ) -> list[Any]: ...


class AnswerClient(Protocol):
    def complete_text(self, system_prompt: str, user_prompt: str) -> str: ...


def ask_sources(
    query: str,
    filters: AskFilters | None = None,
    limit: int = 5,
    ready_source_ids: set[int] | None = None,
    embeddings_client: AskEmbeddingsClient | None = None,
    qdrant_client: AskVectorStoreClient | None = None,
    answer_client: AnswerClient | None = None,
) -> AskResponse:
    resolved_embeddings_client = embeddings_client or get_openai_embeddings_client()
    resolved_qdrant_client = qdrant_client or get_qdrant_client()
    resolved_answer_client = answer_client or get_deepseek_chat_client()

    vectors = resolved_embeddings_client.embed_texts([query])
    if len(vectors) != 1:
        raise ValueError("Ask query must produce exactly one embedding")

    search_results = resolved_qdrant_client.search(
        query_vector=vectors[0],
        filters=build_qdrant_filters(filters),
        limit=limit,
    )

    if ready_source_ids is not None:
        search_results = filter_results_to_ready_sources(search_results, ready_source_ids)

    citations = [build_citation(result) for result in search_results]
    # Skip generation when retrieval is empty so the API never invents an unsupported answer.
    answer = build_answer(query, citations, resolved_answer_client) if citations else None
    return AskResponse(answer=answer, citations=citations)


def build_qdrant_filters(filters: AskFilters | None) -> QdrantSearchFilters | None:
    if filters is None:
        return None

    return QdrantSearchFilters(
        source_id=filters.source_id,
        tags=filters.tags or None,
        cwes=filters.cwes or None,
        cves=filters.cves or None,
    )


def filter_results_to_ready_sources(results: list[Any], ready_source_ids: set[int]) -> list[Any]:
    return [
        result
        for result in results
        if int((getattr(result, "payload", None) or {}).get("source_id", -1)) in ready_source_ids
    ]


def build_citation(result: Any) -> CitationRead:
    payload = getattr(result, "payload", None) or {}

    if "source_id" not in payload or "chunk_id" not in payload or "text" not in payload:
        raise ValueError("Qdrant result payload is missing required citation fields")

    return CitationRead(
        source_id=int(payload["source_id"]),
        chunk_id=str(payload["chunk_id"]),
        title=payload.get("title"),
        snippet=str(payload["text"]),
        score=float(getattr(result, "score", 0.0)),
        source_type=payload.get("source_type"),
        summary=payload.get("summary"),
        techs=coerce_string_list(payload.get("techs")),
        tags=coerce_string_list(payload.get("tags")),
        cwes=coerce_string_list(payload.get("cwes")),
        cves=coerce_string_list(payload.get("cves")),
        start_offset=coerce_optional_int(payload.get("start_offset")),
        end_offset=coerce_optional_int(payload.get("end_offset")),
    )


def build_answer(query: str, citations: list[CitationRead], answer_client: AnswerClient) -> str:
    prompt = build_answer_prompt(query, citations)
    return answer_client.complete_text(ANSWER_SYSTEM_PROMPT, prompt)


def build_answer_prompt(query: str, citations: list[CitationRead]) -> str:
    citation_blocks = []
    for index, citation in enumerate(citations, start=1):
        citation_blocks.append(
            "\n".join(
                [
                    f"Citation {index}",
                    f"chunk_id: {citation.chunk_id}",
                    f"title: {citation.title or 'Untitled'}",
                    f"score: {citation.score}",
                    f"snippet: {citation.snippet}",
                ]
            )
        )

    citations_text = "\n\n".join(citation_blocks)

    # Keep the prompt plain text so we can inspect the exact grounding sent to the model.
    return (
        f"Question:\n{query}\n\n"
        "Citations:\n"
        f"{citations_text}\n\n"
        "Write the answer in plain text and ground it in the citations."
    )


def coerce_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, str)]


def coerce_optional_int(value: object) -> int | None:
    if isinstance(value, int):
        return value

    return None
