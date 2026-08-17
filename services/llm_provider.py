"""
Unified LLM Provider abstraction supporting OpenAI, Google Gemini, and an Offline/Mock fallback.
Handles multi-turn dialogue, multimodal image diagnosis, and the tool-calling execution loop.
"""

import os
import json
import base64
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import io
from PIL import Image

from agent.agent_config import AGENT_CONFIG
from agent.tools import OPENAI_TOOLS_SCHEMA, execute_tool

logger = logging.getLogger(__name__)


@dataclass
class ToolExecutionRecord:
    tool_name: str
    arguments: Dict[str, Any]
    result: Any


@dataclass
class ProviderResponse:
    text: str
    tool_records: List[ToolExecutionRecord] = field(default_factory=list)
    recommended_product_ids: List[str] = field(default_factory=list)
    order_created: Optional[Dict[str, Any]] = None
    provider_used: str = "openai"
    model_used: str = ""


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        image_bytes: Optional[bytes] = None,
        model: Optional[str] = None,
    ) -> ProviderResponse:
        pass


import config

class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-4o-mini) with function calling and Vision support."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.get_openai_api_key() or os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError("OpenAI API Key is required for OpenAIProvider.")
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)

    def chat(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        image_bytes: Optional[bytes] = None,
        model: Optional[str] = None,
    ) -> ProviderResponse:
        target_model = model or AGENT_CONFIG["openai"]["default_model"]
        temperature = AGENT_CONFIG["openai"]["temperature"]
        max_tool_iterations = AGENT_CONFIG["max_tool_iterations"]

        # Build message history
        conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]

        for idx, msg in enumerate(messages):
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # If it's the latest user message and image_bytes are present, construct multimodal payload
            if role == "user" and idx == len(messages) - 1 and image_bytes:
                base64_image = base64.b64encode(image_bytes).decode("utf-8")
                content_payload = [
                    {"type": "text", "text": content or "Please analyze this crop image for pests, diseases, or symptoms."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ]
                conversation_history.append({"role": "user", "content": content_payload})
            else:
                conversation_history.append({"role": role, "content": content})

        tool_records: List[ToolExecutionRecord] = []
        recommended_product_ids: List[str] = []
        order_created: Optional[Dict[str, Any]] = None

        # Execute conversation and tool loop
        for _ in range(max_tool_iterations):
            response = self.client.chat.completions.create(
                model=target_model,
                messages=conversation_history,
                tools=OPENAI_TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=temperature,
            )

            choice = response.choices[0]
            message = choice.message

            # Check if model made tool calls
            if message.tool_calls:
                # Add assistant message with tool calls to history
                conversation_history.append(message)

                # Process each tool call
                for tool_call in message.tool_calls:
                    fn_name = tool_call.function.name
                    try:
                        fn_args = json.loads(tool_call.function.arguments)
                    except Exception:
                        fn_args = {}

                    # Execute the tool function
                    result = execute_tool(fn_name, fn_args)
                    tool_records.append(
                        ToolExecutionRecord(
                            tool_name=fn_name,
                            arguments=fn_args,
                            result=result,
                        )
                    )

                    # Extract recommended product IDs
                    if fn_name == "search_products" and isinstance(result, dict) and "products" in result:
                        for p in result["products"]:
                            pid = p.get("product_id")
                            if pid and pid not in recommended_product_ids:
                                recommended_product_ids.append(pid)
                    elif fn_name in ("get_product_details", "get_current_price", "check_stock"):
                        pid = fn_args.get("product_id")
                        if pid and pid not in recommended_product_ids:
                            recommended_product_ids.append(pid)
                    elif fn_name == "create_order" and isinstance(result, dict) and result.get("success"):
                        order_created = result
                        pid = fn_args.get("product_id")
                        if pid and pid not in recommended_product_ids:
                            recommended_product_ids.append(pid)

                    # Feed tool response back into conversation
                    conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": fn_name,
                        "content": json.dumps(result, ensure_ascii=False),
                    })
            else:
                # Model produced final text
                final_text = message.content or ""
                return ProviderResponse(
                    text=final_text,
                    tool_records=tool_records,
                    recommended_product_ids=recommended_product_ids,
                    order_created=order_created,
                    provider_used="openai",
                    model_used=target_model,
                )

        # Fallback if loop exceeded
        return ProviderResponse(
            text=message.content or "I have retrieved the relevant product details for your crop. Please let me know if you would like to proceed with an order.",
            tool_records=tool_records,
            recommended_product_ids=recommended_product_ids,
            order_created=order_created,
            provider_used="openai",
            model_used=target_model,
        )


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (gemini-3.6-flash) using Google GenAI SDK."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.get_gemini_api_key() or os.getenv("GEMINI_API_KEY", "")
        if not self.api_key:
            raise ValueError("Gemini API Key is required for GeminiProvider.")
        from google import genai
        self.client = genai.Client(api_key=self.api_key)

    def chat(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        image_bytes: Optional[bytes] = None,
        model: Optional[str] = None,
    ) -> ProviderResponse:
        from google.genai import types
        target_model = model or AGENT_CONFIG["gemini"]["default_model"]

        # Define tool functions for Gemini
        from agent.tools import search_products, get_product_details, check_stock, get_current_price, create_order
        gemini_tools = [search_products, get_product_details, check_stock, get_current_price, create_order]

        # Construct contents
        contents = []
        for idx, msg in enumerate(messages):
            role = "user" if msg.get("role") == "user" else "model"
            text_content = msg.get("content", "")

            parts = []
            if role == "user" and idx == len(messages) - 1 and image_bytes:
                pil_image = Image.open(io.BytesIO(image_bytes))
                parts.append(pil_image)
                parts.append(text_content or "Analyze this crop image.")
            else:
                parts.append(text_content)

            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=p) if isinstance(p, str) else p for p in parts]))

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=gemini_tools,
            temperature=AGENT_CONFIG["gemini"]["temperature"],
        )

        response = self.client.models.generate_content(
            model=target_model,
            contents=contents,
            config=config,
        )

        tool_records: List[ToolExecutionRecord] = []
        recommended_product_ids: List[str] = []
        order_created: Optional[Dict[str, Any]] = None

        # Check function calls
        if response.function_calls:
            for call in response.function_calls:
                fn_name = call.name
                fn_args = dict(call.args) if hasattr(call, "args") else {}
                result = execute_tool(fn_name, fn_args)
                tool_records.append(ToolExecutionRecord(tool_name=fn_name, arguments=fn_args, result=result))

                if fn_name == "search_products" and isinstance(result, dict) and "products" in result:
                    for p in result["products"]:
                        pid = p.get("product_id")
                        if pid and pid not in recommended_product_ids:
                            recommended_product_ids.append(pid)
                elif fn_name in ("get_product_details", "get_current_price", "check_stock"):
                    pid = fn_args.get("product_id")
                    if pid and pid not in recommended_product_ids:
                        recommended_product_ids.append(pid)
                elif fn_name == "create_order" and isinstance(result, dict) and result.get("success"):
                    order_created = result

        final_text = response.text or ""
        return ProviderResponse(
            text=final_text,
            tool_records=tool_records,
            recommended_product_ids=recommended_product_ids,
            order_created=order_created,
            provider_used="gemini",
            model_used=target_model,
        )


