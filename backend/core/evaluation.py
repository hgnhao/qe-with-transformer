from typing import List, Tuple, Set

def average_precision(ranked_docs: List[Tuple[int, float]], relevant_docs: Set[int]) -> float:
    """
    Calculate Average Precision (AP) for a single query's ranked results.
    """
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
    """
    Calculate Mean Average Precision (MAP) given a list of AP scores.
    """
    if not ap_scores:
        return 0.0
    return sum(ap_scores) / len(ap_scores)
