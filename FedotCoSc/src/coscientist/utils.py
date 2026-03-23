from __future__ import annotations

import json
import logging
import os
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

# File handler
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def _load_mcp_urls() -> dict[str, str]:
    """Load and validate the ``MCP_URLS`` environment variable.

    The project stores MCP endpoints as a JSON object mapping a stable
    server key to its HTTP MCP URL, for example
    ``{"paper_search": "http://host:7331/mcp"}``.

    Returns:
        A dictionary where keys are MCP server names exposed to the agent and
        values are non-empty MCP endpoint URLs.

    Raises:
        ValueError: If ``MCP_URLS`` is not valid JSON or is not a JSON object.
    """
    raw_value = os.getenv("MCP_URLS", "{}")
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ValueError("MCP_URLS must contain a valid JSON object: {name: url}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("MCP_URLS must be a JSON object: {name: url}")

    urls: dict[str, str] = {}
    for name, url in parsed.items():
        if isinstance(name, str) and isinstance(url, str) and url.strip():
            urls[name] = url.strip()
    return urls


def _dedupe_urls(urls: list[str]) -> list[str]:
    """Return URLs in their original order without duplicates or empty values."""
    seen: set[str] = set()
    unique_urls: list[str] = []
    for url in urls:
        normalized = url.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_urls.append(normalized)
    return unique_urls


def _resolve_mcp_names(
    mcp_names: list[str] | None,
    mcp_urls: dict[str, str],
) -> list[str]:
    """Validate MCP server keys requested by the agent.

    Args:
        mcp_names: MCP server keys chosen by the agent.
        mcp_urls: Full configured mapping ``{name: url}`` used as the source of
            truth for valid server names.

    Returns:
        A cleaned list of valid MCP server keys in their original order.

    Raises:
        ValueError: If no keys are provided, no valid keys remain after
            normalization, or any requested key is not present in ``mcp_urls``.
    """
    available_names = tuple(sorted(mcp_urls))
    if not mcp_names:
        raise ValueError(
            "mcp_names must contain one or more keys from MCP_URLS. "
            f"Available: {list(available_names)}"
        )

    unknown_names: list[str] = []
    resolved_names: list[str] = []
    seen: set[str] = set()

    for raw_name in mcp_names:
        candidate = raw_name.strip()
        if not candidate:
            continue
        if candidate not in mcp_urls:
            unknown_names.append(candidate)
            continue
        if candidate not in seen:
            seen.add(candidate)
            resolved_names.append(candidate)

    if unknown_names:
        raise ValueError(
            f"Unknown MCP server keys: {unknown_names}. "
            f"Available: {list(available_names)}"
        )
    if not resolved_names:
        raise ValueError(
            "mcp_names must contain one or more valid MCP server keys. "
            f"Available: {list(available_names)}"
        )
    return resolved_names


def _summarize_input_schema(input_schema: Any) -> list[dict[str, Any]]:
    """Extract a compact parameter summary from an MCP tool JSON schema."""
    if not isinstance(input_schema, dict):
        return []

    properties = input_schema.get("properties")
    if not isinstance(properties, dict):
        return []

    required = input_schema.get("required")
    required_fields = set(required) if isinstance(required, list) else set()
    params: list[dict[str, Any]] = []

    for field_name, schema in properties.items():
        field_schema = schema if isinstance(schema, dict) else {}
        field_type = field_schema.get("type")
        if isinstance(field_type, list):
            type_repr = "|".join(str(item) for item in field_type)
        else:
            type_repr = str(field_type) if field_type is not None else None

        params.append(
            {
                "name": field_name,
                "type": type_repr,
                "required": field_name in required_fields,
                "description": field_schema.get("description"),
            }
        )

    return params


def _format_exception(exc: BaseException) -> str:
    """Convert nested async/client exceptions into a readable error string."""
    if isinstance(exc, BaseExceptionGroup):
        parts = [_format_exception(sub_exc) for sub_exc in exc.exceptions]
        message = "; ".join(part for part in parts if part)
        if message:
            return message
    message = str(exc).strip()
    if message:
        return message
    return repr(exc)


async def _fetch_mcp_server_info(
    mcp_name: str,
    url: str,
    *,
    timeout_seconds: int | float = 20,
) -> dict[str, Any]:
    """Query a single MCP server for its metadata and available tools."""
    async with streamablehttp_client(
        url,
        timeout=timeout_seconds,
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            initialize_result = await session.initialize()

            tools = []
            cursor: str | None = None
            while True:
                list_tools_result = await session.list_tools(cursor=cursor)
                tools.extend(list_tools_result.tools)
                cursor = list_tools_result.nextCursor
                if not cursor:
                    break

    server_info = initialize_result.serverInfo
    tool_summaries = [
        {
            "name": tool.name,
            "title": tool.title,
            "description": tool.description,
            "parameters": _summarize_input_schema(tool.inputSchema),
        }
        for tool in tools
    ]

    description = (initialize_result.instructions or "").strip()
    if not description:
        description = (
            f"{server_info.name} exposes {len(tool_summaries)} tool(s) "
            "through this MCP endpoint."
        )

    return {
        "configured_name": mcp_name,
        "url": url,
        "server_name": server_info.name,
        "server_version": server_info.version,
        "description": description,
        "tool_count": len(tool_summaries),
        "tools": tool_summaries,
    }
