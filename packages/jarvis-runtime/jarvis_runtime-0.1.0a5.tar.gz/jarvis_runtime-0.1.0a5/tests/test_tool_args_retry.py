import json
import unittest
from tempfile import TemporaryDirectory
from typing import Any, Optional

from jarvis_runtime.orchestrator import FlowOrchestrator
from jarvis_runtime.roles import HeuristicChat, HeuristicPlanner, ToolArgsGenerator, ToolExecutor
from jarvis_runtime.tool_registry_client import InProcessToolRegistryClient
from jarvis_runtime.trace import TraceWriter


class FlakyArgsGenerator(ToolArgsGenerator):
    def __init__(self) -> None:
        self._calls = 0

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
        self._calls += 1
        if self._calls == 1:
            return {}
        return {"expression": "19*23"}


class AlwaysInvalidArgsGenerator(ToolArgsGenerator):
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
        return {}


class TestToolArgsRetry(unittest.TestCase):
    def test_retries_once_on_invalid_args(self) -> None:
        with TemporaryDirectory() as tmp:
            tool_registry = InProcessToolRegistryClient()
            tool_executor = ToolExecutor(tool_registry=tool_registry, args_generator=FlakyArgsGenerator())
            orchestrator = FlowOrchestrator(
                planner=HeuristicPlanner(),
                tool_registry=tool_registry,
                tool_executor=tool_executor,
                chat=HeuristicChat(),
                trace_dir=tmp,
            )
            result = orchestrator.run(user_request="What is (19*23)?")
            self.assertEqual(result.status, "completed")
            self.assertIn("437", result.final_text)

            events = [json.loads(line) for line in result.trace.trace_jsonl.read_text(encoding="utf-8").splitlines()]
            invalids = [e for e in events if e.get("type") == "tool_args_invalid"]
            self.assertGreaterEqual(len(invalids), 1)

    def test_fails_after_retries_exhausted(self) -> None:
        with TemporaryDirectory() as tmp:
            tool_registry = InProcessToolRegistryClient()
            tool_executor = ToolExecutor(tool_registry=tool_registry, args_generator=AlwaysInvalidArgsGenerator())
            orchestrator = FlowOrchestrator(
                planner=HeuristicPlanner(),
                tool_registry=tool_registry,
                tool_executor=tool_executor,
                chat=HeuristicChat(),
                trace_dir=tmp,
            )
            result = orchestrator.run(user_request="What is (19*23)?")
            self.assertEqual(result.status, "failed")
            self.assertIn("tool.invalid_args", result.final_text)

            events = [json.loads(line) for line in result.trace.trace_jsonl.read_text(encoding="utf-8").splitlines()]
            invalids = [e for e in events if e.get("type") == "tool_args_invalid"]
            self.assertEqual(len(invalids), 2)
            invocations = [e for e in events if e.get("type") == "tool_invocation"]
            self.assertEqual(len(invocations), 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
