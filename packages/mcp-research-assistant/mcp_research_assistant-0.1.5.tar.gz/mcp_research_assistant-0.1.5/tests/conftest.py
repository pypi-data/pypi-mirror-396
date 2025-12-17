"""Pytest configuration and fixtures for research-assistant-mcp tests."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest


@pytest.fixture
def temp_db_path():
    """Provide a temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_env_vars(temp_db_path, monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("RESEARCH_DB_PATH", temp_db_path)
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key-12345")
    return {
        "RESEARCH_DB_PATH": temp_db_path,
        "OPENAI_API_KEY": "test-api-key-12345"
    }


@pytest.fixture
def sample_documents():
    """Provide sample documents for testing."""
    return [
        {
            "content": "Machine learning is a subset of artificial intelligence.",
            "metadata": {"source": "test1"}
        },
        {
            "content": "Deep learning uses neural networks with multiple layers.",
            "metadata": {"source": "test2"}
        },
        {
            "content": "Natural language processing deals with text and language.",
            "metadata": {"source": "test3"}
        }
    ]
