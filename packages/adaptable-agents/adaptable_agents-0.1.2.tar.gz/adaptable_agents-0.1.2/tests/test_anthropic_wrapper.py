"""Comprehensive unit tests for the AdaptableAnthropicClient wrapper."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, List, Any

from adaptable_agents.anthropic_wrapper import AdaptableAnthropicClient, MessagesWrapper
from adaptable_agents.client import AdaptableAgent, ContextConfig


class MockAnthropicMessage:
    """Mock Anthropic message object for testing."""

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class MockAnthropicResponse:
    """Mock Anthropic response for testing."""

    def __init__(self, content: str):
        self.content = [Mock()]
        self.content[0].text = content


class TestAdaptableAnthropicClientInitialization:
    """Test AdaptableAnthropicClient initialization with various parameters."""

    def test_initialization_with_api_keys_enabled(self):
        """Test initialization with API keys and adaptable agents enabled."""
        with patch(
            "adaptable_agents.anthropic_wrapper.Anthropic"
        ) as mock_anthropic, patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            mock_anthropic_instance = Mock()
            mock_anthropic.return_value = mock_anthropic_instance

            mock_agent_instance = Mock()
            mock_agent.return_value = mock_agent_instance

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-adaptable-key",
                anthropic_api_key="test-anthropic-key",
                enable_adaptable_agents=True,
            )

            assert client.enable_adaptable_agents is True
            assert client.adaptable_agent == mock_agent_instance
            assert client.anthropic_client == mock_anthropic_instance
            assert client.auto_store_memories is True
            assert client.summarize_input is None
            assert isinstance(client.messages, MessagesWrapper)

            # Verify AdaptableAgent was initialized correctly
            mock_agent.assert_called_once_with(
                api_key="test-adaptable-key",
                api_base_url="http://localhost:8000",
                memory_scope_path="default",
                context_config=None,
            )

            # Verify Anthropic client was initialized
            mock_anthropic.assert_called_once_with(api_key="test-anthropic-key")

    def test_initialization_with_pre_initialized_anthropic_client(self):
        """Test initialization with pre-initialized Anthropic client."""
        with patch("adaptable_agents.anthropic_wrapper.AdaptableAgent") as mock_agent:
            pre_initialized_client = Mock()
            mock_agent_instance = Mock()
            mock_agent.return_value = mock_agent_instance

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                anthropic_client=pre_initialized_client,
                enable_adaptable_agents=True,
            )

            assert client.anthropic_client == pre_initialized_client
            assert client.adaptable_agent == mock_agent_instance

    def test_initialization_with_disabled_adaptable_agents(self):
        """Test initialization with adaptable agents disabled."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic") as mock_anthropic:
            mock_anthropic_instance = Mock()
            mock_anthropic.return_value = mock_anthropic_instance

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                anthropic_api_key="test-anthropic-key",
                enable_adaptable_agents=False,
            )

            assert client.enable_adaptable_agents is False
            assert client.adaptable_agent is None
            assert client.anthropic_client == mock_anthropic_instance

    def test_initialization_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        with patch(
            "adaptable_agents.anthropic_wrapper.Anthropic"
        ) as mock_anthropic, patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            custom_config = ContextConfig(similarity_threshold=0.9, max_items=10)

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                anthropic_api_key="test-anthropic-key",
                api_base_url="https://custom-api.com",
                memory_scope_path="custom/path",
                context_config=custom_config,
                auto_store_memories=False,
                summarize_input=True,
                enable_adaptable_agents=True,
            )

            assert client.auto_store_memories is False
            assert client.summarize_input is True

            mock_agent.assert_called_once_with(
                api_key="test-key",
                api_base_url="https://custom-api.com",
                memory_scope_path="custom/path",
                context_config=custom_config,
            )

    def test_initialization_missing_anthropic_key_without_client(self):
        """Test initialization without Anthropic key or client."""
        with patch(
            "adaptable_agents.anthropic_wrapper.Anthropic"
        ) as mock_anthropic, patch("adaptable_agents.anthropic_wrapper.AdaptableAgent"):

            mock_anthropic.return_value = Mock()

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=True
            )

            # Should still create Anthropic client with None key
            mock_anthropic.assert_called_once_with(api_key=None)


