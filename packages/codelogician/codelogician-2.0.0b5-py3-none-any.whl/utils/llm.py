import os
from typing import Literal, cast, get_args

import structlog
import tiktoken
from langchain.chat_models.base import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.base import LanguageModelInput, LanguageModelOutput
from langchain_core.messages import BaseMessage, _message_from_dict, message_to_dict
from langchain_core.runnables.fallbacks import RunnableWithFallbacks
from langchain_google_vertexai import ChatVertexAI
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain_xai import ChatXAI
from pydantic import SecretStr

logger = cast(structlog.stdlib.BoundLogger, structlog.get_logger("util.llm"))
LLM_USE_GOOGLE = os.environ.get("LLM_USE_GOOGLE", False)

ChatModelWithFallback = RunnableWithFallbacks[LanguageModelInput, LanguageModelOutput]

# Models
OpenAIModel = Literal[
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-3.5-turbo",
    "o3-mini:low",
    "o3-mini:medium",
    "o3-mini:high",
]
AnthropicModel = Literal[
    "claude-sonnet-4-20250514",
    "claude-3-5-haiku-latest",
    "claude-4-opus-20250514",
    "claude-sonnet-4-5-20250929",
]
GoogleModel = Literal[
    "gemini-2.0-flash-001",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    # "gemini-2.0-flash-thinking-exp-01-21",
    # "gemini-2.0-pro-exp-02-05",
]
XAIModel = Literal[
    "grok-code-fast-1",
    "grok-4-fast-reasoning",
    "grok-4-fast-nonreasoning",
]
DeepSeekModel = Literal["deepseek-chat", "deepseek-reasoner"]
OllamaModel = Literal["ollama:llama3.2"]
MODEL_NAME = (
    OpenAIModel | AnthropicModel | GoogleModel | DeepSeekModel | OllamaModel | XAIModel
)
MODELS = {
    "openai": list(get_args(OpenAIModel)),
    "anthropic": list(get_args(AnthropicModel)),
    "google": list(get_args(GoogleModel)),
    "deepseek": list(get_args(DeepSeekModel)),
    "ollama": list(get_args(OllamaModel)),
    "xai": list(get_args(XAIModel)),
}

# Use cases
USE_CASE = Literal["chat", "code", "json", "tools", "reasoning"]
GOOGLE_DEFAULT_MODELS: dict[USE_CASE, MODEL_NAME] = {
    "chat": "gemini-2.0-flash-001",
    # Note: pro model rate-limited to 10 queries per minute during preview
    "code": "gemini-2.0-pro-exp-02-05",
    "json": "gemini-2.0-flash-001",
    "tools": "gemini-2.0-flash-001",
    "reasoning": "gemini-2.0-flash-thinking-exp-01-21",
}
NON_GOOGLE_DEFAULT_MODELS: dict[USE_CASE, MODEL_NAME] = {
    "chat": "gpt-4o-mini",
    "code": (
        "claude-sonnet-4-5-20250929"
        if os.environ.get("ANTHROPIC_API_KEY")
        else "gpt-4o-mini"
    ),
    "json": "gpt-4o-mini",
    "tools": "gpt-4o-mini",
    "reasoning": "o3-mini:low",
}
DEFAULT_LLM: dict[USE_CASE, MODEL_NAME] = (
    GOOGLE_DEFAULT_MODELS if LLM_USE_GOOGLE else NON_GOOGLE_DEFAULT_MODELS
)


def _get_model_provider(
    model_name: str,
) -> Literal["openai", "anthropic", "deepseek", "google", "ollama", "xai"]:
    """Determine the provider for a given model name."""
    if model_name in get_args(OpenAIModel):
        return "openai"
    elif model_name in get_args(AnthropicModel):
        return "anthropic"
    elif model_name in get_args(GoogleModel):
        return "google"
    elif model_name in get_args(DeepSeekModel):
        return "deepseek"
    elif model_name in get_args(OllamaModel):
        return "ollama"
    elif model_name in get_args(XAIModel):
        return "xai"
    else:
        raise ValueError(f"Unknown model name: {model_name}")


