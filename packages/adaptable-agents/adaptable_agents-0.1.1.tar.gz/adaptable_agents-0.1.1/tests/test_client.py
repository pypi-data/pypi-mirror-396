"""Comprehensive unit tests for the AdaptableAgent client."""

import pytest
import requests
from unittest.mock import Mock, patch, call
from dataclasses import dataclass

from adaptable_agents.client import AdaptableAgent, ContextConfig


class TestAdaptableAgentInitialization:
    """Test AdaptableAgent initialization with various parameters."""

    def test_valid_initialization_minimal(self):
        """Test initialization with minimal valid parameters."""
        agent = AdaptableAgent(api_key="test_key")

        assert agent.api_key == "test_key"
        assert agent.api_base_url == "http://localhost:8000"
        assert agent.memory_scope_path == "default"
        assert isinstance(agent.context_config, ContextConfig)
        assert agent.context_config.similarity_threshold == 0.8
        assert agent.context_config.max_items == 5
        assert agent._headers == {
            "Authorization": "Bearer test_key",
            "Content-Type": "application/json",
        }

    def test_valid_initialization_all_params(self):
        """Test initialization with all parameters specified."""
        context_config = ContextConfig(similarity_threshold=0.9, max_items=10)
        agent = AdaptableAgent(
            api_key="custom_key",
            api_base_url="https://api.example.com/",
            memory_scope_path="custom/scope",
            context_config=context_config,
        )

        assert agent.api_key == "custom_key"
        assert agent.api_base_url == "https://api.example.com"  # trailing slash removed
        assert agent.memory_scope_path == "custom/scope"
        assert agent.context_config == context_config

    def test_api_key_whitespace_stripped(self):
        """Test that API key whitespace is properly stripped."""
        agent = AdaptableAgent(api_key="  test_key  ")
        assert agent.api_key == "test_key"

    def test_empty_api_key_raises_error(self):
        """Test that empty API key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            AdaptableAgent(api_key="")

    def test_none_api_key_raises_error(self):
        """Test that None API key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            AdaptableAgent(api_key=None)

    def test_whitespace_only_api_key_raises_error(self):
        """Test that whitespace-only API key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            AdaptableAgent(api_key="   ")

    def test_url_trailing_slash_removed(self):
        """Test that trailing slashes are removed from base URL."""
        agent = AdaptableAgent(api_key="test", api_base_url="http://example.com/")
        assert agent.api_base_url == "http://example.com"

    def test_custom_context_config(self):
        """Test initialization with custom context configuration."""
        config = ContextConfig(similarity_threshold=0.7, max_items=3)
        agent = AdaptableAgent(api_key="test", context_config=config)
        assert agent.context_config.similarity_threshold == 0.7
        assert agent.context_config.max_items == 3


class TestGetContext:
    """Test context generation functionality."""

    @pytest.fixture
    def agent(self):
        """Create a test AdaptableAgent instance."""
        return AdaptableAgent(api_key="test_key")

    @patch("adaptable_agents.client.requests.post")
    def test_get_context_success(self, mock_post, agent):
        """Test successful context generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cheatsheet": "Generated context content"}
        mock_post.return_value = mock_response

        result = agent.get_context("test input")

        assert result == "Generated context content"
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/v1/dc/generate",
            headers={
                "Authorization": "Bearer test_key",
                "Content-Type": "application/json",
            },
            json={
                "memory_scope_path": "default",
                "input": "test input",
                "similarity_threshold": 0.8,
                "max_items": 5,
            },
            timeout=300,
        )

    @patch("adaptable_agents.client.requests.post")
    def test_get_context_with_custom_config(self, mock_post, agent):
        """Test context generation with custom configuration."""
        agent.context_config = ContextConfig(similarity_threshold=0.9, max_items=10)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cheatsheet": "Context with custom config"}
        mock_post.return_value = mock_response

        result = agent.get_context("test input")

        expected_payload = {
            "memory_scope_path": "default",
            "input": "test input",
            "similarity_threshold": 0.9,
            "max_items": 10,
        }
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/v1/dc/generate",
            headers=agent._headers,
            json=expected_payload,
            timeout=300,
        )

    @patch("adaptable_agents.client.requests.post")
    @patch("builtins.print")
    def test_get_context_401_authentication_error(self, mock_print, mock_post, agent):
        """Test handling of 401 authentication errors."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized access"
        mock_post.return_value = mock_response

        result = agent.get_context("test input")

        assert result is None
        mock_print.assert_called_once()
        print_call = mock_print.call_args[0][0]
        assert "API authentication failed (401)" in print_call
        assert (
            "test_key" in print_call
        )  # API key "test_key" is 8 chars, so no "..." suffix

    @patch("adaptable_agents.client.requests.post")
    @patch("builtins.print")
    def test_get_context_other_http_error(self, mock_print, mock_post, agent):
        """Test handling of non-401 HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response

        result = agent.get_context("test input")

        assert result is None
        mock_print.assert_called_once()
        print_call = mock_print.call_args[0][0]
        assert "Context generation failed with status 500" in print_call

    @patch("adaptable_agents.client.requests.post")
    @patch("builtins.print")
    def test_get_context_request_exception(self, mock_print, mock_post, agent):
        """Test handling of request exceptions."""
        mock_post.side_effect = requests.RequestException("Network error")

        result = agent.get_context("test input")

        assert result is None
        mock_print.assert_called_once()
        print_call = mock_print.call_args[0][0]
        assert "Error fetching context: Network error" in print_call

    @patch("adaptable_agents.client.requests.post")
    @patch("builtins.print")
    def test_get_context_value_error(self, mock_print, mock_post, agent):
        """Test handling of JSON decode errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        result = agent.get_context("test input")

        assert result is None
        mock_print.assert_called_once()
        print_call = mock_print.call_args[0][0]
        assert "Error fetching context: Invalid JSON" in print_call

    @patch("adaptable_agents.client.requests.post")
    def test_get_context_missing_cheatsheet(self, mock_post, agent):
        """Test handling when response doesn't contain cheatsheet."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"other_field": "value"}
        mock_post.return_value = mock_response

        result = agent.get_context("test input")

        assert result is None

    def test_get_context_api_key_preview_long_key(self, agent):
        """Test API key preview generation for long keys."""
        agent.api_key = "very_long_api_key_for_testing"
        with patch("adaptable_agents.client.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response

            with patch("builtins.print") as mock_print:
                agent.get_context("test")
                print_call = mock_print.call_args[0][0]
                assert "very_lon..." in print_call

    def test_get_context_api_key_preview_short_key(self, agent):
        """Test API key preview generation for short keys."""
        agent.api_key = "short"
        with patch("adaptable_agents.client.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response

            with patch("builtins.print") as mock_print:
                agent.get_context("test")
                print_call = mock_print.call_args[0][0]
                assert "short" in print_call


class TestCachedContext:
    """Test cached context functionality."""

    @pytest.fixture
    def agent(self):
        """Create a test AdaptableAgent instance."""
        return AdaptableAgent(api_key="test_key", memory_scope_path="test/scope")

    @patch("adaptable_agents.client.requests.get")
    @patch("adaptable_agents.client.requests.post")
    def test_get_context_with_cache_hit(self, mock_post, mock_get, agent):
        """Test context retrieval when cache hit occurs."""
        # Mock successful cached context
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "found": True,
            "cheatsheet": "Cached context content",
        }
        mock_get.return_value = mock_get_response

        result = agent.get_context("test input", use_cache=True)

        assert result == "Cached context content"
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/v1/dc/test/scope",
            headers=agent._headers,
            timeout=10,
        )
        # Should not make POST request when cache hit
        mock_post.assert_not_called()

    @patch("adaptable_agents.client.requests.get")
    @patch("adaptable_agents.client.requests.post")
    def test_get_context_with_cache_miss(self, mock_post, mock_get, agent):
        """Test context retrieval when cache miss occurs."""
        # Mock cache miss
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"found": False}
        mock_get.return_value = mock_get_response

        # Mock successful context generation
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"cheatsheet": "Generated context"}
        mock_post.return_value = mock_post_response

        result = agent.get_context("test input", use_cache=True)

        assert result == "Generated context"
        mock_get.assert_called_once()
        mock_post.assert_called_once()

    @patch("adaptable_agents.client.requests.get")
    @patch("adaptable_agents.client.requests.post")
    def test_get_context_cache_error_fallback(self, mock_post, mock_get, agent):
        """Test fallback to generation when cache retrieval fails."""
        # Mock cache request failure
        mock_get.side_effect = requests.RequestException("Cache error")

        # Mock successful context generation
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"cheatsheet": "Generated context"}
        mock_post.return_value = mock_post_response

        result = agent.get_context("test input", use_cache=True)

        assert result == "Generated context"
        mock_get.assert_called_once()
        mock_post.assert_called_once()

    @patch("adaptable_agents.client.requests.get")
    def test_cached_context_not_found(self, mock_get, agent):
        """Test cached context retrieval when not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"found": False}
        mock_get.return_value = mock_response

        result = agent._get_cached_context()

        assert result is None

    @patch("adaptable_agents.client.requests.get")
    def test_cached_context_404_error(self, mock_get, agent):
        """Test cached context retrieval with 404 error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = agent._get_cached_context()

        assert result is None

    @patch("adaptable_agents.client.requests.get")
    def test_cached_context_request_exception(self, mock_get, agent):
        """Test cached context retrieval with request exception."""
        mock_get.side_effect = requests.RequestException("Network error")

        result = agent._get_cached_context()

        assert result is None

    @patch("adaptable_agents.client.requests.get")
    def test_cached_context_json_error(self, mock_get, agent):
        """Test cached context retrieval with JSON decode error."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = agent._get_cached_context()

        assert result is None


class TestStoreMemory:
    """Test memory storage functionality."""

    @pytest.fixture
    def agent(self):
        """Create a test AdaptableAgent instance."""
        return AdaptableAgent(api_key="test_key", memory_scope_path="test/scope")

    @patch("adaptable_agents.client.requests.post")
    def test_store_memory_success(self, mock_post, agent):
        """Test successful memory storage."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"memory_id": "mem_123", "status": "created"}
        mock_post.return_value = mock_response

        result = agent.store_memory("input text", "output text")

        assert result == {"memory_id": "mem_123", "status": "created"}
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/v1/memories",
            headers=agent._headers,
            json={
                "memory_scope_path": "test/scope",
                "input": "input text",
                "output": "output text",
            },
            timeout=10,
        )

    @patch("adaptable_agents.client.requests.post")
    def test_store_memory_with_summarize_input_true(self, mock_post, agent):
        """Test memory storage with summarize_input=True."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"memory_id": "mem_456"}
        mock_post.return_value = mock_response

        result = agent.store_memory("input", "output", summarize_input=True)

        assert result == {"memory_id": "mem_456"}
        expected_payload = {
            "memory_scope_path": "test/scope",
            "input": "input",
            "output": "output",
            "summarize_input": True,
        }
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/v1/memories",
            headers=agent._headers,
            json=expected_payload,
            timeout=10,
        )

    @patch("adaptable_agents.client.requests.post")
    def test_store_memory_with_summarize_input_false(self, mock_post, agent):
        """Test memory storage with summarize_input=False."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"memory_id": "mem_789"}
        mock_post.return_value = mock_response

        result = agent.store_memory("input", "output", summarize_input=False)

        expected_payload = {
            "memory_scope_path": "test/scope",
            "input": "input",
            "output": "output",
            "summarize_input": False,
        }
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/v1/memories",
            headers=agent._headers,
            json=expected_payload,
            timeout=10,
        )

    @patch("adaptable_agents.client.requests.post")
    @patch("builtins.print")
    def test_store_memory_401_error(self, mock_print, mock_post, agent):
        """Test memory storage with 401 authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized access"
        mock_post.return_value = mock_response

        result = agent.store_memory("input", "output")

        assert result is None
        mock_print.assert_called_once()
        print_call = mock_print.call_args[0][0]
        assert "API authentication failed (401) when storing memory" in print_call

    @patch("adaptable_agents.client.requests.post")
    @patch("builtins.print")
    def test_store_memory_other_http_error(self, mock_print, mock_post, agent):
        """Test memory storage with non-401 HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.text = "Validation error"
        mock_post.return_value = mock_response

        result = agent.store_memory("input", "output")

        assert result is None
        mock_print.assert_called_once()
        print_call = mock_print.call_args[0][0]
        assert "Memory storage failed with status 422" in print_call

    @patch("adaptable_agents.client.requests.post")
    @patch("builtins.print")
    def test_store_memory_request_exception(self, mock_print, mock_post, agent):
        """Test memory storage with request exception."""
        mock_post.side_effect = requests.RequestException("Connection timeout")

        result = agent.store_memory("input", "output")

        assert result is None
        mock_print.assert_called_once()
        print_call = mock_print.call_args[0][0]
        assert "Error storing memory: Connection timeout" in print_call

    @patch("adaptable_agents.client.requests.post")
    @patch("builtins.print")
    def test_store_memory_json_error(self, mock_print, mock_post, agent):
        """Test memory storage with JSON decode error."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.side_effect = ValueError("Invalid JSON response")
        mock_post.return_value = mock_response

        result = agent.store_memory("input", "output")

        assert result is None
        mock_print.assert_called_once()
        print_call = mock_print.call_args[0][0]
        assert "Error storing memory: Invalid JSON response" in print_call


class TestFormatPromptWithContext:
    """Test prompt formatting functionality."""

    @pytest.fixture
    def agent(self):
        """Create a test AdaptableAgent instance."""
        return AdaptableAgent(api_key="test_key")

    def test_format_prompt_with_context(self, agent):
        """Test formatting prompt with context."""
        user_prompt = "How do I fix this error?"
        context = "Error handling best practices:\n- Always use try/catch\n- Log errors properly"

        result = agent.format_prompt_with_context(user_prompt, context)

        expected = """Here's relevant context from past experiences that might help:

