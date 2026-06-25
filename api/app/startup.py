import os
from rag.llm import llm_groq_agent
from rag.hybrid.ingestion_chunking import process_data_directory
from rag.hybrid.embedding_store import store_chunks_to_qdrant
from rag.hybrid.hybrid_prompt import generate_prompt
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv, find_dotenv

# load values from .env file
load_dotenv(find_dotenv())

# Load config values from .env
EMBED_MODEL         = os.getenv("EMBED_MODEL",          "sentence-transformers/all-MiniLM-L6-v2")
COLLECTION_NAME     = os.getenv("COLLECTION_NAME",      "mediassit-vector-db")
QDRANT_PATH         = os.getenv("QDRANT_PATH",          "./db/mediassist_qdrant")
DATA_PATH           = os.getenv("DATA_PATH",            "./data")
GROQ_MODEL          = os.getenv("GROQ_MODEL",           "openai/gpt-oss-20b")
CROSS_ENCODER_MODEL = os.getenv("CROSS_ENCODER_MODEL",  "cross-encoder/ms-marco-MiniLM-L-6-v2")
DATABASE_PATH       = os.getenv("DATABASE_PATH",        "./data/db/mediassist.db")

def initialize_app(app_state: dict):
    """Run all one-time startup initializations and store results in app_state dict."""

    if "GROQ_API_KEY" not in os.environ:
        groq_key = os.getenv("GROQ_KEY", "")
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
    else:
        raise ValueError("GROQ_KEY not set in .env file")

    # groq agent
    llm = llm_groq_agent(groq_model=GROQ_MODEL)
    app_state["llm"] = llm

    # process data directory
    chunks = process_data_directory(data_dir_path=DATA_PATH, embed_model=EMBED_MODEL)

    # store to qdrant
    vectorstore = store_chunks_to_qdrant(embed_model=EMBED_MODEL, qdrant_path=QDRANT_PATH, collection_name=COLLECTION_NAME, chunks=chunks)
    app_state["vectorstore"] = vectorstore

    # hybrid prompt
    hybrid_prompt = generate_prompt()
    app_state["hybrid_prompt"] = hybrid_prompt

    # sql database
    db = SQLDatabase.from_uri(f"sqlite:///{DATABASE_PATH}")
    app_state["sql_db"] = db

print("[Startup] All initializations complete.")
