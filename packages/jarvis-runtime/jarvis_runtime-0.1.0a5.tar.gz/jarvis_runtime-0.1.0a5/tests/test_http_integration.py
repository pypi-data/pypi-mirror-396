import json
import unittest
from email.message import Message
from io import BytesIO
from tempfile import TemporaryDirectory
from typing import Any, Optional
from urllib.parse import urlparse
from urllib.error import HTTPError
from unittest.mock import patch

from jarvis_runtime.orchestrator import FlowOrchestrator
from jarvis_runtime.roles import HeuristicChat, HeuristicPlanner, HeuristicToolArgsGenerator, ToolArgsGenerator, ToolExecutor
from jarvis_runtime.tool_registry_client import HttpToolRegistryClient
from jarvis_runtime.trace import TraceWriter


try:
    from tool_registry.catalog import ToolCatalog, load_domain_tools
    from tool_registry.server import ToolRegistryApp
except Exception:  # pragma: no cover
    ToolCatalog = None  # type: ignore[assignment]
    load_domain_tools = None  # type: ignore[assignment]
    ToolRegistryApp = None  # type: ignore[assignment]


class InMemoryToolRegistryTransport:
    """Routes HttpToolRegistryClient urlopen() calls into ToolRegistryApp.

    This keeps the Runtime<->Tool Registry integration tests runnable even when local sockets are blocked.
    """

    def __init__(self, *, domains: Optional[list[str]] = None):
        if ToolCatalog is None or load_domain_tools is None or ToolRegistryApp is None:
            raise RuntimeError("tool_registry is not installed")

        catalog = ToolCatalog(load_domain_tools(domains or ["core"]))
        self._app = ToolRegistryApp(catalog)
        self.requests: list[tuple[str, str]] = []

    def urlopen(self, req, timeout: float | None = None):  # noqa: ARG002
        method = req.get_method() if hasattr(req, "get_method") else "GET"
        url = getattr(req, "full_url", "")
        parsed = urlparse(url)
        path = parsed.path

        body = None
        data = getattr(req, "data", None)
        if isinstance(data, (bytes, bytearray)):
            try:
                decoded = data.decode("utf-8")
                loaded = json.loads(decoded)
                body = loaded if isinstance(loaded, dict) else None
            except Exception:
                body = None

        self.requests.append((method, path))
        status, payload, _ = self._app.handle(method=method, path=path, body=body)
        encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        code = int(status)

        if code >= 400:
            raise HTTPError(url, code, "error", hdrs=Message(), fp=BytesIO(encoded))

        return _FakeResponse(status=code, body=encoded)


class _FakeResponse:
    def __init__(self, *, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


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


def _read_events(path) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


class TestHttpIntegration(unittest.TestCase):
    def setUp(self) -> None:
        if ToolCatalog is None or load_domain_tools is None or ToolRegistryApp is None:
            raise unittest.SkipTest("tool_registry is not installed; skipping HTTP integration tests")

    def test_time_now_end_to_end_over_http(self) -> None:
        with TemporaryDirectory() as tmp:
            transport = InMemoryToolRegistryTransport()
            with patch("jarvis_runtime.tool_registry_client.urlopen", new=transport.urlopen):
                tool_registry = HttpToolRegistryClient("http://tool-registry.test")
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

            paths = [p for _, p in transport.requests]
            self.assertIn("/v1/tools", paths)
            self.assertIn("/v1/tools/time_now", paths)
            self.assertIn("/v1/tools/time_now:invoke", paths)

    def test_no_tool_path_over_http(self) -> None:
        with TemporaryDirectory() as tmp:
            transport = InMemoryToolRegistryTransport()
            with patch("jarvis_runtime.tool_registry_client.urlopen", new=transport.urlopen):
                tool_registry = HttpToolRegistryClient("http://tool-registry.test")
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

            paths = [p for _, p in transport.requests]
            self.assertIn("/v1/tools", paths)
            self.assertFalse(any(p.endswith(":invoke") for p in paths))

    def test_invalid_args_do_not_invoke_over_http(self) -> None:
        with TemporaryDirectory() as tmp:
            transport = InMemoryToolRegistryTransport()
            with patch("jarvis_runtime.tool_registry_client.urlopen", new=transport.urlopen):
                tool_registry = HttpToolRegistryClient("http://tool-registry.test")
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

            paths = [p for _, p in transport.requests]
            self.assertIn("/v1/tools", paths)
            self.assertIn("/v1/tools/calc", paths)
            self.assertFalse(any(p.endswith(":invoke") for p in paths))

            events = _read_events(result.trace.trace_jsonl)
            invalids = [e for e in events if e.get("type") == "tool_args_invalid" and e.get("tool_name") == "calc"]
            self.assertEqual(len(invalids), 2)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
