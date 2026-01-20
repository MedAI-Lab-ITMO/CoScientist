from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


class Category(str, Enum):
    """Enumeration of possible output categories."""
    CROSS_SECTIONAL = "cross-sectional"
    COHORT = "cohort"
    CASE_CONTROL = "case-control"

class StructuredResponse(BaseModel):
    """The final output structure."""
    category: Category = Field(description="The assigned category from the allowed options.")
    reasoning: str = Field(description="Brief explanation for the category choice.")

prompt = ChatPromptTemplate.from_template(
"You are a medical AI assistant specializing in research type analysis." 
" You are analyzing a paper with an observational study."
" You are given the title and the abstract of the paper."
" Your task is to determine whether this study is cross-sectional, cohort, case-control."
"""
Title: {title}

Abstract: {abstract}
""")