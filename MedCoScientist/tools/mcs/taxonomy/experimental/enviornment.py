from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

class Category(str, Enum):
    """Enumeration of possible output categories."""
    CLINICAL = "clinical"
    IN_VIVO = "in vivo"
    IN_VITRO = "in vitro"
    IN_SILICO = "in silico"

class StructuredResponse(BaseModel):
    """The final output structure."""
    category: Category = Field(description="The assigned category from the allowed options.")
    reasoning: str = Field(description="Brief explanation for the category choice.")

prompt = ChatPromptTemplate.from_template(
"You are a medical AI assistant specializing in research type analysis." 
" You are analyzing a paper with an experimental study."
" You are given the title and the abstract of the paper."
" Your task is to determine whether this study is clinical, in vivo, in vitro, or in silico"
"""
Title: {title}

Abstract: {abstract}
""")