class TestEnableAdaptableAgentsFlag:
    """Test the enable_adaptable_agents flag functionality."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock Anthropic client."""
        client = Mock()
        client.messages = Mock()
        client.messages.create = Mock()
        return client

    @pytest.fixture
    def mock_adaptable_agent(self):
        """Create a mock AdaptableAgent."""
        agent = Mock()
        agent.get_context = Mock(return_value="test context")
        agent.format_prompt_with_context = Mock(return_value="enhanced prompt")
        agent.store_memory = Mock()
        return agent

    def test_enabled_flag_true_creates_adaptable_agent(self):
        """Test that enabled flag creates AdaptableAgent instance."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic"), patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=True
            )

            assert client.enable_adaptable_agents is True
            mock_agent.assert_called_once()
            assert client.adaptable_agent is not None

    def test_enabled_flag_false_skips_adaptable_agent(self):
        """Test that disabled flag skips AdaptableAgent creation."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic"), patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=False
            )

            assert client.enable_adaptable_agents is False
            mock_agent.assert_not_called()
            assert client.adaptable_agent is None


class TestMessagesWrapper:
    """Test MessagesWrapper behavior."""

    @pytest.fixture
    def mock_parent_enabled(self):
        """Create a mock parent with adaptable agents enabled."""
        parent = Mock()
        parent.enable_adaptable_agents = True
        parent.adaptable_agent = Mock()
        parent.anthropic_client = Mock()
        parent._extract_user_message = Mock(return_value="user message")
        parent._store_memory_if_enabled = Mock()
        return parent

    @pytest.fixture
    def mock_parent_disabled(self):
        """Create a mock parent with adaptable agents disabled."""
        parent = Mock()
        parent.enable_adaptable_agents = False
        parent.anthropic_client = Mock()
        return parent

    def test_wrapper_initialization(self):
        """Test MessagesWrapper initialization."""
        parent = Mock()
        wrapper = MessagesWrapper(parent)

        assert wrapper.parent == parent

    def test_create_with_adaptable_agents_disabled_passes_through(
        self, mock_parent_disabled
    ):
        """Test that create passes through when adaptable agents disabled."""
        wrapper = MessagesWrapper(mock_parent_disabled)
        mock_response = MockAnthropicResponse("test response")
        mock_parent_disabled.anthropic_client.messages.create.return_value = (
            mock_response
        )

        messages = [{"role": "user", "content": "test message"}]
        result = wrapper.create(
            model="claude-3-opus-20240229",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )

        assert result == mock_response
        mock_parent_disabled.anthropic_client.messages.create.assert_called_once_with(
            model="claude-3-opus-20240229",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )

    def test_create_with_adaptable_agents_enabled_enhances_prompt(
        self, mock_parent_enabled
    ):
        """Test that create enhances prompt when adaptable agents enabled."""
        wrapper = MessagesWrapper(mock_parent_enabled)
        mock_response = MockAnthropicResponse("enhanced response")

        # Setup mocks
        mock_parent_enabled.adaptable_agent.get_context.return_value = "context"
        mock_parent_enabled.adaptable_agent.format_prompt_with_context.return_value = (
            "enhanced prompt"
        )
        mock_parent_enabled.anthropic_client.messages.create.return_value = (
            mock_response
        )

        messages = [{"role": "user", "content": "original message"}]
        result = wrapper.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Verify context was fetched
        mock_parent_enabled.adaptable_agent.get_context.assert_called_once_with(
            "user message"
        )

        # Verify prompt was enhanced
        mock_parent_enabled.adaptable_agent.format_prompt_with_context.assert_called_once_with(
            "user message", "context"
        )

        # Verify memory was stored
        mock_parent_enabled._store_memory_if_enabled.assert_called_once_with(
            "user message", "enhanced response"
        )

        assert result == mock_response

    def test_create_with_no_user_message_skips_enhancement(self, mock_parent_enabled):
        """Test that create skips enhancement when no user message found."""
        wrapper = MessagesWrapper(mock_parent_enabled)
        mock_response = MockAnthropicResponse("response")

        mock_parent_enabled._extract_user_message.return_value = None
        mock_parent_enabled.anthropic_client.messages.create.return_value = (
            mock_response
        )

        messages = [{"role": "system", "content": "system message"}]
        result = wrapper.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Should not fetch context or store memory
        mock_parent_enabled.adaptable_agent.get_context.assert_not_called()
        mock_parent_enabled._store_memory_if_enabled.assert_not_called()

        assert result == mock_response

    def test_create_with_no_context_skips_enhancement(self, mock_parent_enabled):
        """Test that create skips enhancement when no context returned."""
        wrapper = MessagesWrapper(mock_parent_enabled)
        mock_response = MockAnthropicResponse("response")

        mock_parent_enabled.adaptable_agent.get_context.return_value = None
        mock_parent_enabled.anthropic_client.messages.create.return_value = (
            mock_response
        )

        messages = [{"role": "user", "content": "test message"}]
        result = wrapper.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Should fetch context but not enhance prompt
        mock_parent_enabled.adaptable_agent.get_context.assert_called_once()
        mock_parent_enabled.adaptable_agent.format_prompt_with_context.assert_not_called()

        # Should still store memory
        mock_parent_enabled._store_memory_if_enabled.assert_called_once_with(
            "user message", "response"
        )

        assert result == mock_response

    def test_create_requires_max_tokens_parameter(self, mock_parent_enabled):
        """Test that max_tokens parameter is properly handled (required for Anthropic)."""
        wrapper = MessagesWrapper(mock_parent_enabled)
        mock_response = MockAnthropicResponse("response")

        mock_parent_enabled.adaptable_agent.get_context.return_value = None
        mock_parent_enabled.anthropic_client.messages.create.return_value = (
            mock_response
        )

        messages = [{"role": "user", "content": "test message"}]

        # Test with max_tokens
        result = wrapper.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Verify max_tokens was passed to Anthropic API
        call_args = mock_parent_enabled.anthropic_client.messages.create.call_args
        assert call_args[1]["max_tokens"] == 1024
        assert result == mock_response


