import spacy

class SciSpacyTokenizer:
    """
    SciSpaCy tokenizer for chemical texts.
    Converts text into lowercased tokens excluding punctuation.
    """

    def __init__(self, model_name="en_core_sci_sm", lowercase=True, remove_punct=True):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(
                f"SpaCy model '{model_name}' not found.\n"
            )
        self.lowercase = lowercase
        self.remove_punct = remove_punct

    def __call__(self, text: str):
        doc = self.nlp(text)
        tokens = []
        for token in doc:
            if self.remove_punct and (token.is_punct or token.is_space):
                continue
            tok = token.text
            if self.lowercase:
                tok = tok.lower()
            tokens.append(tok)
        return tokens
