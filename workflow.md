User Query: "python programming"
    ↓
Tokenize: ["python", "programming"]
    ↓
Stem: ["python", "program"] (Porter stemmer)
    ↓
Remove stopwords: (none removed here)
    ↓
Look up in inverted index:
    "python" → [doc1, doc3, doc7]
    "program" → [doc1, doc2, doc5]
    ↓
Candidate docs = {doc1, doc2, doc3, doc5, doc7}  (only 5 docs instead of 10,000)
    ↓
For each candidate, compute TF-IDF vector and cosine similarity to query
    ↓
Push (score, doc_id) into min-heap of size K=10
    ↓
Return top 10 documents with titles and snippets