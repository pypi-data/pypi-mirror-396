import copy
import json
import re
from typing import Literal, cast

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, ToolMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.types import Command, RetryPolicy, StreamWriter
from loguru import logger
from universal_mcp.types import ToolFormat

from universal_mcp.agentr import AgentrRegistry
from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.codeact0.llm_tool import smart_print
from universal_mcp.agents.codeact0.nodes.planner import build_or_patch_code, create_or_update_plan
from universal_mcp.agents.codeact0.prompts import (
    build_tool_definitions,
    create_default_prompt,
)
from universal_mcp.agents.codeact0.sandbox import (
    Sandbox,
    execute_python_code,
)
from universal_mcp.agents.codeact0.state_transient import (
    CodeActState,
)
from universal_mcp.agents.codeact0.tools import (
    create_agent_builder_tools,
    create_meta_tools,
)
from universal_mcp.agents.codeact0.utils import (
    build_anthropic_cache_message,
    detect_pending_tool,
    get_connected_apps_string,
)
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.utils import filter_retry_on


class CodeActPlaybookAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver | None = None,
        registry: AgentrRegistry | None = None,
        agent_builder_registry: object | None = None,
        sandbox_timeout: int = 20,
        **kwargs,
    ):
        super().__init__(
            name=name,
            instructions=instructions,
            model=model,
            memory=memory,
            **kwargs,
        )
        self.model_instance = load_chat_model(model, thinking=False)
        self.agent_builder_model_instance = load_chat_model(
            "anthropic:claude-sonnet-4-5-20250929", thinking=False, disable_streaming=True, tags=("quiet",)
        )
        self.registry = registry
        self.agent_builder_registry = agent_builder_registry
        self.agent = agent_builder_registry.get_agent() if agent_builder_registry else None

        self.tools_config = self.agent.tools if self.agent else {}
        self.sandbox_timeout = sandbox_timeout
        self.final_instructions = ""
        self.sandbox = Sandbox()
        self.meta_tools = create_meta_tools(self.registry)

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
        # Ideally we should add the context to sandbox directly, but we don't have a way to do that yet.
        return tool_defs, tool_context

    async def _load_default_tools(self):
        logger.info("Loading default tools")
        all_tools = []
        # Sandbox specific tools
        all_tools.append(smart_print)
        # Load llm tools
        llm_tools_list = ["llm__generate_text", "llm__classify_data", "llm__extract_data", "llm__call_llm"]
        exported_llm_tools: list = await self.registry.export_tools(llm_tools_list, ToolFormat.NATIVE)
        all_tools.extend(exported_llm_tools)
        # Load web search
        web_search = self.meta_tools.get("web_search")
        all_tools.append(web_search)
        # Load filesystem tools
        all_tools.append(self.meta_tools["read_file"])
        all_tools.append(self.meta_tools["save_file"])
        all_tools.append(self.meta_tools["upload_file"])
        # Playbook specific tools
        if self.tools_config:
            playbook_tools: list = await self.registry.export_tools(self.tools_config)
            all_tools.extend(playbook_tools)

        # Build and export
        tool_defs, tool_context = build_tool_definitions(all_tools)
        return tool_defs, tool_context

    async def _build_graph(self):  # noqa: PLR0915
        """Build the graph for the CodeAct Playbook Agent."""

        agent_builder_tools = create_agent_builder_tools()

        async def call_model(state: CodeActState) -> Command[Literal["execute_tools"]]:
            """This node now only ever binds the four meta-tools to the LLM."""
            last_code_output = state.get("last_code_output", None)
            messages = build_anthropic_cache_message(self.final_instructions) + state["messages"]
            agent_facing_tools = [
                execute_python_code,
                agent_builder_tools["plan_agent"],
                agent_builder_tools["code_and_save_agent"],
                self.meta_tools["search_functions"],
                self.meta_tools["load_functions"],
            ]

            if isinstance(self.model_instance, ChatAnthropic):
                model_with_tools = self.model_instance.bind_tools(
                    tools=agent_facing_tools,
                    tool_choice="auto",
                    cache_control={"type": "ephemeral", "ttl": "5m"},
                )
                if isinstance(messages[-1], ToolMessage):
                    last = copy.deepcopy(messages[-1])
                    last.additional_kwargs["cache_control"] = {"type": "ephemeral", "ttl": "5m"}
                    messages[-1] = last
                elif isinstance(messages[-1].content, str):
                    last = copy.deepcopy(messages[-1])
                    last.content = [{"type": "text", "text": messages[-1].content}]
                    last.content[-1]["cache_control"] = {"type": "ephemeral", "ttl": "5m"}
                    messages[-1] = last
                else:
                    last = copy.deepcopy(messages[-1])
                    last.content[-1]["cache_control"] = {"type": "ephemeral", "ttl": "5m"}
                    messages[-1] = last
            else:
                model_with_tools = self.model_instance.bind_tools(
                    tools=agent_facing_tools,
                    tool_choice="auto",
                )
            if last_code_output:
                code_message = HumanMessage(content=last_code_output)
                messages.append(code_message)

            response = cast(AIMessage, await model_with_tools.with_retry().ainvoke(messages))
            if response.tool_calls:
                return Command(goto="execute_tools", update={"messages": [response]})
            else:
                return Command(update={"messages": [response], "model_with_tools": model_with_tools})

        async def execute_tools(state: CodeActState, writer: StreamWriter) -> Command[Literal["call_model"]]:
            """Execute tool calls"""
            last_message = state["messages"][-1]
            tool_calls = last_message.tool_calls if isinstance(last_message, AIMessage) else []

            tool_messages = []
            new_tool_ids = []
            tool_result = ""
            ask_user = False
            ai_msg = None
            effective_previous_add_context = state.get("add_context", {})
            effective_existing_context = state.get("context", {})
            plan = state.get("plan", None)
            agent_name = state.get("agent_name", None)
            agent_description = state.get("agent_description", None)
            last_code_output = None
            # logging.info(f"Initial new_tool_ids_for_context: {new_tool_ids_for_context}")

            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                try:
                    if tool_name == "execute_python_code":
                        code = tool_args["snippet"]
                        display = tool_args.get("display_output_to_user", False)
                        output, new_context, new_add_context = await self.sandbox.handle_execute_python_code(
                            code,
                            self.sandbox.context,  # Uses the dynamically updated context
                            effective_previous_add_context,
                            effective_existing_context,
                            display,
                        )
                        effective_existing_context = new_context
                        effective_previous_add_context = new_add_context
                        if display and not re.search(r"error", output, re.IGNORECASE):
                            ask_user = True
                            tool_result = "Code output added to response"
                            ai_msg = output
                        else:
                            tool_result = "Code executed"
                            last_code_output = output
                    elif tool_name == "load_functions":
                        # The tool now does all the work of validation and formatting.
                        tool_result, new_context_for_sandbox, valid_tools, unconnected_links = await self.meta_tools[
                            "load_functions"
                        ].ainvoke(tool_args)
                        # We still need to update the sandbox context for `execute_python_code`
                        new_tool_ids.extend(valid_tools)
                        if new_tool_ids:
                            self.sandbox.update_context(new_context_for_sandbox)
                        if unconnected_links:
                            ask_user = True
                            ai_msg = f"Please login to the following app(s) using the following links and let me know in order to proceed:\n {unconnected_links} "

                    elif tool_name == "search_functions":
                        tool_result = await self.meta_tools["search_functions"].ainvoke(tool_args)

                    elif tool_name == "plan_agent":
                        plan, tool_result = await create_or_update_plan(
                            self=self, state=state, writer=writer, plan=plan
                        )
                        # TODO: This should be an interrupt
                        ask_user = True

                    elif tool_name == "code_and_save_agent":
                        (
                            tool_result,
                            effective_previous_add_context,
                            agent_name,
                            agent_description,
                        ) = await build_or_patch_code(
                            self=self,
                            state=state,
                            writer=writer,
                        )
                    else:
                        raise Exception(
                            f"Unexpected tool call: {tool_call['name']}. "
                            "tool calls must be one of 'execute_python_code', 'load_functions', 'search_functions', 'plan_agent', or 'code_and_save_agent'. For using functions, call them in code using 'execute_python_code'."
                        )
                except Exception as e:
                    tool_result = str(e)

                tool_message = ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
                tool_messages.append(tool_message)

            if ask_user:
                if ai_msg:
                    tool_messages.append(AIMessage(content=ai_msg))
                return Command(
                    update={
                        "messages": tool_messages,
                        "selected_tool_ids": new_tool_ids,
                        "context": effective_existing_context,
                        "add_context": effective_previous_add_context,
                        "agent_name": agent_name,
                        "agent_description": agent_description,
                        "plan": plan,
                        "last_code_output": last_code_output,
                    }
                )
            return Command(
                goto="call_model",
                update={
                    "messages": tool_messages,
                    "selected_tool_ids": new_tool_ids,
                    "context": effective_existing_context,
                    "add_context": effective_previous_add_context,
                    "agent_name": agent_name,
                    "agent_description": agent_description,
                    "plan": plan,
                    "last_code_output": last_code_output,
                },
            )

        async def route_entry(state: CodeActState) -> Command[Literal["call_model", "execute_tools"]]:
            """Route to either normal mode or agent builder creation"""
            # Create the initial system prompt and tools_context in one go
            self.final_instructions = create_default_prompt(
                self.instructions,
                await get_connected_apps_string(self.registry),
                self.agent,
                is_initial_prompt=True,
            )
            default_tool_defs, default_tool_context = await self._load_default_tools()
            self.sandbox.update_context(default_tool_context)
            self.final_instructions += "\nIn addition to the Python Standard Library, you can use the following external functions:\n Carefully note which functions are normal and which functions are async. CRITICAL: Use `await` with async functions and async functions ONLY.\n"
            self.final_instructions += "\n".join(default_tool_defs)
            tool_defs, loaded_tools_context = await self._load_tools(state["selected_tool_ids"])
            # The tool defs are avilable in old tool messages so we don't need to update the prompt
            self.sandbox.update_context(loaded_tools_context)
            if (
                len(state["messages"]) == 1 and self.agent
            ):  # Inject the agent's script function into add_context for execution
                script = self.agent.instructions.get("script")
                plan = self.agent.instructions.get("plan")
                add_context = {"functions": [script]}
                return Command[Literal["call_model", "execute_tools"]](
                    goto="call_model", update={"add_context": add_context, "plan": plan}
                )
            elif detect_pending_tool(state["messages"]):  # Detect corrupted (i.e. incomplete tool call) state
                return Command(
                    goto="execute_tools",
                    update={"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *state["messages"]]},
                )
            return Command(goto="call_model", update={"last_code_output": None})

        agent = StateGraph(state_schema=CodeActState)
        agent.add_node(call_model, retry_policy=RetryPolicy(max_attempts=3, retry_on=filter_retry_on))
        agent.add_node(execute_tools)
        agent.add_node(route_entry)
        agent.add_edge(START, "route_entry")
        return agent.compile(checkpointer=self.memory)
