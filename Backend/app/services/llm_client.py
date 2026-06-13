from __future__ import annotations

from typing import Protocol


class LLMProviderError(RuntimeError):
    pass


class ExplanationProvider(Protocol):
    def generate_explanation(self, facts: dict) -> dict:
        ...
