import re

def tokenize(text: str) -> list[str]:
    """
    Convert text into a list of lowercase alphanumeric tokens.
    
    Example:
        >>> tokenize("Hello, World! 123")
        ['hello', 'world', '123']
    """
    """
    Inferior implementation:
    # first separate words by space
    text_arr = text.split()

    # prune off punctuations and convert to lower
    out_arr = []

    for word in text_arr:
        pruned = re.sub(r'[^a-zA-Z0-9]', '', word).lower()
        if pruned:
            out_arr.append(pruned)

    return out_arr
    """

    # Find all alphanumeric sequences in one pass
    return re.findall(r'[a-zA-Z0-9]+', text.lower())



def remove_stopwords(tokens: list[str]) -> list[str]:
    """
    Remove common words from tokens to reduce noise and computational overhead
    "In TF-IDF, stopwords naturally get low IDF scores because they appear in almost all documents. 
    However, explicitly removing them before indexing has two benefits: 
    it shrinks the inverted index size, and it prevents these terms from contributing to cosine similarity calculations at all 
        – effectively giving them a weight of zero rather than a very small number. 
    This improves both performance and retrieval quality."
    """

    STOPWORDS = {'the', 'a', 'an', 'of', 'for', 'on', 'at', 'to', 'in', 'and', 'or', 'but'}

    return [t for t in tokens if t not in STOPWORDS]