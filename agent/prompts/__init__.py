"""Prompts and domain knowledge package."""
from .system_prompt import get_system_prompt
from .agricultural_knowledge import AGRICULTURAL_DIAGNOSTIC_GUIDE

__all__ = ["get_system_prompt", "AGRICULTURAL_DIAGNOSTIC_GUIDE"]
