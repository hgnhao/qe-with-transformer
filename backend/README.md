# Backend: IR API & Query Expansion Engine

The backend module of the Information Retrieval project, responsible for text processing, index management, query expansion using AI, and mapping API routes to the Vue frontend.

## Architecture & Modules

This application relies on `FastAPI` for asynchronous web services and modern python typings.
- `core/ir_engine.py`: Manages document parsing and local inverted index construction.
- `core/vsm.py`: Implements Vector Space Model mechanics for ranking documents.
- `core/preprocess.py` & `parser.py`: Executes stemming and stop-word removals using the `nltk` toolkit.
- `core/expansion.py`: Handles semantic query expansions leveraging NLP via `sentence-transformers`.
- `routers/`: Maps exposed web endpoints (`/search`, `/config`, `/index`).

## Key Dependencies
- `fastapi` & `uvicorn`
- `sentence-transformers` & `scikit-learn`
- `nltk`
- `pydantic` & `python-multipart`

## Setup Instructions
1. Navigate to the `backend/` directory.
2. Set up your Python environment (e.g., `python -m venv .venv`).
3. Activate the environment (`.\.venv\Scripts\Activate.ps1`).
4. Install dependencies through uv or pip. 
5. Run the ASGI server leveraging FastAPI CLI or Uvicorn:
   fastapi dev main.py

6. Interactive REST API docs (Swagger UI) will be automatically live at `http://localhost:8000/docs`.

## Query Expansion Note
The first request triggering query expansion may take slightly longer due to the Sentence Transformer model caching phase (`all-MiniLM-L6-v2`) processing vocabulary embeddings into memory.
