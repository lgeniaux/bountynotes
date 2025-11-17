from openai import OpenAI

from app.core.config import settings


class OpenAIEmbeddingsClientError(Exception):
    pass


class OpenAIEmbeddingsClientNotConfiguredError(OpenAIEmbeddingsClientError):
    pass


class OpenAIEmbeddingsUpstreamError(OpenAIEmbeddingsClientError):
    pass


class OpenAIEmbeddingsClient:
    def __init__(self, api_key: str, base_url: str | None, model: str | None) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self._api_key:
            raise OpenAIEmbeddingsClientNotConfiguredError("OPENAI_API_KEY is not configured")
        if not self._base_url:
            raise OpenAIEmbeddingsClientNotConfiguredError("OPENAI_BASE_URL is not configured")
        if not self._model:
            raise OpenAIEmbeddingsClientNotConfiguredError(
                "OPENAI_EMBEDDING_MODEL is not configured"
            )

        if not texts:
            return []

        client = OpenAI(api_key=self._api_key, base_url=self._base_url)

        try:
            response = client.embeddings.create(model=self._model, input=texts)
        except Exception as exc:
            raise OpenAIEmbeddingsUpstreamError("OpenAI embeddings request failed") from exc

        vectors = [item.embedding for item in response.data]
        if len(vectors) != len(texts):
            raise OpenAIEmbeddingsUpstreamError("OpenAI returned an unexpected embeddings count")

        return vectors


def get_openai_embeddings_client() -> OpenAIEmbeddingsClient:
    return OpenAIEmbeddingsClient(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_embedding_model,
    )
