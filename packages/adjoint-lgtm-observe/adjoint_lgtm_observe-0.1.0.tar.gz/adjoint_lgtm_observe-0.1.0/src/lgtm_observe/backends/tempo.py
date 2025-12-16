"""Tempo backend for distributed tracing."""

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..config import get_config


@dataclass
class Span:
    """A single span in a trace."""

    service: str
    name: str
    duration_ms: float
    attributes: dict = field(default_factory=dict)


@dataclass
class TraceSearchResult:
    """A trace search result."""

    trace_id: str
    root_service: str
    root_name: str
    duration_ms: int
    start_time: Optional[datetime] = None


def get_trace(trace_id: str) -> list[Span]:
    """
    Get a specific trace from Tempo.

    Args:
        trace_id: The trace ID to fetch

    Returns:
        List of Span objects
    """
    config = get_config()
    url = f"{config.tempo_url}/api/traces/{trace_id}"

    try:
        with urllib.request.urlopen(url, timeout=config.timeout) as resp:
            data = json.load(resp)
    except Exception as e:
        raise RuntimeError(f"Error querying Tempo: {e}") from e

    spans = []
    for batch in data.get("batches", []):
        svc = "unknown"
        for attr in batch.get("resource", {}).get("attributes", []):
            if attr["key"] == "service.name":
                svc = attr["value"].get("stringValue", "unknown")

        for scope in batch.get("scopeSpans", []):
            for span_data in scope.get("spans", []):
                name = span_data.get("name", "unknown")
                start = int(span_data.get("startTimeUnixNano", 0))
                end = int(span_data.get("endTimeUnixNano", 0))
                duration_ms = (end - start) / 1e6

                attrs = {}
                for a in span_data.get("attributes", []):
                    val = list(a.get("value", {}).values())
                    attrs[a["key"]] = val[0] if val else None

                spans.append(Span(
                    service=svc,
                    name=name,
                    duration_ms=duration_ms,
                    attributes=attrs,
                ))

    return spans


def search_traces(service: Optional[str] = None, limit: int = 10) -> list[TraceSearchResult]:
    """
    Search for recent traces.

    Args:
        service: Filter by service name
        limit: Maximum number of traces to return

    Returns:
        List of TraceSearchResult objects
    """
    config = get_config()

    params = {"limit": str(limit)}
    if service:
        params["tags"] = f"service.name={service}"

    url = f"{config.tempo_url}/api/search?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=config.timeout) as resp:
            data = json.load(resp)
    except Exception as e:
        raise RuntimeError(f"Error searching Tempo: {e}") from e

    results = []
    for t in data.get("traces", []):
        start_ns = int(t.get("startTimeUnixNano", 0))
        start_time = datetime.fromtimestamp(start_ns / 1e9) if start_ns else None

        results.append(TraceSearchResult(
            trace_id=t.get("traceID", "unknown"),
            root_service=t.get("rootServiceName", "unknown"),
            root_name=t.get("rootTraceName", "unknown"),
            duration_ms=t.get("durationMs", 0),
            start_time=start_time,
        ))

    return results


def format_trace(trace_id: str, spans: list[Span]) -> str:
    """Format a trace for display."""
    lines = [f"Trace: {trace_id}\n"]

    for span in spans:
        lines.append(f"[{span.service}] {span.name} ({span.duration_ms:.1f}ms)")
        for k, v in span.attributes.items():
            lines.append(f"    {k}: {v}")

    return "\n".join(lines)


def format_trace_search(results: list[TraceSearchResult]) -> str:
    """Format trace search results for display."""
    if not results:
        return "No traces found"

    lines = [f"Recent traces (limit {len(results)}):\n"]

    for t in results:
        time_str = t.start_time.strftime("%H:%M:%S") if t.start_time else "?"
        lines.append(f"  {t.trace_id}")
        lines.append(f"    {t.root_service}/{t.root_name} ({t.duration_ms}ms) @ {time_str}")
        lines.append("")

    return "\n".join(lines)
