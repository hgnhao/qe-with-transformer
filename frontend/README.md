# Frontend: Information Retrieval Workspace

This is the front-end interface for the Information Retrieval with Query Expansion project. Built to be lightning-fast, reactive, and user-friendly, this Single Page Application (SPA) integrates directly with our FastAPI backend.

## Tech Stack
- **Vue 3**: The core reactive JavaScript framework.
- **Vite**: Ultra-fast module bundler.
- **Tailwind CSS**: Utility-first CSS framework for slick, modern designs.
- **Axios**: Promised-based HTTP client for API interactions.

## Components Structure
- `InteractiveSearch.vue` - Primary search bar and document result visualizations.
- `ConfigPanel.vue` - Control panel to dynamically alter Preprocessing toggles, Weighting Schemes, and Query Expansion settings.
- `IndexInspector.vue` - Tooling to inspect backend inverted index arrays.
- `BatchProcessing.vue` - Handles batch testing evaluation utilizing provided `.all` and `qrels` text datasets.

## Getting Started
1. Ensure [Node.js](https://nodejs.org/) is installed.
2. Run `npm install` within this directory to download all dependencies.
3. Execute `npm run dev` to spin up the local development Vite server.
4. Navigate to your localhost port displayed in the terminal.

\* _Make sure the backend server (FastAPI) is simultaneously running to successfully fetch queries and configurations._

## Configuration
Application state and API logistics are managed centrally within `src/store.js`. Ensure backend CORS configurations match your Vite output origin if modifying explicit ports.
