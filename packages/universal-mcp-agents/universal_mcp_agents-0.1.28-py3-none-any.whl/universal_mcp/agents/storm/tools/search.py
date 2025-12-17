import asyncio
from collections import defaultdict
from typing import Annotated

from pydantic import Field


async def search_functions(
    self,
    queries: Annotated[
        list[str] | None,
        Field(description="A list of search terms to find relevant tools."),
    ],
    app_id: Annotated[
        str | None,
        Field(description="The ID of a specific application to search within."),
    ] = None,
) -> str:
    """
    Searches for relevant functions based on queries and/or applications. This function
    operates in three powerful modes with support for multi-query searches:

    1.  **Global Search** (`queries` only as List[str]):
        - Searches all functions across all applications.
        - Supports multiple independent searches in parallel.

        Examples:
        - Single global search:
            `search_functions(queries=["create presentation"])`

        - Multiple independent global searches:
            `search_functions(queries=["send email","schedule meeting"])`

        - Multi-term search for comprehensive results:
            `search_functions(queries=["send email", "draft email", "compose email"])`

    2.  **App Discovery** (`app_id` only as str):
        - Returns ALL available functions for one specific applications.
        - Use this to explore the complete capability set of an application.

        Examples:
        - Single app discovery:
            `search_functions(app_id=["Gmail"])`

    3.  **Scoped Search** (`queries` as List[str] and `app_id` as str):
        - Performs targeted searches within specific applications in parallel.
        - Supports multiple search terms per app for comprehensive discovery.

        Examples:
        - Basic scoped search (one query per app):
            `search_functions(queries=["find email", "share file"], app_id="google-mail")`

    **Pro Tips:**
    - Use multiple search terms in a single query list to cast a wider net and discover related functionality
    - Multi-term searches are more efficient than separate calls
    - Scoped searches return more focused results than global searches
    - The function returns connection status for each app (connected vs NOT connected)
    - All searches within a single call execute in parallel for maximum efficiency

    **Parameters:**
    - `queries` (List[str], optional): A list of query lists. Each inner list contains one or more
        search terms that will be used together to find relevant tools.
    - `app_ids` (List[str], optional): A list of application IDs to search within or discover.

    **Returns:**
    - A structured response containing:
        - Matched tools with their descriptions
        - Connection status for each app
        - Recommendations for which tools to load next
    """
    TOOL_THRESHOLD = 0.75

    if not queries:
        queries = [""]  # Empty query for searching app tools

    if app_id:
        tasks = [self.registry.search_tools(query=q, app_id=app_id, distance_threshold=TOOL_THRESHOLD) for q in queries]
    else:
        tasks = [self.registry.search_tools(query=q, distance_threshold=TOOL_THRESHOLD) for q in queries]

    results = await asyncio.gather(*tasks)

    # Flatten the list of lists and deduplicate
    all_tools = {}
    for tool_list in results:
        for tool_def in tool_list:
            all_tools[tool_def["id"]] = tool_def

    if not all_tools:
        return "No relevant functions were found."

    # Group tools by app_id
    grouped_by_app = defaultdict(list)
    for tool_def in all_tools.values():
        grouped_by_app[tool_def["app_id"]].append(tool_def)

    # Format the output
    connections = await self.registry.list_connected_apps()
    connected_app_ids = {connection["app_id"] for connection in connections}

    result_parts = []
    for app, tools in grouped_by_app.items():
        status = "connected" if app in connected_app_ids else "NOT connected"
        result_parts.append(f"Tools from {app} (status: {status}):")
        for t in tools:
            description = t.get("description", "").split("Context:")[0].strip()
            result_parts.append(f" - {t['id']}: {description}")
        result_parts.append("")

    return "\n".join(result_parts)
