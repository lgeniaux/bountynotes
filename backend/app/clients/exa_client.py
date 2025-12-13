from exa_py import Exa

from app.core.config import settings


class ExaClientError(Exception):
    pass


class ExaClientNotConfiguredError(ExaClientError):
    pass


class ExaEmptyContentError(ExaClientError):
    pass


class ExaUpstreamError(ExaClientError):
    pass


class ExaClient:
    def __init__(self, api_key: str, max_characters: int) -> None:
        self._api_key = api_key
        # Cap the fetch size here so chunking and embeddings do not blow up later.
        self._max_characters = max_characters

    def fetch_clean_text(self, url: str) -> str:
        if not self._api_key:
            raise ExaClientNotConfiguredError("EXA_API_KEY is not configured")

        client = Exa(api_key=self._api_key)

        try:
            response = client.get_contents(
                urls=[url],
                text={
                    "max_characters": self._max_characters,
                    "include_html_tags": False,
                },
            )
        except Exception as exc:
            raise ExaUpstreamError("Exa content fetch failed") from exc

        results = getattr(response, "results", [])
        if not results:
            raise ExaEmptyContentError("Exa returned no content")

        text = getattr(results[0], "text", None)
        # Treat empty text as an upstream failure. A blank source is useless.
        if not text:
            raise ExaEmptyContentError("Exa returned empty text")

        return text.strip()


def get_exa_client() -> ExaClient:
    return ExaClient(
        api_key=settings.exa_api_key,
        max_characters=settings.exa_max_characters,
    )
