from typing import List, Tuple, Set

def average_precision(ranked_docs: List[Tuple[int, float]], relevant_docs: Set[int]) -> float:
    # hitung AP untuk satu kueri
    if not relevant_docs:
        return 0.0

    hits = 0
    sum_precisions = 0.0

    for i, (doc_id, score) in enumerate(ranked_docs):
        if doc_id in relevant_docs:
            hits += 1
            precision_at_i = hits / (i + 1)
            sum_precisions += precision_at_i

    return sum_precisions / len(relevant_docs)

def mean_average_precision(ap_scores: List[float]) -> float:
    # hitung MAP dari daftar skor AP
    if not ap_scores:
        return 0.0
    return sum(ap_scores) / len(ap_scores)

def precision_at_k(ranked_docs: List[Tuple[int, float]], relevant_docs: Set[int], k: int) -> float:
    # presisi pada peringkat k
    if k <= 0 or not relevant_docs:
        return 0.0
    top_k = ranked_docs[:k]
    hits = sum(1 for doc_id, _ in top_k if doc_id in relevant_docs)
    return hits / k

def recall_at_k(ranked_docs: List[Tuple[int, float]], relevant_docs: Set[int], k: int) -> float:
    # recall pada peringkat k
    if k <= 0 or not relevant_docs:
        return 0.0
    top_k = ranked_docs[:k]
    hits = sum(1 for doc_id, _ in top_k if doc_id in relevant_docs)
    return hits / len(relevant_docs)