def _create_model(
    model_name: str,
    provider: Literal["openai", "anthropic", "deepseek", "google", "ollama", "xai"],
    temperature: float,
) -> BaseChatModel:
    """Create a base chat model for the specified provider."""

    if provider == "openai":
        if model_name.startswith("o"):
            (model_name, reasoning_effort) = model_name.split(":")
            return ChatOpenAI(model_name=model_name, reasoning_effort=reasoning_effort)
        else:
            return ChatOpenAI(model_name=model_name, temperature=temperature)
    elif provider == "anthropic":
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens=8192,
        )
    elif provider == "deepseek":
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        api_key = SecretStr(api_key) if api_key else None
        return BaseChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com",
            max_tokens=8192,
        )
    elif provider == "google":
        return ChatVertexAI(
            model=model_name,
            # us-central1 required for pro (preview). Change to europe-west1 when GA.
            location=os.environ.get("GOOGLE_COMPUTE_REGION", "us-central1"),
        )
    elif provider == "ollama":
        if ollama_url := os.environ.get("OLLAMA_URL"):
            # Note: Ollama currently doesn't stream tokens back when tools are specified
            # We could work around this by separating the chat response to a different
            # node, rather than chatting directly from `supervisor`
            # See https://github.com/ollama/ollama/issues/7886
            return ChatOpenAI(
                model_name=model_name.removeprefix("ollama:"),
                temperature=temperature,
                openai_api_base=ollama_url,
                openai_api_key=None,
            )
        else:
            raise ValueError("Ollama models not available")
    elif provider == "xai":
        return ChatXAI(
            model=model_name,
            temperature=temperature,
        )


def get_llm(
    model_name: MODEL_NAME | None = None,
    use_case: USE_CASE | None = None,
    with_fallback: bool | None = None,
    temperature: float | None = None,
) -> BaseChatModel:
    # NOTE: actual return type is BaseChatModel | ChatModelWithFallback
    # But they are equivalent so we can ignore the type difference for convenience
    """
    Get the requested LLM, or choose a suitable one for the use case.
    At least one of model_name or use_case must be provided.
    model_name takes precedence.
    """
    if with_fallback is None:
        disable_fallback_str: str = os.environ.get("DISABLE_LLM_FALLBACK", "false")
        with_fallback: bool = disable_fallback_str.lower() != "true"

    if temperature is None:
        temperature = float(os.getenv("IU_LLM_TEMPERATURE", 0.0))

    if (model_name is None) and (use_case is None):
        raise ValueError("At least one of model_name or use_case must be provided")

    model_name = model_name if model_name is not None else DEFAULT_LLM[use_case]
    provider = _get_model_provider(model_name)

    # Create base model
    model = _create_model(model_name, provider, temperature)

    # Add fallback support
    if with_fallback:
        if provider != "google":
            fallback_model_name = "gemini-2.5-pro"
            fallback_provider = "google"
        else:
            fallback_model_name = "claude-sonnet-4-20250514"
            fallback_provider = "anthropic"
        fallback_model = _create_model(
            fallback_model_name,
            fallback_provider,
            temperature,
        )
        model = model.with_fallbacks([fallback_model])
        logger.info(
            "initialized_model",
            model=model_name,
            fallback_model=fallback_model_name,
        )
    else:
        logger.info("initialized_model", model=model_name)

    return model  # type: ignore


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def anthropic_mark_cache_control(msg: BaseMessage) -> BaseMessage:
    """
    Convert a langchain message to an message that will be cached by Anthropic.

    Note:
    - Not applicable to other LLMs
    - Only works for the first message
    - Exact match is required for reading cached message
    - Number of tokens should be greater than 1024
    - Cached are evicted after 5-10 minutes
    - Cache writing is 25% more expensive, reading is faster and 90% cheaper
    """
    msg_dict = message_to_dict(msg)
    if isinstance(msg_dict["data"]["content"], list):
        raise ValueError("Message content need to be a string")
    new_msg_dict = msg_dict.copy()
    new_msg_dict["data"]["content"] = [
        {
            "type": "text",
            "text": msg_dict["data"]["content"],
            "cache_control": {"type": "ephemeral"},
        }
    ]
    return _message_from_dict(new_msg_dict)


def support_anthropic_prompt_caching(llm: BaseChatModel) -> bool:
    if not isinstance(llm, ChatAnthropic):
        return False
    for model in [
        "claude-4-sonnet",
        "claude-3-5-sonnet",
        "claude-3-5-haiku",
        "claude-3-haiku",
        "claude-3-opus",
    ]:
        if llm.model.startswith(model):
            return True
    return False
