from loguru import logger
from pydantic import BaseModel


class LoadToolResult(BaseModel):
    message: str  # Message to be send to LLM
    loaded_tools: list[str] = []  # Apps that are actually loaded
    unconnected_apps: dict[str, str] | None = None  # Map of app_id to connection url


async def load_functions(self, tool_ids: list[str]):
    """
    Loads specified functions and returns their Python signatures and docstrings.
    This makes the functions available for use inside the 'execute_python_code' tool.
    The agent MUST use the returned information to understand how to call the functions correctly.

    Args:
        tool_ids: A list of function IDs in the format 'app__function'. Example: ['google_mail__send_email']

    Returns:
        message: Message for LLM
        loaded_tools: list
        unconnected_apps
    """

    if not tool_ids:
        return "No tool IDs provided to load."

    # Load the functions
    tool_defs, tool_context = await self._load_tools(tool_ids)
    valid_tool_ids = tool_context.keys()

    if not valid_tool_ids:
        return LoadToolResult(
            message="Error: None of the provided tool IDs could be loaded.",
        ).model_dump_json()
    loaded_app_ids = {valid_tool_id.split("__")[0] for valid_tool_id in valid_tool_ids}
    logger.info(f"Loaded app ids: {loaded_app_ids}")
    connected_apps = await self.registry.list_connected_apps()
    connected_app_ids = {
        connection["app_id"] for connection in connected_apps if connection["app_id"] in loaded_app_ids
    }
    logger.info(f"Connected app ids: {connected_app_ids}")
    # unconnected apps
    unconnected_app_ids = loaded_app_ids - connected_app_ids
    logger.info(f"Unconnected app ids: {unconnected_app_ids}")

    # Generate links for unconnected app_ids
    unconnected_links = {}
    for unconnected_app_id in unconnected_app_ids:
        text = await self.registry.authorise_app(app_id=unconnected_app_id)
        start = text.find(":") + 1
        end = text.find(". R", start)
        url = text[start:end].strip()
        # markdown_link = f"[Connect to {unconnected_app_id.capitalize()}]({url})"
        unconnected_links[unconnected_app_id] = url

    logger.info(unconnected_links)
    tool_defs_string = "\n".join(tool_defs)
    response_string = f"Successfully loaded {len(valid_tool_ids)} functions. They are now available for use inside `execute_python_code`. Loaded tool definitions: {tool_defs_string}"
    result = LoadToolResult(message=response_string, loaded_tools=valid_tool_ids, unconnected_apps=unconnected_links)
    logger.info(result)
    return result.model_dump()
