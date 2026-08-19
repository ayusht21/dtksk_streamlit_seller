"""
Configuration module for Datta Krushi Seva Kendra AI Assistant.
Supports both OpenAI and Google Gemini LLM providers, SQLite database settings,
shop metadata, and robust multi-format Streamlit Secrets / .env resolution.
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
    """
    Robust configuration retriever that checks:
    1. os.environ (case-insensitive)
    2. Streamlit Secrets (exact, uppercase, lowercase, nested sections e.g. [openai] api_key)
    3. Provided default fallback
    """
    # 1. Direct environment variable lookup
    for env_k in [key, key.upper(), key.lower()]:
        val = os.getenv(env_k)
        if val and str(val).strip():
            return str(val).strip()

    # 2. Streamlit Secrets lookup
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets:
            # Top-level direct keys
            for test_k in [key, key.upper(), key.lower()]:
                if test_k in st.secrets:
                    val = str(st.secrets[test_k]).strip()
                    if val:
                        os.environ[key.upper()] = val
                        return val

            # Nested sections lookup (e.g. st.secrets["openai"]["api_key"] or st.secrets["gemini"]["api_key"])
            for section_name in ["openai", "gemini", "google", "general", "database", "OPENAI", "GEMINI", "GOOGLE"]:
                if section_name in st.secrets:
                    sec = st.secrets[section_name]
                    if hasattr(sec, "get") or isinstance(sec, dict):
                        short_k = key.lower().replace(f"{section_name.lower()}_", "")
                        for candidate in [key, key.upper(), key.lower(), short_k, short_k.upper(), short_k.lower(), "api_key", "key", "model", "url"]:
                            if candidate in sec:
                                val = str(sec[candidate]).strip()
                                if val:
                                    os.environ[key.upper()] = val
                                    return val
    except Exception:
        pass

    return default


def sync_secrets_to_env() -> None:
    """Syncs discovered Streamlit secrets into os.environ for external SDKs."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets:
            for k, v in st.secrets.items():
                if isinstance(v, (str, int, float, bool)):
                    str_v = str(v).strip()
                    if str_v:
                        os.environ.setdefault(k.upper(), str_v)
                        os.environ.setdefault(k, str_v)
                elif hasattr(v, "items"):
                    for sub_k, sub_v in v.items():
                        str_sub_v = str(sub_v).strip()
                        if str_sub_v:
                            combined = f"{k.upper()}_{sub_k.upper()}"
                            os.environ.setdefault(combined, str_sub_v)
    except Exception:
        pass


# Dynamic getters
def get_openai_api_key() -> str:
    return get_config_value("OPENAI_API_KEY", "")

def get_openai_model() -> str:
    return get_config_value("OPENAI_MODEL", "gpt-4o-mini")

def get_openai_vision_model() -> str:
    return get_config_value("OPENAI_VISION_MODEL", "gpt-4o")

def get_gemini_api_key() -> str:
    return get_config_value("GEMINI_API_KEY", "") or get_config_value("GOOGLE_API_KEY", "")

def get_gemini_model() -> str:
    return get_config_value("GEMINI_MODEL", "gemini-3.6-flash")

def get_default_provider() -> str:
    explicit = get_config_value("DEFAULT_PROVIDER", "")
    if explicit:
        return explicit.lower()
    if get_openai_api_key():
        return "openai"
    if get_gemini_api_key():
        return "gemini"
    return "openai"

def get_database_url() -> str:
    return get_config_value("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")


# Module-level legacy aliases (evaluated on demand or at import)
DATABASE_URL = get_database_url()
OPENAI_API_KEY = get_openai_api_key()
OPENAI_DEFAULT_MODEL = get_openai_model()
OPENAI_VISION_MODEL = get_openai_vision_model()
GEMINI_API_KEY = get_gemini_api_key()
GEMINI_DEFAULT_MODEL = get_gemini_model()
DEFAULT_PROVIDER = get_default_provider()
