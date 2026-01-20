from typing import List
from metapub import PubMedFetcher
from dataclasses import dataclass


@dataclass
class LitItem:
    title: str
    authors: List[str]
    journal: str
    year: str
    abstract: str
    # link: str

def search_pubmed(keywords:List[str], num_results:int=10) -> List[LitItem]:
    pubmed_query = " AND ".join(keywords)

    # Initialize the fetcher
    fetch = PubMedFetcher()

    # Search for articles
    pmids = fetch.pmids_for_query(pubmed_query, retmax=num_results)

    # Get article details
    lit_items = []
    for pmid in pmids:
        article = fetch.article_by_pmid(pmid)
        lit_item = LitItem(
            title=article.title, 
            authors=article.authors,
            journal=article.journal,
            year=article.year,
            abstract=article.abstract
            # link=article.link
        )
        lit_items.append(lit_item)
    return lit_items