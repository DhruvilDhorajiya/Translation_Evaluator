from typing import Any, Dict, List, Optional

from api_clients import APIError
from api_clients import OpenAIClient
from api_clients import TranslationAPIClient
from utils.similarity import compute_cosine_similarity


class TranslationService:

  def __init__(self):
    self.translation_client = TranslationAPIClient()
    self.evaluation_client = OpenAIClient()

  async def translate_text(
      self,
      text: str,
      source_language: str,
      target_language: str,
      evaluate: bool = False,
      model_name: Optional[str] = None,
      endpoint_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Translate text and optionally evaluate the translation.
    Args:
        text: Text to translate
        source_language: Source language code
        target_language: Target language code
        evaluate: Whether to evaluate the translation
        model_name: Model to use for evaluation (required if evaluate is True)
        endpoint_url: Optional custom endpoint URL for translation
    Returns:
        Dictionary containing translation and evaluation results.
    """
    try:
      # Split text into lines and clean
      text_lines = [line.strip() for line in text.split('\n') if line.strip()]

      # Get reference translation from user-provided endpoint
      translation_result = await self.translation_client.translate(
          text_list=text_lines,
          source_lang=source_language,
          target_lang=target_language,
          endpoint_url=endpoint_url)

      # Extract reference translation
      reference_translation = self._extract_translated_text(translation_result)

      result = {
          "success": True,
          "reference_translation": reference_translation,
          "raw_response": translation_result
      }

      # Get OpenAI translation and evaluate it against reference if evaluation is requested
      if evaluate and model_name:
        # Get OpenAI translation
        openai_result = await self.evaluation_client.get_translation(
            text, source_language, target_language, model_name)
        result["openai_translation"] = openai_result["text"]

        # Compute cosine similarity between translations
        similarity = compute_cosine_similarity(reference_translation,
                                               result["openai_translation"])
        result["similarity_score"] = similarity

        # Evaluate OpenAI translation against reference translation
        evaluation = await self.evaluation_client.evaluate_translation(
            text,
            result["openai_translation"],
            source_language,
            target_language,
            model_name,
            reference_translation=reference_translation)
        result["evaluation"] = evaluation

      return result

    except APIError as e:
      return {"success": False, "error": str(e)}
    except Exception as e:
      return {"success": False, "error": f"Unexpected error: {str(e)}"}

  def _extract_translated_text(self, response: Dict[str, Any]) -> str:
    """Extract translated text from API response."""
    if "text" in response:
      return response["text"]
    elif "translations" in response:
      translations = response["translations"]
      translated_parts = []
      for translation_obj in translations:
        if isinstance(translation_obj, dict) and "text" in translation_obj:
          translated_parts.append(translation_obj["text"])
        else:
          translated_parts.append(str(translation_obj))
      return " ".join(translated_parts)
    else:
      raise APIError("Unexpected translation response format")
