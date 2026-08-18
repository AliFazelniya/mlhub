"""Language-model client factory utilities."""

import logging
import os

try:
    from langchain_openai import ChatOpenAI
except Exception:
    # Preserve deferred failure so Django can start when the optional wrapper is absent.
    ChatOpenAI = None


logger = logging.getLogger(__name__)


class LLMFactory:
    """Create LangChain-compatible LLM instances in fallback order.

    Args:
        config: Optional configuration containing an ordered_models list.
    """

    def __init__(self, config: dict = None):
        """Initialize the factory with optional model configuration.

        Args:
            config: Optional configuration containing an ordered_models list.
        """
        self.config = config or {}
        self.api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get(
            "OPENAI_API_KEY"
        )
        self.ordered_models = self.config.get(
            "ordered_models",
            [
                "google/gemma-4-26b-a4b-it:free",
                "openai/gpt-oss-20b:free",
                "nvidia/nemotron-3-ultra-550b-a55b:free",
                "dots-studio/dots-3-note-preview:free",
            ],
        )

    def get_candidate_model_names(self):
        """Return a copy of model identifiers in their fallback order.

        Returns:
            A list of configured model identifiers.
        """
        return list(self.ordered_models)

    def get_llm(self, model_name: str):
        """Create a configured LLM client for a specific model.

        Args:
            model_name: The OpenRouter model identifier to use.

        Returns:
            A configured ChatOpenAI instance.

        Raises:
            RuntimeError: If the LangChain OpenAI wrapper is unavailable.
        """
        if ChatOpenAI is None:
            raise RuntimeError(
                "ChatOpenAI wrapper not available - implement your own "
                "LLMFactory.get_llm"
            )
        return ChatOpenAI(
            model=model_name,
            api_key=self.api_key,
            temperature=0.0,
            base_url="https://openrouter.ai/api/v1",
        )
