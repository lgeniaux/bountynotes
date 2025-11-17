import json
from dataclasses import dataclass
from typing import Protocol

from app.clients.deepseek_client import DeepSeekClient, get_deepseek_client

METADATA_SYSTEM_PROMPT = (
    "Extract bug bounty write-up metadata as strict JSON with keys summary, techs, tags, cwes, cves. "
    "Return arrays of short strings for techs, tags, cwes, cves. Return no prose outside JSON."
)


@dataclass
class SourceMetadata:
    summary: str | None
    techs: list[str]
    tags: list[str]
    cwes: list[str]
    cves: list[str]


class MetadataCompletionClient(Protocol):
    def complete_text(self, system_prompt: str, user_prompt: str) -> str: ...


def extract_source_metadata(
    text: str,
    deepseek_client: MetadataCompletionClient | None = None,
) -> SourceMetadata:
    client = deepseek_client or get_deepseek_client()
    # Fail fast here so a missing or invalid LLM configuration is visible during processing.
    return extract_llm_metadata(text, client)


def extract_llm_metadata(text: str, deepseek_client: MetadataCompletionClient) -> SourceMetadata:
    # Keep the prompt contract strict so the next parsing step stays deterministic.
    prompt = "Write-up text:\n" f"{text[:12000]}\n\n" "Return strict JSON only."
    response = deepseek_client.complete_text(METADATA_SYSTEM_PROMPT, prompt)

    try:
        payload = json.loads(response)
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
