import asyncio
import base64
from collections import defaultdict
from pathlib import Path
from typing import Annotated, Any

from langchain_core.tools import tool
from pydantic import Field
from universal_mcp.applications.markitdown.app import MarkitdownApp
from universal_mcp.types import ToolFormat

from universal_mcp.agentr.client import AgentrClient
from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.codeact0.prompts import build_tool_definitions


def enter_agent_builder_mode():
    """Call this function to enter agent builder mode. Agent builder mode is when the user wants to store a repeated task as a script with some inputs for the future."""
    return


def create_meta_tools(tool_registry: AgentrRegistry) -> dict[str, Any]:
    """Create the meta tools for searching and loading tools"""

    @tool
    async def search_functions(
        queries: Annotated[
            list[list[str]] | None,
            Field(
                description="A list of query lists. Each inner list contains one or more search terms that will be used together to find relevant tools."
            ),
        ] = None,
        app_ids: Annotated[
            list[str] | None,
            Field(description="The ID or list of IDs (common names) of specific applications to search within."),
        ] = None,
    ) -> str:
        """
        Searches for relevant functions based on queries and/or applications. This function
        operates in three powerful modes with support for multi-query searches:

        1.  **Global Search** (`queries` only as List[List[str]]):
            - Searches all functions across all applications.
            - Supports multiple independent searches in parallel.
            - Each inner list represents a separate search query.

            Examples:
            - Single global search:
              `search_functions(queries=[["create presentation"]])`

            - Multiple independent global searches:
              `search_functions(queries=[["send email"], ["schedule meeting"]])`

            - Multi-term search for comprehensive results:
              `search_functions(queries=[["send email", "draft email", "compose email"]])`

        2.  **App Discovery** (`app_ids` only as List[str]):
            - Returns ALL available functions for one or more specific applications.
            - Use this to explore the complete capability set of an application.

            Examples:
            - Single app discovery:
              `search_functions(app_ids=["Gmail"])`

            - Multiple app discovery:
              `search_functions(app_ids=["Gmail", "Google Calendar", "Slack"])`

        3.  **Scoped Search** (`queries` as List[List[str]] and `app_ids` as List[str]):
            - Performs targeted searches within specific applications in parallel.
            - The number of app_ids must match the number of inner query lists.
            - Each query list is searched within its corresponding app_id.
            - Supports multiple search terms per app for comprehensive discovery.

            Examples:
            - Basic scoped search (one query per app):
              `search_functions(queries=[["find email"], ["share file"]], app_ids=["Gmail", "Google_Drive"])`

            - Multi-term scoped search (multiple queries per app):
              `search_functions(
                  queries=[
                      ["send email", "draft email", "compose email", "reply to email"],
                      ["create event", "schedule meeting", "find free time"],
                      ["upload file", "share file", "create folder", "search files"]
                  ],
                  app_ids=["Gmail", "Google Calendar", "Google_Drive"]
              )`

            - Mixed complexity (some apps with single query, others with multiple):
              `search_functions(
                  queries=[
                      ["list messages"],
                      ["create event", "delete event", "update event"]
                  ],
                  app_ids=["Gmail", "Google Calendar"]
              )`

        **Pro Tips:**
        - Use multiple search terms in a single query list to cast a wider net and discover related functionality
        - Multi-term searches are more efficient than separate calls
        - Scoped searches return more focused results than global searches
        - The function returns connection status for each app (connected vs NOT connected)
        - All searches within a single call execute in parallel for maximum efficiency

        **Parameters:**
        - `queries` (List[List[str]], optional): A list of query lists. Each inner list contains one or more
          search terms that will be used together to find relevant tools.
        - `app_ids` (List[str], optional): A list of application IDs to search within or discover.

        **Returns:**
        - A structured response containing:
          - Matched tools with their descriptions
          - Connection status for each app
          - Recommendations for which tools to load next
        """
        registry = tool_registry

        TOOL_THRESHOLD = 0.75
        APP_THRESHOLD = 0.7

        # --- Helper Functions for Different Search Modes ---

        async def _handle_global_search(queries: list[str]) -> list[list[dict[str, Any]]]:
            """Performs a broad search across all apps to find relevant tools and apps."""
            # 1. Perform initial broad searches for tools and apps concurrently.
            initial_tool_tasks = [registry.search_tools(query=q, distance_threshold=TOOL_THRESHOLD) for q in queries]
            app_search_tasks = [registry.search_apps(query=q, distance_threshold=APP_THRESHOLD) for q in queries]

            initial_tool_results, app_search_results = await asyncio.gather(
                asyncio.gather(*initial_tool_tasks), asyncio.gather(*app_search_tasks)
            )

            # 2. Create a prioritized list of app IDs for the final search.
            app_ids_from_apps = {app["id"] for result_list in app_search_results for app in result_list}
            prioritized_app_id_list = list(app_ids_from_apps)

            app_ids_from_tools = {tool["app_id"] for result_list in initial_tool_results for tool in result_list}
            for tool_app_id in app_ids_from_tools:
                if tool_app_id not in app_ids_from_apps:
                    prioritized_app_id_list.append(tool_app_id)

            if not prioritized_app_id_list:
                return []

            # 3. Perform the final, comprehensive tool search across the prioritized apps.
            final_tool_search_tasks = [
                registry.search_tools(query=query, app_id=app_id_to_search, distance_threshold=TOOL_THRESHOLD)
                for app_id_to_search in prioritized_app_id_list
                for query in queries
            ]
            return await asyncio.gather(*final_tool_search_tasks)

        async def _handle_scoped_search(app_ids: list[str], queries: list[list[str]]) -> list[list[dict[str, Any]]]:
            """Performs targeted searches for specific queries within specific applications."""
            if len(app_ids) != len(queries):
                raise ValueError("The number of app_ids must match the number of query lists.")

            tasks = []
            for app_id, query_list in zip(app_ids, queries):
                for query in query_list:
                    # Create a search task for each query in the list for the corresponding app
                    tasks.append(registry.search_tools(query=query, app_id=app_id, distance_threshold=TOOL_THRESHOLD))

            return await asyncio.gather(*tasks)

        async def _handle_app_discovery(app_ids: list[str]) -> list[list[dict[str, Any]]]:
            """Fetches all tools for a list of applications."""
            tasks = [registry.search_tools(query="", app_id=app_id, limit=20) for app_id in app_ids]
            return await asyncio.gather(*tasks)

        # --- Helper Functions for Structuring and Formatting Results ---

        def _format_response(structured_results: list[dict[str, Any]]) -> str:
            """Builds the final, user-facing formatted string response from structured data."""
            if not structured_results:
                return "No relevant functions were found."

            result_parts = []
            apps_in_results = {app["app_id"] for app in structured_results}
            connected_apps_in_results = {
                app["app_id"] for app in structured_results if app["connection_status"] == "connected"
            }

            for app in structured_results:
                app_id = app["app_id"]
                app_status = "connected" if app["connection_status"] == "connected" else "NOT connected"
                result_parts.append(f"Tools from {app_id} (status: {app_status} by user):")

                for tool_def in app["tools"]:
                    result_parts.append(f" - {tool_def['id']}: {tool_def['description']}")
                result_parts.append("")  # Empty line for readability

            # Add summary connection status messages
            if not connected_apps_in_results and len(apps_in_results) > 1:
                result_parts.append(
                    "Connection Status: None of the apps in the results are connected. "
                    "You must ask the user to choose the application."
                )
            elif len(connected_apps_in_results) > 1:
                connected_list = ", ".join(sorted(list(connected_apps_in_results)))
                result_parts.append(
                    f"Connection Status: Multiple apps are connected ({connected_list}). "
                    "You must ask the user to select which application they want to use."
                )

            result_parts.append("Call load_functions to select the required functions only.")
            if 0 <= len(connected_apps_in_results) < len(apps_in_results):
                result_parts.append(
                    "Unconnected app functions can also be loaded if asked for by the user, they will generate a connection link"
                    "but prefer connected ones. Ask the user to choose the app if none of the "
                    "relevant apps are connected."
                )

            return "\n".join(result_parts)

        def _structure_tool_results(
            raw_tool_lists: list[list[dict[str, Any]]], connected_app_ids: set[str]
        ) -> list[dict[str, Any]]:
            """
            Converts raw search results into a structured format, handling duplicates,
            cleaning descriptions, and adding connection status.
            """
            aggregated_tools = defaultdict(dict)
            # Use a list to maintain the order of apps as they are found.
            ordered_app_ids = []

            for tool_list in raw_tool_lists:
                for tool_def in tool_list:
                    app_id = tool_def.get("app_id", "unknown")
                    tool_id = tool_def.get("id")

                    if not tool_id:
                        continue

                    if app_id not in aggregated_tools:
                        ordered_app_ids.append(app_id)

                    if tool_id not in aggregated_tools[app_id]:
                        aggregated_tools[app_id][tool_id] = {
                            "id": tool_id,
                            "description": _clean_tool_description(tool_def.get("description", "")),
                        }

            # Build the final results list respecting the discovery order.
            found_tools_result = []
            for app_id in ordered_app_ids:
                if app_id in aggregated_tools and aggregated_tools[app_id]:
                    found_tools_result.append(
                        {
                            "app_id": app_id,
                            "connection_status": "connected" if app_id in connected_app_ids else "not_connected",
                            "tools": list(aggregated_tools[app_id].values()),
                        }
                    )
            return found_tools_result

        def _clean_tool_description(description: str) -> str:
            """Consistently formats tool descriptions by removing implementation details."""
            return description.split("Context:")[0].strip()

        # Main Function Logic

        if not queries and not app_ids:
            raise ValueError("You must provide 'queries', 'app_ids', or both.")

        # --- Initialization and Input Normalization ---
        connections = await registry.list_connected_apps()
        connected_app_ids = {connection["app_id"] for connection in connections}

        canonical_app_ids = []
        if app_ids:
            # Concurrently search for all provided app names
            app_search_tasks = [
                registry.search_apps(query=app_name, distance_threshold=APP_THRESHOLD) for app_name in app_ids
            ]
            app_search_results = await asyncio.gather(*app_search_tasks)

            # Process results and build the list of canonical IDs, handling not found errors
            for app_name, result_list in zip(app_ids, app_search_results):
                if not result_list:
                    raise ValueError(f"Application '{app_name}' could not be found.")
                # Assume the first result is the correct one
                canonical_app_ids.append(result_list[0]["id"])

        # --- Mode Dispatching ---
        raw_results = []

        if canonical_app_ids and queries:
            raw_results = await _handle_scoped_search(canonical_app_ids, queries)
        elif canonical_app_ids:
            raw_results = await _handle_app_discovery(canonical_app_ids)
        elif queries:
            # Flatten list of lists to list of strings for global search
            flat_queries = (
                [q for sublist in queries for q in sublist] if queries and not isinstance(queries[0], str) else queries
            )
            raw_results = await _handle_global_search(flat_queries)

        # --- Structuring and Formatting ---
        structured_data = _structure_tool_results(raw_results, connected_app_ids)
        return _format_response(structured_data)

    @tool
    async def load_functions(tool_ids: list[str]) -> str:
        """
        Loads specified functions and returns their Python signatures and docstrings.
        This makes the functions available for use inside the 'execute_python_code' tool.
        The agent MUST use the returned information to understand how to call the functions correctly.

        Args:
            tool_ids: A list of function IDs in the format 'app__function'. Example: ['google_mail__send_email']

        Returns:
            A string containing the signatures and docstrings of the successfully loaded functions,
            ready for the agent to use in its code.
        """
        if not tool_ids:
            return "No tool IDs provided to load."

        # Step 1: Validate which tools are usable and get login links for others.
        valid_tools, unconnected_links = await get_valid_tools(tool_ids=tool_ids, registry=tool_registry)

        if not valid_tools:
            response_string = "Error: None of the provided tool IDs could be validated or loaded."
            return response_string, {}, [], ""

        # Step 2: Export the schemas of the valid tools.
        await tool_registry.load_tools(valid_tools)
        exported_tools = await tool_registry.export_tools(
            valid_tools, ToolFormat.NATIVE
        )  # Get definition for only the new tools

        # Step 3: Build the informational string for the agent.
        tool_definitions, new_tools_context = build_tool_definitions(exported_tools)

        result_parts = [
            f"Successfully loaded {len(exported_tools)} functions. They are now available for use inside `execute_python_code`:",
            "\n".join(tool_definitions),
        ]

        response_string = "\n\n".join(result_parts)
        unconnected_links = "\n".join(unconnected_links)

        return response_string, new_tools_context, valid_tools, unconnected_links

    async def web_search(query: str) -> dict:
        """
        Get an LLM answer to a question informed by Exa search results. Useful when you need information from a wide range of real-time sources on the web. Do not use this when you need to access contents of a specific webpage.

        This tool performs an Exa `/answer` request, which:
        1. Provides a **direct answer** for factual queries (e.g., "What is the capital of France?" → "Paris")
        2. Generates a **summary with citations** for open-ended questions
        (e.g., "What is the state of AI in healthcare?" → A detailed summary with source links)

        Args:
            query (str): The question or topic to answer.
        Returns:
            dict: A structured response containing only:
                - answer (str): Generated answer
                - citations (list[dict]): List of cited sources
        """
        await tool_registry.export_tools(["exa__answer"], ToolFormat.LANGCHAIN)
        response = await tool_registry.call_tool("exa__answer", {"query": query, "text": True})

        # Extract only desired fields
        return {
            "answer": response.get("answer"),
            "citations": response.get("citations", []),
        }

    async def read_file(uri: str) -> str:
        """
        Asynchronously reads a local file or uri and returns the content as a markdown string.

        This tool aims to extract the main text content from various sources.
        It automatically prepends 'file://' to the input string if it appears
        to be a local path without a specified scheme (like http, https, data, file).

        Args:
            uri (str): The URI pointing to the resource or a local file path.
                       Supported schemes:
                       - http:// or https:// (Web pages, feeds, APIs)
                       - file:// (Local or accessible network files)
                       - data: (Embedded data)

        Returns:
            A string containing the markdown representation of the content at the specified URI

        Raises:
            ValueError: If the URI is invalid, empty, or uses an unsupported scheme
                        after automatic prefixing.

        Tags:
            convert, markdown, async, uri, transform, document, important
        """
        markitdown = MarkitdownApp()
        response = await markitdown.convert_to_markdown(uri)
        return response

    def save_file(file_name: str, content: str | bytes, is_base64: bool = False) -> dict:
        """
        Saves a file (text or binary) to the local filesystem.

        Args:
            file_name (str): The name of the file to save.
            content (str | bytes): The file content. Can be:
                - plain text
                - bytes
                - base64-encoded string (set is_base64=True)
            is_base64 (bool): Whether the provided content is base64-encoded.

        Returns:
            dict: A dictionary containing the result of the save operation:
                - status (str): "success" if saved successfully, "error" otherwise.
                - message (str): Status message describing the operation.
                - file_path (str): Absolute file path of the saved file.
        """
        try:
            path = Path(file_name)

            # Handle base64 input if needed
            if is_base64 and isinstance(content, str):
                content_bytes = base64.b64decode(content)
            elif isinstance(content, bytes):
                content_bytes = content
            else:
                # Assume plain text
                content_bytes = content.encode("utf-8")

            # Write bytes directly (works for all file types)
            with path.open("wb") as f:
                f.write(content_bytes)

            return {
                "status": "success",
                "message": f"File '{file_name}' saved successfully.",
                "file_path": str(path.absolute()),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to save file '{file_name}': {e}",
                "file_path": None,
            }

    def upload_file(file_name: str, mime_type: str, base64_data: str) -> dict:
        """
        Uploads a file to the server.

        Args:
            file_name (str): The name of the file to upload.
            mime_type (str): The MIME type of the file.
            base64_data (str): The file content encoded as a base64 string.

        Returns:
            dict: A dictionary containing the result of the upload operation with the following fields:
                - status (str): "success" if the upload succeeded, "error" otherwise.
                - message (str): A message returned by the server, typically indicating success or providing error details.
                - signed_url (str or None): The signed URL to access the uploaded file if successful, None otherwise.
        """
        client: AgentrClient = tool_registry.client
        bytes_data = base64.b64decode(base64_data)
        response = client._upload_file(file_name, mime_type, bytes_data)
        if response.get("status") != "success":
            return {
                "status": "error",
                "message": response.get("message"),
                "signed_url": None,
            }
        return {
            "status": "success",
            "message": response.get("message"),
            "signed_url": response.get("signed_url"),
        }

    return {
        "search_functions": search_functions,
        "load_functions": load_functions,
        "web_search": web_search,
        "read_file": read_file,
        "upload_file": upload_file,
        "save_file": save_file,
    }


