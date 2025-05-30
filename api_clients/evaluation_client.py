import json
from typing import Any, Dict, List, Optional

from config import HTTP_TIMEOUT
from config import OPENAI_API_CONFIG
import httpx

from .exceptions import APIError


class OpenAIClient:

    def __init__(self):
        self.base_url = OPENAI_API_CONFIG["base_url"]
        self.api_key = OPENAI_API_CONFIG["api_key"]

    def _get_completion_url(self, model_name: str) -> str:
        """Construct the completion URL for the specified model."""
        return f"{self.base_url}/{model_name}/chat/completions"

    async def get_translation(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        model_name: str,
    ) -> Dict[str, Any]:
        """Get translation using OpenAI."""
        translation_prompt = f"""You are an expert translator with deep knowledge of both {source_language} and {target_language}.
Please translate the following text from {source_language} to {target_language}.

SOURCE TEXT ({source_language}):
{source_text}

Provide ONLY the translation in {target_language}, with no additional comments or explanations."""

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert bilingual translator. Translate the text accurately while preserving meaning, tone, and cultural nuances. Respond only with the translation.",
                },
                {"role": "user", "content": translation_prompt},
            ]
        }

        headers = {"Content-Type": "application/json", "api-key": self.api_key}

        try:
            url = self._get_completion_url(model_name)
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                response_data = response.json()
                if "choices" not in response_data or not response_data["choices"]:
                    raise APIError("Invalid response format from OpenAI API")
                return {
                    "text": response_data["choices"][0]["message"]["content"].strip()
                }
        except httpx.HTTPError as e:
            raise APIError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise APIError(f"Unexpected error during translation: {str(e)}")

    async def evaluate_translation(
        self,
        source_text: str,
        translated_text: str,
        source_language: str,
        target_language: str,
        model_name: str,
        reference_translation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate translation quality using OpenAI."""
        evaluation_prompt = self._create_evaluation_prompt(
            source_text,
            translated_text,
            source_language,
            target_language,
            reference_translation,
        )

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert bilingual evaluator tasked with judging the quality of translations. Given a source text, a reference translation, and a candidate translation, your role is to assess how well the candidate translation matches the reference while maintaining accuracy to the source. Your evaluation must be precise, unbiased, and clearly explain your reasoning.",
                },
                {"role": "user", "content": evaluation_prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        headers = {"Content-Type": "application/json", "api-key": self.api_key}

        try:
            url = self._get_completion_url(model_name)
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return self._process_evaluation_response(response.json())
        except httpx.HTTPError as e:
            raise APIError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise APIError(f"Unexpected error during evaluation: {str(e)}")

    def _create_evaluation_prompt(
        self,
        source_text: str,
        translated_text: str,
        source_language: str,
        target_language: str,
        reference_translation: Optional[str] = None,
    ) -> str:
        """Create the evaluation prompt for the LLM."""
        return f"""You are an expert translation evaluator with deep knowledge of both {source_language} and {target_language}. 
Please evaluate the following translation with careful attention to detail.

SOURCE TEXT ({source_language}):
{source_text}

REFERENCE TRANSLATION ({target_language}):
{reference_translation or "Not provided"}

CANDIDATE TRANSLATION ({target_language}):
{translated_text}

Evaluate the candidate translation based on these specific criteria:

1. ACCURACY (Semantic Equivalence)
- How well does it match the reference translation?
- Are all key concepts and information transferred correctly?
- Are there any mistranslations or semantic errors compared to both source and reference?

2. FLUENCY (Linguistic Quality)
- Is the grammar completely correct?
- Does it read naturally in the target language?
- Is the word choice and phrasing idiomatic?

3. FAITHFULNESS (Style & Tone)
- Does it maintain the same style as the reference translation?
- Are cultural nuances preserved similarly to the reference?
- Is the tone consistent with both source and reference?

4. TECHNICAL QUALITY
- Completeness: Are there any omissions or additions compared to the reference?
- Consistency: Is terminology used consistently with the reference?
- Formatting: Are proper nouns, numbers, and special elements handled correctly?

Based on your evaluation, classify the translation into ONE of these categories:
- excellent: Near perfect match with reference translation
- very good: High similarity with only minor differences
- good: Acceptable similarity with some noticeable differences
- bad: Significant differences from reference translation
- very bad: Major deviations making it unsuitable

IMPORTANT: Respond ONLY with a JSON object in this exact format:
{{
    "category": "<category>",
    "reason": "<concise explanation focusing on how well the candidate translation matches the reference while maintaining accuracy to the source>"
}}

Your reason should be clear, specific, and reference actual content from both translations."""

    def _process_evaluation_response(
        self, response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and clean the evaluation response."""
        if "choices" not in response_data or not response_data["choices"]:
            raise APIError("Invalid response format from OpenAI API")

        content = response_data["choices"][0]["message"]["content"].strip()

        # Clean up markdown if present
        if content.startswith("```") and content.endswith("```"):
            # Remove the opening ```json and closing ``` tags
            content = content.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise APIError(f"Failed to parse LLM response as JSON: {str(e)}")