Error handling best practices:
- Always use try/catch
- Log errors properly

---

User Query: How do I fix this error?"""

        assert result == expected

    def test_format_prompt_with_empty_context(self, agent):
        """Test formatting prompt with empty context."""
        user_prompt = "How do I fix this error?"

        result = agent.format_prompt_with_context(user_prompt, "")

        assert result == user_prompt

    def test_format_prompt_with_none_context(self, agent):
        """Test formatting prompt with None context."""
        user_prompt = "How do I fix this error?"

        result = agent.format_prompt_with_context(user_prompt, None)

        assert result == user_prompt

    def test_format_prompt_with_whitespace_context(self, agent):
        """Test formatting prompt with whitespace-only context."""
        user_prompt = "Test prompt"
        context = "   \n\t   "

        result = agent.format_prompt_with_context(user_prompt, context)

        # Context with only whitespace is still considered "truthy"
        expected = f"""Here's relevant context from past experiences that might help:

{context}

---

User Query: {user_prompt}"""

        assert result == expected

    def test_format_prompt_multiline_context(self, agent):
        """Test formatting prompt with multiline context."""
        user_prompt = "How to optimize database queries?"
        context = """Database optimization tips:
1. Use indexes on frequently queried columns
2. Avoid N+1 queries
3. Use connection pooling
4. Monitor query execution plans"""

        result = agent.format_prompt_with_context(user_prompt, context)

        expected = f"""Here's relevant context from past experiences that might help:

