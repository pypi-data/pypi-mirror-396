import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jarvis_runtime.orchestrator import FlowOrchestrator
from jarvis_runtime.roles import HeuristicChat, HeuristicPlanner, HeuristicToolArgsGenerator, ToolExecutor
from jarvis_runtime.tool_registry_client import InProcessToolRegistryClient


def _read_events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class TestRuntimeDemo(unittest.TestCase):
    def test_time_now_calls_tool(self) -> None:
        with TemporaryDirectory() as tmp:
            tool_registry = InProcessToolRegistryClient()
            tool_executor = ToolExecutor(tool_registry=tool_registry, args_generator=HeuristicToolArgsGenerator())
            orchestrator = FlowOrchestrator(
                planner=HeuristicPlanner(),
                tool_registry=tool_registry,
                tool_executor=tool_executor,
                chat=HeuristicChat(),
                trace_dir=tmp,
            )
            result = orchestrator.run(user_request="What time is it in UTC?")
            self.assertEqual(result.status, "completed")
            self.assertIn("UTC", result.final_text)

            events = _read_events(result.trace.trace_jsonl)
            tool_calls = [e for e in events if e.get("type") == "tool_invocation" and e.get("tool_name") == "time_now"]
            self.assertEqual(len(tool_calls), 1)

    def test_calc_calls_tool(self) -> None:
        with TemporaryDirectory() as tmp:
            tool_registry = InProcessToolRegistryClient()
            tool_executor = ToolExecutor(tool_registry=tool_registry, args_generator=HeuristicToolArgsGenerator())
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

    def test_rephrase_does_not_call_tool(self) -> None:
        with TemporaryDirectory() as tmp:
            tool_registry = InProcessToolRegistryClient()
            tool_executor = ToolExecutor(tool_registry=tool_registry, args_generator=HeuristicToolArgsGenerator())
            orchestrator = FlowOrchestrator(
                planner=HeuristicPlanner(),
                tool_registry=tool_registry,
                tool_executor=tool_executor,
                chat=HeuristicChat(),
                trace_dir=tmp,
            )
            result = orchestrator.run(user_request="Rephrase this sentence: hello world")
            self.assertEqual(result.status, "completed")
            self.assertTrue(result.final_text)

            events = _read_events(result.trace.trace_jsonl)
            tool_calls = [e for e in events if e.get("type") == "tool_invocation"]
            self.assertEqual(len(tool_calls), 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