class TestContextIntegrationAndPromptEnhancement:
    """Test context integration and prompt enhancement."""

    @pytest.fixture
    def client_with_mocks(self):
        """Create client with mocked dependencies."""
        with patch(
            "adaptable_agents.anthropic_wrapper.Anthropic"
        ) as mock_anthropic, patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            mock_anthropic_instance = Mock()
            mock_anthropic.return_value = mock_anthropic_instance

            mock_agent_instance = Mock()
            mock_agent.return_value = mock_agent_instance

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=True
            )

            return client, mock_anthropic_instance, mock_agent_instance

    def test_context_fetched_and_prompt_enhanced(self, client_with_mocks):
        """Test that context is fetched and prompt is enhanced."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Setup mocks
        mock_response = MockAnthropicResponse("test response")
        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = "relevant context"
        mock_agent.format_prompt_with_context.return_value = (
            "enhanced: original message"
        )

        messages = [{"role": "user", "content": "original message"}]

        result = client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Verify context was fetched
        mock_agent.get_context.assert_called_once_with("original message")

        # Verify prompt was enhanced
        mock_agent.format_prompt_with_context.assert_called_once_with(
            "original message", "relevant context"
        )

        # Verify enhanced message was sent to Anthropic
        call_args = mock_anthropic.messages.create.call_args
        sent_messages = call_args[1]["messages"]
        assert sent_messages[0]["content"] == "enhanced: original message"

    def test_message_content_updated_in_place(self, client_with_mocks):
        """Test that message content is updated in place."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Setup mocks
        mock_response = MockAnthropicResponse("test response")
        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = "context"
        mock_agent.format_prompt_with_context.return_value = "enhanced prompt"

        messages = [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "user question"},
        ]

        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Verify the last user message was enhanced
        call_args = mock_anthropic.messages.create.call_args
        sent_messages = call_args[1]["messages"]
        assert sent_messages[0]["content"] == "system prompt"  # unchanged
        assert sent_messages[1]["content"] == "enhanced prompt"  # enhanced

    def test_multiple_user_messages_last_one_enhanced(self, client_with_mocks):
        """Test that only the last user message is enhanced."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Setup mocks
        mock_response = MockAnthropicResponse("test response")
        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = "context"
        mock_agent.format_prompt_with_context.return_value = "enhanced: last message"

        messages = [
            {"role": "user", "content": "first user message"},
            {"role": "assistant", "content": "assistant response"},
            {"role": "user", "content": "last message"},
        ]

        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Verify only the last user message was enhanced
        call_args = mock_anthropic.messages.create.call_args
        sent_messages = call_args[1]["messages"]
        assert sent_messages[0]["content"] == "first user message"  # unchanged
        assert sent_messages[1]["content"] == "assistant response"  # unchanged
        assert sent_messages[2]["content"] == "enhanced: last message"  # enhanced


class TestMemoryStorageAfterCompletions:
    """Test memory storage after completions."""

    @pytest.fixture
    def client_with_auto_store(self):
        """Create client with auto store memories enabled."""
        with patch(
            "adaptable_agents.anthropic_wrapper.Anthropic"
        ) as mock_anthropic, patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                auto_store_memories=True,
                enable_adaptable_agents=True,
            )

            return client, mock_anthropic.return_value, mock_agent.return_value

    @pytest.fixture
    def client_no_auto_store(self):
        """Create client with auto store memories disabled."""
        with patch(
            "adaptable_agents.anthropic_wrapper.Anthropic"
        ) as mock_anthropic, patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                auto_store_memories=False,
                enable_adaptable_agents=True,
            )

            return client, mock_anthropic.return_value, mock_agent.return_value

    def test_memory_stored_when_auto_store_enabled(self, client_with_auto_store):
        """Test that memory is stored when auto_store_memories is True."""
        client, mock_anthropic, mock_agent = client_with_auto_store

        mock_response = MockAnthropicResponse("assistant response")
        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = None  # No context to simplify test

        messages = [{"role": "user", "content": "user input"}]

        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Verify memory was stored
        mock_agent.store_memory.assert_called_once_with(
            input_text="user input",
            output_text="assistant response",
            summarize_input=None,
        )

    def test_memory_not_stored_when_auto_store_disabled(self, client_no_auto_store):
        """Test that memory is not stored when auto_store_memories is False."""
        client, mock_anthropic, mock_agent = client_no_auto_store

        mock_response = MockAnthropicResponse("assistant response")
        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = None

        messages = [{"role": "user", "content": "user input"}]

        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Verify memory was not stored
        mock_agent.store_memory.assert_not_called()

    def test_memory_stored_with_summarize_input_parameter(self, client_with_auto_store):
        """Test memory storage with summarize_input parameter."""
        client, mock_anthropic, mock_agent = client_with_auto_store
        client.summarize_input = True

        mock_response = MockAnthropicResponse("response")
        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = None

        messages = [{"role": "user", "content": "input"}]

        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        mock_agent.store_memory.assert_called_once_with(
            input_text="input", output_text="response", summarize_input=True
        )

    def test_memory_not_stored_when_adaptable_agent_disabled(self):
        """Test that memory is not stored when adaptable agent is disabled."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic") as mock_anthropic:
            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=False
            )

            mock_response = MockAnthropicResponse("response")
            mock_anthropic.return_value.messages.create.return_value = mock_response

            messages = [{"role": "user", "content": "input"}]

            # Should not raise any errors even though there's no adaptable agent
            result = client.messages.create(
                model="claude-3-opus-20240229", messages=messages, max_tokens=1024
            )
            assert result == mock_response

    def test_memory_not_stored_when_no_user_input(self, client_with_auto_store):
        """Test that memory is not stored when no user input is found."""
        client, mock_anthropic, mock_agent = client_with_auto_store

        mock_response = MockAnthropicResponse("response")
        mock_anthropic.messages.create.return_value = mock_response

        messages = [{"role": "system", "content": "system message"}]

        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # No user input means no memory storage
        mock_agent.store_memory.assert_not_called()

    def test_anthropic_response_format_content_access(self, client_with_auto_store):
        """Test that Anthropic's response format (response.content[0].text) is properly handled."""
        client, mock_anthropic, mock_agent = client_with_auto_store

        # Create a proper Anthropic response mock
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "assistant response text"

        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = None

        messages = [{"role": "user", "content": "user input"}]

        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Verify memory was stored with the correct text from Anthropic response format
        mock_agent.store_memory.assert_called_once_with(
            input_text="user input",
            output_text="assistant response text",
            summarize_input=None,
        )

    def test_anthropic_response_format_empty_content(self, client_with_auto_store):
        """Test handling of empty content in Anthropic response format."""
        client, mock_anthropic, mock_agent = client_with_auto_store

        # Create response with empty content
        mock_response = Mock()
        mock_response.content = []

        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = None

        messages = [{"role": "user", "content": "user input"}]

        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Verify memory was stored with empty string
        mock_agent.store_memory.assert_called_once_with(
            input_text="user input", output_text="", summarize_input=None
        )


