"""
Agent Configuration settings for models, temperature, and provider parameters.
"""

from typing import Dict, Any

AGENT_CONFIG: Dict[str, Any] = {
    "openai": {
        "default_model": "gpt-4o",
        "fallback_model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 1500,
    },
    "gemini": {
        "default_model": "gemini-3.6-flash",
        "fallback_model": "gemini-2.5-flash",
        "temperature": 0.3,
        "max_output_tokens": 1500,
    },
    "max_tool_iterations": 5,
}
