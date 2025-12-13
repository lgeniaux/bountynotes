from dataclasses import dataclass

from app.services.chunking_service import TextChunk, chunk_text
from app.services.metadata_service import (
    MetadataCompletionClient,
    SourceMetadata,
    extract_source_metadata,
)
from app.services.text_service import normalize_text


@dataclass
class PreprocessingResult:
    clean_content: str
    summary: str | None
    techs: list[str]
    tags: list[str]
    cwes: list[str]
    cves: list[str]
    chunks: list[TextChunk]


def preprocess_source_content(
    content: str,
    deepseek_client: MetadataCompletionClient | None = None,
) -> PreprocessingResult:
    clean_content = normalize_text(content)
    # If cleanup leaves nothing, stop here instead of indexing garbage.
    if not clean_content:
        raise ValueError("Source content is empty after normalization")

    metadata: SourceMetadata = extract_source_metadata(
        clean_content, deepseek_client=deepseek_client
    )
    # Chunk after metadata extraction so the LLM sees the broadest context we have for V1.
    chunks = chunk_text(clean_content)
    if not chunks:
        raise ValueError("Source content produced no chunks")

    return PreprocessingResult(
        clean_content=clean_content,
        summary=metadata.summary,
        techs=metadata.techs,
        tags=metadata.tags,
        cwes=metadata.cwes,
        cves=metadata.cves,
        chunks=chunks,
    )
