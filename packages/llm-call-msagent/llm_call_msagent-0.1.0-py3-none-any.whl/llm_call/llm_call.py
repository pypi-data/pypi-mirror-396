import os
from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
import asyncio

load_dotenv()

# Create client once globally
_client = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
)

async def _ask_llm_async(prompt: str) -> str:
    response = await _client.client.chat.completions.create(
        model=_client.deployment_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def ask_llm(prompt: str) -> str:
    """Synchronous wrapper so user can call ask_llm(prompt) easily."""
    return asyncio.run(_ask_llm_async(prompt))
