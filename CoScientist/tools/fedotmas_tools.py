"""Tools for fedotmas inference"""

import asyncio
import inspect

from google.adk.tools import FunctionTool
from google.adk.tools.base_toolset import BaseToolset

from CoScientist.tools.utils import tool


class FedotMASToolset(BaseToolset):
    """Toolset for fedotmas usage"""
    def __init__(self):
        pass

    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:

        tools = []

        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if getattr(method, "_is_tool", False):
                tools.append(FunctionTool(
                                func=method,
                                name=method._tool_name,
                                description=method._tool_description,
                            ))

        return tools
        
    async def close(self) -> None:
        await asyncio.sleep(0)  # Placeholder for async cleanup if needed

    @tool
    async def fedot_tool(task_description: str) -> Dict[str, Any]:
        """
        Tool for generating and executing multi-agent pipelines via FEDOT.MAS. Use it for experiments completion and calculations
        
        Args:
            task_description: Clear description of the task, including goals,
                            inputs, constraints, and expected outputs.
        
        Returns:
            Result of the executed MAS pipeline.
        """

        mas = MAS(mcp_servers={
                "automl_server": HttpMCPServer(
                    url=MCP_URLS['auto_ml'],
                    description="Remote server for automl training and predicting",
                ),
            })


        result = await mas.run(task_description)

        return {
            "status": "success",
            "result": result,
        }

    
fedot_toolset_instance = FedotMASToolset()


