"""Anthropic client wrapper with Adaptable Agents integration."""

from typing import Optional, Dict, Any, List, Union
from anthropic import Anthropic
from .client import AdaptableAgent, ContextConfig


class AdaptableAnthropicClient:
    """
    Anthropic client wrapper that automatically fetches and appends context.

    This class wraps the Anthropic client and automatically:
    - Fetches relevant context before each API call
    - Appends context to user prompts
    - Optionally stores input/output pairs as memories
    - Proxies all other methods directly to the underlying Anthropic client

    Example:
        >>> from adaptable_agents import AdaptableAnthropicClient
        >>>
        >>> client = AdaptableAnthropicClient(
        ...     adaptable_api_key="your-adaptable-api-key",
        ...     anthropic_api_key="your-anthropic-api-key",
        ...     memory_scope_path="customer-support/billing"
        ... )
        >>>
        >>> # Output-generating methods are intercepted
        >>> response = client.messages.create(
        ...     model="claude-3-opus-20240229",
        ...     max_tokens=1024,
        ...     messages=[{"role": "user", "content": "Help me with billing"}]
        ... )
        >>>
        >>> # All other methods are proxied directly
        >>> models = client.models.list()
    """

    def __init__(
        self,
        adaptable_api_key: str,
        anthropic_api_key: Optional[str] = None,
        api_base_url: str = "http://localhost:8000",
        memory_scope_path: str = "default",
        context_config: Optional[ContextConfig] = None,
        auto_store_memories: bool = True,
        anthropic_client: Optional[Anthropic] = None,
        summarize_input: Optional[bool] = None,
        enable_adaptable_agents: bool = True,
    ):
        """
        Initialize the Adaptable Anthropic client.

        Args:
            adaptable_api_key: API key for the Adaptable Agents API
            anthropic_api_key: Anthropic API key (optional if anthropic_client is provided)
            api_base_url: Base URL of the Adaptable Agents API
            memory_scope_path: Memory scope path for organizing memories
            context_config: Configuration for context generation
            auto_store_memories: Whether to automatically store memories after generation
            anthropic_client: Pre-initialized Anthropic client (optional)
            summarize_input: Whether to summarize inputs before storage. If None, uses default configuration.
            enable_adaptable_agents: If True, intercepts calls to fetch context and store memories.
                                   If False, passes calls directly through to the underlying Anthropic client.
        """
        self.enable_adaptable_agents = enable_adaptable_agents
        if enable_adaptable_agents:
            self.adaptable_agent = AdaptableAgent(
                api_key=adaptable_api_key,
                api_base_url=api_base_url,
                memory_scope_path=memory_scope_path,
                context_config=context_config,
            )
        else:
            self.adaptable_agent = None
        self.auto_store_memories = auto_store_memories
        self.anthropic_client = anthropic_client or Anthropic(api_key=anthropic_api_key)
        self.summarize_input = summarize_input

        # Create a messages wrapper
        self.messages = MessagesWrapper(self)

    def __getattr__(self, name: str):
        """
        Proxy all other attributes and methods to the underlying Anthropic client.

        This allows users to call any method on the Anthropic client directly,
        except for messages.create which is intercepted.
        """
        return getattr(self.anthropic_client, name)

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


class MessagesWrapper:
    """Wrapper for Anthropic messages API."""

    def __init__(self, parent: AdaptableAnthropicClient):
        self.parent = parent

    def create(
        self,
        model: str,
        messages: Union[List[Dict[str, str]], Any],
        max_tokens: int,
        **kwargs,
    ) -> Any:
        """
        Create a message completion with automatic context integration.

        Args:
            model: The model to use (e.g., "claude-3-opus-20240229")
            messages: List of message dictionaries or Anthropic message objects
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional arguments to pass to Anthropic API

        Returns:
            Anthropic Message object
        """
        # If adaptable agents is disabled, pass through directly
        if not self.parent.enable_adaptable_agents:
            return self.parent.anthropic_client.messages.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
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

        # Call Anthropic API
        response = self.parent.anthropic_client.messages.create(
            model=model,
            messages=messages_list,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Store memory if enabled
        if user_input:
            output_text = response.content[0].text if response.content else ""
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
            # Try to convert Anthropic message objects to dicts
            normalized = []
            for msg in messages:
                if hasattr(msg, "role") and hasattr(msg, "content"):
                    normalized.append({"role": msg.role, "content": msg.content})
                elif isinstance(msg, dict):
                    normalized.append(msg)
            return normalized
        return messages
