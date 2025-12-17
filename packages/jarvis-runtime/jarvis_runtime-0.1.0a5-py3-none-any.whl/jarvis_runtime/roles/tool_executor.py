from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from jarvis_model import ToolArgsValidationError, validate_tool_args

from ..tool_registry_client import ToolRegistryClient
from ..trace import TraceWriter
from ..util import get_as
from .tool_args import ToolArgsGenerator


@dataclass(frozen=True, slots=True)
class ToolExecutionResult:
    tool_name: str
    args: dict[str, Any]
    tool_result: dict[str, Any]
    attempts: int


class ToolExecutor:
    def __init__(
        self,
        *,
        tool_registry: ToolRegistryClient,
        args_generator: ToolArgsGenerator,
        trace: Optional[TraceWriter] = None,
        max_arg_retries: int = 1,
    ):
        self._tool_registry = tool_registry
        self._args_generator = args_generator
        self._trace = trace
        self._max_arg_retries = max_arg_retries

    def execute(
        self,
        *,
        tool_name: str,
        intent: str,
        targets: list[str],
        context: dict[str, Any],
        trace_ctx: dict[str, Any],
        trace: Optional[TraceWriter] = None,
    ) -> ToolExecutionResult:
        trace_writer = trace or self._trace
        definition = self._tool_registry.get_tool(tool_name)
        if not isinstance(definition, dict):
            raise ValueError("Tool definition must be an object")

        tool_schema = definition.get("parameters")
        if not isinstance(tool_schema, dict):
            raise ValueError("Tool definition missing parameters schema")

        tool_description = get_as(definition, "description", str, default=None)

        attempt = 0
        last_validation_error: Optional[dict[str, Any]] = None
        while True:
            attempt += 1
            args = self._args_generator.generate(
                tool_name=tool_name,
                tool_schema=tool_schema,
                context=context,
                intent=intent,
                targets=targets,
                tool_description=tool_description,
                validation_error=last_validation_error,
                trace=trace_writer,
            )
            if trace_writer:
                trace_writer.write(
                    "tool_args_generated",
                    {"tool_name": tool_name, "attempt": attempt, "args": args, "trace": trace_ctx},
                )

            try:
                validate_tool_args(tool_schema, args)
            except ToolArgsValidationError as exc:
                last_validation_error = exc.error.to_dict()
                if trace_writer:
                    trace_writer.write(
                        "tool_args_invalid",
                        {"tool_name": tool_name, "attempt": attempt, "error": exc.error.to_dict(), "trace": trace_ctx},
                    )
                if attempt <= self._max_arg_retries:
                    continue
                tool_result = {"ok": False, "error": exc.error.to_dict(), "schema_version": exc.error.schema_version}
                return ToolExecutionResult(tool_name=tool_name, args=args, tool_result=tool_result, attempts=attempt)

            if trace_writer:
                trace_writer.write("tool_invocation", {"tool_name": tool_name, "args": args, "trace": trace_ctx})

            result = self._tool_registry.invoke(tool_name, args=args, context=context, trace=trace_ctx)
            if trace_writer:
                trace_writer.write("tool_result", {"tool_name": tool_name, "result": result, "trace": trace_ctx})
            return ToolExecutionResult(tool_name=tool_name, args=args, tool_result=result, attempts=attempt)
