from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from uuid import uuid4

from jarvis_model import Error, FlowRun, FlowStep

from .roles import ChatRunner, PlannerRunner, ToolExecutor
from .tool_registry_client import ToolRegistryClient
from .trace import JsonlTraceWriter, TracePaths, TraceWriter, default_trace_paths
from .util import as_type, get_as


@dataclass(frozen=True, slots=True)
class RunResult:
    flow_id: str
    trace_id: str
    status: str
    final_text: str
    steps: list[FlowStep]
    trace: TracePaths


class FlowOrchestrator:
    def __init__(
        self,
        *,
        planner: PlannerRunner,
        tool_registry: ToolRegistryClient,
        tool_executor: ToolExecutor,
        chat: ChatRunner,
        trace_dir: str | Path = "./runs",
        redact_prompts: bool = False,
        max_steps: int = 20,
    ):
        self._planner = planner
        self._tool_registry = tool_registry
        self._tool_executor = tool_executor
        self._chat = chat
        self._trace_dir = Path(trace_dir)
        self._redact_prompts = redact_prompts
        self._max_steps = max_steps

    def run(self, *, user_request: str) -> RunResult:
        flow_id = str(uuid4())
        trace_id = str(uuid4())
        trace_paths = default_trace_paths(self._trace_dir, flow_id)
        trace_writer: TraceWriter = JsonlTraceWriter(trace_paths.trace_jsonl)

        try:
            return self._run_with_trace(
                user_request=user_request,
                flow_id=flow_id,
                trace_id=trace_id,
                trace_paths=trace_paths,
                trace=trace_writer,
            )
        finally:
            trace_writer.close()

    def _run_with_trace(
        self,
        *,
        user_request: str,
        flow_id: str,
        trace_id: str,
        trace_paths: TracePaths,
        trace: TraceWriter,
    ) -> RunResult:
        flow = FlowRun.new(flow_id=flow_id, input={"user_request": user_request})
        context: dict[str, Any] = {"user_request": user_request, "step_results": [], "tool_results": [], "meta": {"trace_id": trace_id}}
        steps: list[FlowStep] = []

        seed_plan = FlowStep.new(step_id=str(uuid4()), type="plan", payload={"plan_prompt": user_request, "planner_config": None})
        steps.append(seed_plan)

        trace.write(
            "flow_started",
            {
                "flow_id": flow_id,
                "trace_id": trace_id,
                "input": {"user_request": "<redacted>"} if self._redact_prompts else flow.input,
            },
        )
        trace.write("step_created", {"flow_id": flow_id, "step": _step_dict(seed_plan), "index": 0})

        flow_error: Error | None = None
        current_idx = 0
        while current_idx < len(steps):
            if len(steps) > self._max_steps:
                err = Error(code="flow.max_steps", message=f"Exceeded max_steps={self._max_steps}", retryable=False)
                flow_error = err
                break

            step = steps[current_idx]
            trace.write(
                "step_started",
                {"flow_id": flow_id, "step_id": step.step_id, "index": current_idx, "step_type": step.type},
            )

            try:
                if step.type == "plan":
                    step, new_steps = self._execute_plan_step(
                        step=step,
                        flow_id=flow_id,
                        trace_id=trace_id,
                        context=context,
                        all_steps=steps,
                        trace=trace,
                    )
                    steps[current_idx] = step
                    if new_steps:
                        insert_at = current_idx + 1
                        for offset, new_step in enumerate(new_steps):
                            trace.write(
                                "step_created",
                                {"flow_id": flow_id, "step": _step_dict(new_step), "index": insert_at + offset},
                            )
                        steps[insert_at:insert_at] = new_steps

                elif step.type == "tool":
                    step = self._execute_tool_step(
                        step=step, flow_id=flow_id, trace_id=trace_id, context=context, trace=trace
                    )
                    steps[current_idx] = step
                    if step.status == "failed":
                        flow_error = step.error or Error(code="tool.failed", message="Tool execution failed", retryable=False)
                        break

                elif step.type == "chat":
                    step, final_text = self._execute_chat_step(step=step, context=context, trace=trace)
                    steps[current_idx] = step
                    trace.write(
                        "flow_completed",
                        {"flow_id": flow_id, "trace_id": trace_id, "status": "completed", "final_text": final_text},
                    )
                    return RunResult(
                        flow_id=flow_id,
                        trace_id=trace_id,
                        status="completed",
                        final_text=final_text,
                        steps=steps,
                        trace=trace_paths,
                    )
                else:
                    raise ValueError(f"Unsupported step type: {step.type}")

            except Exception as exc:
                err = Error(code="flow.step_failed", message=str(exc), details={"step_id": step.step_id, "type": step.type})
                failed_step = replace(step, status="failed", error=err)
                steps[current_idx] = failed_step
                flow_error = err
                break

            trace.write("step_completed", {"flow_id": flow_id, "step_id": steps[current_idx].step_id, "status": steps[current_idx].status})
            current_idx += 1

        if flow_error:
            trace.write("flow_failed", {"flow_id": flow_id, "trace_id": trace_id, "error": flow_error.to_dict()})
            context["error"] = flow_error.to_dict()

        # If we ran out of steps, append and execute exactly one final chat step.
        final_step = FlowStep.new(
            step_id=str(uuid4()),
            type="chat",
            payload={"user_request": user_request, "error": flow_error.to_dict() if flow_error else None},
        )
        steps.append(final_step)
        trace.write("step_created", {"flow_id": flow_id, "step": _step_dict(final_step), "index": len(steps) - 1})

        step, final_text = self._execute_chat_step(step=final_step, context=context, trace=trace)
        steps[-1] = step
        status = "failed" if flow_error else "completed"
        trace.write("flow_completed", {"flow_id": flow_id, "trace_id": trace_id, "status": status, "final_text": final_text})
        return RunResult(flow_id=flow_id, trace_id=trace_id, status=status, final_text=final_text, steps=steps, trace=trace_paths)

    def _execute_plan_step(
        self,
        *,
        step: FlowStep,
        flow_id: str,
        trace_id: str,
        context: dict[str, Any],
        all_steps: list[FlowStep],
        trace: TraceWriter,
    ) -> tuple[FlowStep, list[FlowStep]]:
        payload = as_type(step.payload, dict, default={})
        plan_prompt = get_as(payload, "plan_prompt", str, default=None)
        if not isinstance(plan_prompt, str):
            raise ValueError("plan_prompt is required for plan steps")

        steps_so_far = [_step_summary(s, idx=i) for i, s in enumerate(all_steps)]
        tools = self._tool_registry.list_tools()
        result = self._planner.plan(goal=plan_prompt, context=context, tools=tools, steps_so_far=steps_so_far, trace=trace)

        context["step_results"].append({"type": "plan", "step_result": result.step_result})

        new_steps: list[FlowStep] = []
        for raw in result.steps:
            if raw.get("type") == "tool":
                new_steps.append(
                    FlowStep.new(
                        step_id=str(uuid4()),
                        type="tool",
                        payload={
                            "tool_name": raw["tool_name"],
                            "intent": raw["intent"],
                            "targets": raw.get("targets") or [],
                        },
                    )
                )
            elif raw.get("type") == "plan":
                new_steps.append(
                    FlowStep.new(step_id=str(uuid4()), type="plan", payload={"plan_prompt": raw["plan_prompt"], "planner_config": raw.get("planner_config")})
                )
            else:
                raise ValueError(f"Planner returned unsupported step type: {raw.get('type')}")

        completed = replace(
            step,
            status="completed",
            result={"step_result": result.step_result, "planned_steps": result.steps, "metrics": result.metrics},
        )
        return completed, new_steps

    def _execute_tool_step(
        self,
        *,
        step: FlowStep,
        flow_id: str,
        trace_id: str,
        context: dict[str, Any],
        trace: TraceWriter,
    ) -> FlowStep:
        payload = as_type(step.payload, dict, default={})
        tool_name = get_as(payload, "tool_name", str, default=None)
        intent = get_as(payload, "intent", str, default="")
        targets = get_as(payload, "targets", list, default=[])
        if tool_name is None or not tool_name.strip():
            raise ValueError("tool_name is required for tool steps")
        if not isinstance(targets, list) or not all(isinstance(t, str) for t in targets):
            targets = []

        trace_ctx = {"trace_id": trace_id, "flow_id": flow_id, "step_id": step.step_id}
        exec_result = self._tool_executor.execute(
            tool_name=tool_name,
            intent=str(intent),
            targets=list(targets),
            context=context,
            trace_ctx=trace_ctx,
            trace=trace,
        )
        tool_result = exec_result.tool_result

        if tool_result.get("ok") is True:
            context["tool_results"].append({"tool_name": tool_name, "result": tool_result.get("result"), "step_id": step.step_id})
            context["step_results"].append({"type": "tool", "tool_name": tool_name, "ok": True})
            return replace(step, status="completed", result={"tool_name": tool_name, "args": exec_result.args, "tool_result": tool_result})

        error_obj = tool_result.get("error")
        err = Error.from_dict(error_obj) if isinstance(error_obj, dict) else Error(code="tool.failed", message="Tool failed")
        context["step_results"].append({"type": "tool", "tool_name": tool_name, "ok": False, "error": err.to_dict()})
        return replace(step, status="failed", error=err, result={"tool_name": tool_name, "args": exec_result.args, "tool_result": tool_result})

    def _execute_chat_step(self, *, step: FlowStep, context: dict[str, Any], trace: TraceWriter) -> tuple[FlowStep, str]:
        user_request = get_as(context, "user_request", str, default="")
        result = self._chat.run(user_request=user_request, context=context, trace=trace)
        completed = replace(step, status="completed", result={"text": result.text, "metrics": result.metrics})
        return completed, result.text


def _step_summary(step: FlowStep, *, idx: int) -> dict[str, Any]:
    return {"index": idx, "step_id": step.step_id, "type": step.type, "status": step.status}


def _step_dict(step: FlowStep) -> dict[str, Any]:
    return {"step_id": step.step_id, "type": step.type, "status": step.status, "created_at": step.created_at, "payload": step.payload}
