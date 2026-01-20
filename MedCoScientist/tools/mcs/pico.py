from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from MedCoScientist.tools.mcs.pubmed import LitItem


class StructuredResponse(BaseModel):
    """The final output structure."""
    population: str = Field(description="The target patient population with characteristics.")
    intervention: str = Field(description="The main intervention, treatment, or procedure.")
    comparison: str = Field(description="The comparative intervention or control.")
    outcome: str = Field(description="The measured clinical outcome.")
    # reasoning: str = Field(description="Brief explanation for the category choice.")

prompt = ChatPromptTemplate.from_template("""
You are a medical AI assistant specializing in extracting PICO elements from research abstracts or hypotheses.

Definition of PICO:
* population: The target patient population with characteristics
* intervention: The main intervention, treatment, or procedure
* comparison: The comparative intervention or control
* outcome: The measured clinical outcome

Extract PICO element from this paper given the title and the abstrac.

Title: {title}

Abstract: {abstract}
""")

def get_pico(lit_item:LitItem, llm):
    args = {"title": lit_item.title, "abstract": lit_item.abstract}

    try:
        chain = (prompt | llm.with_structured_output(StructuredResponse))
        result = chain.invoke(args)
        return result
    except:
        return None