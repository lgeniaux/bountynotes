from openai import OpenAI

from app.core.config import settings


class DeepSeekClientError(Exception):
    pass


class DeepSeekClientNotConfiguredError(DeepSeekClientError):
    pass


class DeepSeekUpstreamError(DeepSeekClientError):
    pass


class DeepSeekClient:
    def __init__(
        self,
        api_key: str,
        base_url: str | None,
        model: str | None,
        model_env_name: str,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._model_env_name = model_env_name

    def complete_text(self, system_prompt: str, user_prompt: str) -> str:
        if not self._api_key:
            raise DeepSeekClientNotConfiguredError("DEEPSEEK_API_KEY is not configured")
        if not self._base_url:
            raise DeepSeekClientNotConfiguredError("DEEPSEEK_BASE_URL is not configured")
        if not self._model:
            raise DeepSeekClientNotConfiguredError(f"{self._model_env_name} is not configured")

        client = OpenAI(api_key=self._api_key, base_url=self._base_url)

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:
            raise DeepSeekUpstreamError("DeepSeek completion failed") from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise DeepSeekUpstreamError("DeepSeek returned empty content")

        return content.strip()


def get_deepseek_metadata_client() -> DeepSeekClient:
    # Metadata extraction and final answer generation can evolve at different speeds, so keep model selection separate.
    return DeepSeekClient(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_metadata_model,
        model_env_name="DEEPSEEK_METADATA_MODEL",
    )


def get_deepseek_chat_client() -> DeepSeekClient:
    return DeepSeekClient(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_chat_model,
        model_env_name="DEEPSEEK_CHAT_MODEL",
    )
