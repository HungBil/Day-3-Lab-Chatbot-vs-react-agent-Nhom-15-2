import ast
import json
import re
from typing import Any, Callable, Dict, List

from src.tools.travel_tools import (
    check_budget,
    estimate_food_cost,
    get_hotel_price,
    get_weather,
    search_attraction,
    search_destination,
)

ToolFunction = Callable[..., str]

TOOL_REGISTRY: List[Dict[str, Any]] = [
    {
        "name": "search_destination",
        "description": "Get overview, best season, and food of a destination city.",
        "function": search_destination,
        "args": ["city"],
    },
    {
        "name": "get_weather",
        "description": "Get weather by city and month.",
        "function": get_weather,
        "args": ["city", "month"],
    },
    {
        "name": "get_hotel_price",
        "description": "Estimate hotel cost by city, star_level, and nights.",
        "function": get_hotel_price,
        "args": ["city", "star_level", "nights"],
    },
    {
        "name": "estimate_food_cost",
        "description": "Estimate food cost by city, days, and budget_level.",
        "function": estimate_food_cost,
        "args": ["city", "days", "budget_level"],
    },
    {
        "name": "search_attraction",
        "description": "Find attractions by city and interest.",
        "function": search_attraction,
        "args": ["city", "interest"],
    },
    {
        "name": "check_budget",
        "description": "Compare total_cost with budget and report remaining or over amount.",
        "function": check_budget,
        "args": ["total_cost", "budget"],
    },
]

_TOOL_INDEX: Dict[str, Dict[str, Any]] = {tool["name"]: tool for tool in TOOL_REGISTRY}


def get_tool_descriptions() -> str:
    lines: List[str] = []
    for tool in TOOL_REGISTRY:
        args = ", ".join(tool["args"])
        lines.append(f"- {tool['name']}({args}): {tool['description']}")
    return "\n".join(lines)


def _parse_args(args_str: str) -> List[str]:
    text = args_str.strip()
    if not text:
        return []

    # Accept JSON array: ["a", "b"]
    if text.startswith("[") and text.endswith("]"):
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("Action args JSON must be a list.")
        return [str(item) for item in data]

    # Accept Python/JSON-like tuple/list/object
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple)):
            return [str(item) for item in parsed]
        if isinstance(parsed, dict):
            return [str(v) for _, v in parsed.items()]
        if parsed is not None:
            return [str(parsed)]
    except (SyntaxError, ValueError):
        pass

    # Fallback: split by commas while preserving quoted segments.
    parts = re.split(r",(?=(?:[^\"']|\"[^\"]*\"|'[^']*')*$)", text)
    cleaned = [part.strip().strip("\"'") for part in parts if part.strip()]
    return cleaned


def execute_tool(tool_name: str, args_str: str) -> str:
    tool = _TOOL_INDEX.get(tool_name)
    if not tool:
        return f"Tool '{tool_name}' not found."

    func: ToolFunction = tool["function"]
    expected_args: List[str] = tool["args"]

    try:
        values = _parse_args(args_str)
    except Exception as exc:  # pylint: disable=broad-except
        return f"Failed to parse args for {tool_name}: {exc}"

    if len(values) != len(expected_args):
        return (
            f"Invalid argument count for {tool_name}. "
            f"Expected {len(expected_args)} args ({', '.join(expected_args)}), got {len(values)}."
        )

    try:
        return func(*values)
    except Exception as exc:  # pylint: disable=broad-except
        return f"Tool '{tool_name}' execution error: {exc}"
