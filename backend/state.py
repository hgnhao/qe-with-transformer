import os
from core import (
    IREngine, VSM, QueryExpander, 
    parse_cisi_documents, parse_queries, parse_qrels
)

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
