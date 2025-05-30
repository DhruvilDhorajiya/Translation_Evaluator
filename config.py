from typing import List
import streamlit as st

# Available languages for translation
AVAILABLE_LANGUAGES: List[str] = [
    "EN-US", "JA-JP", "KO-KR", "ZH-CN", "ZH-TW", "ES-ES", "FR-FR", "DE-DE",
    "IT-IT", "PT-PT", "RU-RU"
]

# Language display names mapping
LANGUAGE_DISPLAY_NAMES = {
    "EN-US": "English (US)",
    "JA-JP": "Japanese",
    "KO-KR": "Korean",
    "ZH-CN": "Chinese (Simplified)",
    "ZH-TW": "Chinese (Traditional)",
    "ES-ES": "Spanish",
    "FR-FR": "French",
    "DE-DE": "German",
    "IT-IT": "Italian",
    "PT-PT": "Portuguese",
    "RU-RU": "Russian"
}

# Model configurations
MODEL_CONFIG = {
    "gpt-35-turbo": "GPT-3.5 Turbo",
    "gpt-4": "GPT-4",
    "gpt-4o": "GPT-4o",
    "o3-mini": "O3 Mini",
    "gemini-15-pro": "Gemini 1.5 Pro",
    "gemini-15-flash": "Gemini 1.5 Flash",
    "deepseek-chat": "DeepSeek Chat"
}

# Technical model names for API endpoints
AVAILABLE_MODELS = list(MODEL_CONFIG.keys())

# Display names for UI
MODEL_DISPLAY_NAMES = list(MODEL_CONFIG.values())

# Translation API Configuration
TRANSLATION_API_CONFIG = {
    "base_url": "https://fragma-api-dev.yanolja.com",
    # "api_key": st.secrets["API_KEY"],
    "api_key": "5OSQZiZ2ELTtzJMrWjvsEWoq3tNvIvBNJa4Q8qwqSiNFZbgU8e",
}

# OpenAI API Configuration
OPENAI_API_CONFIG = {
    "base_url": "https://fragma-api.dev.yanolja.in/openai/deployments",
    # "api_key": st.secrets["API_KEY"],
    "api_key": "5OSQZiZ2ELTtzJMrWjvsEWoq3tNvIvBNJa4Q8qwqSiNFZbgU8e",
}

# HTTP Client Configuration
HTTP_TIMEOUT = 60.0
