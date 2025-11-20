import json
from dataclasses import dataclass
from typing import Any, Protocol

from app.clients.deepseek_client import DeepSeekClient, get_deepseek_metadata_client

METADATA_SYSTEM_PROMPT = (
    "Extract bug bounty write-up metadata as a single JSON object. "
    "Output only JSON and never wrap it in markdown. "
    'Use exactly this shape: {"summary": string|null, "techs": string[], "tags": string[], '
    '"cwes": string[], "cves": string[]}. '
    "Return short strings in arrays and use an empty array when a field is unknown."
)


@dataclass
class SourceMetadata:
    summary: str | None
    techs: list[str]
    tags: list[str]
    cwes: list[str]
    cves: list[str]


class MetadataCompletionClient(Protocol):
    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
    ) -> str: ...


def extract_source_metadata(
    text: str,
    deepseek_client: MetadataCompletionClient | None = None,
) -> SourceMetadata:
    client = deepseek_client or get_deepseek_metadata_client()
    # Fail fast here so a missing or invalid LLM configuration is visible during processing.
    return extract_llm_metadata(text, client)


def extract_llm_metadata(text: str, deepseek_client: MetadataCompletionClient) -> SourceMetadata:
    # Keep the prompt contract strict so the next parsing step stays deterministic.
    prompt = (
        "Write-up text:\n"
        f"{text[:12000]}\n\n"
        "Return exactly one JSON object with keys summary, techs, tags, cwes, cves."
    )
    response = deepseek_client.complete_text(
        METADATA_SYSTEM_PROMPT,
        prompt,
        response_format={"type": "json_object"},
    )

    try:
        payload = json.loads(extract_json_object_text(response))
    except json.JSONDecodeError as exc:
        raise ValueError("Metadata response must be valid JSON") from exc

    if not isinstance(payload, dict):
        raise ValueError("Metadata response must be a JSON object")

    return SourceMetadata(
        summary=normalize_optional_string(payload.get("summary")),
        techs=normalize_string_list(payload.get("techs")),
        tags=normalize_string_list(payload.get("tags")),
        cwes=normalize_string_list(payload.get("cwes"), uppercase=True),
        cves=normalize_string_list(payload.get("cves"), uppercase=True),
    )


def extract_json_object_text(response: str) -> str:
    cleaned = response.strip()
    if cleaned.startswith("```"):
        cleaned = strip_markdown_fence(cleaned)

    if cleaned.startswith("{") and cleaned.endswith("}"):
        return cleaned

    start_index = cleaned.find("{")
    end_index = cleaned.rfind("}")
    if start_index == -1 or end_index == -1 or end_index <= start_index:
        return cleaned

    # Some providers still prepend prose or wrap JSON in fences despite JSON mode.
    return cleaned[start_index : end_index + 1]


def strip_markdown_fence(response: str) -> str:
    lines = response.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()


def normalize_optional_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    normalized = " ".join(value.split())
    return normalized or None


def normalize_string_list(value: object, uppercase: bool = False) -> list[str]:
    if not isinstance(value, list):
        return []

    normalized_values: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue

        normalized = " ".join(item.split())
        if not normalized:
            continue

        normalized_values.append(normalized.upper() if uppercase else normalized)

    return list(dict.fromkeys(normalized_values))
