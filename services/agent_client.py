"""
Agent Client service that handles provider initialization and LLM execution.
"""

from typing import List, Dict, Any, Optional
import os
import config
from services.llm_provider import (
    BaseLLMProvider,
    OpenAIProvider,
    GeminiProvider,
    MockOfflineProvider,
    ProviderResponse,
)


class AgentClient:
    """Factory and manager for LLM providers."""

    @staticmethod
    def get_provider(
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> BaseLLMProvider:
        # Determine provider name
        name = (provider_name or config.DEFAULT_PROVIDER or "openai").strip().lower()

        # Try OpenAI
        if name == "openai":
            key = api_key or os.getenv("OPENAI_API_KEY") or config.OPENAI_API_KEY
            if key:
                try:
                    return OpenAIProvider(api_key=key)
                except Exception as e:
                    print(f"⚠️ OpenAI init error: {e}. Falling back...")
            return MockOfflineProvider()

        # Try Gemini
        elif name == "gemini":
            key = api_key or os.getenv("GEMINI_API_KEY") or config.GEMINI_API_KEY
            if key:
                try:
                    return GeminiProvider(api_key=key)
                except Exception as e:
                    print(f"⚠️ Gemini init error: {e}. Falling back...")
            return MockOfflineProvider()

        # Default fallback
        return MockOfflineProvider()
