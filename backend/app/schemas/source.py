from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SourceManualCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    raw_content: str = Field(min_length=1)


class SourceUrlCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    url: str = Field(min_length=1, max_length=2048)


class SourceListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    source_type: str
    status: str
    error_message: str | None
    processed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    source_type: str
    status: str
    raw_content: str
    clean_content: str | None
    summary: str | None
    techs: list[str]
    tags: list[str]
    cwes: list[str]
    cves: list[str]
    error_message: str | None
    processed_at: datetime | None
    created_at: datetime
    updated_at: datetime