class TestMessageNormalization:
    """Test message normalization (dict format vs Anthropic objects)."""

    def test_normalize_dict_messages(self):
        """Test normalization of dict format messages."""
        parent = Mock()
        wrapper = MessagesWrapper(parent)

        messages = [
            {"role": "user", "content": "test message"},
            {"role": "assistant", "content": "test response"},
        ]

        result = wrapper._normalize_messages(messages)

        assert result == messages
        assert isinstance(result, list)
        assert all(isinstance(msg, dict) for msg in result)

    def test_normalize_anthropic_message_objects(self):
        """Test normalization of Anthropic message objects."""
        parent = Mock()
        wrapper = MessagesWrapper(parent)

        messages = [
            MockAnthropicMessage("user", "test message"),
            MockAnthropicMessage("assistant", "test response"),
        ]

        result = wrapper._normalize_messages(messages)

        expected = [
            {"role": "user", "content": "test message"},
            {"role": "assistant", "content": "test response"},
        ]
        assert result == expected

    def test_normalize_mixed_format_messages(self):
        """Test normalization of mixed format messages."""
        parent = Mock()
        wrapper = MessagesWrapper(parent)

        # When first message is dict, the method returns the original list
        messages = [
            {"role": "system", "content": "system message"},
            MockAnthropicMessage("user", "user message"),
            {"role": "assistant", "content": "assistant response"},
        ]

        result = wrapper._normalize_messages(messages)

        # Should return original list since first message is dict
        assert result == messages

        # Test when first message is Anthropic object
        messages_anthropic_first = [
            MockAnthropicMessage("system", "system message"),
            {"role": "user", "content": "user message"},
            MockAnthropicMessage("assistant", "assistant response"),
        ]

        result = wrapper._normalize_messages(messages_anthropic_first)

        expected = [
            {"role": "system", "content": "system message"},
            {"role": "user", "content": "user message"},
            {"role": "assistant", "content": "assistant response"},
        ]
        assert result == expected

    def test_normalize_non_list_messages(self):
        """Test normalization of non-list messages."""
        parent = Mock()
        wrapper = MessagesWrapper(parent)

        messages = "not a list"

        result = wrapper._normalize_messages(messages)

        assert result == messages

    def test_normalize_empty_list(self):
        """Test normalization of empty list."""
        parent = Mock()
        wrapper = MessagesWrapper(parent)

        messages = []

        result = wrapper._normalize_messages(messages)

        assert result == []

    def test_normalize_objects_without_role_content(self):
        """Test normalization of objects without role/content attributes."""
        parent = Mock()
        wrapper = MessagesWrapper(parent)

        # Create mock object without role/content
        invalid_obj = Mock(spec=[])  # No attributes
        messages = [invalid_obj]

        result = wrapper._normalize_messages(messages)

        assert result == []  # Should filter out invalid objects


