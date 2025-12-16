"""Example usage of AdaptableAnthropicClient."""

from adaptable_agents import AdaptableAnthropicClient

# Initialize the client
client = AdaptableAnthropicClient(
    adaptable_api_key="your-adaptable-agents-api-key",
    anthropic_api_key="your-anthropic-api-key",
    memory_scope_path="customer-support/billing",
    api_base_url="http://localhost:8000",
    auto_store_memories=True,
)

# Use it just like the regular Anthropic client
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "User asked about billing issues with subscription renewal",
        }
    ],
)

print("Response:", response.content[0].text)
