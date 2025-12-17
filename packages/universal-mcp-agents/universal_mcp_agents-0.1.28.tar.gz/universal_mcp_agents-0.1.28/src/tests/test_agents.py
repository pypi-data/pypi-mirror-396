from uuid import uuid4

import pytest
from langgraph.checkpoint.memory import MemorySaver

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents import get_agent
from universal_mcp.agents.utils import get_message_text


@pytest.mark.asyncio
async def test_simple_agent():
    """Tests the simple agent."""
    agent = get_agent("simple")(
        name="Test Simple",
        instructions="Test instructions",
        model="anthropic/claude-haiku-4-5",
    )
    result = await agent.invoke(user_input="What is the capital of France?")
    assert result is not None
    last_message = result["messages"][-1]
    last_message_text = get_message_text(last_message)
    assert "paris" in last_message_text.lower()


@pytest.mark.asyncio
async def test_codeact_single_turn():
    """Tests the codeact-repl agent."""
    agent = get_agent("codeact-repl")(
        name="Test Codeact Repl",
        instructions="Test instructions",
        model="anthropic/claude-haiku-4-5",
        registry=AgentrRegistry(),
    )
    result = await agent.invoke(user_input="What is 2+2?")
    assert result is not None
    last_message = result["messages"][-1]
    last_message_text = get_message_text(last_message)
    assert "4" in last_message_text.lower()


@pytest.mark.asyncio
async def test_codeact_multi_turn():
    """Tests the codeact-repl agent."""
    checkpoint_saver = MemorySaver()
    agent = get_agent("codeact-repl")(
        name="Test Codeact Repl",
        instructions="You are a helpful assistant",
        model="anthropic/claude-haiku-4-5",
        registry=AgentrRegistry(),
        memory=checkpoint_saver,
    )
    thread_id = str(uuid4())
    result = await agent.invoke(
        user_input="Generate a function to calculate fibonnaci number, and get 10th number in the sequence. Use fib(0) = 0 and fib(1) = 1 as the base cases. Set x = fib(10)",
        thread_id=thread_id,
    )
    assert result is not None
    last_message = result["messages"][-1]
    last_message_text = get_message_text(last_message)
    assert "55" in last_message_text.lower()
    turn2 = await agent.invoke(
        user_input="What is the x+5?",
        thread_id=thread_id,
    )
    assert turn2 is not None
    last_message2 = turn2["messages"][-1]
    last_message2_text = get_message_text(last_message2)
    assert "60" in last_message2_text.lower()
