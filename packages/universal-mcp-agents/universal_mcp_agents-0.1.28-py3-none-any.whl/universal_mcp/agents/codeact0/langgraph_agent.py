from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.codeact0 import CodeActPlaybookAgent


async def agent():
    agent_obj = CodeActPlaybookAgent(
        name="CodeAct Agent",
        instructions="Be very concise in your answers.",
        model="anthropic:claude-sonnet-4-5-20250929",
        tools=[],
        registry=AgentrRegistry(),
    )
    return await agent_obj._build_graph()
