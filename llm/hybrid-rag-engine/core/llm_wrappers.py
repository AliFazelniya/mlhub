
import os
import logging

# NOTE: This example uses the existing ChatOpenAI wrapper used in the repo.
# If you have a different LangChain LLM wrapper for OpenRouter, replace accordingly.
try:
    from langchain_openai import ChatOpenAI
except Exception:
    # If langchain-openai is not available, user should replace with their own LLM factory implementation.
    ChatOpenAI = None

logger = logging.getLogger(__name__)

class LLMFactory:
    """
    Returns LangChain-compatible LLM objects in primary->fallback order.
    Each LLM instance will be configured with low temperature and deterministic settings.
    Adapt this to your OpenRouter integration if you have a custom LLM wrapper.
    """

    def __init__(self, config: dict = None):
        # config["ordered_models"] is a list of model ids/names
        # e.g. ["google/gemma-4-31b-it:free", "meta-llama/llama-3.1-8b-instruct:free", ...]
        self.config = config or {}
        self.api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.ordered_models = self.config.get("ordered_models", [
            "google/gemma-4-26b-a4b-it:free",
            "openai/gpt-oss-20b:free",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "dots-studio/dots-3-note-preview:free",
        ])

    def get_candidate_model_names(self):
        return list(self.ordered_models)

    def get_llm(self, model_name: str):
            if ChatOpenAI is None:
                raise RuntimeError("ChatOpenAI wrapper not available - implement your own LLMFactory.get_llm")
            return ChatOpenAI(
                model=model_name, 
                api_key=self.api_key, 
                temperature=0.0,
                base_url="https://openrouter.ai/api/v1"
            )