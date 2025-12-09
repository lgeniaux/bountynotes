from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.clients.deepseek_client import DeepSeekClientError
from app.clients.openai_embeddings_client import OpenAIEmbeddingsClientError
from app.clients.qdrant_client import QdrantClientError
from app.db.session import get_session
from app.schemas.ask import AskRequest, AskResponse
from app.services.ask_service import ask_sources
from app.services.source_service import list_ready_source_ids

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("", response_model=AskResponse)
def ask_endpoint(payload: AskRequest, session: Session = Depends(get_session)) -> AskResponse:
    try:
        return ask_sources(
            query=payload.query,
            filters=payload.filters,
            limit=payload.limit,
            ready_source_ids=list_ready_source_ids(session),
        )
    except (DeepSeekClientError, OpenAIEmbeddingsClientError, QdrantClientError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
