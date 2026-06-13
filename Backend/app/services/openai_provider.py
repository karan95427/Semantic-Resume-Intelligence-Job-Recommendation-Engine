from __future__ import annotations

import json
import os
from typing import Any

import httpx

from .llm_client import LLMProviderError


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5.4-mini"
DEFAULT_TIMEOUT_SECONDS = 12.0


EXPLANATION_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "summary",
        "matched_skills",
        "missing_skills",
        "strengths",
        "weaknesses",
        "improvement_suggestions",
    ],
    "properties": {
        "summary": {"type": "string"},
        "matched_skills": {"type": "array", "items": {"type": "string"}},
        "missing_skills": {"type": "array", "items": {"type": "string"}},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "weaknesses": {"type": "array", "items": {"type": "string"}},
        "improvement_suggestions": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
}


SYSTEM_PROMPT = """You explain finalized resume-to-job recommendations.
Rules:
- Rankings and scores are already final.
- Do not change, reinterpret, or challenge scores.
- Use only the provided structured facts.
- matched_skills must only contain supplied matched_skills.
- missing_skills must only contain supplied missing_skills.
- Do not invent skills, jobs, companies, credentials, or experience.
- Return only JSON matching the schema."""


class OpenAIExplanationProvider:
    provider_name = "openai"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", DEFAULT_MODEL)
        self.timeout_seconds = timeout_seconds or float(
            os.getenv("LLM_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
        )

    def generate_explanation(self, facts: dict) -> dict:
        if not self.api_key:
            raise LLMProviderError("OPENAI_API_KEY is not configured.")

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": SYSTEM_PROMPT,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": json.dumps(facts, ensure_ascii=True),
                        }
                    ],
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "recommendation_explanation",
                    "strict": True,
                    "schema": EXPLANATION_OUTPUT_SCHEMA,
                }
            },
        }

        try:
            response = httpx.post(
                OPENAI_RESPONSES_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMProviderError("OpenAI explanation request failed.") from exc

        try:
            output_text = _extract_output_text(response.json())
            return json.loads(output_text)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise LLMProviderError("OpenAI explanation response was malformed.") from exc


def _extract_output_text(payload: dict[str, Any]) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text:
        return output_text

    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str) and text:
                return text

    raise KeyError("No output text found in response.")
