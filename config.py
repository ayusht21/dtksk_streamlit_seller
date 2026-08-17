"""
Configuration module for Datta Krushi Seva Kendra AI Assistant.
Supports both OpenAI and Google Gemini LLM providers, SQLite database settings,
and shop metadata.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database" / "krushi_kendra.db"
SAMPLE_CSV_PATH = BASE_DIR / "catalogue" / "sample_products.csv"

# Shop Metadata
SHOP_NAME = "Datta Krushi Seva Kendra"
SHOP_NAME_MR = "दत्त कृषी सेवा केंद्र"
SHOP_TAGLINE = "आपला विश्वासू कृषी सल्लागार आणि दर्जेदार कृषी निविष्ठा केंद्र"
SHOP_LOCATION = "Block 31, Orange Plaza, Katol"
SHOP_LOCATION_MR = "ब्लॉक ३१, ऑरेंज प्लाझा, काटोल"
SHOP_PHONE = "+91 99701 51397"
SHOP_WHATSAPP = "919970151397"

def get_config_value(key: str, default: str = "") -> str:
    """Retrieves configuration from environment variable (.env) or Streamlit Secrets."""
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


# Database Configuration
DATABASE_URL = get_config_value("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

# LLM Providers Configuration
OPENAI_API_KEY = get_config_value("OPENAI_API_KEY", "")
OPENAI_DEFAULT_MODEL = get_config_value("OPENAI_MODEL", "gpt-4o")

GEMINI_API_KEY = get_config_value("GEMINI_API_KEY", "")
GEMINI_DEFAULT_MODEL = get_config_value("GEMINI_MODEL", "gemini-3.6-flash")

# Default Provider: prefer OPENAI if key is present, else GEMINI, else mock
DEFAULT_PROVIDER = get_config_value("DEFAULT_PROVIDER", "openai" if OPENAI_API_KEY else "gemini")
