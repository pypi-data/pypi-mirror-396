from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Optional, Protocol
from uuid import uuid4

from ..llm import LlmClient
from ..trace import TraceWriter, maybe_redact


class ToolArgsGenerator(Protocol):
    def generate(
        self,
        *,
        tool_name: str,
        tool_schema: dict[str, Any],
        context: dict[str, Any],
        intent: str,
        targets: list[str],
        tool_description: Optional[str] = None,
        validation_error: Optional[dict[str, Any]] = None,
        trace: Optional[TraceWriter] = None,
    ) -> dict[str, Any]: ...


@dataclass(frozen=True, slots=True)
class HeuristicToolArgsGenerator:
    def generate(
        self,
        *,
        tool_name: str,
        tool_schema: dict[str, Any],
        context: dict[str, Any],
        intent: str,
        targets: list[str],
        tool_description: Optional[str] = None,
        validation_error: Optional[dict[str, Any]] = None,
        trace: Optional[TraceWriter] = None,
    ) -> dict[str, Any]:
        if tool_name == "time_now":
            tz = "UTC"
            if targets and isinstance(targets[0], str):
                tz = targets[0]
            return {"tz": tz}

        if tool_name == "calc":
            expr = _extract_expression(intent) or _extract_expression(str(context.get("user_request") or ""))
            return {"expression": expr} if expr else {}

        if tool_name == "echo":
            return {"text": str(intent)}

        return {}


class LlmToolArgsGenerator:
    def __init__(
        self,
        client: LlmClient,
        *,
        model: Optional[str] = None,
        trace: Optional[TraceWriter] = None,
        redact_prompts: bool = False,
    ):
        self._client = client
        self._model = model
        self._trace = trace
        self._redact = redact_prompts

    def generate(
        self,
        *,
        tool_name: str,
        tool_schema: dict[str, Any],
        context: dict[str, Any],
        intent: str,
        targets: list[str],
        tool_description: Optional[str] = None,
        validation_error: Optional[dict[str, Any]] = None,
        trace: Optional[TraceWriter] = None,
    ) -> dict[str, Any]:
        trace_writer = trace or self._trace
        system_prompt = (
            "You are a tool parameter generator. Return ONLY a JSON object that matches the provided tool schema. "
            "No prose. Follow the tool schema strictly."
        )
        user_payload = {
            "tool": tool_name,
            "intent": intent,
            "targets": targets,
            "description": tool_description,
            "context": context,
            "validation_error": validation_error,
        }
        user_prompt = json.dumps(user_payload, separators=(",", ":"))
        output_schema = {"format": {"type": "json_schema", "name": f"{tool_name}_args", "schema": tool_schema, "strict": True}}

        call_id = str(uuid4())
        if trace_writer:
            trace_writer.write(
                "llm_call",
                {
                    "call_id": call_id,
                    "role": "tool_args",
                    "tool_name": tool_name,
                    "model": self._model,
                    "system_prompt": maybe_redact(system_prompt, enabled=self._redact),
                    "user_prompt": maybe_redact(user_prompt, enabled=self._redact),
                    "output_schema": output_schema,
                },
            )

        response = self._client.responses(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=output_schema,
            model_override=self._model,
        )

        if trace_writer:
            trace_writer.write(
                "llm_result",
                {
                    "call_id": call_id,
                    "role": "tool_args",
                    "tool_name": tool_name,
                    "parsed": maybe_redact(response.get("parsed"), enabled=self._redact),
                    "output_text": maybe_redact(response.get("output_text"), enabled=self._redact),
                    "usage": response.get("usage"),
                    "latency_ms": response.get("latency_ms"),
                },
            )

        parsed = response.get("parsed")
        if isinstance(parsed, dict):
            return parsed

        text = response.get("output_text") or "{}"
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Tool args output must be an object")
        return data


def _extract_expression(text: str) -> str:
    match = re.search(r"\(([^)]+)\)", text)
    if match:
        return match.group(1).strip()
    match = re.search(r"(\d[\d\s+*/%().-]*)", text)
    if match:
        return match.group(1).strip()
    return ""
