"""OpenAI client wrapper with Adaptable Agents integration."""

from typing import Optional, Dict, Any, List, Union
from openai import OpenAI
from .client import AdaptableAgent, ContextConfig


class AdaptableOpenAIClient:
    """
    OpenAI client wrapper that automatically fetches and appends context.

    This class wraps the OpenAI client and automatically:
    - Fetches relevant context before each API call
    - Appends context to user prompts
    - Optionally stores input/output pairs as memories
    - Proxies all other methods directly to the underlying OpenAI client

    Example:
        >>> from adaptable_agents import AdaptableOpenAIClient
        >>>
        >>> client = AdaptableOpenAIClient(
        ...     adaptable_api_key="your-adaptable-api-key",
        ...     openai_api_key="your-openai-api-key",
        ...     memory_scope_path="customer-support/billing"
        ... )
        >>>
        >>> # Output-generating methods are intercepted
        >>> response = client.chat.completions.create(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "Help me with billing"}]
        ... )
        >>>
        >>> # All other methods are proxied directly
        >>> models = client.models.list()
        >>> files = client.files.list()
    """

    def __init__(
        self,
        adaptable_api_key: str,
        openai_api_key: Optional[str] = None,
        api_base_url: str = "http://localhost:8000",
        memory_scope_path: str = "default",
        context_config: Optional[ContextConfig] = None,
        auto_store_memories: bool = True,
        openai_client: Optional[OpenAI] = None,
        summarize_input: Optional[bool] = None,
    ):
        """
        Initialize the Adaptable OpenAI client.

        Args:
            adaptable_api_key: API key for the Adaptable Agents API
            openai_api_key: OpenAI API key (optional if openai_client is provided)
            api_base_url: Base URL of the Adaptable Agents API
            memory_scope_path: Memory scope path for organizing memories
            context_config: Configuration for context generation
            auto_store_memories: Whether to automatically store memories after generation
            openai_client: Pre-initialized OpenAI client (optional)
            summarize_input: Whether to summarize inputs before storage. If None, uses default configuration.

        Note:
            Use the `enable_adaptable_agents` property to control whether calls are intercepted
            to fetch context and store memories (True, default) or passed directly through
            to the underlying OpenAI client (False).
        """
        # Store configuration for potential lazy initialization
        self._adaptable_api_key = adaptable_api_key
        self._api_base_url = api_base_url
        self._memory_scope_path = memory_scope_path
        self._context_config = context_config

        # Initialize with adaptable agents enabled by default
        self._enable_adaptable_agents = True
        self.adaptable_agent = AdaptableAgent(
            api_key=adaptable_api_key,
            api_base_url=api_base_url,
            memory_scope_path=memory_scope_path,
            context_config=context_config,
        )

        self.auto_store_memories = auto_store_memories
        self.openai_client = openai_client or OpenAI(api_key=openai_api_key)
        self.summarize_input = summarize_input

        # Create a chat completions wrapper
        self.chat = ChatCompletionsWrapper(self)

    def __getattr__(self, name: str):
        """
        Proxy all other attributes and methods to the underlying OpenAI client.

        This allows users to call any method on the OpenAI client directly,
        except for chat.completions.create which is intercepted.
        """
        return getattr(self.openai_client, name)

    @property
    def enable_adaptable_agents(self) -> bool:
        """
        Whether to enable adaptable agents functionality.

        When True (default), intercepts calls to fetch context and store memories.
        When False, passes calls directly through to the underlying OpenAI client.

        Returns:
            bool: Current state of adaptable agents enablement
        """
        return self._enable_adaptable_agents

    @enable_adaptable_agents.setter
    def enable_adaptable_agents(self, value: bool) -> None:
        """
        Enable or disable adaptable agents functionality.

        Args:
            value: True to enable adaptable agents, False to disable
        """
        self._enable_adaptable_agents = value

        if value and self.adaptable_agent is None:
            # Lazy initialization when enabling
            self.adaptable_agent = AdaptableAgent(
                api_key=self._adaptable_api_key,
                api_base_url=self._api_base_url,
                memory_scope_path=self._memory_scope_path,
                context_config=self._context_config,
            )
        elif not value:
            # Optionally set to None when disabling to free resources
            # (but keep the instance for potential re-enabling)
            pass

    def _extract_user_message(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Extract the user message from messages list."""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg.get("content")
        return None

    def _store_memory_if_enabled(self, user_input: str, output_text: str):
        """Store memory if auto_store_memories is enabled."""
        if self.auto_store_memories and self.adaptable_agent:
            try:
                self.adaptable_agent.store_memory(
                    input_text=user_input,
                    output_text=output_text,
                    summarize_input=self.summarize_input,
                )
            except Exception:
                # Silently continue if memory storage fails
                pass


class ChatCompletionsWrapper:
    """Wrapper for OpenAI chat completions API."""

    def __init__(self, parent: AdaptableOpenAIClient):
        self.parent = parent
        # Create a nested completions object for OpenAI API compatibility
        self.completions = self

    def create(
        self,
        model: str,
        messages: Union[List[Dict[str, str]], Any],
        **kwargs,
    ) -> Any:
        """
        Create a chat completion with automatic context integration.

        Args:
            model: The model to use (e.g., "gpt-4", "gpt-3.5-turbo")
            messages: List of message dictionaries or OpenAI message objects
            **kwargs: Additional arguments to pass to OpenAI API

        Returns:
            OpenAI ChatCompletion object
        """
        # If adaptable agents is disabled, pass through directly
        if not self.parent.enable_adaptable_agents:
            return self.parent.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs,
            )

        # Convert messages to dict format if needed
        messages_list = self._normalize_messages(messages)

        # Extract user input
        user_input = self.parent._extract_user_message(messages_list)

        # Get context
        context = None
        if user_input:
            try:
                context = self.parent.adaptable_agent.get_context(user_input)
            except Exception:
                # Silently continue if context generation fails
                context = None

        # Modify the last user message to include context
        if context and user_input:
            try:
                enhanced_prompt = (
                    self.parent.adaptable_agent.format_prompt_with_context(
                        user_input, context
                    )
                )
                # Update the last user message
                for msg in reversed(messages_list):
                    if msg.get("role") == "user":
                        msg["content"] = enhanced_prompt
                        break
            except Exception:
                # Silently continue if prompt enhancement fails
                pass

        # Call OpenAI API
        response = self.parent.openai_client.chat.completions.create(
            model=model,
            messages=messages_list,
            **kwargs,
        )

        # Store memory if enabled
        if user_input:
            output_text = response.choices[0].message.content or ""
            self.parent._store_memory_if_enabled(user_input, output_text)

        return response

    def _normalize_messages(
        self, messages: Union[List[Dict[str, str]], Any]
    ) -> List[Dict[str, str]]:
        """Normalize messages to dict format."""
        if isinstance(messages, list):
            # Check if it's already dict format
            if messages and isinstance(messages[0], dict):
                return messages
            # Try to convert OpenAI message objects to dicts
            normalized = []
            for msg in messages:
                if hasattr(msg, "role") and hasattr(msg, "content"):
                    normalized.append({"role": msg.role, "content": msg.content})
                elif isinstance(msg, dict):
                    normalized.append(msg)
            return normalized
        return messages
