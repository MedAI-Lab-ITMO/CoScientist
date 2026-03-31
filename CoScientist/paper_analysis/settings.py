import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from CoScientist.config import get_settings
settings = get_settings()

allowed_providers = settings.llm.allowed_providers


class ChromaSettings(BaseSettings):
    """
    Manages settings for Chroma database and related components.
    
    This class encapsulates configuration details for connecting to and interacting with ChromaDB, an embedding
    database, as well as related embedding and reranking services.
    
    Attributes:
        - chroma_host
        - chroma_port
        - allow_reset
        - embedding_host
        - embedding_port
        - embedding_endpoint
        - reranker_host
        - reranker_port
        - reranker_endpoint
    """

    # Chroma DB settings
    chroma_host: str = settings.hosts_ports.chroma_host
    chroma_port: int = settings.hosts_ports.chroma_port
    allow_reset: bool = False
    
    # Documents collection's settings
    embedding_host: str = settings.hosts_ports.embedding_host
    embedding_port: int = settings.hosts_ports.embedding_port
    embedding_endpoint: str = "/embed"
    
    # Reranker settings
    reranker_host: str = settings.hosts_ports.reranker_host
    reranker_port: int = settings.hosts_ports.reranker_port
    reranker_endpoint: str = "/rerank"

settings = ChromaSettings()