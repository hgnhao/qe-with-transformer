import math
from collections import defaultdict
from typing import Dict, List, Set, Any
from .preprocess import preprocess_text

class IREngine:
    def __init__(self):
        self.inverted_index: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self.forward_index: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.doc_lengths: Dict[int, int] = {}
        self.doc_max_freqs: Dict[int, int] = {}
        self.document_count = 0
        self.term_doc_freqs: Dict[str, int] = defaultdict(int)
        
        self.docs_metadata = {} # Store title, author, abstract for retrieval

    def build_index(self, documents: Dict[int, Dict[str, str]], apply_stemming: bool = True, remove_stopwords: bool = True):
        """
        Build inverted index from documents.
        documents: Dict[doc_id, {"title": title, "abstract": abstract, "author": author, "content": full_text}]
        """
        self.inverted_index.clear()
        self.forward_index.clear()
        self.doc_lengths.clear()
        self.doc_max_freqs.clear()
        self.term_doc_freqs.clear()
        self.docs_metadata = documents
        self.document_count = len(documents)

        for doc_id, doc_data in documents.items():
            text = doc_data["content"]
            tokens = preprocess_text(text, apply_stemming=apply_stemming, remove_stopwords=remove_stopwords)
            
            self.doc_lengths[doc_id] = len(tokens)
            
            # Count frequencies
            term_counts = defaultdict(int)
            for token in tokens:
                term_counts[token] += 1
                
            if term_counts:
                self.doc_max_freqs[doc_id] = max(term_counts.values())
            else:
                self.doc_max_freqs[doc_id] = 1 # Avoid division by zero
                
            for term, count in term_counts.items():
                self.inverted_index[term][doc_id] = count
                self.forward_index[doc_id][term] = count
                self.term_doc_freqs[term] += 1
                
    def get_inverted_file_for_doc(self, doc_id: int) -> List[Dict[str, Any]]:
        """
        Returns the inverted file data specifically for a given doc_id.
        This represents the terms in the document and their frequencies/postings.
        """
        if doc_id not in self.doc_lengths:
            return []
            
        result = []
        for term, postings in self.inverted_index.items():
            if doc_id in postings:
                result.append({
                    "term": term,
                    "frequency": postings[doc_id],
                    "total_doc_frequency": self.term_doc_freqs[term]
                })
        
        # Sort by frequency descending
        result.sort(key=lambda x: x["frequency"], reverse=True)
        return result
