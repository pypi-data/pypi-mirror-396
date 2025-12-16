from __future__ import annotations

import dataclasses
import os
import typing

if typing.TYPE_CHECKING:
    from pydantic_ai.models import Model

    from typing import Self, TypeAliasType

    Provider = TypeAliasType(
        "Provider",
        typing.Literal["openai", "openrouter", "anthropic", "vercel"],
    )


@dataclasses.dataclass(frozen=True)
class Connector:
    provider: Provider
    base_url: str | None
    api_key: str
    model_name: str

    _cookie: object = dataclasses.field(repr=False, default=None)

    def __post_init__(self) -> None:
        if self._cookie is not _marker:
            raise ValueError(
                "use Gateway.from_environment() "
                "instead of a direct constructor call"
            )

    @classmethod
    def from_environment(cls) -> Self:
        llm_key = os.environ.get("PI_LLM_API_KEY")
        if not llm_key:
            raise ValueError("PI_LLM_API_KEY is not set")

        llm_model = os.environ.get("PI_LLM_MODEL")
        if not llm_model:
            raise ValueError("PI_LLM_MODEL is not set")

        provider: Provider
        base_url = None
        if llm_key.startswith("sk-or-v1-"):
            base_url = "https://openrouter.ai/api/v1"
            provider = "openrouter"
        elif llm_key.startswith("sk-ant-"):
            provider = "anthropic"
        elif llm_key.startswith("sk-"):
            provider = "openai"
        elif llm_key.startswith("vck_"):
            provider = "vercel"
        else:
            raise ValueError("PI_LLM_API_KEY is set to an unknown provider")

        return cls(
            provider=provider,
            base_url=base_url,
            api_key=llm_key,
            model_name=llm_model,
            _cookie=_marker,
        )

    async def validate_key(self) -> None:
        if self.provider == "openai":
            import openai

            oai_client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            try:
                await oai_client.models.retrieve(self.model_name, timeout=1)
            except Exception as e:
                raise ValueError(
                    f"Invalid OpenAI API key or the model name: {e!r}"
                )

        elif self.provider == "anthropic":
            import anthropic

            ant_client = anthropic.AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            try:
                await ant_client.models.retrieve(self.model_name, timeout=1)
            except anthropic.AnthropicError as e:
                raise ValueError(
                    f"Invalid Anthropic API key or the model name: {e}"
                )

        elif self.provider == "openrouter":
            import openai

            oai_client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            try:
                models = await oai_client.models.list(timeout=1)
            except Exception as e:
                raise ValueError(f"Invalid OpenRouter API key: {e!r}")
            else:
                if self.model_name not in {m.id async for m in models}:
                    raise ValueError(
                        f"OpenRouter does not expose model "
                        f"{self.model_name!r} with the provided API key"
                    )

        elif self.provider == "vercel":
            # TODO
            pass

        else:
            raise ValueError(f"Unknown provider: {self.provider!r}")

    def make_model(self) -> Model:
        if self.provider == "openai":
            from pydantic_ai.models.openai import OpenAIModel
            from pydantic_ai.providers.openai import OpenAIProvider

            return OpenAIModel(
                self.model_name,
                provider=OpenAIProvider(api_key=self.api_key),
            )

        elif self.provider == "anthropic":
            from pydantic_ai.models.anthropic import AnthropicModel
            from pydantic_ai.providers.anthropic import AnthropicProvider

            return AnthropicModel(
                self.model_name,
                provider=AnthropicProvider(api_key=self.api_key),
            )

        elif self.provider == "openrouter":
            from pydantic_ai.models.openai import OpenAIModel
            from pydantic_ai.providers.openrouter import OpenRouterProvider

            return OpenAIModel(
                self.model_name,
                provider=OpenRouterProvider(api_key=self.api_key),
            )

        elif self.provider == "vercel":
            from pydantic_ai.models.openai import OpenAIModel
            from pydantic_ai.providers.vercel import VercelProvider

            return OpenAIModel(
                self.model_name,
                provider=VercelProvider(api_key=self.api_key),
            )

        else:
            raise ValueError(f"Unknown provider: {self.provider!r}")


_marker = object()
