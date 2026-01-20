from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


class DistrCategory(str, Enum):
    """Enumeration of possible output categories."""
    RANDOMIZED = "randomized"
    NONRANDOMIZED = "non-randomized"
    PROPENSITY = "propensity score matching"

class DistrStructuredResponse(BaseModel):
    """The final output structure."""
    category: DistrCategory = Field(description="The assigned category from the allowed options.")
    reasoning: str = Field(description="Brief explanation for the category choice.")

prompt = ChatPromptTemplate.from_template(
"You are a medical AI assistant specializing in research type analysis." 
" You are analyzing a paper with an experimental study."
" You are given the title and the abstract of the paper."
" Your task is to determine this study is randomized, non-randomized, or propensity score matching."
"""
Title: {title}

Abstract: {abstract}
""")