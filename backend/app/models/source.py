from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = Field(default=None, max_length=255)
    source_type: str = Field(default="manual", max_length=50)
    status: str = Field(default="pending", max_length=50)
    raw_content: str
    clean_content: Optional[str] = None
    summary: Optional[str] = None
    # Store metadata as JSON arrays so SQLite can keep the MVP schema flat while Qdrant filters stay explicit.
    techs: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    cwes: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    cves: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    error_message: Optional[str] = Field(default=None, max_length=500)
    processed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
