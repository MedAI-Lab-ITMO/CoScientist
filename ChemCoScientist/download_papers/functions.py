
import requests
import re
import os
import time
import base64
import logging
from typing import Dict, List, Any

from paperscraper.pdf import save_pdf
from protollm.connectors import create_llm_connector, get_allowed_providers
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from definitions import CONFIG_PATH

from ChemCoScientist.download_papers.prompts import OPENALEX_QUERY_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(CONFIG_PATH)
VISION_LLM_URL = os.environ.get("VISION_LLM_URL")
DOWNLOADED_PAPERS_PATH = os.environ.get("DOWNLOADED_PAPERS_PATH")


def sanitize_filename(name: str) -> str:
    """Remove invalid filename characters from a string."""
    return re.sub(r'[\\/*?:"<>|]', "", name)


def request_with_retry(
    url: str,
    max_retries: int = 3,
    timeout: int = 30
) -> requests.Response:
    """Make an HTTP GET request with automatic retry logic for rate limits and server errors."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                # Rate limited
                wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
                time.sleep(wait_time)
            elif response.status_code >= 500:
                # Server error
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                # Other error, don't retry
                response.raise_for_status()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print("Retrying... Attempt", attempt + 2)
                time.sleep(2 ** attempt)
            else:
                raise
    raise Exception(f"Failed after {max_retries} retries")


def download_from_openalex(pdf_url: str, paper_title: str) -> str:
    """Download a PDF from a given URL and save it with a sanitized paper title."""
    response = request_with_retry(pdf_url)
    filepath = f"{DOWNLOADED_PAPERS_PATH}/{sanitize_filename(paper_title)}.pdf"
    with open(filepath, "wb") as f:
        f.write(response.content)
    print(f"Downloaded: {filepath}")
    return filepath
        
        
def download_from_paperscraper(doi: str, title: str) -> str:
    """Download a PDF using PaperScraper given a DOI and paper title."""
    filepath = f'/{sanitize_filename(title)}.pdf'
    paper_data = {'doi': doi}
    try:
        save_pdf(paper_data, filepath=filepath)
        if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
            raise Exception("Failed to download from PaperScraper")
        print(f"Downloaded {title} using PaperScraper.")
        return filepath
    except Exception as e:
        raise


def search_openalex(query: str, openalex_docs_path: str = "ChemCoScientist/tools/OpenAlex technical documentation.pdf") -> Dict[str, Any]:
    """Search for scientific papers on OpenAlex using an LLM to generate the appropriate API request."""
    llm = create_llm_connector(VISION_LLM_URL, extra_body={"provider": {"only": get_allowed_providers()}})

    content = []

    with open(openalex_docs_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    paper_part = {
        "type": "file",
        "file": {
            "filename": openalex_docs_path,
            "file_data": f"data:application/pdf;base64,{base64_pdf}",
        },
    }
    content.append(paper_part)

    text_part = {"type": "text", "text": f"USER QUESTION: {query}"}
    content.append(text_part)

    messages = [
        SystemMessage(content=OPENALEX_QUERY_PROMPT),
        HumanMessage(content=content)
    ]

    res = llm.invoke(messages)
    print("Generated OpenAlex API request URL:", res.content)
    response = request_with_retry(res.content)
    return response.json()
    

def process_doi(doi: str) -> str:
    """Extract the DOI from a DOI URL."""
    return re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)


def download_papers(task: str) -> List[str]:
    """Search for papers matching a task query and download their PDFs using OpenAlex and PaperScraper."""
    response = search_openalex(task)
    print("Downloading PDFs...")
    downloaded_papers = []
    for work in response.get("results", []):
        title = work["title"]
        oa_info = work.get("open_access", {})
        pdf_url = oa_info.get("oa_url", None)

        if pdf_url:
            print(f"Title: {title}\nPDF URL: {pdf_url}\n")
            try:
                print("Trying to download from OpenAlex...")
                filepath = download_from_openalex(pdf_url, title)
                downloaded_papers.append(filepath)
            except Exception as e:
                print(f"Failed to download from OpenAlex: {e}")
                print("Trying PaperScraper...")
                try:
                    doi = process_doi(work.get("doi", None))
                    print(f"DOI: {doi}")
                    filepath = download_from_paperscraper(doi, title)
                    downloaded_papers.append(filepath)
                except Exception as e2:
                    print(f"{e2}")
    return {'answer': 'These are downloaded papers:',
            'metadata': {'dataset': downloaded_papers}}

if __name__ == "__main__":
    result = download_papers("find 2 papers onadvances in CRISPR gene editing technology since 2024")
    print(result)