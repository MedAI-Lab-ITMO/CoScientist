import pickle, json
from pathlib import Path
from tokenizer import SciSpacyTokenizer

class BM25Retriever:
    def __init__(self, index_path="data/bm25_index.pkl", metadata_path="data/bm25_metadata.json"):
        with open(index_path, "rb") as f:
            self.bm25 = pickle.load(f)
        with open(metadata_path, "r") as f:
            self.metadata = json.load(f)

    def retrieve(self, query: str, top_n: int = 5):
        tokenized_query = SciSpacyTokenizer(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
        return [self.metadata[i] | {"score": scores[i]} for i in top_idx]
