from fastapi import APIRouter, HTTPException
import state

router = APIRouter(prefix="/index", tags=["index"])

@router.get("/{doc_id}")
def get_inverted_index(doc_id: int):
    if not state.config_state["dataset_loaded"]:
        raise HTTPException(status_code=500, detail="Dataset not loaded")
    
    data = state.ir_engine.get_inverted_file_for_doc(doc_id)
    if not data:
        raise HTTPException(status_code=404, detail="Document not found or empty")
        
    return {
        "doc_id": doc_id,
        "inverted_file": data
    }
