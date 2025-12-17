from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Protocol

from .util import utc_now_iso


class TraceWriter(Protocol):
    def write(self, event_type: str, payload: dict[str, Any]) -> None: ...

    def close(self) -> None: ...


class NullTraceWriter:
    def write(self, event_type: str, payload: dict[str, Any]) -> None:
        return

    def close(self) -> None:
        return


@dataclass(frozen=True, slots=True)
class TracePaths:
    run_dir: Path
    trace_jsonl: Path


class JsonlTraceWriter:
    def __init__(self, trace_path: Path):
        self._path = trace_path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._fp = self._path.open("a", encoding="utf-8")

    @property
    def path(self) -> Path:
        return self._path

    def write(self, event_type: str, payload: dict[str, Any]) -> None:
        record = {"ts": utc_now_iso(), "type": event_type, **payload}
        self._fp.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._fp.flush()

    def close(self) -> None:
        self._fp.close()


def default_trace_paths(trace_dir: str | Path, flow_id: str) -> TracePaths:
    base = Path(trace_dir)
    run_dir = base / flow_id
    return TracePaths(run_dir=run_dir, trace_jsonl=run_dir / "trace.jsonl")


def maybe_redact(value: Any, *, enabled: bool) -> Any:
    if not enabled:
        return value
    if value is None:
        return None
    return "<redacted>"

