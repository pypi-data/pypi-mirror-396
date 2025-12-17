from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Optional, Protocol
from uuid import uuid4

from ..llm import LlmClient
from ..trace import TraceWriter, maybe_redact
from ..util import as_type, get_as


@dataclass(frozen=True, slots=True)
class ChatResult:
    text: str
    metrics: dict[str, Any]


class ChatRunner(Protocol):
    def run(self, *, user_request: str, context: dict[str, Any], trace: Optional[TraceWriter] = None) -> ChatResult: ...


class HeuristicChat:
    def run(self, *, user_request: str, context: dict[str, Any], trace: Optional[TraceWriter] = None) -> ChatResult:
        err = get_as(context, "error", dict, default=None)
        if isinstance(err, dict):
            message = get_as(err, "message", str, default="Unknown error")
            code = get_as(err, "code", str, default="error")
            return ChatResult(text=f"Failed ({code}): {message}", metrics={})

        tool_results = get_as(context, "tool_results", list, default=[])
        if tool_results:
            last = as_type(tool_results[-1], dict, default={})
            if last:
                tool_name = get_as(last, "tool_name", str, default="")
                result = get_as(last, "result", dict, default={})
                if tool_name == "time_now":
                    tz = result.get("tz") or "UTC"
                    iso = result.get("iso") or ""
                    return ChatResult(text=f"The current time in {tz} is {iso}.", metrics={})
                if tool_name == "calc":
                    expr = result.get("expression") or ""
                    value = result.get("value")
                    return ChatResult(text=f"{expr} = {value}", metrics={})

        if re.search(r"\brephrase\b", user_request, re.IGNORECASE):
            # Best-effort rephrase without LLM.
            stripped = re.sub(r"(?i)rephrase\s*:?\s*", "", user_request).strip()
            text = stripped if stripped else user_request
            return ChatResult(text=f"Rephrased: {text}", metrics={})

        return ChatResult(text="Done.", metrics={})


class LlmChat:
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

    def run(self, *, user_request: str, context: dict[str, Any], trace: Optional[TraceWriter] = None) -> ChatResult:
        trace_writer = trace or self._trace
        system_prompt = (
            "You are the final response writer. Tools have already been executed elsewhere. "
            "Use the provided context (step/tool results) to answer the user. Be concise and factual."
        )
        user_prompt = json.dumps({"user_request": user_request, "context": context}, separators=(",", ":"))

        call_id = str(uuid4())
        if trace_writer:
            trace_writer.write(
                "llm_call",
                {
                    "call_id": call_id,
                    "role": "chat",
                    "model": self._model,
                    "system_prompt": maybe_redact(system_prompt, enabled=self._redact),
                    "user_prompt": maybe_redact(user_prompt, enabled=self._redact),
                },
            )

        response = self._client.responses(system_prompt=system_prompt, user_prompt=user_prompt, model_override=self._model)

        if trace_writer:
            trace_writer.write(
                "llm_result",
                {
                    "call_id": call_id,
                    "role": "chat",
                    "parsed": maybe_redact(response.get("parsed"), enabled=self._redact),
                    "output_text": maybe_redact(response.get("output_text"), enabled=self._redact),
                    "usage": response.get("usage"),
                    "latency_ms": response.get("latency_ms"),
                },
            )

        text = response.get("output_text")
        if not isinstance(text, str) or not text.strip():
            parsed = response.get("parsed")
            text = str(parsed) if parsed is not None else ""
        metrics = {"usage": response.get("usage"), "latency_ms": response.get("latency_ms")}
        return ChatResult(text=text.strip() or "Done.", metrics=metrics)
