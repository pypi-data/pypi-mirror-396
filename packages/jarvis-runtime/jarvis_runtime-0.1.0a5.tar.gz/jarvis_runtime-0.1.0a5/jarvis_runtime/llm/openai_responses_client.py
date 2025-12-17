from __future__ import annotations

import importlib
import time
from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True, slots=True)
class OpenAIResponsesClient:
    """OpenAI Responses API client (SDK-backed).

    Mirrors the interface used in RefRepos/Jarvis: a single `responses()` call
    that can optionally request structured outputs via JSON Schema.
    """

    api_key: str
    base_url: str = "https://api.openai.com/v1"
    timeout_s: float = 60.0
    default_model: str = "gpt-5-nano"
    temperature: Optional[float] = None

    def responses(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Optional[Mapping[str, Any]] = None,
        model_override: Optional[str] = None,
    ) -> dict[str, Any]:
        model = model_override or self.default_model

        start = time.perf_counter()
        client, omit = _load_openai_client(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout_s=self.timeout_s,
        )

        text_param: Any = omit
        if output_schema is not None:
            # Expected shape: {"format": {"type": "json_schema", "name": "...", "schema": {...}, "strict": True}}
            text_param = dict(output_schema)

        try:
            resp = client.responses.parse(
                model=model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                text=text_param,
                temperature=self.temperature,
                reasoning={
                    "effort": "low"
                }
            )
        except Exception as exc:  # pragma: no cover - defensive network call
            latency_ms = int((time.perf_counter() - start) * 1000)
            details = _format_openai_exception(exc)
            raise RuntimeError(f"OpenAI request failed after {latency_ms}ms: {details}") from exc

        latency_ms = int((time.perf_counter() - start) * 1000)

        parsed_output = getattr(resp, "output_parsed", None)
        parsed_output = _maybe_model_to_dict(parsed_output)

        usage = getattr(resp, "usage", None)
        usage = _maybe_model_to_dict(usage)

        return {
            "parsed": parsed_output,
            "output_text": getattr(resp, "output_text", None),
            "usage": usage,
            "latency_ms": latency_ms,
            "response": resp,
        }


def _load_openai_client(*, api_key: str, base_url: str, timeout_s: float) -> tuple[Any, Any]:
    try:
        openai_mod = importlib.import_module("openai")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "OpenAI SDK is not installed. Install it with: `python -m pip install openai`"
        ) from exc

    OpenAI = getattr(openai_mod, "OpenAI", None)
    omit = getattr(openai_mod, "omit", None)
    if OpenAI is None or omit is None:
        raise RuntimeError("Unsupported OpenAI SDK version: missing OpenAI/omit")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout_s,
        _strict_response_validation=True,
    )
    return client, omit


def _maybe_model_to_dict(obj: Any) -> Any:
    if obj is None:
        return None
    model_dump = getattr(obj, "model_dump", None)
    if callable(model_dump):
        return model_dump()
    as_dict = getattr(obj, "dict", None)
    if callable(as_dict):
        return as_dict()
    return obj


def _format_openai_exception(exc: Exception) -> str:
    status = getattr(exc, "status_code", None)
    body = getattr(exc, "body", None)
    if status is not None and body is not None:
        return f"status={status} body={body}"
    if status is not None:
        return f"status={status} message={exc}"
    if body is not None:
        return f"body={body}"
    return str(exc)
