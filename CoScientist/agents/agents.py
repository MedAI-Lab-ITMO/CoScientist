
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm 
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from CoScientist.config import get_settings
from CoScientist.agents.prompts import hypotheses_instruction, research_instruction, fedot_instruction, orchestrator_instruction
from CoScientist.tools import fedot_toolset_instance, websearch_toolset_instance

from typing import Dict, Any
import uuid
import os
import asyncio
import json


settings = get_settings()

MODEL = settings.llm.main_model

hypotheses_agent = LlmAgent(
    name="HypothesesAgent",
    model=LiteLlm(model=MODEL),
    instruction=hypotheses_instruction,
    description="Agent to generate scientific hypotheses and ideas for given task",
    output_key="hypotheses"
)

research_agent = LlmAgent(
    name="ResearchAgent",
    model=LiteLlm(model=MODEL),
    instruction=research_instruction,
    description="Agent to answer questions and knowledge mining using Literature and Web Search.",
    output_key="search_results",
    tools=[websearch_toolset_instance]
)


fedot_agent = LlmAgent(
    name="ExperimentAgent",
    model=LiteLlm(model=MODEL),
    instruction=fedot_instruction,
    description="Agent to complete experiments and run calculations. Use it for any computation and idea validation. Includes automl",
    output_key="fedot_results",
    tools=[fedot_toolset_instance]
)


orchestrator_agent = LlmAgent(
    name="OrchestratorAgent",
    model=LiteLlm(model=MODEL),
    instruction=orchestrator_instruction,
    description="Main Orchestrator Agent",
    tools=[AgentTool(agent=hypotheses_agent), AgentTool(agent=research_agent), AgentTool(agent=fedot_agent)],
)