class TestUserMessageExtraction:
    """Test user message extraction from message lists."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic"), patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ):
            return AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=True
            )

    def test_extract_user_message_single_user_message(self, client):
        """Test extracting user message from single user message."""
        messages = [{"role": "user", "content": "test message"}]

        result = client._extract_user_message(messages)

        assert result == "test message"

    def test_extract_user_message_multiple_user_messages(self, client):
        """Test extracting user message returns the last one."""
        messages = [
            {"role": "user", "content": "first message"},
            {"role": "assistant", "content": "assistant response"},
            {"role": "user", "content": "last message"},
        ]

        result = client._extract_user_message(messages)

        assert result == "last message"

    def test_extract_user_message_no_user_messages(self, client):
        """Test extracting user message when none exist."""
        messages = [
            {"role": "system", "content": "system message"},
            {"role": "assistant", "content": "assistant response"},
        ]

        result = client._extract_user_message(messages)

        assert result is None

    def test_extract_user_message_empty_list(self, client):
        """Test extracting user message from empty list."""
        messages = []

        result = client._extract_user_message(messages)

        assert result is None

    def test_extract_user_message_with_none_content(self, client):
        """Test extracting user message with None content."""
        messages = [{"role": "user", "content": None}]

        result = client._extract_user_message(messages)

        assert result is None

    def test_extract_user_message_with_empty_content(self, client):
        """Test extracting user message with empty content."""
        messages = [{"role": "user", "content": ""}]

        result = client._extract_user_message(messages)

        assert result == ""

    def test_extract_user_message_missing_content_key(self, client):
        """Test extracting user message missing content key."""
        messages = [{"role": "user"}]

        result = client._extract_user_message(messages)

        assert result is None

    def test_extract_user_message_missing_role_key(self, client):
        """Test extracting user message missing role key."""
        messages = [{"content": "test message"}]

        result = client._extract_user_message(messages)

        assert result is None


class TestProxyFunctionality:
    """Test proxy functionality (__getattr__)."""

    @pytest.fixture
    def client_with_mock_anthropic(self):
        """Create client with mock Anthropic client."""
        with patch("adaptable_agents.anthropic_wrapper.AdaptableAgent"):
            mock_anthropic = Mock()

            # Add some methods to mock Anthropic client
            mock_anthropic.models = Mock()
            mock_anthropic.models.list = Mock(return_value="models_list_result")
            mock_anthropic.count_tokens = Mock(return_value="count_tokens_result")
            mock_anthropic.beta = Mock()
            mock_anthropic.beta.tools = Mock()
            mock_anthropic.beta.tools.messages = Mock()

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                anthropic_client=mock_anthropic,
                enable_adaptable_agents=True,
            )

            return client, mock_anthropic

    def test_proxy_models_list(self, client_with_mock_anthropic):
        """Test proxying models.list() method."""
        client, mock_anthropic = client_with_mock_anthropic

        result = client.models.list()

        assert result == "models_list_result"
        mock_anthropic.models.list.assert_called_once()

    def test_proxy_count_tokens(self, client_with_mock_anthropic):
        """Test proxying count_tokens() method."""
        client, mock_anthropic = client_with_mock_anthropic

        result = client.count_tokens(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": "test"}],
        )

        assert result == "count_tokens_result"
        mock_anthropic.count_tokens.assert_called_once_with(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": "test"}],
        )

    def test_proxy_beta_tools_access(self, client_with_mock_anthropic):
        """Test proxying beta.tools access."""
        client, mock_anthropic = client_with_mock_anthropic

        result = client.beta.tools.messages

        assert result == mock_anthropic.beta.tools.messages

    def test_proxy_attribute_access(self, client_with_mock_anthropic):
        """Test proxying attribute access."""
        client, mock_anthropic = client_with_mock_anthropic
        mock_anthropic.some_attribute = "test_value"

        result = client.some_attribute

        assert result == "test_value"

    def test_proxy_messages_attribute_not_proxied(self, client_with_mock_anthropic):
        """Test that messages attribute is not proxied (uses wrapper instead)."""
        client, mock_anthropic = client_with_mock_anthropic
        mock_anthropic.messages = Mock()

        # Should return the wrapper, not the proxied messages
        assert isinstance(client.messages, MessagesWrapper)
        assert client.messages is not mock_anthropic.messages

    def test_proxy_nonexistent_attribute_raises_error(self, client_with_mock_anthropic):
        """Test that accessing nonexistent attribute raises AttributeError."""
        client, mock_anthropic = client_with_mock_anthropic

        # Create a simple object that will raise AttributeError for nonexistent attributes
        class SimpleObject:
            pass

        simple_obj = SimpleObject()
        client.anthropic_client = simple_obj

        with pytest.raises(AttributeError):
            _ = client.nonexistent_attribute


class TestErrorHandlingAndSilentFailures:
    """Test error handling and silent failures."""

    @pytest.fixture
    def client_with_mocks(self):
        """Create client with mocked dependencies."""
        with patch(
            "adaptable_agents.anthropic_wrapper.Anthropic"
        ) as mock_anthropic, patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=True
            )

            return client, mock_anthropic.return_value, mock_agent.return_value

    def test_get_context_error_handled_silently(self, client_with_mocks):
        """Test that get_context errors are handled silently."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Mock get_context to raise an exception
        mock_agent.get_context.side_effect = Exception("Context error")
        mock_response = MockAnthropicResponse("response")
        mock_anthropic.messages.create.return_value = mock_response

        messages = [{"role": "user", "content": "test message"}]

        # Should not raise an exception
        result = client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        assert result == mock_response
        # Should still try to store memory
        mock_agent.store_memory.assert_called_once()

    def test_store_memory_error_handled_silently(self, client_with_mocks):
        """Test that store_memory errors are handled silently."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Mock store_memory to raise an exception
        mock_agent.store_memory.side_effect = Exception("Memory error")
        mock_response = MockAnthropicResponse("response")
        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = None

        messages = [{"role": "user", "content": "test message"}]

        # Should not raise an exception
        result = client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        assert result == mock_response

    def test_format_prompt_error_handled_silently(self, client_with_mocks):
        """Test that format_prompt_with_context errors are handled silently."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Mock format_prompt_with_context to raise an exception
        mock_agent.get_context.return_value = "context"
        mock_agent.format_prompt_with_context.side_effect = Exception("Format error")
        mock_response = MockAnthropicResponse("response")
        mock_anthropic.messages.create.return_value = mock_response

        messages = [{"role": "user", "content": "test message"}]

        # Should not raise an exception
        result = client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        assert result == mock_response

    def test_anthropic_api_error_propagated(self, client_with_mocks):
        """Test that Anthropic API errors are propagated."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Mock Anthropic to raise an exception
        mock_anthropic.messages.create.side_effect = Exception("Anthropic API error")
        mock_agent.get_context.return_value = None

        messages = [{"role": "user", "content": "test message"}]

        # Should raise the Anthropic exception
        with pytest.raises(Exception, match="Anthropic API error"):
            client.messages.create(
                model="claude-3-opus-20240229", messages=messages, max_tokens=1024
            )


class TestEnabledAndDisabledModes:
    """Test both enabled and disabled adaptable agents modes."""

    def test_disabled_mode_complete_passthrough(self):
        """Test that disabled mode provides complete passthrough."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic") as mock_anthropic:
            mock_anthropic_instance = Mock()
            mock_anthropic.return_value = mock_anthropic_instance
            mock_response = MockAnthropicResponse("direct response")
            mock_anthropic_instance.messages.create.return_value = mock_response

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=False
            )

            messages = [{"role": "user", "content": "test message"}]
            kwargs = {"temperature": 0.7, "max_tokens": 1024}

            result = client.messages.create(
                model="claude-3-opus-20240229", messages=messages, **kwargs
            )

            assert result == mock_response
            mock_anthropic_instance.messages.create.assert_called_once_with(
                model="claude-3-opus-20240229", messages=messages, **kwargs
            )

    def test_enabled_mode_with_enhancements(self):
        """Test that enabled mode applies all enhancements."""
        with patch(
            "adaptable_agents.anthropic_wrapper.Anthropic"
        ) as mock_anthropic, patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            mock_anthropic_instance = Mock()
            mock_anthropic.return_value = mock_anthropic_instance
            mock_agent_instance = Mock()
            mock_agent.return_value = mock_agent_instance

            mock_response = MockAnthropicResponse("enhanced response")
            mock_anthropic_instance.messages.create.return_value = mock_response
            mock_agent_instance.get_context.return_value = "context"
            mock_agent_instance.format_prompt_with_context.return_value = (
                "enhanced prompt"
            )

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=True
            )

            messages = [{"role": "user", "content": "original message"}]

            result = client.messages.create(
                model="claude-3-opus-20240229", messages=messages, max_tokens=1024
            )

            # Verify all enhancements were applied
            mock_agent_instance.get_context.assert_called_once_with("original message")
            mock_agent_instance.format_prompt_with_context.assert_called_once()
            mock_agent_instance.store_memory.assert_called_once()

            # Verify enhanced message was sent
            call_args = mock_anthropic_instance.messages.create.call_args
            sent_messages = call_args[1]["messages"]
            assert sent_messages[0]["content"] == "enhanced prompt"

            assert result == mock_response

    def test_mode_switching_behavior(self):
        """Test behavior when switching between modes."""
        with patch(
            "adaptable_agents.anthropic_wrapper.Anthropic"
        ) as mock_anthropic, patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            mock_anthropic_instance = Mock()
            mock_anthropic.return_value = mock_anthropic_instance

            # Test disabled first
            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=False
            )

            assert client.enable_adaptable_agents is False
            assert client.adaptable_agent is None
            mock_agent.assert_not_called()

            # Test enabled
            client_enabled = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=True
            )

            assert client_enabled.enable_adaptable_agents is True
            assert client_enabled.adaptable_agent is not None
            mock_agent.assert_called_once()


