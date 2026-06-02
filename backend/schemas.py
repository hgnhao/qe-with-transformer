from pydantic import BaseModel
from typing import Optional

class ConfigUpdate(BaseModel):
    apply_stemming: bool
    remove_stopwords: bool

class SearchRequest(BaseModel):
    query: str
    query_id: Optional[int] = None
    weight_scheme: str = "tf" # 'tf', 'idf', 'tf-idf', 'tf-idf-cosine'
    tf_variant: str = "raw" # 'raw', 'logarithmic', 'binary', 'augmented'
    top_k_expansion: int = 5
    all_expansion_terms: bool = False
