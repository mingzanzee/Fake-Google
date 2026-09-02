25/7/2026: On the server, making a query with any relevant word causes an error. While making a query with an irrelevant word correctly returns no result found.
    i realised that the number after cross corresponds to the doc_id of the matching documents, so it should have no problem opening the data files.
    Probably a html side error as it was built by AI, or the AI didnt make it return the matching text on the webpage.
    it is a response not OK error (500)
    after some investigation i found that the line "candidates.update(self.tfidf_index[term].keys())" causes the error as keys is all of the id, title and body.
    problem occurs in step 5 of search function
    my self.documents is somehow empty
28/7/2026: Refactored Indexer.py, removed document_store.py as I wanted to fully delegate the task of processing, storing and loading data to the Indexer class. Still having the http error. 
30/7/2026: Error caused by last step of the searcher function.
    Error was due to doc_id from top_k being an integer, but in the json file the doc_id keys are strings. [1]
    Bug is solved.
    Now I need to extend the functionality to click into the search results

