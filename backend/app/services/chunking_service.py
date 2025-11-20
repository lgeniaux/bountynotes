from dataclasses import dataclass


@dataclass
class TextChunk:
    index: int
    text: str
    start_offset: int
    end_offset: int


def chunk_text(text: str, max_chars: int = 1200, overlap_chars: int = 200) -> list[TextChunk]:
    normalized_text = text.strip()
    if not normalized_text:
        return []

    chunks: list[TextChunk] = []
    start_offset = 0
    text_length = len(normalized_text)

    while start_offset < text_length:
        end_offset = min(start_offset + max_chars, text_length)
        if end_offset < text_length:
            # Prefer natural boundaries first so citations stay readable in the ask response.
            split_offset = normalized_text.rfind("\n", start_offset, end_offset)
            if split_offset == -1:
                split_offset = normalized_text.rfind(" ", start_offset, end_offset)
            if split_offset > start_offset:
                end_offset = split_offset

        chunk_text_value = normalized_text[start_offset:end_offset].strip()
        if chunk_text_value:
            chunks.append(
                TextChunk(
                    index=len(chunks),
                    text=chunk_text_value,
                    start_offset=start_offset,
                    end_offset=end_offset,
                )
            )

        if end_offset >= text_length:
            break

        # Keep a small overlap so nearby context survives retrieval without needing parent-child chunks yet.
        next_start = max(end_offset - overlap_chars, start_offset + 1)
        start_offset = next_start

    return chunks
