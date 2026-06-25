# main.py
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.app.routes import router
from api.app.middleware import setup_cors
from api.app.startup import initialize_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    # === STARTUP ===
    print("[Startup] Initializing RAG components...")
    app.state.rag = {}           # shared state dict for all RAG objects
    initialize_app(app.state.rag)
    
    yield  # app is running here
    
    # === SHUTDOWN (optional cleanup) ===
    print("[Shutdown] Cleaning up resources...")
    app.state.rag.clear()

app = FastAPI(title="MediAssist RAG Backend", lifespan=lifespan)

# Setup CORS middleware
setup_cors(app)

# Include the API endpoints
app.include_router(router)

if __name__ == "__main__":
    print("Starting server...")
    # Start the server (listening on port 8000)
    # uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)

