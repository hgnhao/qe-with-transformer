from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import state
from routers import config, search, index

app = FastAPI(title="IR System with Query Expansion")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config.router)
app.include_router(search.router)
app.include_router(index.router)

@app.on_event("startup")
async def startup_event():
    # Attempt to load dataset on startup
    state.reload_dataset()