class TestStoreMemoryIfEnabled:
    """Test the _store_memory_if_enabled method."""

    def test_store_memory_when_enabled_and_agent_exists(self):
        """Test storing memory when auto_store_memories is True and agent exists."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic"), patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            mock_agent_instance = Mock()
            mock_agent.return_value = mock_agent_instance

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                auto_store_memories=True,
                enable_adaptable_agents=True,
            )

            client._store_memory_if_enabled("input", "output")

            mock_agent_instance.store_memory.assert_called_once_with(
                input_text="input", output_text="output", summarize_input=None
            )

    def test_store_memory_when_disabled(self):
        """Test not storing memory when auto_store_memories is False."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic"), patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            mock_agent_instance = Mock()
            mock_agent.return_value = mock_agent_instance

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                auto_store_memories=False,
                enable_adaptable_agents=True,
            )

            client._store_memory_if_enabled("input", "output")

            mock_agent_instance.store_memory.assert_not_called()

    def test_store_memory_when_no_agent(self):
        """Test not storing memory when adaptable agent doesn't exist."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic"):
            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                auto_store_memories=True,
                enable_adaptable_agents=False,
            )

            # Should not raise an exception even though agent is None
            client._store_memory_if_enabled("input", "output")

    def test_store_memory_with_summarize_input(self):
        """Test storing memory with summarize_input parameter."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic"), patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            mock_agent_instance = Mock()
            mock_agent.return_value = mock_agent_instance

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                auto_store_memories=True,
                summarize_input=True,
                enable_adaptable_agents=True,
            )

            client._store_memory_if_enabled("input", "output")

            mock_agent_instance.store_memory.assert_called_once_with(
                input_text="input", output_text="output", summarize_input=True
            )

    def test_store_memory_error_handled_silently(self):
        """Test that store_memory errors are handled silently."""
        with patch("adaptable_agents.anthropic_wrapper.Anthropic"), patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            mock_agent_instance = Mock()
            mock_agent_instance.store_memory.side_effect = Exception("Memory error")
            mock_agent.return_value = mock_agent_instance

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key",
                auto_store_memories=True,
                enable_adaptable_agents=True,
            )

            # Should not raise an exception
            client._store_memory_if_enabled("input", "output")

            # Verify the method was called but exception was caught
            mock_agent_instance.store_memory.assert_called_once()


