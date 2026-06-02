# Information Retrieval System with Query Expansion (Transformers)

An advanced Information Retrieval (IR) system built with a modular Client-Server architecture. This application utilizes Vector Space Models (VSM) and integrates an NLP Transformer-based Query Expansion mechanism to improve search accuracy and document retrieval performance.

## Project Structure
- **/backend**: FastAPI-based server handling the search engine, inverted indexing, preprocessing, and NLP query expansion (SentenceTransformers).
- **/frontend**: A reactive Vue 3 + Vite SPA tailored for interactive searches, result visualizations, and configuration adjustments.

## Core Features
1. **Interactive Search**: Real-time querying against an indexed corpus.
2. **Dynamic Preprocessing**: Toggle options for stemming (`nltk`) and stopwords removal.
3. **Weighting Schemes**: Configurable VSM calculations including TF, IDF, TF-IDF, and TF-IDF with Cosine Normalization along with several TF variants.
4. **AI Query Expansion**: Incorporates `all-MiniLM-L6-v2` SentenceTransformer model to capture semantic similarities and suggest expansion terms contextually.
5. **Batch Processing & Evaluation**: Handles batch tests using academic datasets (e.g., CISI).

## Getting Started

### 1. Backend Setup
1. Navigate to the `backend/` directory.
2. Create and activate a Python virtual environment.
3. Install dependencies via your preferred package manager (e.g., `uv`, `pip`).
4. Run the server: `fastapi dev main.py`.

### 2. Frontend Setup
1. Navigate to the `frontend/` directory.
2. Install Node.js dependencies: `npm install`.
3. Start the development server: `npm run dev`.
4. Open the displayed local address in your web browser.

## Team Contribution
- **Frontend Developer & UI/UX**
- **Backend Developer & Core IR Logic**
- **AI/NLP Integrator & System Evaluation**