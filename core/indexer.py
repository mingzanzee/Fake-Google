# core/indexer.py
import json
import math
from collections import defaultdict
from core.tokenizer import tokenize, remove_stopwords
from core.stemmer import stem_tokens

class Indexer:
    def __init__(self, index_path: str = "data/documents.json", auto_load: bool = True):
        self.documents = {}                   # DICT of {id, title, content}
        self.doc_tf = {}                       # doc_id -> {term: frequency}
        self.term_frequencies = defaultdict(dict)  # term -> {doc_id: frequency}  <-- RAW COUNTS
        self.tfidf_index = defaultdict(dict)       # term -> {doc_id: tf_idf_weight} <-- WEIGHTED
        self.doc_norms = {}                    # doc_id -> magnitude
        self.idf = {}                          # term -> idf value
        self.total_docs = 0

        # Auto-load if requested
        if auto_load:
            try:
                self.load_index(index_path)
                print(f"✅ Index loaded from {index_path}")
            except FileNotFoundError:
                print(f"⚠️ No existing index found at {index_path}. Starting fresh.")
            except Exception as e:
                print(f"⚠️ Error loading index: {e}. Starting fresh.")
    
    def add_document(self, title: str, content: str):
        """Add a document to the index."""
        # Store document
        doc_id = len(self.documents) + 1
        self.documents[doc_id] = ({
            "id": doc_id,
            "title": title,
            "content": content
        })
        
        # Process content
        tokens = tokenize(content)
        tokens = remove_stopwords(tokens)
        stems = stem_tokens(tokens)[0]  # Keep duplicates for TF!
        
        # Calculate term frequencies
        tf = defaultdict(int)
        for stem in stems:
            tf[stem] += 1
        
        # Store document TF (raw frequencies)
        self.doc_tf[doc_id] = dict(tf)
        
        # Store term frequencies (for IDF calculation)
        for term, freq in tf.items():
            self.term_frequencies[term][doc_id] = freq
        
        self.total_docs += 1
    
    def finalize_index(self):
        """
        Calculate IDF and document norms after all documents are indexed.
        Formulae from: https://www.geeksforgeeks.org/machine-learning/understanding-tf-idf-term-frequency-inverse-document-frequency/
        """
        # Step 1: Calculate IDF for all terms
        for term, doc_freqs in self.term_frequencies.items():
            doc_count = len(doc_freqs)
            if doc_count > 0:
                self.idf[term] = math.log(self.total_docs / doc_count)
            else:
                self.idf[term] = 0
        
        # Step 2: Build TF-IDF index from term frequencies
        for term, doc_freqs in self.term_frequencies.items():
            idf = self.idf.get(term, 0)
            for doc_id, freq in doc_freqs.items():
                self.tfidf_index[term][doc_id] = freq * idf
        
        # Step 3: Calculate document norms using TF-IDF weights
        for doc_id, tf in self.doc_tf.items():
            norm = 0
            for term, freq in tf.items():
                weight = freq * self.idf.get(term, 0)
                norm += weight ** 2
            self.doc_norms[doc_id] = math.sqrt(norm)

    # TODO: rename path and refactor functionality to store everything instead
    def save_index(self, index_path: str = "data/documents.json"):
        """Save the TF-IDF index to disk."""
        # Convert to serializable format
        serializable_index = {
            term: dict(doc_weights) 
            for term, doc_weights in self.tfidf_index.items()
        }
        
        # ✅ Convert defaultdict to dict
        term_freq_dict = dict(self.term_frequencies)
        
        data = {
            "documents": self.documents,  # ← Already a dict, keep as dict
            "doc_tf": self.doc_tf,
            "term_frequencies": term_freq_dict,
            "tfidf_index": serializable_index,
            "doc_norms": self.doc_norms,
            "idf": self.idf,
            "total_docs": self.total_docs
        }
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(self.documents)} documents to index")
    
    def load_index(self, index_path: str = "data/documents.json"):
        """Load the TF-IDF index from disk."""
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Load documents - handle both dict and list
        docs_data = data.get("documents", {})
        if isinstance(docs_data, dict):
            # Already a dict (doc_id -> doc)
            self.documents = docs_data
            print(f"📚 Loaded {len(self.documents)} documents (dict format)")
        elif isinstance(docs_data, list):
            # Convert list to dict
            self.documents = {doc["id"]: doc for doc in docs_data}
            print(f"📚 Loaded {len(self.documents)} documents (converted from list)")
        else:
            self.documents = {}
            print("⚠️ No documents found in index file")

        # 2. Load doc_tf
        doc_tf_data = data.get("doc_tf", {})
        self.doc_tf = {}
        for doc_id, tf in doc_tf_data.items():
            self.doc_tf[int(doc_id)] = dict(tf)

        # 3. Load term_frequencies (convert back to defaultdict)
        tf_data = data.get("term_frequencies", {})
        self.term_frequencies = defaultdict(dict)
        for term, doc_freqs in tf_data.items():
            self.term_frequencies[term] = {
                int(doc_id): freq for doc_id, freq in doc_freqs.items()
            }

        # 4. Load tfidf_index
        tfidf_data = data.get("tfidf_index", {})
        self.tfidf_index = defaultdict(dict)
        for term, doc_weights in tfidf_data.items():
            self.tfidf_index[term] = {
                int(doc_id): weight for doc_id, weight in doc_weights.items()
            }

        # 5. Load doc_norms
        self.doc_norms = {int(doc_id): norm for doc_id, norm in data.get("doc_norms", {}).items()}

        # 6. Load idf and total_docs
        self.idf = data.get("idf", {})
        self.total_docs = data.get("total_docs", 0)
        
        print(f"✅ Index loaded successfully!")
        print(f"   - Documents: {len(self.documents)}")
        print(f"   - Unique terms: {len(self.idf)}")
    
    def get_stats(self):
        """Return statistics about the index."""
        return {
            "total_docs": self.total_docs,
            "unique_terms": len(self.term_frequencies),
            "total_term_occurrences": sum(len(doc_freqs) for doc_freqs in self.term_frequencies.values())
        }