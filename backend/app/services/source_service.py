from sqlmodel import Session, desc, select

from app.db.session import engine
from app.models.source import Source
from app.models.source import utc_now
from app.schemas.source import SourceManualCreate, SourceUrlCreate
from app.services.url_ingestion_service import ingest_url_content, normalize_text


def create_manual_source(session: Session, payload: SourceManualCreate) -> Source:
    source = Source(
        title=payload.title,
        status="pending",
        raw_content=payload.raw_content,
    )

    session.add(source)
    session.commit()
    session.refresh(source)

    return source


def create_url_source(session: Session, payload: SourceUrlCreate) -> Source:
    content = ingest_url_content(payload.url)
    source = Source(
        title=payload.title or payload.url,
        source_type="url",
        status="pending",
        raw_content=content.raw_content,
        clean_content=content.clean_content,
    )

    session.add(source)
    session.commit()
    session.refresh(source)

    return source


def process_source(source_id: int) -> None:
    with Session(engine) as session:
        source = session.get(Source, source_id)
        if source is None:
            return

        source.status = "processing"
        source.error_message = None
        source.updated_at = utc_now()
        session.add(source)
        session.commit()
        session.refresh(source)

        try:
            processed_content = normalize_text(source.clean_content or source.raw_content)
            if not processed_content:
                raise ValueError("Source content is empty after normalization")

            source.clean_content = processed_content
            source.status = "ready"
            source.processed_at = utc_now()
            source.error_message = None
        except ValueError as exc:
            source.status = "failed"
            source.error_message = str(exc)
        finally:
            source.updated_at = utc_now()
            session.add(source)
            session.commit()


def list_sources(session: Session) -> list[Source]:
    statement = select(Source).order_by(desc(Source.created_at))
    return list(session.exec(statement))


def get_source_by_id(session: Session, source_id: int) -> Source | None:
    return session.get(Source, source_id)
