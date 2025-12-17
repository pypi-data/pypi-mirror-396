import asyncio

from langgraph.checkpoint.memory import MemorySaver

from universal_mcp.agentr import AgentrRegistry
from universal_mcp.agents.storm.agent import StormAgent


async def main():
    """Entry point for the agent."""
    memory = MemorySaver()
    registry = AgentrRegistry()
    agent = StormAgent(memory=memory, registry=registry)
    await agent.load_functions(["google_calendar__list_events"])
    # await agent.invoke("Write function to get n'th fibonnaci number. get 21st number", thread_id=1)

    # # Check state
    # state = await agent.get_state(thread_id=1)
    # print(state)


if __name__ == "__main__":
    asyncio.run(main())
