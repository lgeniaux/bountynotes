from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.models.source import Source


def _sqlite_connect_args(database_url: str) -> dict[str, bool]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


def _ensure_sqlite_directory(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return

    database_path = Path(database_url.removeprefix("sqlite:///"))
    # SQLite will not create the parent folder for us on first run.
    database_path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_directory(settings.database_url)

engine = create_engine(
    settings.database_url,
    connect_args=_sqlite_connect_args(settings.database_url),
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    # One session per request keeps the API path simple and predictable.
    with Session(engine) as session:
        yield session
