import ast
import re

from langchain.tools.render import render_text_description
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool

from MedCoScientist.agents.tools_prompts import (
    extract_concepts_prompt,
    extract_keywords_prompt
)


def _process_list(text: str) -> list:
    return [item.strip() for item in text.split(",") if item.strip()]

def _process_string_to_dict(text: str) -> dict:
    start_index = text.find('{')
    end_index = text.rfind('}') + 1

    dict_str = text[start_index:end_index].strip()

    return ast.literal_eval(dict_str)

def _mask_text(text: str, words_to_mask: list) -> str:
    """
    Заменяет все слова из списка на [MASKED] в исходном тексте.
    Регистронезависимо, заменяет только целые слова.
    """
    pattern = r'\b(' + '|'.join(map(re.escape, words_to_mask)) + r')\b'
    
    masked_text = re.sub(pattern, '[MASKED]', text, flags=re.IGNORECASE)
    return masked_text

# @ tool
def extract_keywords_node(hypothesis: str, llm: BaseChatModel) -> str:
    """
    Extracts keywords from the hypothesis by saliency.
    
    This method utilizes a language model to evaluate the saliency.
    
    Args:
        hypothesis (str): A textual formulation of the hypothesis.
        config (RunnableConfig): Configuration object containing the language model to be used for saliency evaluation.
    
    Returns:
        keywords (str): A string containing the list of dectected keywords separated with a comma. May return an error message if prediction fails.
    """
    try:
        chain = extract_concepts_prompt | llm
        key_concepts = chain.invoke(hypothesis).content
        
        chain = extract_keywords_prompt | llm
        key_words = chain.invoke({"hypothesis": hypothesis, "key_concepts": key_concepts}).content

        key_concepts = _process_list(key_concepts)
        key_words = _process_string_to_dict(key_words)
        return ", ".join([word for words in key_words.values() for word in words])
    except Exception as e:
        return f"I couldn't extract keywords because of: {str(e)}, I should move to the next task if any"

# keywords_tools = [
#     extract_keywords_node,
# ]

# keywords_tools_rendered = render_text_description(keywords_tools)
