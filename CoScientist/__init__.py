"""
CoScientist Module - A multiagent system for solving scientific tasks.
"""

from CoScientist.main import (
    CoScientistManager,
    create_manager
)

from CoScientist.tools import FedotMASToolset, WebSearchToolset

from CoScientist.agents import (
    orchestrator_agent,
    hypotheses_agent, 
    research_agent, 
    fedot_agent
)

__version__ = "1.0.0"

__all__ = [
    # Main classes
    "CoScientistManager",
    # Models
    # Tools
    'FedotMASToolset',
    'WebSearchToolset',
    #Agents
    'orchestrator_agent',
    'hypotheses_agent',
    'research_agent',
    'fedot_agent',
    # Functions
    "create_manager"
]
