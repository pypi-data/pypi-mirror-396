from __future__ import annotations

from typing import Any, Mapping, Optional, Protocol


class LlmClient(Protocol):
    """Interface for OpenAI-compatible Responses calls (sync)."""

    def responses(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Optional[Mapping[str, Any]] = None,
        model_override: Optional[str] = None,
    ) -> dict[str, Any]:
        ...