class MockOfflineProvider(BaseLLMProvider):
    """
    Offline/Demo fallback provider that runs rule-based diagnostic heuristics
    and queries the database directly without requiring an external API key.
    """

    def chat(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        image_bytes: Optional[bytes] = None,
        model: Optional[str] = None,
    ) -> ProviderResponse:
        last_message = messages[-1].get("content", "").lower() if messages else ""
        tool_records: List[ToolExecutionRecord] = []
        recommended_product_ids: List[str] = []

        # Diagnostic logic
        if any(w in last_message for w in ["कापूस", "cotton", "बोंडअळी", "bollworm"]):
            res = execute_tool("search_products", {"crop": "Cotton", "problem": "Bollworm"})
            tool_records.append(ToolExecutionRecord("search_products", {"crop": "Cotton", "problem": "Bollworm"}, res))
            recommended_product_ids = [p["product_id"] for p in res.get("products", [])]
            text = (
                "रामराम शेतकरी बंधू! तुमच्या कापसाच्या पिकावर बोंडअळीचा (Bollworm) प्रादुर्भाव आढळल्यास "
                "आमच्या दत्त कृषी सेवा केंद्रात **Coragen (कोराजन)** किंवा **Ampligo (अँप्लीगो)** उपलब्ध आहे.\n\n"
                "• **Coragen Insecticide (६० मि.ली.)** — ₹780 (स्टॉकमध्ये उपलब्ध)\n"
                "  फायदा: बोंडअळीच्या सर्व अवस्थांवर प्रदीर्घ नियंत्रण.\n\n"
                "आपल्याला हे हवे असल्यास आपण लगेच ऑर्डर नोंदवू शकता!"
            )
        elif any(w in last_message for w in ["सोयाबीन", "soybean", "पिवळे", "yellow"]):
            res = execute_tool("search_products", {"crop": "Soybean", "problem": "Yellowing"})
            tool_records.append(ToolExecutionRecord("search_products", {"crop": "Soybean", "problem": "Yellowing"}, res))
            recommended_product_ids = [p["product_id"] for p in res.get("products", [])]
            text = (
                "सोयाबीनची पाने पिवळी पडत असल्यास झिंक किंवा सूक्ष्म अन्नद्रव्यांची कमतरता असू शकते.\n"
                "आमच्याकडे **Chelated Zinc EDTA (२५० ग्रॅम)** आणि **१९:१९:१९ विद्राव्य खत** उपलब्ध आहे."
            )
        elif any(w in last_message for w in ["मिरची", "chilli", "चुरडा", "thrips"]):
            res = execute_tool("search_products", {"crop": "Chilli", "problem": "Thrips"})
            tool_records.append(ToolExecutionRecord("search_products", {"crop": "Chilli", "problem": "Thrips"}, res))
            recommended_product_ids = [p["product_id"] for p in res.get("products", [])]
            text = (
                "मिरचीवरील चुरडा-मुरडा (Thrips & Mites) नियंत्रणासाठी **Pegasus Insecticide (२५० ग्रॅम - ₹1150)** "
                "किंवा **Delegate (१०० मि.ली. - ₹1350)** अत्यंत प्रभावी ठरते."
            )
        elif image_bytes:
            res = execute_tool("search_products", {"category": "Insecticide"})
            tool_records.append(ToolExecutionRecord("search_products", {"category": "Insecticide"}, res))
            recommended_product_ids = [p["product_id"] for p in res.get("products", [])[:2]]
            text = (
                "📷 फोटोच्या प्राथमिक निरीक्षणावरून पिकावर कीड/रोगाचा प्रादुर्भाव दिसत आहे. "
                "अधिक अचूक सल्ल्यासाठी झाडाची नेमकी कोणती पाने बाधित आहेत ते सांगा."
            )
        else:
            text = (
                "रामराम शेतकरी बंधू! दत्त कृषी सेवा केंद्रात आपले स्वागत आहे. "
                "तुमच्या शेतातील पिकाचे नाव (उदा. कापूस, सोयाबीन, मिरची, टोमॅटो) आणि कोणती समस्या दिसते ते सांगा."
            )

        return ProviderResponse(
            text=text,
            tool_records=tool_records,
            recommended_product_ids=recommended_product_ids,
            provider_used="mock",
            model_used="demo-mode",
        )
