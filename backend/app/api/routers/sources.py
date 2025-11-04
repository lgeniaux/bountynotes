from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.source import SourceListItem, SourceManualCreate, SourceRead
from app.services.source_service import create_manual_source, get_source_by_id, list_sources

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/manual", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_manual_source_endpoint(
    payload: SourceManualCreate,
    session: Session = Depends(get_session),
) -> SourceRead:
    source = create_manual_source(session, payload)
    return SourceRead.model_validate(source)


@router.get("", response_model=list[SourceListItem])
def list_sources_endpoint(session: Session = Depends(get_session)) -> list[SourceListItem]:
    sources = list_sources(session)
    return [SourceListItem.model_validate(source) for source in sources]


@router.get("/{source_id}", response_model=SourceRead)
def get_source_endpoint(source_id: int, session: Session = Depends(get_session)) -> SourceRead:
    source = get_source_by_id(session, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    return SourceRead.model_validate(source)
