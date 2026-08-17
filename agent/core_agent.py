"""
Core Framework-Agnostic Agent for Datta Krushi Seva Kendra.
Independent of Streamlit — can be plugged into WhatsApp, Telegram, or Web APIs directly.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from agent.prompts.system_prompt import get_system_prompt
from services.agent_client import AgentClient
from services.product_search import ProductSearchService
from services.llm_provider import ToolExecutionRecord


@dataclass
class AgentResponse:
    text: str
    recommended_products: List[Dict[str, Any]] = field(default_factory=list)
    tool_records: List[ToolExecutionRecord] = field(default_factory=list)
    order_created: Optional[Dict[str, Any]] = None
    provider_used: str = ""
    model_used: str = ""


class CoreAgent:
    """
    Central reasoning and conversation engine for farmer support & sales.
    """

    def __init__(
        self,
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider_name = provider_name
        self.api_key = api_key
        self.model = model
        self.system_prompt = get_system_prompt()

    def chat(
        self,
        messages: List[Dict[str, Any]],
        image_bytes: Optional[bytes] = None,
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AgentResponse:
        """
        Processes a conversation turn.
        `messages` is a list of {'role': 'user'|'assistant', 'content': '...'}.
        """
        active_provider_name = provider_name or self.provider_name
        active_api_key = api_key or self.api_key
        active_model = model or self.model

        provider = AgentClient.get_provider(
            provider_name=active_provider_name,
            api_key=active_api_key,
        )

        response = provider.chat(
            messages=messages,
            system_prompt=self.system_prompt,
            image_bytes=image_bytes,
            model=active_model,
        )

        # Retrieve rich verified product records for any recommended product IDs
        rich_products: List[Dict[str, Any]] = []
        seen_ids = set()

        for pid in response.recommended_product_ids:
            if pid and pid not in seen_ids:
                prod = ProductSearchService.get_product_by_id(pid)
                if prod:
                    rich_products.append(prod)
                    seen_ids.add(pid)

        return AgentResponse(
            text=response.text,
            recommended_products=rich_products,
            tool_records=response.tool_records,
            order_created=response.order_created,
            provider_used=response.provider_used,
            model_used=response.model_used,
        )
