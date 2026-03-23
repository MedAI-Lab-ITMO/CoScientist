from __future__ import annotations

import asyncio
import os
from typing import Any, Dict

from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from coscientist.instructions import (
    fedot_instruction,
    hypotheses_instruction,
    orchestrator_instruction,
    research_instruction,
)
from coscientist.utils import (
    _dedupe_urls,
    _fetch_mcp_server_info,
    _format_exception,
    _load_mcp_urls,
    _resolve_mcp_names,
)
from fedotmas import HttpMCPServer, MAS

MODEL = os.environ.get("MODEL", "openrouter/qwen/qwen3-235b-a22b-2507")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
DEFAULT_FEDOT_MCP_NAMES = ("auto_ml",)
MCP_DISCOVERY_TIMEOUT_SECONDS = 20


MCP_URLS = _load_mcp_urls()
AVAILABLE_MCP_SERVER_NAMES = tuple(sorted(MCP_URLS))
AVAILABLE_MCP_SERVER_NAMES_TEXT = ", ".join(AVAILABLE_MCP_SERVER_NAMES) or "none"


hypotheses_agent = LlmAgent(
    name="HypothesesAgent",
    model=LiteLlm(model=MODEL),
    instruction=hypotheses_instruction,
    description="Agent to generate scientific hypotheses and ideas for given task",
    output_key="hypotheses",
)

research_agent = LlmAgent(
    name="ResearchAgent",
    model=LiteLlm(model=MODEL),
    instruction=research_instruction,
    description="Agent to answer questions and knowledge mining using Literature and Web Search.",
    output_key="search_results",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
            ),
        ),
    ],
)


async def inspect_mcp_servers(mcp_names: list[str]) -> Dict[str, Any]:
    """
    Inspect configured MCP servers and return their descriptions and tools.

    Args:
        mcp_names: Keys from MCP_URLS for the servers that should be inspected.

    Returns:
        Compact metadata for each reachable MCP server.
    """

    try:
        requested_names = _resolve_mcp_names(mcp_names, MCP_URLS)
    except ValueError as exc:
        return {
            "status": "error",
            "message": str(exc),
            "available_mcp_servers": list(AVAILABLE_MCP_SERVER_NAMES),
        }

    requested_urls = [MCP_URLS[name] for name in requested_names]
    results = await asyncio.gather(
        *(
            _fetch_mcp_server_info(
                mcp_name,
                MCP_URLS[mcp_name],
                timeout_seconds=MCP_DISCOVERY_TIMEOUT_SECONDS,
            )
            for mcp_name in requested_names
        ),
        return_exceptions=True,
    )

    servers: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for mcp_name, url, result in zip(requested_names, requested_urls, results, strict=True):
        if isinstance(result, Exception):
            errors.append(
                {"mcp_name": mcp_name, "url": url, "error": _format_exception(result)}
            )
            continue
        servers.append(result)

    status = "success" if servers and not errors else "partial" if servers else "error"
    return {
        "status": status,
        "requested_mcp_names": requested_names,
        "servers": servers,
        "errors": errors,
        "available_mcp_servers": list(AVAILABLE_MCP_SERVER_NAMES),
        "selection_hint": (
            "Inspect only MCP server keys relevant to the user task. Then choose "
            "URLs from the returned servers and pass them as mcp_urls to fedot_tool."
        ),
    }


async def fedot_tool(
    task_description: str,
    mcp_urls: list[str] | None = None,
) -> Dict[str, Any]:
    """
    Tool for generating and executing multi-agent pipelines via FEDOT.MAS.

    Args:
        task_description: Clear description of the task, including goals,
                          inputs, constraints, and expected outputs.
        mcp_urls: List of MCP server URLs that FEDOT.MAS is allowed to use.
                  If omitted, the default auto_ml MCP server is used when configured.

    Returns:
        Result of the executed MAS pipeline.
    """

    resolved_urls = _dedupe_urls(mcp_urls) if mcp_urls else _dedupe_urls(
        [MCP_URLS[name] for name in DEFAULT_FEDOT_MCP_NAMES if name in MCP_URLS]
    )
    if not resolved_urls:
        return {
            "status": "error",
            "message": (
                "No MCP URLs were provided for FEDOT.MAS and no default MCP "
                "server is configured."
            ),
            "configured_servers": MCP_URLS,
        }

    configured_names_by_url = {url: name for name, url in MCP_URLS.items()}
    mcp_registry = {
        configured_names_by_url.get(url, f"mcp_server_{idx + 1}"): HttpMCPServer(
            url=url,
            description=(
                f"Remote MCP server '{configured_names_by_url.get(url, f'mcp_server_{idx + 1}')}'"
            ),
        )
        for idx, url in enumerate(resolved_urls)
    }
    mas = MAS(mcp_servers=mcp_registry)
    result = await mas.run(task_description)

    return {
        "status": "success",
        "used_mcp_servers": list(mcp_registry.keys()),
        "used_mcp_urls": resolved_urls,
        "result": result,
    }


fedot_agent = LlmAgent(
    name="ExperimentAgent",
    model=LiteLlm(model=MODEL),
    instruction=(
        f"{fedot_instruction}\n\n"
        f"Available MCP server keys from MCP_URLS: {AVAILABLE_MCP_SERVER_NAMES_TEXT}."
    ),
    description=(
        "Agent to complete experiments and run calculations. It can inspect "
        "available MCP servers, select the relevant ones, and pass their URLs "
        f"to FEDOT.MAS. Available MCP keys: {AVAILABLE_MCP_SERVER_NAMES_TEXT}."
    ),
    output_key="fedot_results",
    tools=[inspect_mcp_servers, fedot_tool],
)


orchestrator_agent = LlmAgent(
    name="OrchestratorAgent",
    model=LiteLlm(model=MODEL),
    instruction=orchestrator_instruction,
    description="Main Orchestrator Agent",
    tools=[
        AgentTool(agent=hypotheses_agent),
        AgentTool(agent=research_agent),
        AgentTool(agent=fedot_agent),
    ],
)
