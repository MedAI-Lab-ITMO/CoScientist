"""Tools for websearch"""
from typing import List, Optional, Dict, Any

from CoScientist.tools.utils import tool, toolset
from CoScientist.config import get_settings

from google.adk.tools import FunctionTool, BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams


settings = get_settings()

tavily_toolset_instance = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"https://mcp.tavily.com/mcp/?tavilyApiKey={settings.services.tavily_api_key}"
    ),
)


class WebSearchToolset(BaseToolset):
    """Toolset for websearch usage"""
    def __init__(self):
        pass

    async def get_tools(
        self
    ) -> List[BaseTool]:

        tools = []

        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if getattr(method, "_is_tool", False):
                tools.append(FunctionTool(
                                func=method,
                                name=method._tool_name,
                                description=method._tool_description,
                            ))
            elif getattr(method, "_is_toolset", False):
                tools.append(method)

        return tools
        
    async def close(self) -> None:
        await asyncio.sleep(0)  # Placeholder for async cleanup if needed

    @toolset
    async def tavily_toolset() -> McpToolset:

        return McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=f"https://mcp.tavily.com/mcp/?tavilyApiKey={settings.services.tavily_api_key}"
                ),
            )
    
websearch_toolset_instance = WebSearchToolset()

