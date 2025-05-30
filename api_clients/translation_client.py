from typing import Any, Dict, List, Optional

from config import HTTP_TIMEOUT
from config import TRANSLATION_API_CONFIG
import httpx

from .exceptions import APIError


class TranslationAPIClient:

  def __init__(self):
    self.base_url = TRANSLATION_API_CONFIG["base_url"]
    self.api_key = TRANSLATION_API_CONFIG["api_key"]

  async def translate(self,
                      text_list: List[str],
                      source_lang: str,
                      target_lang: str,
                      endpoint_url: Optional[str] = None) -> Dict[str, Any]:
    """Call the translation API endpoint."""
    # Use provided endpoint URL if available, otherwise construct from base_url
    url = endpoint_url if endpoint_url else f"{self.base_url}/pre/translate"

    payload = {
        "text": text_list,
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": self.api_key
    }

    try:
      async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
      raise APIError(f"Translation API error: {str(e)}")
    except Exception as e:
      raise APIError(f"Unexpected error during translation: {str(e)}")
