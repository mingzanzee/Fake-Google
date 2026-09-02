from collections import defaultdict
import json
import math
from . import tokenizer
from . import stemmer

class Searcher:
    def __init__(self, indexer):
        # Instead of taking 5 separate variables, just take the indexer
        self.tfidf_index = indexer.tfidf_index
        self.documents = indexer.documents
        self.doc_norms = indexer.doc_norms
        self.idf = indexer.idf
        self.total_docs = indexer.total_docs
        # Keep a reference to the indexer just in case (optional)
        self.indexer = indexer 
    
    
    def search(self, query: str, k: int = 10):
        # Process query
        tokenized = tokenizer.tokenize(query)
        trimmed = tokenizer.remove_stopwords(tokenized)
        stemmed = stemmer.stem_tokens(trimmed)
        stemmed_non_unique = stemmed[0]
        stemmed_unique = stemmed[1]


        # calculate query Term Frequencies
        query_tf = defaultdict(int)
        for stem in stemmed_non_unique:
            query_tf[stem] += 1

        # normalize unique query terms
        query_length = len(stemmed_non_unique)
        for term in query_tf:
            # replace count with proportion of total words
            query_tf[term] /= query_length

        # find candidates
        candidates = set()
        for term in stemmed_unique:
            if term in self.tfidf_index:
                candidates.update(self.tfidf_index[term].keys())
    

        
        # ===== COMPLETE THE SCORING LOOP =====
        
        # Step 1: Build query vector (TF * IDF)
        query_vector = {}
        for term, tf in query_tf.items():
            idf = self.idf.get(term, 0)  # Get IDF from corpus
            query_vector[term] = tf * idf
        
        # Step 2: Calculate query norm
        query_norm = math.sqrt(sum(weight ** 2 for weight in query_vector.values()))

        
        # Step 3: Score each candidate document
        scores = []
        for doc_id in candidates:
            # Calculate dot product: sum(query_weight * doc_weight)
            dot_product = 0
            for term, query_weight in query_vector.items():
                # Check if the document has this term
                if term in self.tfidf_index and doc_id in self.tfidf_index[term]:
                    doc_weight = self.tfidf_index[term][doc_id]  # ← Already tf * idf!
                    dot_product += query_weight * doc_weight
            
            # Get document norm (pre-computed)
            doc_norm = self.doc_norms.get(doc_id, 1.0)
            
            # Calculate cosine similarity
            if query_norm == 0 or doc_norm == 0:
                score = 0
            else:
                score = dot_product / (query_norm * doc_norm)
            
            scores.append((score, doc_id))

        

        # Step 4: Sort and return top-k
        scores.sort(reverse=True)  # Highest score first
        top_k = scores[:k]

        # Step 5: Get document details for results
        results = []
        for score, doc_id in top_k:
            doc = self.documents[str(doc_id)] # [1] bug fixed
            results.append({
                "id": doc_id,
                "title": doc["title"],
                "score": score,
                "snippet": self._get_snippet(doc["content"], query)
            })

        print("search done", flush=True)
        return results
    
    def _get_snippet(self, content: str, query: str, max_len: int = 200) -> str:
        """Generate a snippet with highlighted query terms."""
        if len(content) <= max_len:
            return content
        return content[:max_len] + "..."