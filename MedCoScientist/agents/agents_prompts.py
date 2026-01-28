from langchain_core.prompts import ChatPromptTemplate


memory_prompt = ChatPromptTemplate.from_template(
    """If the response suffers from the lack of memory, adjust it. Don't add any of your comments

Your objective is this:
input: {input};
response: {response};
memory {summary};
"""
)

worker_prompt = "You are a helpful assistant. You can use provided tools. \
    If there is no appropriate tool, or you can't use one, answer yourself"

argument_extraction_prompt = ChatPromptTemplate.from_template(
    """Your task is to extract keywords from a given prompt. Your answer must be number of keywords divided by comma.
    For example for the prompt 'I would like to find relevant PubMed papers for the following keywords: hypophysitis MRI, Xray spectroscopy, lung cancer' 
    you should return:  hypophysitis MRI, Xray spectroscopy, lung cancer
    Here is the prompt of interest: {prompt}"""
    )
