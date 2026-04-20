from __future__ import annotations

import base64
import os
import threading
from contextlib import nullcontext
from typing import Any

import httpx
import requests
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

try:
    from langfuse import Langfuse, propagate_attributes
except Exception:  # pragma: no cover
    class _DummyClient:
        def start_as_current_observation(self, **kwargs: Any):
            return nullcontext()

        def update_current_span(self, **kwargs: Any) -> None:
            return None

        def flush(self) -> None:
            return None

    def propagate_attributes(*args: Any, **kwargs: Any):
        return nullcontext()

    def get_langfuse_client():
        return _DummyClient()
else:
    _CLIENT: Langfuse | None = None
    _CLIENT_LOCK = threading.Lock()

    def _build_span_exporter(base_url: str, public_key: str, secret_key: str, timeout: int) -> OTLPSpanExporter:
        basic_auth_header = "Basic " + base64.b64encode(
            f"{public_key}:{secret_key}".encode("utf-8")
        ).decode("ascii")
        headers = {
            "Authorization": basic_auth_header,
            "x-langfuse-sdk-name": "python",
            "x-langfuse-public-key": public_key,
            "x-langfuse-ingestion-version": "4",
        }
        session = requests.Session()
        session.trust_env = False
        return OTLPSpanExporter(
            endpoint=f"{base_url}/api/public/otel/v1/traces",
            headers=headers,
            timeout=timeout,
            session=session,
        )

    def _build_client() -> Langfuse:
        timeout = int(os.getenv("LANGFUSE_TIMEOUT", "20"))
        base_url = os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        httpx_client = httpx.Client(timeout=timeout, trust_env=False)

        return Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            base_url=base_url,
            timeout=timeout,
            httpx_client=httpx_client,
            span_exporter=_build_span_exporter(base_url, public_key or "", secret_key or "", timeout)
            if public_key and secret_key
            else None,
            environment=os.getenv("LANGFUSE_TRACING_ENVIRONMENT"),
        )

    def get_langfuse_client() -> Langfuse:
        global _CLIENT
        if _CLIENT is None:
            with _CLIENT_LOCK:
                if _CLIENT is None:
                    _CLIENT = _build_client()
        return _CLIENT


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