def create_agent_builder_tools() -> dict[str, Any]:
    """Create tools for agent plan and code creation, saving, modifying"""

    @tool
    async def plan_agent():
        """
        Creates a new agent plan if none exists, or update the existing plan using a minimal patch.
        Non-interactive; relies only on conversation/code history. Missing details must be external variables.
        No arguments are required; all context is implicit.
        """
        return "ok"

    @tool
    async def code_and_save_agent():
        """
        Generates new Python code from a confirmed plan, or patch existing agent code using a minimal diff.
        Non-interactive; main agent must ensure capabilities are loaded beforehand.
        No arguments are required; all context is implicit.
        """
        return "ok"

    return {
        "plan_agent": plan_agent,
        "code_and_save_agent": code_and_save_agent,
    }


async def get_valid_tools(tool_ids: list[str], registry: AgentrRegistry) -> tuple[list[str], list[str]]:
    """For a given list of tool_ids, validates the tools and returns a list of links for the apps that have not been logged in"""
    correct, incorrect = [], []
    connections = await registry.list_connected_apps()
    connected_apps = {connection["app_id"] for connection in connections}
    unconnected = set()
    unconnected_links = []
    app_tool_list: dict[str, set[str]] = {}

    # Group tool_ids by app for fewer registry calls
    app_to_tools: dict[str, list[tuple[str, str]]] = {}
    for tool_id in tool_ids:
        if "__" not in tool_id:
            incorrect.append(tool_id)
            continue
        app, tool_name = tool_id.split("__", 1)
        app_to_tools.setdefault(app, []).append((tool_id, tool_name))

    # Fetch all apps concurrently
    async def fetch_tools(app: str):
        try:
            tools_dict = await registry.list_tools(app)
            return app, {tool_unit["name"] for tool_unit in tools_dict}
        except Exception:
            return app, None

    results = await asyncio.gather(*(fetch_tools(app) for app in app_to_tools))

    # Build map of available tools per app
    for app, tools in results:
        if tools is not None:
            app_tool_list[app] = tools

    # Validate tool_ids
    for app, tool_entries in app_to_tools.items():
        available = app_tool_list.get(app)
        if available is None:
            incorrect.extend(tool_id for tool_id, _ in tool_entries)
            continue
        if app not in connected_apps and app not in unconnected:
            unconnected.add(app)
            text = await registry.authorise_app(app_id=app)
            start = text.find(":") + 1
            end = text.find(". R", start)
            url = text[start:end].strip()
            markdown_link = f"[Connect to {app.capitalize()}]({url})"
            unconnected_links.append(markdown_link)
        for tool_id, tool_name in tool_entries:
            if tool_name in available:
                correct.append(tool_id)
            else:
                incorrect.append(tool_id)

    return correct, unconnected_links


async def main():
    registry = AgentrRegistry()
    create_meta_tools(registry)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main)
