"""Prometheus backend for metrics queries."""

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass

from ..config import get_config


@dataclass
class MetricResult:
    """A single metric result."""

    name: str
    labels: dict
    value: str


def query_metrics(query: str) -> list[MetricResult]:
    """
    Query Prometheus for metrics.

    Args:
        query: PromQL query string

    Returns:
        List of MetricResult objects
    """
    config = get_config()

    params = {"query": query}
    url = f"{config.prometheus_url}/api/v1/query?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=config.timeout) as resp:
            data = json.load(resp)
    except Exception as e:
        raise RuntimeError(f"Error querying Prometheus: {e}") from e

    results = []
    for r in data.get("data", {}).get("result", []):
        metric = r.get("metric", {})
        value = r.get("value", [None, "?"])[1]
        name = metric.pop("__name__", "value")

        results.append(MetricResult(
            name=name,
            labels=metric,
            value=value,
        ))

    return results


def format_metrics(results: list[MetricResult]) -> str:
    """Format metric results for display."""
    if not results:
        return "No metrics found"

    lines = []
    for r in results:
        labels = ", ".join(f"{k}={v}" for k, v in r.labels.items())
        lines.append(f"{r.name}{{{labels}}}: {r.value}")

    return "\n".join(lines)
