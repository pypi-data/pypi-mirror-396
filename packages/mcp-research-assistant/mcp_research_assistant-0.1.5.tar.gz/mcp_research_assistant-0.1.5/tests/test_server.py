"""Tests for the research assistant MCP server."""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestContentHashing:
    """Test content hashing functionality."""

    def test_get_content_hash(self):
        """Test content hash generation."""
        # Import here to avoid issues with environment variables
        from research_assistant_mcp.server import get_content_hash

        content1 = "Test content"
        content2 = "Test content"
        content3 = "Different content"

        hash1 = get_content_hash(content1)
        hash2 = get_content_hash(content2)
        hash3 = get_content_hash(content3)

        # Same content should produce same hash
        assert hash1 == hash2
        # Different content should produce different hash
        assert hash1 != hash3
        # Hash should be a string
        assert isinstance(hash1, str)
        # MD5 hash should be 32 characters
        assert len(hash1) == 32

    def test_save_and_load_content_hashes(self, temp_db_path):
        """Test saving and loading content hashes."""
        from research_assistant_mcp.server import save_content_hashes, load_content_hashes

        topic_path = Path(temp_db_path) / "test_topic"
        topic_path.mkdir(parents=True, exist_ok=True)

        # Test saving hashes
        test_hashes = {"hash1", "hash2", "hash3"}
        save_content_hashes(topic_path, test_hashes)

        # Test loading hashes
        loaded_hashes = load_content_hashes(topic_path)
        assert loaded_hashes == test_hashes

    def test_load_content_hashes_nonexistent_file(self, temp_db_path):
        """Test loading hashes when file doesn't exist."""
        from research_assistant_mcp.server import load_content_hashes

        topic_path = Path(temp_db_path) / "nonexistent_topic"
        loaded_hashes = load_content_hashes(topic_path)

        # Should return empty set when file doesn't exist
        assert loaded_hashes == set()


class TestVectorstore:
    """Test vectorstore functionality."""

    @patch('research_assistant_mcp.server.Chroma')
    @patch('research_assistant_mcp.server.embeddings')
    def test_get_vectorstore(self, mock_embeddings, mock_chroma, mock_env_vars, temp_db_path, monkeypatch):
        """Test getting or creating a vectorstore."""
        # Need to reload the module with mocked environment
        import importlib
        import research_assistant_mcp.server as server_module

        # Set environment before importing
        monkeypatch.setenv("RESEARCH_DB_PATH", temp_db_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        # Reload module to pick up environment variables
        importlib.reload(server_module)

        # Mock Chroma to avoid actual DB operations
        mock_vectorstore = MagicMock()
        mock_chroma.return_value = mock_vectorstore

        topic = "Machine Learning"
        result = server_module.get_vectorstore(topic)

        # Should normalize topic name
        expected_topic = "machine_learning"

        # Verify Chroma was called with correct parameters
        mock_chroma.assert_called_once()
        call_kwargs = mock_chroma.call_args[1]

        assert expected_topic in call_kwargs['persist_directory']
        assert call_kwargs['collection_name'] == f"research_{expected_topic}"


class TestBasicFunctionality:
    """Test basic server functionality without actual API calls."""

    def test_module_imports(self):
        """Test that the module can be imported."""
        try:
            import research_assistant_mcp.server
            assert hasattr(research_assistant_mcp.server, 'mcp')
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")

    def test_constants_defined(self, mock_env_vars, monkeypatch):
        """Test that required constants are defined."""
        monkeypatch.setenv("RESEARCH_DB_PATH", mock_env_vars["RESEARCH_DB_PATH"])
        monkeypatch.setenv("OPENAI_API_KEY", mock_env_vars["OPENAI_API_KEY"])

        import importlib
        import research_assistant_mcp.server as server_module
        importlib.reload(server_module)

        assert hasattr(server_module, 'RESEARCH_DB_PATH')
        assert hasattr(server_module, 'CHROMA_DB_ROOT')
        assert hasattr(server_module, 'EMBED_MODEL')
        assert hasattr(server_module, 'API_URL')


class TestEnvironmentValidation:
    """Test environment variable validation."""

    def test_missing_research_db_path(self, monkeypatch):
        """Test that missing RESEARCH_DB_PATH raises error."""
        # Clear the environment variable
        monkeypatch.delenv("RESEARCH_DB_PATH", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        # Importing should raise ValueError
        with pytest.raises(ValueError, match="RESEARCH_DB_PATH environment variable is required"):
            import importlib
            import research_assistant_mcp.server as server_module
            importlib.reload(server_module)


class TestTopicNormalization:
    """Test topic name normalization."""

    @patch('research_assistant_mcp.server.Chroma')
    def test_topic_name_normalization(self, mock_chroma, mock_env_vars, monkeypatch):
        """Test that topic names are properly normalized."""
        monkeypatch.setenv("RESEARCH_DB_PATH", mock_env_vars["RESEARCH_DB_PATH"])
        monkeypatch.setenv("OPENAI_API_KEY", mock_env_vars["OPENAI_API_KEY"])

        import importlib
        import research_assistant_mcp.server as server_module
        importlib.reload(server_module)

        mock_chroma.return_value = MagicMock()

        # Test various topic names
        test_cases = [
            ("Machine Learning", "machine_learning"),
            ("  Deep Learning  ", "deep_learning"),
            ("NATURAL Language", "natural_language"),
        ]

        for input_topic, expected_normalized in test_cases:
            server_module.get_vectorstore(input_topic)
            call_kwargs = mock_chroma.call_args[1]
            assert expected_normalized in call_kwargs['persist_directory']
            assert call_kwargs['collection_name'] == f"research_{expected_normalized}"
            mock_chroma.reset_mock()


class TestIntegration:
    """Integration tests that require mocking external services."""

    @pytest.mark.asyncio
    @patch('research_assistant_mcp.server.OpenAIEmbeddings')
    @patch('research_assistant_mcp.server.Chroma')
    async def test_server_initialization(self, mock_chroma, mock_embeddings, mock_env_vars, monkeypatch):
        """Test that the server initializes correctly."""
        monkeypatch.setenv("RESEARCH_DB_PATH", mock_env_vars["RESEARCH_DB_PATH"])
        monkeypatch.setenv("OPENAI_API_KEY", mock_env_vars["OPENAI_API_KEY"])

        import importlib
        import research_assistant_mcp.server as server_module
        importlib.reload(server_module)

        # Verify MCP server is initialized
        assert server_module.mcp is not None
        assert server_module.mcp.name == "Research Assistant"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
