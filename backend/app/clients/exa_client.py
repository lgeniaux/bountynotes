from importlib import import_module
from typing import Any

from app.core.config import settings


class ExaClientError(Exception):
    pass


class ExaClientNotConfiguredError(ExaClientError):
    pass


class ExaEmptyContentError(ExaClientError):
    pass


class ExaClient:
    def __init__(self, api_key: str, max_characters: int) -> None:
        self._api_key = api_key
        self._max_characters = max_characters

    def _build_client(self) -> Any:
        exa_module = import_module("exa_py")
        return exa_module.Exa(api_key=self._api_key)

    def fetch_clean_text(self, url: str) -> str:
        if not self._api_key:
            raise ExaClientNotConfiguredError("EXA_API_KEY is not configured")

        client = self._build_client()
        response = client.get_contents(
            urls=[url],
            text={
                "max_characters": self._max_characters,
                "include_html_tags": False,
            },
        )

        results = getattr(response, "results", [])
        if not results:
            raise ExaEmptyContentError("Exa returned no content")

        text = getattr(results[0], "text", None)
        if not text:
            raise ExaEmptyContentError("Exa returned empty text")

        return text.strip()


def get_exa_client() -> ExaClient:
    return ExaClient(
        api_key=settings.exa_api_key,
        max_characters=settings.exa_max_characters,
    )
