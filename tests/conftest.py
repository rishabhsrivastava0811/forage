"""Shared test fixtures."""

import tempfile
from pathlib import Path

import pytest
import yaml

from forage.infra.config import load_config
from forage.infra.database import init_db


@pytest.fixture
def tmp_config(tmp_path):
    """Create a minimal config in a temp directory."""
    config_data = {
        "name": "test-agent",
        "seed": {"amount": 50.0, "currency": "USD"},
        "providers": [
            {"name": "groq", "api_key": "test-key", "models": ["llama-3.1-8b-instant"], "tier": "routine"}
        ],
        "hardware": {"mode": "manual", "cpu_cores": 4, "ram_gb": 8},
        "revenue": {
            "default": {"owner": 0.0, "reinvest": 1.0, "reserve": 0.0},
            "milestones": [
                {"name": "survival", "trigger": {"balance_above": 75.0},
                 "split": {"owner": 0.10, "reinvest": 0.80, "reserve": 0.10}},
                {"name": "growth", "trigger": {"balance_above": 200.0, "consecutive_profitable_days": 7},
                 "split": {"owner": 0.50, "reinvest": 0.30, "reserve": 0.20}},
            ],
        },
        "spending": {"daily_limit": 5.0, "per_action_limit": 1.0, "emergency_reserve": 10.0},
        "payout": {"method": "manual", "min_payout": 5.0, "frequency": "weekly"},
        "capabilities": {
            "content_creation": True, "digital_products": True, "api_services": False,
            "inference_service": False, "crypto_yield": False, "trading": False, "freelancing": False,
            "allowed_services": [], "deploy_targets": [],
        },
        "evolution": {"enabled": True, "cycle": "daily", "strategy": "conservative"},
        "schedule": {"wake_interval_minutes": 30},
        "dashboard": {"enabled": False, "port": 3000, "host": "127.0.0.1"},
        "logging": {"level": "info", "file": "logs/forage.log", "max_size_mb": 50},
        "notifications": {"enabled": False},
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.dump(config_data))
    return config_path


@pytest.fixture
def config(tmp_config):
    """Load config from temp file."""
    return load_config(tmp_config)


@pytest.fixture
def initialized_db(config):
    """Config with initialized database."""
    init_db(config)
    return config
