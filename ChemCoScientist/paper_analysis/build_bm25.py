from rank_bm25 import BM25Okapi
import json, pickle
from collections import defaultdict
from pathlib import Path
from tokenizer import SciSpacyTokenizer

from ChemCoScientist.paper_analysis.chroma_db_operations import ChromaClient

def build_bm25_index(collection_name="bm25_text_context_img2txt", save_dir="ChemCoScientist/paper_analysis"):
    """Tokenizes articles, builds BM25 index with tokenized corpus and saves it."""
    
    client = ChromaClient()
    collection = client.get_or_create_chroma_collection(collection_name)
    results = collection.get(include=["documents", "metadatas"])
    documents = results["documents"]
    metadatas = results["metadatas"]
    
    tokenizer = SciSpacyTokenizer()
    
    articles = defaultdict(list)
    for doc, meta in zip(documents, metadatas):
        source = meta.get("source")
        articles[source].append(doc)
        
    full_articles = {source: " ".join(chunks) for source, chunks in articles.items()}
    
    tokenized_corpus = []
    metadata = []
    for source, text in full_articles.items():
        tokens = tokenizer(text)
        tokenized_corpus.append(tokens)
        metadata.append({"source": source})
    print(tokenized_corpus[0])
    
    bm25 = BM25Okapi(tokenized_corpus)

    with open(Path(save_dir) / "bm25_index.pkl", "wb") as f:
        pickle.dump(bm25, f)
        
    with open(Path(save_dir) / "bm25_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"BM25 index created and saved to {save_dir}/bm25_index.pkl")

if __name__ == "__main__":
    build_bm25_index()
