from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import io

from core import (
    IREngine, VSM, QueryExpander, 
    parse_cisi_documents, parse_queries, parse_qrels,
    preprocess_text, average_precision, mean_average_precision
)

app = FastAPI(title="IR System with Query Expansion")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global states
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(BASE_DIR, 'test')

ir_engine = IREngine()
vsm = None
expander = QueryExpander(model_name='all-MiniLM-L6-v2')
qrels = {}
original_queries = {}

# Current Config
config_state = {
    "apply_stemming": True,
    "remove_stopwords": True,
    "dataset_loaded": False
}

def reload_dataset():
    global vsm, qrels, original_queries
    
    docs_path = os.path.join(TEST_DIR, 'cisi.all')
    qrels_path = os.path.join(TEST_DIR, 'qrels.text')
    queries_path = os.path.join(TEST_DIR, 'query.text')
    
    if os.path.exists(docs_path):
        docs = parse_cisi_documents(docs_path)
        ir_engine.build_index(
            docs, 
            apply_stemming=config_state["apply_stemming"],
            remove_stopwords=config_state["remove_stopwords"]
        )
        vsm = VSM(ir_engine)
        
        # Fit Query Expander with vocabulary
        vocab = list(ir_engine.inverted_index.keys())
        expander.fit_vocab(vocab)
        
        config_state["dataset_loaded"] = True
        
    if os.path.exists(qrels_path):
        qrels = parse_qrels(qrels_path)
        
    if os.path.exists(queries_path):
        original_queries = parse_queries(queries_path)

@app.on_event("startup")
async def startup_event():
    # Attempt to load dataset on startup
    reload_dataset()

class ConfigUpdate(BaseModel):
    apply_stemming: bool
    remove_stopwords: bool

@app.get("/config")
def get_config():
    return config_state

@app.post("/config")
def update_config(config: ConfigUpdate):
    config_state["apply_stemming"] = config.apply_stemming
    config_state["remove_stopwords"] = config.remove_stopwords
    reload_dataset()
    return {"status": "success", "config": config_state}

class SearchRequest(BaseModel):
    query: str
    query_id: Optional[int] = None
    weight_scheme: str = "tf" # 'tf', 'idf', 'tf-idf', 'tf-idf-cosine'
    tf_variant: str = "raw" # 'raw', 'logarithmic', 'binary', 'augmented'
    top_k_expansion: int = 5
    all_expansion_terms: bool = False

@app.post("/search/interactive")
def search_interactive(request: SearchRequest):
    if not config_state["dataset_loaded"]:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
        
    # Process original query
    q_tokens = preprocess_text(
        request.query, 
        apply_stemming=config_state["apply_stemming"],
        remove_stopwords=config_state["remove_stopwords"]
    )
    
    # Original query terms with weight 1.0
    orig_q_terms = {t: 1.0 for t in q_tokens}
    
    # Rank original
    orig_results = vsm.rank_documents(orig_q_terms, request.weight_scheme, request.tf_variant, top_n=50)
    
    # Expand query
    expanded_terms_weights = expander.expand_query(
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
    exp_results = vsm.rank_documents(combined_q_terms, request.weight_scheme, request.tf_variant, top_n=50)
    
    # Compute MAP if query_id provided
    orig_map = 0.0
    exp_map = 0.0
    if request.query_id is not None and request.query_id in qrels:
        relevant = qrels[request.query_id]
        orig_map = average_precision(orig_results, relevant)
        exp_map = average_precision(exp_results, relevant)
        
    # Format results
    def format_results(ranked):
        return [{"doc_id": doc_id, "score": score, "title": ir_engine.docs_metadata[doc_id]["title"]} for doc_id, score in ranked]
        
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

@app.post("/search/batch")
async def search_batch(
    file: UploadFile = File(...), 
    weight_scheme: str = Form("tf"), 
    tf_variant: str = Form("raw"),
    top_k_expansion: int = Form(5),
    all_expansion_terms: bool = Form(False)
):
    if not config_state["dataset_loaded"]:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
        
    content = await file.read()
    content_str = content.decode('utf-8')
    
    import tempfile
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
            apply_stemming=config_state["apply_stemming"],
            remove_stopwords=config_state["remove_stopwords"]
        )
        orig_q_terms = {t: 1.0 for t in q_tokens}
        orig_results = vsm.rank_documents(orig_q_terms, weight_scheme, tf_variant, top_n=50)
        
        expanded_weights = expander.expand_query(q_tokens, top_k=top_k_expansion, all_terms=all_expansion_terms)
        combined_q_terms = orig_q_terms.copy()
        for t, w in expanded_weights.items():
            if t not in combined_q_terms:
                combined_q_terms[t] = w
                
        exp_results = vsm.rank_documents(combined_q_terms, weight_scheme, tf_variant, top_n=50)
        
        orig_ap = 0.0
        exp_ap = 0.0
        if q_id and q_id in qrels:
            orig_ap = average_precision(orig_results, qrels[q_id])
            exp_ap = average_precision(exp_results, qrels[q_id])
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

@app.get("/index/{doc_id}")
def get_inverted_index(doc_id: int):
    if not config_state["dataset_loaded"]:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    data = ir_engine.get_inverted_file_for_doc(doc_id)
    if not data:
        raise HTTPException(status_code=404, detail="Document not found or empty")
        
    return {
        "doc_id": doc_id,
        "inverted_file": data
    }
