from langgraph.graph import END, StateGraph
from universal_mcp.types import ToolFormat

from universal_mcp.agentr import AgentrRegistry
from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.codeact0.prompts import build_tool_definitions
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.storm.sandbox import Sandbox

from .nodes import agent_node, cleanup_node, entry_node
from .state import StormState
from .tools import execute_python_code, load_functions, search_functions

DEVELOPER_PROMPT = """
You are {name}, a helpful assistant.

{instructions}
"""


class StormAgent(BaseAgent):
    """
    A simple agent that can be configured to do anything.
    """

    def __init__(
        self,
        name: str = "StormAgent",
        instructions: str = "",
        model="gemini:gemini-2.5-flash",
        registry: AgentrRegistry | None = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            instructions=instructions,
            model=model,
            **kwargs,
        )
        self.llm = load_chat_model(self.model)
        self.registry = registry
        if not self.registry:
            raise Exception("Registry is required")
        self.sandbox = Sandbox()

    search_functions = search_functions
    load_functions = load_functions
    execute_python_code = execute_python_code

    def _build_system_message(self):
        return DEVELOPER_PROMPT.format(name=self.name, instructions=self.instructions)

    async def _load_tools(self, tools: list[str]):
        """Load tools into the registry and return the tool definitions and context
        Args:
            tools: List of tool names to load
        Returns:
            tool_defs: List of tool definitions
            tool_context: Dictionary of tool context
        """
        await self.registry.load_tools(tools)
        exported_tools: list = await self.registry.export_tools(tools, ToolFormat.NATIVE)  # List of callabales
        tool_defs, tool_context = build_tool_definitions(exported_tools)
        self.sandbox.update_context(tool_context)
        return tool_defs, tool_context

    async def _build_graph(self) -> StateGraph:
        graph = StateGraph(StormState)

        agent_node_subgraph = agent_node(self)
        # Add nodes
        graph.add_node("entry", entry_node)
        graph.add_node("agent", agent_node_subgraph)
        graph.add_node("cleanup", cleanup_node)

        # Define graph flow
        graph.set_entry_point("entry")
        graph.add_edge("entry", "agent")
        graph.add_edge("agent", "cleanup")
        graph.add_edge("cleanup", END)

        return graph.compile(checkpointer=self.memory)
