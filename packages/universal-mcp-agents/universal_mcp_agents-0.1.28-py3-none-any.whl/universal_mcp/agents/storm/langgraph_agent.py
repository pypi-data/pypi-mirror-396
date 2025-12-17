from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.storm import StormAgent


async def agent():
    agent_obj = StormAgent(
        name="CodeAct Agent",
        instructions="Be very concise in your answers.",
        model="anthropic:claude-sonnet-4-5-20250929",
        registry=AgentrRegistry(),
    )
    return await agent_obj._build_graph()
