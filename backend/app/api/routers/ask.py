from fastapi import APIRouter, HTTPException, status

from app.clients.deepseek_client import DeepSeekClientError
from app.clients.openai_embeddings_client import OpenAIEmbeddingsClientError
from app.clients.qdrant_client import QdrantClientError
from app.schemas.ask import AskRequest, AskResponse
from app.services.ask_service import ask_sources

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("", response_model=AskResponse)
def ask_endpoint(payload: AskRequest) -> AskResponse:
    try:
        return ask_sources(query=payload.query, filters=payload.filters, limit=payload.limit)
    except (DeepSeekClientError, OpenAIEmbeddingsClientError, QdrantClientError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
