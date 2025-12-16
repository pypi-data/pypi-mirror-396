"""Configuration management for lgtm-observe."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Configuration for observability endpoints."""

    loki_url: str = "http://localhost:3100"
    tempo_url: str = "http://localhost:3200"
    prometheus_url: str = "http://localhost:9090"
    kafka_bootstrap: str = "localhost:9093"
    timeout: int = 10

    @classmethod
    def load(cls) -> "Config":
        """Load config from environment, then config file, then defaults."""
        config = cls()

        # Try config file first
        config_path = Path.home() / ".lgtm-observe.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    data = json.load(f)
                    config.loki_url = data.get("loki_url", config.loki_url)
                    config.tempo_url = data.get("tempo_url", config.tempo_url)
                    config.prometheus_url = data.get("prometheus_url", config.prometheus_url)
                    config.kafka_bootstrap = data.get("kafka_bootstrap", config.kafka_bootstrap)
                    config.timeout = data.get("timeout", config.timeout)
            except Exception:
                pass  # Fall back to defaults

        # Environment variables override config file
        config.loki_url = os.environ.get("LOKI_URL", config.loki_url)
        config.tempo_url = os.environ.get("TEMPO_URL", config.tempo_url)
        config.prometheus_url = os.environ.get("PROMETHEUS_URL", config.prometheus_url)
        config.kafka_bootstrap = os.environ.get("KAFKA_BOOTSTRAP", config.kafka_bootstrap)
        if timeout_str := os.environ.get("LGTM_TIMEOUT"):
            try:
                config.timeout = int(timeout_str)
            except ValueError:
                pass

        return config


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global config."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config
