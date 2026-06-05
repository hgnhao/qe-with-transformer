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

        # menyimpan judul, penulis, abstrak tiap dokumen
        self.docs_metadata = {}

    def build_index(self, documents: Dict[int, Dict[str, str]], apply_stemming: bool = True, remove_stopwords: bool = True):
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

            # hitung frekuensi tiap kata
            term_counts = defaultdict(int)
            for token in tokens:
                term_counts[token] += 1

            if term_counts:
                self.doc_max_freqs[doc_id] = max(term_counts.values())
            else:
                # hindari pembagian dengan nol
                self.doc_max_freqs[doc_id] = 1

            for term, count in term_counts.items():
                self.inverted_index[term][doc_id] = count
                self.forward_index[doc_id][term] = count
                self.term_doc_freqs[term] += 1

    def get_inverted_file_for_doc(self, doc_id: int) -> List[Dict[str, Any]]:
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

        # urut berdasarkan frekuensi tertinggi
        result.sort(key=lambda x: x["frequency"], reverse=True)
        return result