class TestAnthropicSpecificResponseFormat:
    """Test Anthropic-specific response format handling."""

    @pytest.fixture
    def client_with_mocks(self):
        """Create client with mocked dependencies."""
        with patch(
            "adaptable_agents.anthropic_wrapper.Anthropic"
        ) as mock_anthropic, patch(
            "adaptable_agents.anthropic_wrapper.AdaptableAgent"
        ) as mock_agent:

            client = AdaptableAnthropicClient(
                adaptable_api_key="test-key", enable_adaptable_agents=True
            )

            return client, mock_anthropic.return_value, mock_agent.return_value

    def test_anthropic_response_content_structure(self, client_with_mocks):
        """Test that response.content[0].text is properly accessed."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Create proper Anthropic response structure
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "This is the Anthropic response text"

        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = None

        messages = [{"role": "user", "content": "test message"}]

        result = client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        assert result == mock_response
        # Verify memory was stored with the correct text from Anthropic format
        mock_agent.store_memory.assert_called_once_with(
            input_text="test message",
            output_text="This is the Anthropic response text",
            summarize_input=None,
        )

    def test_anthropic_response_multiple_content_blocks(self, client_with_mocks):
        """Test handling of multiple content blocks (takes first one)."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Create response with multiple content blocks
        mock_response = Mock()
        mock_response.content = [Mock(), Mock()]
        mock_response.content[0].text = "First content block"
        mock_response.content[1].text = "Second content block"

        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = None

        messages = [{"role": "user", "content": "test message"}]

        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Should use the first content block
        mock_agent.store_memory.assert_called_once_with(
            input_text="test message",
            output_text="First content block",
            summarize_input=None,
        )

    def test_anthropic_response_empty_content_list(self, client_with_mocks):
        """Test handling of empty content list."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Create response with empty content
        mock_response = Mock()
        mock_response.content = []

        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = None

        messages = [{"role": "user", "content": "test message"}]

        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Should use empty string when no content
        mock_agent.store_memory.assert_called_once_with(
            input_text="test message", output_text="", summarize_input=None
        )

    def test_anthropic_response_none_content(self, client_with_mocks):
        """Test handling of None content."""
        client, mock_anthropic, mock_agent = client_with_mocks

        # Create response with None content
        mock_response = Mock()
        mock_response.content = None

        mock_anthropic.messages.create.return_value = mock_response
        mock_agent.get_context.return_value = None

        messages = [{"role": "user", "content": "test message"}]

        # Should handle the AttributeError gracefully
        client.messages.create(
            model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        )

        # Should use empty string when content is None
        mock_agent.store_memory.assert_called_once_with(
            input_text="test message", output_text="", summarize_input=None
        )
