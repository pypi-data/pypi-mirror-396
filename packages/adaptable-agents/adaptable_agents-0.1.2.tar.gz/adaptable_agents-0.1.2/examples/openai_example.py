"""Example usage of AdaptableOpenAIClient."""

from adaptable_agents import AdaptableOpenAIClient, ContextConfig

# Initialize the client
client = AdaptableOpenAIClient(
    adaptable_api_key="your-adaptable-agents-api-key",
    openai_api_key="your-openai-api-key",
    memory_scope_path="customer-support/billing",
    api_base_url="http://localhost:8000",
    auto_store_memories=True,  # Automatically store memories after each call
)

# Use it just like the regular OpenAI client
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "User asked about billing issues with subscription renewal",
        }
    ],
)

print("Response:", response.choices[0].message.content)

# Example with custom context config
config = ContextConfig(similarity_threshold=0.9, max_items=3)

client_with_config = AdaptableOpenAIClient(
    adaptable_api_key="your-adaptable-agents-api-key",
    openai_api_key="your-openai-api-key",
    memory_scope_path="engineering/frontend",
    context_config=config,
)

response2 = client_with_config.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "How do I implement OAuth2?"}],
)

print("Response 2:", response2.choices[0].message.content)
