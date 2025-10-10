import pickle, json
from pathlib import Path
from tokenizer import SciSpacyTokenizer

class BM25Retriever:
    def __init__(self, index_path="ChemCoScientist/paper_analysis/bm25_index.pkl", metadata_path="ChemCoScientist/paper_analysis/bm25_metadata.json"):
        with open(index_path, "rb") as f:
            self.bm25 = pickle.load(f)
        with open(metadata_path, "r") as f:
            self.metadata = json.load(f)
        self.tokenizer = SciSpacyTokenizer()

    def retrieve(self, query: str, top_n: int = 5):
        tokenized_query = self.tokenizer(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
        return [self.metadata[i] | {"score": scores[i]} for i in top_idx]
    
bm25 = BM25Retriever()
query = "In which solvent did the reaction of [3+2]-cycloaddition of 3-Cyanochromone 1a and N-Cyclopropyloaniline 2a produce the lowest yield?"
bm25_results = bm25.retrieve(query, top_n=3)
print(bm25_results)

