import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from schemas import SearchRequest
import state
from core import preprocess_text, average_precision, mean_average_precision, parse_queries

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/interactive")
def search_interactive(request: SearchRequest):
    if not state.config_state["dataset_loaded"]:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
        
    # Process original query
    q_tokens = preprocess_text(
        request.query, 
        apply_stemming=state.config_state["apply_stemming"],
        remove_stopwords=state.config_state["remove_stopwords"]
    )
    
    # Original query terms with weight 1.0
    orig_q_terms = {t: 1.0 for t in q_tokens}
    
    # Rank original
    orig_results = state.vsm.rank_documents(orig_q_terms, request.weight_scheme, request.tf_variant, top_n=50)
    
    # Expand query
    expanded_terms_weights = state.expander.expand_query(
        q_tokens, 
        top_k=request.top_k_expansion, 
        all_terms=request.all_expansion_terms
    )
    
    # Combined query
    combined_q_terms = orig_q_terms.copy()
    for term, weight in expanded_terms_weights.items():
        if term not in combined_q_terms:
            combined_q_terms[term] = weight
            
    # Rank expanded
    exp_results = state.vsm.rank_documents(combined_q_terms, request.weight_scheme, request.tf_variant, top_n=50)
    
    # Compute MAP if query_id provided
    orig_map = 0.0
    exp_map = 0.0
    if request.query_id is not None and request.query_id in state.qrels:
        relevant = state.qrels[request.query_id]
        orig_map = average_precision(orig_results, relevant)
        exp_map = average_precision(exp_results, relevant)
        
    # Format results
    def format_results(ranked):
        return [{"doc_id": doc_id, "score": score, "title": state.ir_engine.docs_metadata[doc_id]["title"]} for doc_id, score in ranked]
        
    return {
        "original": {
            "query": q_tokens,
            "results": format_results(orig_results),
            "map": orig_map
        },
        "expanded": {
            "query": list(combined_q_terms.keys()),
            "expansion_weights": expanded_terms_weights,
            "results": format_results(exp_results),
            "map": exp_map
        }
    }

@router.post("/batch")
async def search_batch(
    file: UploadFile = File(...), 
    weight_scheme: str = Form("tf"), 
    tf_variant: str = Form("raw"),
    top_k_expansion: int = Form(5),
    all_expansion_terms: bool = Form(False)
):
    if not state.config_state["dataset_loaded"]:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
        
    content = await file.read()
    content_str = content.decode('utf-8')
    
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
        tmp.write(content_str)
        tmp_path = tmp.name
        
    try:
        queries = parse_queries(tmp_path)
    finally:
        os.unlink(tmp_path)
    
    output_lines = []
    output_lines.append(f"Batch Processing Results")
    output_lines.append(f"Scheme: {weight_scheme}, TF Variant: {tf_variant}")
    output_lines.append("="*50)
    
    orig_aps = []
    exp_aps = []
    
    for q_id, q_text in queries.items():
        if not q_text.strip(): continue
            
        q_tokens = preprocess_text(
            q_text, 
            apply_stemming=state.config_state["apply_stemming"],
            remove_stopwords=state.config_state["remove_stopwords"]
        )
        orig_q_terms = {t: 1.0 for t in q_tokens}
        orig_results = state.vsm.rank_documents(orig_q_terms, weight_scheme, tf_variant, top_n=50)
        
        expanded_weights = state.expander.expand_query(q_tokens, top_k=top_k_expansion, all_terms=all_expansion_terms)
        combined_q_terms = orig_q_terms.copy()
        for t, w in expanded_weights.items():
            if t not in combined_q_terms:
                combined_q_terms[t] = w
                
        exp_results = state.vsm.rank_documents(combined_q_terms, weight_scheme, tf_variant, top_n=50)
        
        orig_ap = 0.0
        exp_ap = 0.0
        if q_id and q_id in state.qrels:
            orig_ap = average_precision(orig_results, state.qrels[q_id])
            exp_ap = average_precision(exp_results, state.qrels[q_id])
            orig_aps.append(orig_ap)
            exp_aps.append(exp_ap)
            
        output_lines.append(f"Query {q_id}: {q_text}")
        output_lines.append(f"Expanded Terms: {expanded_weights}")
        output_lines.append(f"Original MAP: {orig_ap:.4f} | Expanded MAP: {exp_ap:.4f}")
        output_lines.append("-" * 30)
        
    avg_orig_map = mean_average_precision(orig_aps)
    avg_exp_map = mean_average_precision(exp_aps)
    
    output_lines.append("="*50)
    output_lines.append(f"OVERALL ORIGINAL MAP: {avg_orig_map:.4f}")
    output_lines.append(f"OVERALL EXPANDED MAP: {avg_exp_map:.4f}")
    
    return {"result_text": "\n".join(output_lines)}
