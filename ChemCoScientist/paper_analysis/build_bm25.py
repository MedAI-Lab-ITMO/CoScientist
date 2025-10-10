from rank_bm25 import BM25Okapi
import json, pickle
from collections import defaultdict
from pathlib import Path
from tokenizer import SciSpacyTokenizer

from ChemCoScientist.paper_analysis.chroma_db_operations import ChromaClient

def build_bm25_index(collection_name="text_context_img2txt", save_dir="ChemCoScientist/paper_alaysis"):
    """Tokenizes articles, builds BM25 index with tokenized corpus and saves it."""
    
    client = ChromaClient()
    collection = client.get_or_create_chroma_collection(collection_name)
    results = collection.get(include=["documents", "metadatas"])
    documents = results["documents"]
    metadatas = results["metadatas"]
    
    articles = defaultdict(list)
    for doc, meta in zip(documents, metadatas):
        article_id = meta.get("article_id") or meta.get("source") or "unknown"
        articles[article_id].append(doc)
        
    full_articles = {aid: " ".join(chunks) for aid, chunks in articles.items()}
    
    tokenized_corpus = []
    for article_id, text in full_articles.items():
        tokens = SciSpacyTokenizer(text)
        tokenized_corpus.append(tokens)
        
    
    bm25 = BM25Okapi(tokenized_corpus)

    with open(Path(save_dir) / "bm25_index.pkl", "wb") as f:
        pickle.dump(bm25, f)

    print(f"BM25 index created and saved to {save_dir}/bm25_index.pkl")

if __name__ == "__main__":
    build_bm25_index()
