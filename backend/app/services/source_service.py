from sqlmodel import Session, desc, select

from app.models.source import Source
from app.schemas.source import SourceManualCreate


def create_manual_source(session: Session, payload: SourceManualCreate) -> Source:
    source = Source(
        title=payload.title,
        raw_content=payload.raw_content,
    )

    session.add(source)
    session.commit()
    session.refresh(source)

    return source


def list_sources(session: Session) -> list[Source]:
    statement = select(Source).order_by(desc(Source.created_at))
    return list(session.exec(statement))


def get_source_by_id(session: Session, source_id: int) -> Source | None:
    return session.get(Source, source_id)
