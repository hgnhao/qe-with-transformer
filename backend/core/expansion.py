import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class QueryExpander:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        logger.info(f"Memuat model transformer {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.vocab = []
        self.vocab_embeddings = None

    def fit_vocab(self, vocabulary: List[str]):
        # enkode seluruh kosakata, dipakai untuk pencarian nearest-neighbor saat ekspansi
        logger.info(f"Mengenkode {len(vocabulary)} kata kosakata...")
        new_embeddings = self.model.encode(vocabulary, show_progress_bar=True, batch_size=256)
        self.vocab = vocabulary
        self.vocab_embeddings = new_embeddings
        logger.info("Enkode kosakata selesai.")

    def expand_query(self, query_terms: List[str], top_k: int = 5, all_terms: bool = False, threshold: float = 0.5) -> Dict[str, float]:
        expanded = {}
        if not self.vocab or self.vocab_embeddings is None:
            return expanded

        if not query_terms:
            return expanded

        # enkode kueri sebagai satu string agar konteks antar kata tertangkap
        query_string = " ".join(query_terms)
        query_emb = self.model.encode([query_string])

        similarities = cosine_similarity(query_emb, self.vocab_embeddings)[0]

        # filter kata yang sudah ada di kueri
        valid_indices = [i for i, term in enumerate(self.vocab) if term not in query_terms]

        if not valid_indices:
            return expanded

        valid_vocab = np.array(self.vocab)[valid_indices]
        valid_sims = similarities[valid_indices]

        if all_terms:
            # tambahkan semua kata di atas threshold
            for term, sim in zip(valid_vocab, valid_sims):
                if sim >= threshold:
                    expanded[str(term)] = float(sim)
        else:
            # ambil top-k kata paling mirip
            top_indices = np.argsort(valid_sims)[::-1][:top_k]
            for idx in top_indices:
                sim = valid_sims[idx]
                if sim > 0:
                    expanded[str(valid_vocab[idx])] = float(sim)

        return expanded

    def get_expansion_stats(self, expansion_result: Dict[str, float]) -> Dict[str, float]:
        # statistik dasar hasil ekspansi: min, maks, rata-rata skor similarity
        if not expansion_result:
            return {"min": 0.0, "max": 0.0, "avg": 0.0, "count": 0}

        scores = list(expansion_result.values())
        return {
            "min": round(min(scores), 4),
            "max": round(max(scores), 4),
            "avg": round(sum(scores) / len(scores), 4),
            "count": len(scores)
        }
