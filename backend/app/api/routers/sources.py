from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.source import SourceListItem, SourceManualCreate, SourceRead, SourceUrlCreate
from app.services.source_service import (
    create_manual_source,
    create_url_source,
    get_source_by_id,
    list_sources,
)
from app.services.url_ingestion_service import (
    ForbiddenUrlError,
    InvalidUrlError,
    UrlContentFetchError,
    UrlIngestionConfigurationError,
)

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/manual", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_manual_source_endpoint(
    payload: SourceManualCreate,
    session: Session = Depends(get_session),
) -> SourceRead:
    source = create_manual_source(session, payload)
    return SourceRead.model_validate(source)


@router.post("/url", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_url_source_endpoint(
    payload: SourceUrlCreate,
    session: Session = Depends(get_session),
) -> SourceRead:
    try:
        source = create_url_source(session, payload)
    except InvalidUrlError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except ForbiddenUrlError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except UrlIngestionConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except UrlContentFetchError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

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
