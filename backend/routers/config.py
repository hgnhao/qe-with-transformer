from fastapi import APIRouter
from schemas import ConfigUpdate
import state

router = APIRouter(prefix="/config", tags=["config"])

@router.get("")
def get_config():
    return state.config_state

@router.post("")
def update_config(config: ConfigUpdate):
    state.config_state["apply_stemming"] = config.apply_stemming
    state.config_state["remove_stopwords"] = config.remove_stopwords
    state.reload_dataset()
    return {"status": "success", "config": state.config_state}
