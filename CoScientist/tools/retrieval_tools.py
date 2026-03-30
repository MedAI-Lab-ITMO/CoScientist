"""Tools for fedotmas inference"""

import asyncio
import inspect
from typing import List, Optional, Dict, Any

from google.adk.tools import FunctionTool, BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.agents.readonly_context import ReadonlyContext

from CoScientist.tools.utils import tool
from CoScientist.storage import RetrievalToolResult

from rag_tools import create_manager, MCPServer
from rag_tools.storage import PostgresClient
from rag_tools.config.settings import get_settings
from rag_tools.retrieval import APIEmbedder, APIReranker, BM25Reranker, HybridReranker
from rag_tools.storage.models import RetrievalResult, MCPServer

settings = get_settings()


class RetrievalToolSet(BaseToolset):
    """Toolset for rag tool usage"""
    def __init__(self, prefix: str = "rag_"):
        super().__init__()
        self.tool_name_prefix = prefix
        self.wrapper = None

    async def get_tools(
        self,
        readonly_context: Optional[ReadonlyContext]
    ) -> List[BaseTool]:

        tools = [self.retrieve_tools, self.get_server_info]

        return tools
        
    async def close(self) -> None:
        await asyncio.sleep(0)  # Placeholder for async cleanup if needed


    async def retrieve_tools(self, query: str) -> Dict[str, Any]:
        """
        Tool for retrieving MCP tools from DB using RAG. 
        
        Args:
            query: query to use for tools lookup in database using RAG.
        
        Returns:
            List ot the most relevant tools in db which can be used to solve the task .
        """
        embedder = APIEmbedder(settings.api_embedding)
        api_reranker = APIReranker(settings.api_reranker)
        bm2_reranker = BM25Reranker(settings.bm_reranker)
        reranker = HybridReranker([api_reranker, bm2_reranker], settings.hybrid_reranker)
        manager = await create_manager(settings, embedder, reranker)

        retrieved_tools: List[RetrievalResult] = await manager.retrieve_tools(query = query, 
                                                                              top_k = settings.rag.default_top_k,
                                                                              rerank = True,
                                                                              rerank_top_k = settings.rag.rerank_top_k,
                                                                              min_score = settings.rag.min_relevance_score)

        results = [
                RetrievalToolResult(
                    tool=r.name,
                    server_id=r.server_id,
                    description=r.description,
                    score=r.rerank_score,
                )
                for r in retrieved_tools
            ]
        await manager.close()

        return {
            "status": "success",
            "result": results,
        }

    async def get_server_info(self, server_id: str) -> Dict[str, Any]:
        """
        Returns MCP server metadata. 
        
        Args:
            server_id: server id to look up for.
        
        Returns:
            Server metadata.
        """

        postgres = PostgresClient(settings.rag.postgres)
        await postgres.initialize()

        server: MCPServer = await postgres.get_server(server_id)

        await postgres.close()

        return {
            "status": "success",
            "result": results,
        }



    
retrieval_toolset_instance = RetrievalToolSet()
retrieval_toolset_instance = asyncio.run(retrieval_toolset_instance.get_tools(None))


