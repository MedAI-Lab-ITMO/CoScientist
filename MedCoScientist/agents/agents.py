import ast
import os
import time
from typing import Annotated, Dict
import operator
import streamlit as st
from langchain_core.language_models import BaseChatModel
from langchain.agents import create_react_agent

from langgraph.types import Command
from langgraph.graph import END

from MedCoScientist.agents.agents_prompts import worker_prompt, argument_extraction_prompt
from MedCoScientist.tools import extract_pico_node, extract_keywords_node, query_pubmed_node

from MedCoScientist.tools.mcs.pubmed import search_pubmed, LitItem
from MedCoScientist.tools.mcs.taxonomy.main import get_taxonomy
from MedCoScientist.tools.mcs.pico import get_pico


import requests


def hypothesis_pico_agent(state: dict, config: dict) -> Command:
    """
    Decomposes a hypothesis into PICO elements.
    
    This method instantiates an agent using a specified LLM, configured with credentials and settings from the provided configuration. 
    It then utilizes this agent to process the task described in the input state and generates a response. The method is designed to automate 
    PICO extraction.
    
    All tools are client functions that can launch training of models (ML-models or transformer model) or call inference.
    
    Args:
        state (dict): A dictionary containing the task to be performed, accessible via the "task" key.
        config (dict): A dictionary containing configuration details.
    
    Returns:
        Command: A command object containing the agent's textual response, the updated task history (`past_steps`) including the current task and response,
            and a record of the agent call (`nodes_calls`) detailing the agent used and its input/output.
    """
    task = state["task"]
    plan = state["plan"]
    llm: BaseChatModel = config["configurable"]["model"]
    arg = (argument_extraction_prompt | llm).invoke({"prompt": task}).content
    pico: str = extract_pico_node(arg, llm)

    return Command(update={
        "past_steps": Annotated[set, operator.or_](set([(task, pico)]))
    })

def image_analyzer_agent(state: dict, config: dict) -> Command:
    """
    Analyzes given image and gives diagnosis with keywords for pubmed search. Must accept description of syptomps given by user
    
    Args:
        state (dict): A dictionary containing the task to be performed, accessible via the "task" key.
        config (dict): A dictionary containing configuration details.
    
    Returns:
        Command: A command object containing the agent's textual response, the updated task history (`past_steps`) including the current task and response,
            and a record of the agent call (`nodes_calls`) detailing the agent used and its input/output.
    """

    
    TASK_URL = os.environ.get('MRI_TASK_URL')
    RESULT_URL = os.environ.get('MRI_RESULT_URL')
    PASSWORD = os.environ.get('MRI_PASSWORD')
    AUTH = ("itmo", PASSWORD)


    if not PASSWORD or not TASK_URL or not RESULT_URL:
        return Command(update={
            "past_steps": {(task_text, "Cant reach server: No auth data provided")}
        })

    task_text = state.get("task")
    imgs = config.get("configurable", {}).get("img_path", [])

    if not imgs:
        return Command(update={
            "past_steps": {(task_text, "No images provided")}
        })

    for img in imgs:
        if img.endswith('dcm'):
            filename = img
            break


    session = requests.Session()
    session.auth = AUTH
    session.timeout = 30

    # 1. Submit task
    try:
        with open(filename, "rb") as f:
            response = session.post(
                TASK_URL,
                data={"text": task_text},
                files={"file": f},
            )
        response.raise_for_status()
        task_id = response.json()["task_id"]
    except Exception as e:
        return Command(update={
            "past_steps": {(task_text, f"Task submission failed with filepath {filename}: {e}")}
        })

    # 2. Poll result
    result_data = None
    max_wait_seconds = 600
    poll_interval = 5
    waited = 0

    while waited < max_wait_seconds:
        try:
            response = session.get(
                RESULT_URL,
                params={"task_id": task_id}
            )
            response.raise_for_status()
            result_data = response.json()

            print(result_data)
            if result_data.get("status") == "ok":
                print('beaking')
                break
        except Exception as e:
            return Command(update={
                "past_steps": {(task_text, f"Result polling failed: {e}")}
            })

        time.sleep(poll_interval)
        waited += poll_interval

    if not result_data or result_data.get("status") != "ok":
        return Command(update={
            "past_steps": {(task_text, "Timed out waiting for result")}
        })

    return Command(update={
        "past_steps": {(task_text, result_data['text'])}
    })


def related_pubmed_literature_agent(state: dict, config: dict) -> Command:
    """
    Finds relevant papers in PubMed database by given keywords.
    Uses them to query PubMed. Then returns PICO-decomposition of relevant papers.
    
    Args:
        state (dict): A dictionary containing the task to be performed, accessible via the "task" key.
        config (dict): A dictionary containing configuration details.
    
    Returns:
        Command: A command object containing the agent's textual response, the updated task history (`past_steps`) including the current task and response,
            and a record of the agent call (`nodes_calls`) detailing the agent used and its input/output.
    """
    user_input = state['input']
    task = state["task"]
    paper_key = 'found_papers_' + user_input

    llm: BaseChatModel = config["configurable"]["model"]
    arg = (argument_extraction_prompt | llm).invoke({"prompt": task}).content

    if isinstance(arg, str):
        arg = [arg]

    lit_items = search_pubmed(arg, num_results=5)
    results = {}

    for idx, lit_item in enumerate(lit_items):
        taxonomy = get_taxonomy(lit_item, llm)
        pico = get_pico(lit_item, llm)

        results[idx] = {'paper': lit_item, 'taxonomy': taxonomy, "pico": pico}

    num_found = len(results)
    result_str = f'I have found {num_found} related papers for this task. Here are the titles: {'\n'.join([f'{idx+1}. {results[idx]['paper'].title}' for idx in range(num_found)])}'

    return Command(update={
        "past_steps": Annotated[set, operator.or_](set([(task, result_str)])),
        'metadata': Annotated[dict, operator.or_]({paper_key: results}) 
    })