{context}

---

User Query: {user_prompt}"""

        assert result == expected

    def test_format_prompt_special_characters(self, agent):
        """Test formatting prompt with special characters in context."""
        user_prompt = "How to handle special chars?"
        context = "Use escape sequences: \\n, \\t, \\r, \", ', \\"

        result = agent.format_prompt_with_context(user_prompt, context)

        assert "Use escape sequences: \\n, \\t, \\r, \", ', \\" in result
        assert "User Query: How to handle special chars?" in result


class TestErrorHandlingAndSilentFailures:
    """Test comprehensive error handling and silent failure behavior."""

    @pytest.fixture
    def agent(self):
        """Create a test AdaptableAgent instance."""
        return AdaptableAgent(api_key="test_key")

    @patch("builtins.print")
    def test_silent_failure_behavior_get_context(self, mock_print, agent):
        """Test that get_context fails silently with appropriate logging."""
        with patch("adaptable_agents.client.requests.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("Failed to connect")

            result = agent.get_context("test input")

            assert result is None
            mock_print.assert_called_once()
            assert "Error fetching context" in mock_print.call_args[0][0]

    @patch("builtins.print")
    def test_silent_failure_behavior_store_memory(self, mock_print, agent):
        """Test that store_memory fails silently with appropriate logging."""
        with patch("adaptable_agents.client.requests.post") as mock_post:
            mock_post.side_effect = requests.Timeout("Request timeout")

            result = agent.store_memory("input", "output")

            assert result is None
            mock_print.assert_called_once()
            assert "Error storing memory" in mock_print.call_args[0][0]

    def test_no_exception_propagation_get_context(self, agent):
        """Test that handled exceptions in get_context don't propagate."""
        with patch("adaptable_agents.client.requests.post") as mock_post:
            mock_post.side_effect = requests.RequestException("Request error")

            # Should not raise an exception
            with patch("builtins.print"):
                result = agent.get_context("test")
                assert result is None

    def test_no_exception_propagation_store_memory(self, agent):
        """Test that handled exceptions in store_memory don't propagate."""
        with patch("adaptable_agents.client.requests.post") as mock_post:
            mock_post.side_effect = requests.RequestException("Request error")

            # Should not raise an exception
            with patch("builtins.print"):
                result = agent.store_memory("input", "output")
                assert result is None

    def test_no_exception_propagation_cached_context(self, agent):
        """Test that handled exceptions in _get_cached_context don't propagate."""
        with patch("adaptable_agents.client.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Request error")

            # Should not raise an exception
            result = agent._get_cached_context()
            assert result is None

    @patch("builtins.print")
    def test_comprehensive_error_scenarios(self, mock_print, agent):
        """Test various error scenarios comprehensively."""
        # Only test exceptions that are actually caught by the code
        error_scenarios = [
            requests.ConnectionError("Connection failed"),
            requests.Timeout("Request timeout"),
            requests.HTTPError("HTTP error"),
            requests.RequestException("Generic request error"),
            ValueError("JSON decode error"),
        ]

        for error in error_scenarios:
            mock_print.reset_mock()
            with patch("adaptable_agents.client.requests.post") as mock_post:
                mock_post.side_effect = error

                # Test get_context
                result = agent.get_context("test")
                assert result is None
                mock_print.assert_called()

                # Test store_memory
                mock_print.reset_mock()
                result = agent.store_memory("input", "output")
                assert result is None
                mock_print.assert_called()


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""

    @pytest.fixture
    def agent(self):
        """Create a test AdaptableAgent instance with custom config."""
        config = ContextConfig(similarity_threshold=0.85, max_items=7)
        return AdaptableAgent(
            api_key="integration_test_key",
            api_base_url="https://custom-api.example.com",
            memory_scope_path="integration/test/scope",
            context_config=config,
        )

    @patch("adaptable_agents.client.requests.get")
    @patch("adaptable_agents.client.requests.post")
    def test_full_workflow_cache_miss_then_store(self, mock_post, mock_get, agent):
        """Test full workflow: cache miss, generate context, store memory."""
        # Mock cache miss
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"found": False}
        mock_get.return_value = mock_get_response

        # Mock successful context generation
        mock_post_response_1 = Mock()
        mock_post_response_1.status_code = 200
        mock_post_response_1.json.return_value = {"cheatsheet": "Generated context"}

        # Mock successful memory storage
        mock_post_response_2 = Mock()
        mock_post_response_2.status_code = 201
        mock_post_response_2.json.return_value = {"memory_id": "mem_123"}

        mock_post.side_effect = [mock_post_response_1, mock_post_response_2]

        # Test the full workflow
        input_text = "How to implement caching?"
        output_text = "Use Redis for distributed caching..."

        # Get context (should miss cache and generate)
        context = agent.get_context(input_text, use_cache=True)
        assert context == "Generated context"

        # Format prompt with context
        formatted_prompt = agent.format_prompt_with_context(input_text, context)
        assert "Generated context" in formatted_prompt
        assert input_text in formatted_prompt

        # Store memory
        memory_result = agent.store_memory(input_text, output_text)
        assert memory_result == {"memory_id": "mem_123"}

        # Verify all calls were made correctly
        mock_get.assert_called_once()
        assert mock_post.call_count == 2

    def test_context_config_applied_correctly(self, agent):
        """Test that custom context configuration is applied correctly."""
        with patch("adaptable_agents.client.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"cheatsheet": "Custom config context"}
            mock_post.return_value = mock_response

            agent.get_context("test input")

            # Verify custom config values were used
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["similarity_threshold"] == 0.85
            assert payload["max_items"] == 7

    def test_custom_api_base_url_used(self, agent):
        """Test that custom API base URL is used correctly."""
        with patch("adaptable_agents.client.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"cheatsheet": "Context"}
            mock_post.return_value = mock_response

            agent.get_context("test")

            # Verify custom URL was used
            call_args = mock_post.call_args
            url = call_args[0][0]
            assert url == "https://custom-api.example.com/api/v1/dc/generate"
