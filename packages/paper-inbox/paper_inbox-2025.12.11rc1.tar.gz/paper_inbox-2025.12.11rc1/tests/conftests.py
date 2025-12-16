# tests/conftest.py
"""Pytest configuration and fixtures"""
import tempfile

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_config():
    """Mock configuration for tests"""
    return {
        'EMAIL_ACCOUNT': 'test@example.com',
        'EMAIL_FROM': ['sender@example.com'],
        'IMAP_SERVER': 'imap.gmail.com',
        'TRUSTED_SSIDS': ['TestWifi'],
        'SEND_TELEGRAM_NOTIFICATIONS': False,
        'TELEGRAM_BOT_TOKEN': '',
        'TELEGRAM_CHAT_ID': '',
    }


@pytest.fixture(autouse=True)
def reset_config():
    """Reset config module state between tests"""
    yield
    # Cleanup code here if needed