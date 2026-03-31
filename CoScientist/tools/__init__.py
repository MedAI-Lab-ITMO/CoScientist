"""Toolset module."""
from CoScientist.tools.fedotmas_tools import FedotMASToolset, fedot_toolset_instance
from CoScientist.tools.web_tools import websearch_toolset_instance
from CoScientist.tools.retrieval_tools import RetrievalToolSet, retrieval_toolset_instance

__all__ = ["FedotMASToolset", 
            "fedot_toolset_instance",
            'websearch_toolset_instance',
            'RetrievalToolSet',
            'retrieval_toolset_instance']
