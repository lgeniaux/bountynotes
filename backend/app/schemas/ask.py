from pydantic import BaseModel, Field


class AskFilters(BaseModel):
    source_id: int | None = None
    tags: list[str] = Field(default_factory=list)
    cwes: list[str] = Field(default_factory=list)
    cves: list[str] = Field(default_factory=list)


class AskRequest(BaseModel):
    query: str = Field(min_length=1)
    filters: AskFilters | None = None
    limit: int = Field(default=5, ge=1, le=20)


class CitationRead(BaseModel):
    source_id: int
    chunk_id: str
    title: str | None
    snippet: str
    score: float
    source_type: str | None = None
    summary: str | None = None
    techs: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    cwes: list[str] = Field(default_factory=list)
    cves: list[str] = Field(default_factory=list)
    start_offset: int | None = None
    end_offset: int | None = None


class AskResponse(BaseModel):
    answer: str | None = None
    citations: list[CitationRead]
