"""Loki backend for log queries."""

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from ..config import get_config


@dataclass
class LogEntry:
    """A single log entry."""

    timestamp: datetime
    line: str
    labels: dict


def query_logs(
    query: str = '{job="systemd-journal"}',
    service: Optional[str] = None,
    limit: int = 20,
    since_minutes: int = 60,
) -> list[LogEntry]:
    """
    Query Loki for logs.

    Args:
        query: LogQL query string
        service: Service name to filter by (overrides query)
        limit: Maximum number of log lines to return
        since_minutes: How far back to search

    Returns:
        List of LogEntry objects
    """
    config = get_config()

    # Override query if service specified
    if service:
        query = f'{{unit="{service}.service"}}'

    now = datetime.now()
    start = now - timedelta(minutes=since_minutes)

    params = {
        "query": query,
        "limit": str(limit),
        "start": str(int(start.timestamp() * 1e9)),
        "end": str(int(now.timestamp() * 1e9)),
    }
    url = f"{config.loki_url}/loki/api/v1/query_range?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=config.timeout) as resp:
            data = json.load(resp)
    except Exception as e:
        raise RuntimeError(f"Error querying Loki: {e}") from e

    results = []
    for stream in data.get("data", {}).get("result", []):
        labels = stream.get("stream", {})
        for ts, line in reversed(stream.get("values", [])):
            dt = datetime.fromtimestamp(int(ts) / 1e9)
            results.append(LogEntry(timestamp=dt, line=line, labels=labels))

    return results


def format_logs(entries: list[LogEntry]) -> str:
    """Format log entries for display."""
    if not entries:
        return "No logs found"

    lines = []
    for entry in entries:
        unit = entry.labels.get("unit", "").replace(".service", "")
        time_str = entry.timestamp.strftime("%H:%M:%S")
        lines.append(f"[{time_str}] [{unit:25}] {entry.line}")

    return "\n".join(lines)
