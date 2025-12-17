import io
import unittest
from contextlib import redirect_stdout
from tempfile import TemporaryDirectory

from jarvis_runtime.cli import main
from jarvis_runtime.orchestrator import FlowOrchestrator
from jarvis_runtime.roles import HeuristicChat, HeuristicPlanner, HeuristicToolArgsGenerator, ToolExecutor
from jarvis_runtime.tool_registry_client import InProcessToolRegistryClient


class TestReplayCli(unittest.TestCase):
    def test_replay_reruns_chat_from_trace(self) -> None:
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

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["replay", "--trace", str(result.trace.trace_jsonl)])

            self.assertEqual(rc, 0)
            self.assertEqual(buf.getvalue().strip(), result.final_text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

