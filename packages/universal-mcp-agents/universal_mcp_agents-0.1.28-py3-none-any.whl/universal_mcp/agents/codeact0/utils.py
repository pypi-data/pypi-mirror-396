import copy
import re
from collections.abc import Sequence
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from universal_mcp.types import ToolConfig

MAX_CHARS = 1000


def extract_code_tools(code: str) -> list[str]:
    """
    Extract tool identifiers of the form 'provider__tool' from arbitrary code text.

    - Matches identifiers that start with a letter followed by letters/digits/underscores/hyphens,
      then a double underscore, then the same pattern again.
    - Captures occurrences in both identifiers and strings/comments.
    - Returns a sorted list of unique matches.
    """
    if not isinstance(code, str) or not code:
        return []

    pattern = re.compile(r"\b([a-zA-Z][\w-]*)__([a-zA-Z][\w-]*)\b")
    found = {m.group(0) for m in pattern.finditer(code)}
    return sorted(found)


def build_anthropic_cache_message(text: str, role: str = "system", ttl: str = "5m") -> list[dict[str, Any]]:
    """Build a complete Anthropic cache messages array from text.

    Returns a list with a single cache message whose content is the
    cached Anthropic content array with ephemeral cache control and TTL.
    """
    return [
        {
            "role": role,
            "content": [
                {
                    "type": "text",
                    "text": text,
                    "cache_control": {"type": "ephemeral", "ttl": ttl},
                }
            ],
        }
    ]


def detect_pending_tool(messages: list[BaseMessage]) -> bool:
    """
    Check if the last AIMessage has a pending tool_call, and prune the messages list in place.

    The function:
    - Finds the last AIMessage in the list.
    - If it has an unresolved (pending) tool_call (i.e., the next message is not a ToolMessage),
      removes all messages after that AIMessage in-place.

    Returns:
        bool: True if a pending tool_call was detected (and messages pruned), False otherwise.
    """
    if not messages:
        return False

    # Find index of last AIMessage
    last_ai_index = None
    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], AIMessage):
            last_ai_index = i
            break

    if last_ai_index is None:
        return False

    ai_msg = messages[last_ai_index]

    # Detect a pending tool call
    has_pending_tool = bool(ai_msg.tool_calls) and (
        last_ai_index == len(messages) - 1 or not isinstance(messages[last_ai_index + 1], ToolMessage)
    )

    if has_pending_tool:
        # In-place prune: keep messages up to and including the AIMessage
        del messages[last_ai_index + 1 :]
        return True

    return False


def sanitize_messages(messages):
    """Remove the last 'thinking' block and unpaired last 'tool_use' message."""
    messages = copy.deepcopy(messages)

    # Find last thinking and remove it
    for i in reversed(range(len(messages))):
        msg = messages[i]
        if hasattr(msg, "content") and isinstance(msg.content, list):
            for j in reversed(range(len(msg.content))):
                if isinstance(msg.content[j], dict) and msg.content[j].get("type") == "thinking":
                    del messages[i].content[j]
                    break
            else:
                continue
            break

    # Remove the *entire last message* if it contains a tool_use (unpaired)
    if messages:
        last_msg = messages[-1]
        has_tool_use = any(
            isinstance(part, dict) and part.get("type") == "tool_use" for part in getattr(last_msg, "content", [])
        )
        if has_tool_use:
            messages.pop()

    return messages


def add_tools(tool_config: ToolConfig, tools_to_add: ToolConfig):
    for app_id, new_tools in tools_to_add.items():
        all_tools = tool_config.get(app_id, []) + new_tools
        tool_config[app_id] = list(set(all_tools))
    return tool_config


def light_copy(data):
    """
    Deep copy a dict[str, any] or Sequence[any] with string truncation.

    Args:
        data: Either a dictionary with string keys, or a sequence of such dictionaries

    Returns:
        A deep copy where all string values are truncated to MAX_CHARS characters
    """

    def truncate_string(value):
        """Truncate string to MAX_CHARS chars, preserve other types"""
        if isinstance(value, str) and len(value) > MAX_CHARS:
            return value[:MAX_CHARS] + "..."
        return value

    def copy_dict(d):
        """Recursively copy a dictionary, truncating strings"""
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = copy_dict(value)
            elif isinstance(value, Sequence) and not isinstance(value, str):
                result[key] = [
                    copy_dict(item) if isinstance(item, dict) else truncate_string(item) for item in value[:20]
                ]  # Limit to first 20 items
            else:
                result[key] = truncate_string(value)
        return result

    # Handle the two main cases
    if isinstance(data, dict):
        return copy_dict(data)
    elif isinstance(data, Sequence) and not isinstance(data, str):
        return [
            copy_dict(item) if isinstance(item, dict) else truncate_string(item) for item in data[:20]
        ]  # Limit to first 20 items
    else:
        # For completeness, handle other types
        return truncate_string(data)


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def make_safe_function_name(name: str) -> str:
    """Convert a tool name to a valid Python function name."""
    # Replace non-alphanumeric characters with underscores
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Ensure the name doesn't start with a digit
    if safe_name and safe_name[0].isdigit():
        safe_name = f"tool_{safe_name}"
    # Handle empty name edge case
    if not safe_name:
        safe_name = "unnamed_tool"
    return safe_name


