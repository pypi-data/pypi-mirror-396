import pytest

from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents.codeact0.tools import create_meta_tools


@pytest.mark.asyncio
async def test_meta_tools_e2e_search_and_load():
    """
    Tests the meta tools for searching and loading functions using a live AgentrRegistry
    with the 'zenquotes' application.
    """
    tool_registry = AgentrRegistry()
    meta_tools = create_meta_tools(tool_registry)
    search_functions = meta_tools["search_functions"]
    load_functions = meta_tools["load_functions"]

    # 1. Search for the 'get_quote' tool.
    search_result = await search_functions.ainvoke({"queries": [["get a quote"]]})

    # Verify that the zenquotes tool is in the search results.
    assert "Tools from zenquotes" in search_result
    assert "zenquotes__get_random_quote" in search_result

    # 2. Load the 'zenquotes__get_random_quote' function.
    tool_id_to_load = "zenquotes__get_random_quote"
    result = await load_functions.ainvoke({"tool_ids": [tool_id_to_load]})

    response_string, new_tools_context, valid_tools, unconnected_links = result

    # Verify that the tool was loaded correctly.
    assert "Successfully loaded 1 function" in response_string
    assert tool_id_to_load in response_string
    assert "async def zenquotes__get_random_quote" in response_string
    assert tool_id_to_load in new_tools_context
    assert valid_tools == [tool_id_to_load]
    assert unconnected_links == ""
