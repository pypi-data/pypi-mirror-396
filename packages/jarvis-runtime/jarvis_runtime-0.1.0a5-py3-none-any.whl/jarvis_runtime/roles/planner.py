from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Optional, Protocol
from uuid import uuid4

from ..llm import LlmClient
from ..trace import TraceWriter, maybe_redact


@dataclass(frozen=True, slots=True)
class PlannerResult:
    steps: list[dict[str, Any]]
    step_result: str
    metrics: dict[str, Any]


class PlannerRunner(Protocol):
    def plan(
        self,
        *,
        goal: str,
        context: dict[str, Any],
        tools: list[dict[str, Any]],
        steps_so_far: list[dict[str, Any]],
        config: Optional[dict[str, Any]] = None,
        trace: Optional[TraceWriter] = None,
    ) -> PlannerResult: ...


class HeuristicPlanner:
    """Deterministic planner used for demos/tests (no network)."""

    def plan(
        self,
        *,
        goal: str,
        context: dict[str, Any],
        tools: list[dict[str, Any]],
        steps_so_far: list[dict[str, Any]],
        config: Optional[dict[str, Any]] = None,
        trace: Optional[TraceWriter] = None,
    ) -> PlannerResult:
        text = (goal or "").strip()
        lower = text.lower()

        if "time" in lower and "utc" in lower:
            return PlannerResult(
                steps=[{"type": "tool", "tool_name": "time_now", "intent": text, "targets": ["UTC"]}],
                step_result="Call time_now for UTC.",
                metrics={},
            )

        if re.search(r"\b\d+\s*[-+*/%()]\s*\d+", text) or "what is" in lower:
            return PlannerResult(
                steps=[{"type": "tool", "tool_name": "calc", "intent": text, "targets": []}],
                step_result="Call calc for the requested expression.",
                metrics={},
            )

        return PlannerResult(steps=[], step_result="No tools needed; respond directly.", metrics={})


class LlmPlanner:
    """LLM-backed planner (M2) using JSON Schema structured outputs."""

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
        self._response_schema = _planner_response_schema()

    def plan(
        self,
        *,
        goal: str,
        context: dict[str, Any],
        tools: list[dict[str, Any]],
        steps_so_far: list[dict[str, Any]],
        config: Optional[dict[str, Any]] = None,
        trace: Optional[TraceWriter] = None,
    ) -> PlannerResult:
        trace_writer = trace or self._trace
        tool_summaries = {t.get("name"): t.get("description") for t in tools if isinstance(t, dict)}
        system_prompt = (
            "You are a workflow planner. Return a list of tool or plan steps to add to the existing one. "
            "The new steps will be appended after the current one, so the first entry "
            "you return should NEVER be another plan step. Avoid duplicated steps, and if no new steps are needed just return empty. " \
            "Other than the steps, also return a very short, 1-2 sentence summary on what planning was done in the step_result field. "
            "Use tool summaries (name+description) to decide tool usage. "
            "Plan steps provides self-mutating capability to flows to think and/or plan future steps, just like this current step."
        )
        user_payload = json.dumps(
            {"goal": goal, "context": context, "tools": tool_summaries, "steps": steps_so_far, "config": config or {}},
            separators=(",", ":"),
        )
        output_schema = {
            "format": {"type": "json_schema", "name": "planner_steps", "schema": self._response_schema, "strict": True}
        }

        call_id = str(uuid4())
        if trace_writer:
            trace_writer.write(
                "llm_call",
                {
                    "call_id": call_id,
                    "role": "planner",
                    "model": self._model,
                    "system_prompt": maybe_redact(system_prompt, enabled=self._redact),
                    "user_prompt": maybe_redact(user_payload, enabled=self._redact),
                    "output_schema": output_schema,
                },
            )

        response = self._client.responses(
            system_prompt=system_prompt,
            user_prompt=user_payload,
            output_schema=output_schema,
            model_override=self._model,
        )

        if trace_writer:
            trace_writer.write(
                "llm_result",
                {
                    "call_id": call_id,
                    "role": "planner",
                    "parsed": maybe_redact(response.get("parsed"), enabled=self._redact),
                    "output_text": maybe_redact(response.get("output_text"), enabled=self._redact),
                    "usage": response.get("usage"),
                    "latency_ms": response.get("latency_ms"),
                },
            )

        parsed = response.get("parsed")
        if not isinstance(parsed, dict):
            text = response.get("output_text") or "{}"
            parsed = json.loads(text)

        steps = parsed.get("steps")
        step_result = parsed.get("step_result") or ""
        if not isinstance(steps, list):
            raise ValueError("Planner output must contain 'steps' array")

        normalized_steps = _validate_planned_steps(steps)
        metrics = {"usage": response.get("usage"), "latency_ms": response.get("latency_ms")}
        return PlannerResult(steps=normalized_steps, step_result=str(step_result), metrics=metrics)


def _planner_response_schema() -> dict[str, Any]:
    tool_step_schema = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["tool"]},
            "tool_name": {"type": "string"},
            "intent": {"type": "string"},
            "targets": {"type": ["array", "null"], "items": {"type": "string"}},
        },
        "required": ["type", "tool_name", "intent", "targets"],
        "additionalProperties": False,
    }

    plan_step_schema = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["plan"]},
            "plan_prompt": {"type": "string"},
            "planner_config": {
                "type": ["array", "null"],
                "items": {"type": "string"}
            },
        },
        "required": ["type", "plan_prompt", "planner_config"],
        "additionalProperties": False,
    }

    return {
        "type": "object",
        "properties": {
            "steps": {"type": "array", "items": {"anyOf": [tool_step_schema, plan_step_schema]}},
            "step_result": {"type": ["string", "null"]},
        },
        "required": ["steps", "step_result"],
        "additionalProperties": False,
    }


def _validate_planned_steps(raw_steps: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(raw_steps):
        if not isinstance(item, dict):
            raise ValueError(f"Planned step {idx} must be an object")
        step_type = item.get("type")
        if step_type == "tool":
            tool_name = item.get("tool_name")
            intent = item.get("intent")
            targets = item.get("targets") or []
            if not isinstance(tool_name, str) or not tool_name.strip():
                raise ValueError("tool_name must be a non-empty string")
            if not isinstance(intent, str) or not intent.strip():
                raise ValueError("intent must be a non-empty string")
            if not isinstance(targets, list) or not all(isinstance(t, str) for t in targets):
                raise ValueError("targets must be a list of strings")
            normalized.append({"type": "tool", "tool_name": tool_name, "intent": intent, "targets": targets})
            continue

        if step_type == "plan":
            plan_prompt = item.get("plan_prompt")
            planner_config = item.get("planner_config")
            if not isinstance(plan_prompt, str) or not plan_prompt.strip():
                raise ValueError("plan_prompt must be a non-empty string")
            if planner_config is not None and (
                not isinstance(planner_config, list) or not all(isinstance(entry, str) for entry in planner_config)
            ):
                raise ValueError("planner_config must be a list of strings or null")
            normalized.append({"type": "plan", "plan_prompt": plan_prompt, "planner_config": planner_config})
            continue

        raise ValueError(f"Unsupported planned step type: {step_type}")

    return normalized
