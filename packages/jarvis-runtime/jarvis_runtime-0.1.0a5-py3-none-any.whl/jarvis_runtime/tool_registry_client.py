from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from jarvis_model import SCHEMA_VERSION


class ToolRegistryClient(Protocol):
    def list_tools(self) -> list[dict[str, Any]]: ...

    def get_tool(self, name: str) -> dict[str, Any]: ...

    def invoke(
        self,
        name: str,
        *,
        args: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        trace: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]: ...


@dataclass(frozen=True, slots=True)
class HttpToolRegistryClient:
    base_url: str
    timeout_s: float = 10.0

    def list_tools(self) -> list[dict[str, Any]]:
        url = self.base_url.rstrip("/") + "/v1/tools"
        status, payload = _request_json("GET", url, timeout_s=self.timeout_s)
        if status != 200 or not isinstance(payload, list):
            raise RuntimeError(f"Tool Registry list_tools failed status={status}")
        return payload

    def get_tool(self, name: str) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + f"/v1/tools/{name}"
        status, payload = _request_json("GET", url, timeout_s=self.timeout_s)
        if status != 200 or not isinstance(payload, dict):
            raise RuntimeError(f"Tool Registry get_tool failed status={status} tool={name}")
        return payload

    def invoke(
        self,
        name: str,
        *,
        args: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        trace: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + f"/v1/tools/{name}:invoke"
        body: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "args": args}
        if context is not None:
            body["context"] = context
        if trace is not None:
            body["trace"] = trace
        status, payload = _request_json("POST", url, body=body, timeout_s=self.timeout_s)
        if not isinstance(payload, dict):
            raise RuntimeError(f"Tool Registry invoke returned non-object status={status}")
        return payload


class InProcessToolRegistryClient:
    """Runs against the Tool Registry router in-process (no port binding).

    This is useful for tests and sandboxed environments that block local sockets.
    Requires the `jarvis-tool-registry` package to be installed.
    """

    def __init__(self, *, domains: Optional[list[str]] = None):
        from tool_registry.catalog import ToolCatalog, load_domain_tools
        from tool_registry.server import ToolRegistryApp

        catalog = ToolCatalog(load_domain_tools(domains or ["core"]))
        self._app = ToolRegistryApp(catalog)

    def list_tools(self) -> list[dict[str, Any]]:
        status, payload, _ = self._app.handle(method="GET", path="/v1/tools", body=None)
        if int(status) != 200 or not isinstance(payload, list):
            raise RuntimeError("InProcess list_tools failed")
        return payload

    def get_tool(self, name: str) -> dict[str, Any]:
        status, payload, _ = self._app.handle(method="GET", path=f"/v1/tools/{name}", body=None)
        if int(status) != 200 or not isinstance(payload, dict):
            raise RuntimeError(f"InProcess get_tool failed tool={name}")
        return payload

    def invoke(
        self,
        name: str,
        *,
        args: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        trace: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "args": args}
        if context is not None:
            body["context"] = context
        if trace is not None:
            body["trace"] = trace
        status, payload, _ = self._app.handle(method="POST", path=f"/v1/tools/{name}:invoke", body=body)
        if not isinstance(payload, dict):
            raise RuntimeError(f"InProcess invoke returned non-object status={int(status)}")
        return payload


def _request_json(
    method: str,
    url: str,
    *,
    body: Optional[dict[str, Any]] = None,
    timeout_s: float,
) -> tuple[int, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = Request(url=url, method=method, data=data, headers=headers)
    try:
        with urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            return int(resp.status), json.loads(raw)
    except HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {"error": raw}
        return int(e.code), payload
    except URLError as e:
        raise RuntimeError(f"Tool Registry request failed: {e}") from e