async def get_connected_apps_string(registry) -> str:
    """Get a formatted string of connected applications from the registry."""
    if not registry:
        return ""

    try:
        # Get connected apps from registry
        connections = await registry.list_connected_apps()
        if not connections:
            return "No applications are currently connected."

        # Extract app names from connections
        connected_app_ids = {connection["app_id"] for connection in connections}

        # Format the apps list
        apps_list = []
        for app_id in connected_app_ids:
            apps_list.append(f"- {app_id}")

        return "\n".join(apps_list)
    except Exception:
        return "Unable to retrieve connected applications."


def is_openai_style_patch(text: str) -> bool:
    """Detect if a string looks like an OpenAI/Codex-style patch.

    Minimal check: presence of the Begin/End Patch fences.
    """
    if not isinstance(text, str):
        return False
    return "*** Begin Patch" in text and "*** End Patch" in text


def _parse_openai_patch_hunks(patch_text: str) -> list[tuple[list[str], list[str]]]:
    """Parse a minimal subset of OpenAI patch format into (src_lines, dst_lines) hunks.

    We ignore file-level headers and only process sections between @@ markers.
    Each hunk collects context lines (prefix ' ') and deletions ('-') for src,
    and context (' ') and additions ('+') for dst, preserving order.
    """
    in_patch = False
    src_acc: list[str] = []
    dst_acc: list[str] = []
    hunks: list[tuple[list[str], list[str]]] = []

    for raw in patch_text.splitlines():
        line = raw.rstrip("\n")
        if not in_patch:
            if line.strip() == "*** Begin Patch":
                in_patch = True
            continue

        # End of patch
        if line.strip() == "*** End Patch":
            if src_acc or dst_acc:
                hunks.append((src_acc, dst_acc))
            break

        # Start of new hunk
        if line.startswith("@@"):
            if src_acc or dst_acc:
                hunks.append((src_acc, dst_acc))
                src_acc, dst_acc = [], []
            continue

        # Ignore file headers like '*** Update File:' etc.
        if line.startswith("*** "):
            continue

        if line.startswith(" "):
            src_acc.append(line[1:])
            dst_acc.append(line[1:])
        elif line.startswith("-"):
            src_acc.append(line[1:])
        elif line.startswith("+"):
            dst_acc.append(line[1:])
        else:
            # Unknown/empty line inside hunk – treat as context
            src_acc.append(line)
            dst_acc.append(line)

    return hunks


def apply_openai_style_patch(original: str, patch_text: str) -> str:
    """Apply a minimal OpenAI-style patch to a single text buffer.

    Strategy per hunk:
    - Build src_block from ' ' and '-' lines; dst_block from ' ' and '+' lines
    - Replace the first occurrence of src_block with dst_block
    - If exact replacement fails, try a lenient fallback using trimmed boundaries
    """
    if not is_openai_style_patch(patch_text):
        return original

    result = original
    hunks = _parse_openai_patch_hunks(patch_text)
    for src_lines, dst_lines in hunks:
        src_block = "\n".join(src_lines)
        dst_block = "\n".join(dst_lines)

        # Fresh generation or insert-only: no source lines
        if not src_lines:
            # If original is empty, take dst as full content; otherwise replace entire buffer
            result = dst_block
            continue

        # Exact match replacement first
        if src_block in result:
            result = result.replace(src_block, dst_block, 1)
            continue

        # Fallback: try boundary-based replacement using first/last lines
        def _find_boundary_replace(text: str, src: list[str], repl: str) -> tuple[bool, str]:
            if not src:
                return False, text
            start_token = src[0].strip()
            end_token = src[-1].strip()
            start_idx = text.find(start_token)
            if start_idx == -1:
                return False, text
            end_idx = text.find(end_token, start_idx + len(start_token))
            if end_idx == -1:
                return False, text
            end_idx += len(end_token)
            # Replace the slice
            new_text = text[:start_idx] + repl + text[end_idx:]
            return True, new_text

        replaced, result2 = _find_boundary_replace(result, src_lines, dst_block)
        if replaced:
            result = result2
            continue

        # As last resort: no-op this hunk
        # (In a richer implementation, raise or collect diagnostics.)
        continue
    return result


def apply_patch_or_use_proposed(original: str, proposed: str) -> str:
    """If proposed content is a patch, apply it to original; otherwise return proposed.

    This provides a unified entry point for handling both full replacements and patch updates.
    """
    if is_openai_style_patch(proposed):
        return apply_openai_style_patch(original, proposed)
    return proposed
