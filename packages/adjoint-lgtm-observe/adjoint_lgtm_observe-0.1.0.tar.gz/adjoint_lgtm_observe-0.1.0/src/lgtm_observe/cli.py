#!/usr/bin/env python3
"""
CLI for lgtm-observe: Unified observability for LGTM stack.

Query Loki, Tempo, Prometheus, and Kafka from your terminal.
"""

import argparse
import sys
import urllib.request

from .backends import kafka, loki, prometheus, tempo
from .config import get_config


def cmd_logs(args):
    """Handle logs command."""
    try:
        entries = loki.query_logs(
            query=args.query,
            service=args.service,
            limit=args.limit,
        )
        print(loki.format_logs(entries))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_trace(args):
    """Handle trace command."""
    try:
        spans = tempo.get_trace(args.trace_id)
        if not spans:
            print("Trace not found or empty")
            sys.exit(1)
        print(tempo.format_trace(args.trace_id, spans))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_traces(args):
    """Handle traces command."""
    try:
        results = tempo.search_traces(service=args.service, limit=args.limit)
        print(tempo.format_trace_search(results))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_metrics(args):
    """Handle metrics command."""
    try:
        results = prometheus.query_metrics(args.query)
        print(prometheus.format_metrics(results))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_kafka_topics(args):
    """Handle kafka topics command."""
    try:
        topics = kafka.list_topics()
        print(kafka.format_topics(topics))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_kafka_consumers(args):
    """Handle kafka consumers command."""
    try:
        consumers = kafka.list_consumers()
        print(kafka.format_consumers(consumers))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_kafka_lag(args):
    """Handle kafka lag command."""
    try:
        lag_results = kafka.get_lag()
        print(kafka.format_lag(lag_results))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_status(args):
    """Handle status command."""
    config = get_config()

    print("System Status:\n")

    # Check HTTP endpoints
    for name, url in [
        ("Loki", f"{config.loki_url}/ready"),
        ("Tempo", f"{config.tempo_url}/ready"),
        ("Prometheus", f"{config.prometheus_url}/-/ready"),
    ]:
        try:
            with urllib.request.urlopen(url, timeout=3):
                print(f"  {name}: OK")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")

    # Check Kafka
    try:
        from kafka.admin import KafkaAdminClient
        admin = KafkaAdminClient(bootstrap_servers=config.kafka_bootstrap)
        topics = admin.list_topics()
        admin.close()
        print(f"  Kafka: OK ({len(topics)} topics)")
    except ImportError:
        print("  Kafka: SKIP (kafka-python not installed)")
    except Exception as e:
        print(f"  Kafka: FAIL ({e})")


def cmd_config(args):
    """Show current configuration."""
    config = get_config()
    print("Current configuration:\n")
    print(f"  LOKI_URL:        {config.loki_url}")
    print(f"  TEMPO_URL:       {config.tempo_url}")
    print(f"  PROMETHEUS_URL:  {config.prometheus_url}")
    print(f"  KAFKA_BOOTSTRAP: {config.kafka_bootstrap}")
    print(f"  TIMEOUT:         {config.timeout}s")
    print()
    print("Set via environment variables or ~/.lgtm-observe.json")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="lgtm-observe",
        description="Unified CLI for LGTM observability stack (Loki, Tempo, Prometheus) + Kafka",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lgtm-observe status                     # Health check all systems
  lgtm-observe logs                       # Recent logs from all services
  lgtm-observe logs -s myservice          # Logs from specific service
  lgtm-observe trace <trace-id>           # Get specific trace
  lgtm-observe traces                     # Search recent traces
  lgtm-observe metrics 'up'               # Query Prometheus
  lgtm-observe kafka topics               # List Kafka topics
  lgtm-observe kafka consumers            # List consumer groups
  lgtm-observe kafka lag                  # Show consumer lag

Configuration:
  Set endpoints via environment variables:
    LOKI_URL, TEMPO_URL, PROMETHEUS_URL, KAFKA_BOOTSTRAP

  Or create ~/.lgtm-observe.json:
    {"loki_url": "http://localhost:3100", ...}
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Status command
    status_parser = subparsers.add_parser("status", help="Health check all systems")
    status_parser.set_defaults(func=cmd_status)

    # Config command
    config_parser = subparsers.add_parser("config", help="Show current configuration")
    config_parser.set_defaults(func=cmd_config)

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Query logs from Loki")
    logs_parser.add_argument(
        "--query", "-q",
        default='{job="systemd-journal"}',
        help="LogQL query"
    )
    logs_parser.add_argument("--service", "-s", help="Filter by service name")
    logs_parser.add_argument("--limit", "-n", type=int, default=20, help="Number of log lines")
    logs_parser.set_defaults(func=cmd_logs)

    # Trace command
    trace_parser = subparsers.add_parser("trace", help="Get a specific trace")
    trace_parser.add_argument("trace_id", help="Trace ID to fetch")
    trace_parser.set_defaults(func=cmd_trace)

    # Traces command
    traces_parser = subparsers.add_parser("traces", help="Search recent traces")
    traces_parser.add_argument("--service", "-s", help="Filter by service")
    traces_parser.add_argument("--limit", "-n", type=int, default=10)
    traces_parser.set_defaults(func=cmd_traces)

    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Query Prometheus")
    metrics_parser.add_argument("query", help="PromQL query")
    metrics_parser.set_defaults(func=cmd_metrics)

    # Kafka command
    kafka_parser = subparsers.add_parser("kafka", help="Kafka observability")
    kafka_subparsers = kafka_parser.add_subparsers(dest="kafka_cmd", required=True)

    kafka_topics = kafka_subparsers.add_parser("topics", help="List topics with message counts")
    kafka_topics.set_defaults(func=cmd_kafka_topics)

    kafka_consumers = kafka_subparsers.add_parser("consumers", help="List consumer groups")
    kafka_consumers.set_defaults(func=cmd_kafka_consumers)

    kafka_lag = kafka_subparsers.add_parser("lag", help="Show consumer lag")
    kafka_lag.set_defaults(func=cmd_kafka_lag)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
