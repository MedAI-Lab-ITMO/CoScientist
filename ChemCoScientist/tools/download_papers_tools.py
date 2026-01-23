import logging
from langchain_core.tools import tool
from langchain.tools.render import render_text_description

from ChemCoScientist.download_papers.download_papers_utils import download_papers
from ChemCoScientist.download_papers.prompts import OPENALEX_QUERY_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tool
def download_papers_from_web(task: str, session_id: str = "1") -> None:
    """
    Searches for scientific papers and downloads their PDFs based on a user query using the OpenAlex API
    and PaperScraper as a fallback.

    Parameters
    ----------
    task (str): The user query for which papers are to be downloaded.
    session_id (str, optional): An identifier for the session. Defaults to "1".

    Returns
    -------
    List[str]: A list of file paths to the downloaded PDFs.
    """
    try:
        print('Running download_papers_from_web tool...')
        print(f'task: {task}')
        return download_papers(task)
    except Exception as e:
        logger.error(f'download_papers_from_web ERROR: {e}')
        return {'answer': 'Could not download any papers from web.'}
        

download_papers_tools = [download_papers_from_web]

download_papers_tools_rendered = render_text_description(download_papers_tools)