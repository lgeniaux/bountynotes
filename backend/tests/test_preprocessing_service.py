from app.services.chunking_service import chunk_text
from app.services.metadata_service import extract_source_metadata
from app.services.preprocessing_service import preprocess_source_content


class FakeDeepSeekClient:
    def __init__(self, response: str) -> None:
        self._response = response

    def complete_text(self, system_prompt: str, user_prompt: str) -> str:
        return self._response


def test_extract_source_metadata_merges_regex_and_llm_values() -> None:
    client = FakeDeepSeekClient(
        '{"summary": "Short summary", "techs": ["Angular", "FastAPI"], '
        '"tags": ["xss", "bug bounty"], "cwes": ["CWE-89"], "cves": ["CVE-2024-9999"]}'
    )

    metadata = extract_source_metadata(
        "Write-up covering CWE-79 and CVE-2024-12345.",
        deepseek_client=client,
    )

    assert metadata.summary == "Short summary"
    assert metadata.techs == ["Angular", "FastAPI"]
    assert metadata.tags == ["xss", "bug bounty"]
    assert metadata.cwes == ["CWE-89"]
    assert metadata.cves == ["CVE-2024-9999"]


def test_preprocess_source_content_returns_chunks_from_llm_metadata() -> None:
    client = FakeDeepSeekClient(
        '{"summary": "Short summary", "techs": ["FastAPI"], '
        '"tags": ["sqli"], "cwes": ["CWE-89"], "cves": []}'
    )

    result = preprocess_source_content(
        "First paragraph.\n\nSecond paragraph with CWE-79.",
        deepseek_client=client,
    )

    assert result.clean_content == "First paragraph.\n\nSecond paragraph with CWE-79."
    assert result.summary == "Short summary"
    assert result.techs == ["FastAPI"]
    assert result.tags == ["sqli"]
    assert result.cwes == ["CWE-89"]
    assert result.cves == []
    assert len(result.chunks) == 1


def test_extract_source_metadata_raises_when_llm_returns_invalid_json() -> None:
    client = FakeDeepSeekClient("not json")

    try:
        extract_source_metadata("text", deepseek_client=client)
    except ValueError as exc:
        assert str(exc) == "Metadata response must be valid JSON"
        return

    raise AssertionError("Expected invalid JSON metadata to raise ValueError")


def test_chunk_text_creates_overlapping_chunks_for_long_content() -> None:
    long_text = "A" * 900 + " " + "B" * 900

    chunks = chunk_text(long_text, max_chars=1000, overlap_chars=100)

    assert len(chunks) >= 2
    assert chunks[0].end_offset > chunks[1].start_offset
