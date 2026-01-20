from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


class LitCategory(str, Enum):
    """Enumeration of possible output categories."""
    HISTORICAL = "historical"
    SYSTEMATIC = "systematic"
    METAANALYSIS = "meta-analysis"

class LitStructuredResponse(BaseModel):
    """The final output structure."""
    category: LitCategory = Field(description="The assigned category from the allowed options.")
    reasoning: str = Field(description="Brief explanation for the category choice.")

prompt = ChatPromptTemplate.from_template(
"You are a medical AI assistant specializing in research type analysis." 
" You are analyzing a paper with a literature review."
" You are given the title and the abstract of the paper."
" Your task is to determine this is literature review is historical, systematic, or meta-analysis."
"""
Title: {title}

Abstract: {abstract}
""")