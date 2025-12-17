from typing import Literal

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.codeact0 import CodeActPlaybookAgent, CodeActTransientAgent
from universal_mcp.agents.react import ReactAgent
from universal_mcp.agents.simple import SimpleAgent


def get_agent(
    agent_name: Literal["react", "simple", "builder", "bigtool", "codeact-repl", "codeact-transient"],
):
    if agent_name == "react":
        return ReactAgent
    elif agent_name == "simple":
        return SimpleAgent
    elif agent_name == "codeact-repl":
        return CodeActPlaybookAgent
    elif agent_name == "codeact-transient":
        return CodeActTransientAgent
    else:
        raise ValueError(f"Unknown agent: {agent_name}. Possible values:  react, simple, codeact-repl")


__all__ = [
    "BaseAgent",
    "ReactAgent",
    "SimpleAgent",
    "CodeActPlaybookAgent",
    "CodeActTransientAgent",
    "get_agent",
]
