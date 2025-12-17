import asyncio
from typing import Annotated

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ClearToolUsesEdit,
    ContextEditingMiddleware,
    ModelFallbackMiddleware,
    SummarizationMiddleware,
)
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.message import add_messages
from rich import print
from typing_extensions import TypedDict

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.utils import messages_to_list

DEVELOPER_PROMPT = """
You are {name}, an helpful assistant who can answer simple questions.

Adhere to the following instructions strictly:
{instructions}
"""


class State(TypedDict):
    messages: Annotated[list, add_messages]


class SimpleAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            instructions=instructions,
            model=model,
            memory=memory,
            **kwargs,
        )
        self.llm = load_chat_model(model)

    def _build_system_message(self):
        return DEVELOPER_PROMPT.format(name=self.name, instructions=self.instructions)

    async def _build_graph(self):
        agent = create_agent(
            model=self.llm,
            tools=[],
            system_prompt=self._build_system_message(),
            checkpointer=self.memory,
            middleware=[
                AnthropicPromptCachingMiddleware(ttl="5m", unsupported_model_behavior="ignore"),
                ModelFallbackMiddleware(
                    load_chat_model("gemini:gemini-2.5-flash-lite"),
                    load_chat_model("anthropic:claude-haiku-4-5"),
                    load_chat_model("azure:gpt-5-mini"),
                ),
                SummarizationMiddleware(
                    model=load_chat_model("gemini:gemini-2.5-flash"),
                    max_tokens_before_summary=20_000,
                    messages_to_keep=20,
                ),
                ContextEditingMiddleware(
                    edits=[
                        ClearToolUsesEdit(trigger=50_000),  # Clear old tool uses
                    ],
                ),
            ],
        )
        return agent


async def main():
    agent = SimpleAgent(
        name="Simple Agent",
        instructions="Act as a 14 year old kid, reply in Gen-Z lingo",
        model="azure:gpt-5-mini",
    )
    output = await agent.invoke("What is the capital of France?")
    print(messages_to_list(output["messages"]))


if __name__ == "__main__":
    asyncio.run(main())
