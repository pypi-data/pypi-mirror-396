import asyncio

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ClearToolUsesEdit,
    ContextEditingMiddleware,
    ModelFallbackMiddleware,
    SummarizationMiddleware,
)
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware
from langchain_core.tools import StructuredTool
from loguru import logger

from universal_mcp.agents.llm import load_chat_model


async def get_my_city():
    """
    Get current city
    """
    logger.info("Checking city")
    return "bangalore"


async def weather(city: str):
    """
    Get weather of a city in degrees celcius
    """
    logger.info("Sleeping")
    await asyncio.sleep(2)
    logger.info("woke up")
    return 20


def agent_node(self):
    """
    The main ReAct loop where tool calling and primary task execution will happen.
    """
    middlewares = [
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
    ]
    tools = [
        StructuredTool.from_function(coroutine=self.search_functions),
        StructuredTool.from_function(coroutine=self.load_functions),
        StructuredTool.from_function(coroutine=self.execute_python_code),
    ]
    agent = create_agent(
        model=self.llm,
        tools=tools,
        system_prompt=self._build_system_message(),
        middleware=middlewares,
        debug=True,
    )
    return agent
