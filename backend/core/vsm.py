import math
from typing import Dict, List, Tuple
from collections import defaultdict
from .ir_engine import IREngine

def calculate_tf(tf_raw: int, max_tf: int, variant: str) -> float:
    if tf_raw == 0:
        return 0.0

    if variant == "raw":
        return float(tf_raw)
    elif variant == "logarithmic":
        return 1.0 + math.log10(tf_raw)
    elif variant == "binary":
        return 1.0
    elif variant == "augmented":
        if max_tf == 0: return 0.5
        return 0.5 + (0.5 * tf_raw / float(max_tf))
    else:
        return float(tf_raw)

def calculate_idf(df: int, N: int) -> float:
    if df == 0: return 0.0
    return math.log10(float(N) / float(df))

class VSM:
    def __init__(self, ir_engine: IREngine):
        self.ir = ir_engine

    def get_document_vector(self, doc_id: int, scheme: str, tf_variant: str = "raw") -> Dict[str, float]:
        # jarang dipakai langsung karena vektor dokumen dihitung saat similarity
        vector = {}
        return vector

    def calculate_similarity(self, query_terms: Dict[str, float], scheme: str, tf_variant: str = "raw") -> Dict[int, float]:
        scores = defaultdict(float)
        query_norm = 0.0

        N = self.ir.document_count

        for term, q_weight in query_terms.items():
            if term not in self.ir.inverted_index:
                continue

            df = self.ir.term_doc_freqs[term]
            idf = calculate_idf(df, N)

            postings = self.ir.inverted_index[term]
            for doc_id, tf_raw in postings.items():
                max_tf = self.ir.doc_max_freqs.get(doc_id, 1)
                tf_weight = calculate_tf(tf_raw, max_tf, tf_variant)

                doc_weight = 0.0
                if scheme == "tf":
                    doc_weight = tf_weight
                elif scheme == "idf":
                    doc_weight = idf
                elif scheme == "tf-idf" or scheme == "tf-idf-cosine":
                    doc_weight = tf_weight * idf

                scores[doc_id] += q_weight * doc_weight

        # normalisasi cosine
        if scheme == "tf-idf-cosine":
            for term, q_weight in query_terms.items():
                query_norm += q_weight ** 2
            query_norm = math.sqrt(query_norm) if query_norm > 0 else 1.0

            for doc_id in scores.keys():
                d_norm_sq = 0.0
                max_tf = self.ir.doc_max_freqs.get(doc_id, 1)

                for d_term, tf_raw in self.ir.forward_index[doc_id].items():
                    d_df = self.ir.term_doc_freqs[d_term]
                    d_idf = calculate_idf(d_df, N)
                    d_tf_weight = calculate_tf(tf_raw, max_tf, tf_variant)
                    d_norm_sq += (d_tf_weight * d_idf) ** 2

                d_norm = math.sqrt(d_norm_sq) if d_norm_sq > 0 else 1.0
                scores[doc_id] = scores[doc_id] / (query_norm * d_norm)

        return scores

    def rank_documents(self, query_terms: Dict[str, float], scheme: str, tf_variant: str = "raw", top_n: int = 100) -> List[Tuple[int, float]]:
        scores = self.calculate_similarity(query_terms, scheme, tf_variant)

        # urut skor dari tertinggi
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return ranked[:top_n]
