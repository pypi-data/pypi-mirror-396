# JARVIS Runtime

This repo contains the **Jarvis Agent Runtime**: a Python runtime for executing Agent Runtime Protocol-style agent flows using the 3-role loop:

Planner → Tool Executor (arg-gen + invoke) → Chat

It is designed to run against the `Tool_Registry` service and share contracts via `jarvis-model`.

## Quickstart

See:

- `docs/quickstart.md`
- `docs/trace.md`

## Install

From PyPI (once published):

```bash
pipx install jarvis-runtime
```

Pre-release (e.g. `0.1.0a1`):

```bash
pipx install --pip-args="--pre" jarvis-runtime
```

Or in a virtualenv:

```bash
pip install jarvis-runtime
```

For `--tool-registry inproc`, install Tool Registry too:

```bash
pip install jarvis-tool-registry
```

Or install the extra:

```bash
pip install "jarvis-runtime[inproc]"
```

## Run against a real Tool Registry service

Terminal A (Tool Registry):

```bash
tool-registry
```

Terminal B (Runtime):

```bash
jarvis-runtime demo --tool-registry http --tool-registry-url http://127.0.0.1:8000
```

## OpenAI mode (optional)

This runtime uses the OpenAI Python SDK for Responses parsing + structured outputs. To enable it:

```bash
pip install -e ".[openai]"
export OPENAI_API_KEY=...
jarvis-runtime demo --mode openai --tool-registry inproc
```

Optional model overrides:

- `JARVIS_MODEL_PLANNER`
- `JARVIS_MODEL_TOOL_ARGS`
- `JARVIS_MODEL_CHAT`
- `JARVIS_MODEL_DEFAULT`

## Validation

Unit tests:

```bash
python -m unittest discover -v
```

Or (if you have `pytest` installed):

```bash
pytest -q
```

Typecheck (pyright):

```bash
pyright -p pyrightconfig.json
```

## Design docs

- `docs/intro.md`
- `docs/design/overview.md`

## Repo boundaries

- This repo: flow execution, LLM role orchestration, runtime packaging.
- `Tool_Registry` (separate repo): tool discovery + schemas + invocation routing (+ MCP aggregation).
- `JARVIS/Model` (separate repo): shared schemas / data model (and eventually the ARP wire protocol spec).

## MVP capabilities + known gaps

Capabilities:

- Stub-mode 3-role loop (Planner → Tool → Chat) with trace JSONL.
- Tool Registry integration via HTTP (and `inproc` for tests/sandboxed environments).
- Trace replay: rerun Chat from recorded tool results.

Known gaps:

- No production hardening (auth, multi-tenancy, concurrency controls, streaming, persistence).
- Prompt packs and planning heuristics are MVP-grade; no memory/scheduler/control plane yet.
