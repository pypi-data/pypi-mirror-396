"""Tests for configuration module."""

import os
from unittest import mock

from lgtm_observe.config import Config


def test_config_defaults():
    """Test default configuration values."""
    config = Config()
    assert config.loki_url == "http://localhost:3100"
    assert config.tempo_url == "http://localhost:3200"
    assert config.prometheus_url == "http://localhost:9090"
    assert config.kafka_bootstrap == "localhost:9093"
    assert config.timeout == 10


def test_config_from_env():
    """Test configuration from environment variables."""
    with mock.patch.dict(os.environ, {
        "LOKI_URL": "http://loki:3100",
        "TEMPO_URL": "http://tempo:3200",
        "PROMETHEUS_URL": "http://prom:9090",
        "KAFKA_BOOTSTRAP": "kafka:9092",
        "LGTM_TIMEOUT": "30",
    }):
        config = Config.load()
        assert config.loki_url == "http://loki:3100"
        assert config.tempo_url == "http://tempo:3200"
        assert config.prometheus_url == "http://prom:9090"
        assert config.kafka_bootstrap == "kafka:9092"
        assert config.timeout == 30
