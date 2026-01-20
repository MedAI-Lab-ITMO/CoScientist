from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


class Category(str, Enum):
    """Enumeration of possible output categories."""
    OBSERVATIONAL = "observational"
    EXPERIMENTAL = "experimental"
    LITREVIEW = "literature review"

class StructuredResponse(BaseModel):
    """The final output structure."""
    category: Category = Field(description="The assigned category from the allowed options.")
    reasoning: str = Field(description="Brief explanation for the category choice.")

prompt = ChatPromptTemplate.from_template("""
You are a medical AI assistant specializing in research type analysis. Your task is to determine the type of study conducted based on the article's title and abstract.
Is the type of the study: observational, experimental, or literature review?

Title: {title}

Abstract: {abstract}
""")