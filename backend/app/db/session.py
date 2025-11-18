from collections.abc import Generator
from pathlib import Path

from sqlalchemy import inspect
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
    database_path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_directory(settings.database_url)

engine = create_engine(
    settings.database_url,
    connect_args=_sqlite_connect_args(settings.database_url),
)

SOURCE_SQLITE_COLUMNS: dict[str, str] = {
    "error_message": "ALTER TABLE source ADD COLUMN error_message VARCHAR(500)",
    "processed_at": "ALTER TABLE source ADD COLUMN processed_at TIMESTAMP",
    "techs": "ALTER TABLE source ADD COLUMN techs JSON NOT NULL DEFAULT '[]'",
    "tags": "ALTER TABLE source ADD COLUMN tags JSON NOT NULL DEFAULT '[]'",
    "cwes": "ALTER TABLE source ADD COLUMN cwes JSON NOT NULL DEFAULT '[]'",
    "cves": "ALTER TABLE source ADD COLUMN cves JSON NOT NULL DEFAULT '[]'",
}


def _upgrade_sqlite_source_table() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "source" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("source")}
    missing_columns = [
        statement
        for column_name, statement in SOURCE_SQLITE_COLUMNS.items()
        if column_name not in existing_columns
    ]

    if not missing_columns:
        return

    with engine.begin() as connection:
        for statement in missing_columns:
            connection.exec_driver_sql(statement)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    _upgrade_sqlite_source_table()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
