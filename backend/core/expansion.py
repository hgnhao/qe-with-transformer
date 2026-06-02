import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class QueryExpander:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        logger.info(f"Loading transformer model {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.vocab = []
        self.vocab_embeddings = None
        
    def fit_vocab(self, vocabulary: List[str]):
        """
        Precompute embeddings for the entire vocabulary.
        This allows fast nearest-neighbor search for query expansion.
        """
        logger.info(f"Encoding {len(vocabulary)} vocabulary terms...")
        # Batch encode to save memory/time
        new_embeddings = self.model.encode(vocabulary, show_progress_bar=True, batch_size=256)
        # Update atomically to prevent IndexError during concurrent searches
        self.vocab = vocabulary
        self.vocab_embeddings = new_embeddings
        logger.info("Vocabulary encoding complete.")

    def expand_query(self, query_terms: List[str], top_k: int = 5, all_terms: bool = False, threshold: float = 0.5) -> Dict[str, float]:
        """
        Expand the query by finding semantically similar terms from the vocabulary.
        Returns a dict of new terms and their weights (similarity scores).
        """
        expanded = {}
        if not self.vocab or self.vocab_embeddings is None:
            return expanded
            
        if not query_terms:
            return expanded
            
        # We can either encode the whole query as a single string and find similar terms,
        # or encode each term and find similar terms for each. 
        # Encoding the whole query captures context better.
        query_string = " ".join(query_terms)
        query_emb = self.model.encode([query_string])
        
        # Calculate cosine similarity with all vocabulary terms
        similarities = cosine_similarity(query_emb, self.vocab_embeddings)[0]
        
        # Filter out terms that are already in the query
        valid_indices = [i for i, term in enumerate(self.vocab) if term not in query_terms]
        
        if not valid_indices:
            return expanded
            
        valid_vocab = np.array(self.vocab)[valid_indices]
        valid_sims = similarities[valid_indices]
        
        if all_terms:
            # Add all terms above threshold
            for term, sim in zip(valid_vocab, valid_sims):
                if sim >= threshold:
                    expanded[str(term)] = float(sim)
        else:
            # Sort by similarity
            top_indices = np.argsort(valid_sims)[::-1][:top_k]
            for idx in top_indices:
                sim = valid_sims[idx]
                if sim > 0:
                    expanded[str(valid_vocab[idx])] = float(sim)
                
        return expanded
