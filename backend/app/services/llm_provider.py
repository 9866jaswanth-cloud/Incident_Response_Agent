"""LLM Provider abstraction supporting Gemini API (via google-genai) with fallback."""

import json
import logging
from typing import Any, Dict, Optional
from app.core.config import settings

logger = logging.getLogger("llm_provider")


class LLMProvider:
    """Provides async text generation for incident analysis."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.LLM_MODEL or "gemini-2.5-flash"
        self._client = None

    def get_client(self):
        if not self._client and self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI Client: {e}")
        return self._client

    async def generate_json(self, prompt: str, system_instruction: str = "") -> Optional[Dict[str, Any]]:
        """
        Attempts to generate structured JSON using Gemini API.
        Returns parsed dict or None if API key not available / error occurs.
        """
        client = self.get_client()
        if not client:
            return None

        try:
            full_prompt = f"{system_instruction}\n\n{prompt}\n\nRespond ONLY with a valid JSON object matching the requested schema."
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=full_prompt,
            )
            text = response.text.strip()
            # Clean markdown codeblocks if wrapped
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
        except Exception as e:
            logger.warning(f"Gemini API generation failed: {e}. Falling back to rule-based diagnostic engine.")
            return None


llm_provider = LLMProvider()
