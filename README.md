# 🏥 RAG-MediBot — Role-Aware Medical RAG Chatbot

A production-style Retrieval-Augmented Generation (RAG) chatbot for **MediAssist Hospital**, featuring **role-based document access control**, **hybrid vector search**, and **SQL-based structured data queries**. The system enforces that users only retrieve documents their role is authorized to see.

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Folder Structure](#folder-structure)
- [Technology Stack](#technology-stack)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Hardcoded Users & Roles](#hardcoded-users--roles)
- [Role-Based Document Access](#role-based-document-access)
- [Data Collections](#data-collections)
- [Request Flow](#request-flow)
- [API Endpoints](#api-endpoints)
- [RAG Pipeline Details](#rag-pipeline-details)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                       │
│              http://localhost:3000                               │
│   ┌──────────────┐          ┌──────────────────────────────┐   │
│   │  /login page │          │       /chat page              │   │
│   └──────┬───────┘          └──────────────┬───────────────┘   │
└──────────┼───────────────────────────────── ┼───────────────────┘
           │  POST /login                     │  POST /chat
           ▼                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
│              http://127.0.0.1:8000                              │
│                                                                 │
│  ┌────────────┐  ┌────────────────┐  ┌────────────────────┐   │
│  │  /login    │  │  /collections  │  │       /chat        │   │
│  │  Auth      │  │  Role Metadata │  │  RAG Orchestrator  │   │
│  └────────────┘  └────────────────┘  └────────┬───────────┘   │
└──────────────────────────────────────────────── ┼───────────────┘
                                                  │
                    ┌─────────────────────────────┤
                    │                             │
                    ▼                             ▼
     ┌──────────────────────────┐   ┌─────────────────────────┐
     │     HYBRID RAG           │   │       SQL RAG            │
     │                          │   │  (admin/billing only)    │
     │  ┌──────────────────┐    │   │                          │
     │  │ HuggingFace      │    │   │  SQLite DB               │
     │  │ Dense Embeddings │    │   │  (claims data)           │
     │  └──────────────────┘    │   │                          │
     │  ┌──────────────────┐    │   │  LangChain SQL Chain     │
     │  │ FastEmbed (BM25) │    │   │  → SQL generation        │
     │  │ Sparse Embeddings│    │   │  → result execution      │
     │  └──────────────────┘    │   │  → natural lang answer   │
     │  ┌──────────────────┐    │   └─────────────────────────┘
     │  │  Qdrant Vector DB│    │
     │  │ (local on-disk)  │    │
     │  └──────────────────┘    │
     │  ┌──────────────────┐    │
     │  │ Cross-Encoder    │    │
     │  │  Re-ranker       │    │
     │  └──────────────────┘    │
     │  ┌──────────────────┐    │
     │  │  Groq LLM        │    │
     │  │ (gpt-oss-20b)    │    │
     │  └──────────────────┘    │
     └──────────────────────────┘
```

---

## Folder Structure

```
RAG-MediBot/
├── api/                          # FastAPI backend
│   ├── main.py                   # App entry point, lifespan startup
│   └── app/
│       ├── config.py             # Role-to-collection access mapping, mock users
│       ├── middleware.py         # CORS configuration (allows localhost:3000)
│       ├── models.py             # Pydantic request/response models
│       ├── routes.py             # API route handlers (/login, /chat, /collections)
│       └── startup.py            # One-time initialization: ingestion, LLM, SQL DB
│
├── rag/                          # RAG pipeline logic
│   ├── llm.py                    # Groq LLM factory (ChatGroq)
│   ├── hybrid/                   # Hybrid RAG (dense + sparse vector search)
│   │   ├── embedding_store.py    # Store chunks to Qdrant (dense + BM25 sparse)
│   │   ├── hybrid_prompt.py      # System prompt for hybrid RAG chain
│   │   ├── hybrid_retriever.py   # Role-filtered Qdrant retriever
│   │   ├── ingestion_chunking.py # PDF/MD parsing with Docling + HierarchicalChunker
│   │   ├── invoke_llm.py         # Execute hybrid RAG chain, return answer + context
│   │   └── reranker.py           # Cross-encoder re-ranking (ContextualCompression)
│   └── sql/                      # SQL RAG for structured/claims data
│       ├── invoke_llm.py         # Natural language answer from SQL result
│       ├── sql_chain_cleanup_run.py  # SQL generation + execution via LangChain
│       └── sql_prompt.py         # System prompt for SQL answer generation
│
├── frontend/                     # Next.js 16 chat UI
│   └── src/app/
│       ├── login/                # Login page
│       └── chat/                 # Chat interface
│
├── data/                         # Source documents (organized by collection)
│   ├── billing/                  # billing_codes.pdf, claim_submission_guide.md
│   ├── clinical/                 # diagnostic_reference.pdf, drug_formulary.pdf, treatment_protocols.pdf
│   ├── equipment/                # equipment_manual.pdf
│   ├── general/                  # code_of_conduct.pdf, general_faqs.pdf, leave_policy.pdf, staff_handbook.pdf
│   ├── nursing/                  # icu_nursing_procedures.pdf, infection_control.pdf
│   └── db/
│       └── mediassist.db         # SQLite database (claims data)
│
├── db/
│   └── mediassist_qdrant/        # Qdrant local vector store (auto-created on startup)
│
├── .env                          # Environment variables (not committed)
├── sample.env                    # Template — copy to .env and fill in values
├── pyproject.toml                # Python dependencies (managed with uv)
└── main.py                       # Standalone script for testing RAG chains locally
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16, React 19 |
| **Backend API** | FastAPI, Uvicorn |
| **LLM** | Groq (`openai/gpt-oss-20b`) via `langchain-groq` |
| **Document Parsing** | Docling (`HierarchicalChunker`) |
| **Dense Embeddings** | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| **Sparse Embeddings** | FastEmbed BM25 (`Qdrant/bm25`) |
| **Vector DB** | Qdrant (local on-disk mode) |
| **Re-ranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` (HuggingFace) |
| **SQL Chain** | LangChain `create_sql_query_chain` + SQLite |
| **Package Manager** | `uv` |

---

## Setup & Installation

### Prerequisites

- Python 3.10+ (project targets Python ≥ 3.13 in `pyproject.toml`)
- Node.js 18+ (for the frontend)
- [uv](https://github.com/astral-sh/uv) package manager

### 1. Clone the repo

```bash
git clone <repo-url>
cd RAG-MediBot
```

### 2. Set up Python environment

```bash
uv sync
```

This installs all dependencies from `pyproject.toml` into a `.venv`.

### 3. Configure environment variables

```bash
cp sample.env .env
```

Edit `.env` and fill in your Groq API key (see [Environment Variables](#environment-variables)).

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Environment Variables

Copy `sample.env` → `.env` and set the values below. **Never commit `.env`** — it's in `.gitignore`.

| Variable | Default | Description |
|---|---|---|
| `GROQ_KEY` | *(required)* | Your Groq API key — get one at [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | `openai/gpt-oss-20b` | Groq model name to use for chat |
| `EMBED_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace dense embedding model |
| `COLLECTION_NAME` | `hybrid_qdrant_medical` | Qdrant collection name |
| `QDRANT_PATH` | `./db/mediassist_qdrant` | Local path for Qdrant on-disk storage |
| `DATA_PATH` | `./data` | Root path of the document collections |
| `CROSS_ENCODER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Re-ranker model |
| `DATABASE_PATH` | `./data/db/mediassist.db` | Path to the SQLite claims database |

**sample.env:**

```env
EMBED_MODEL="sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME="hybrid_qdrant_medical"
QDRANT_PATH="./db/mediassist_qdrant"
DATA_PATH="./data"
GROQ_MODEL="openai/gpt-oss-20b"
CROSS_ENCODER_MODEL="cross-encoder/ms-marco-MiniLM-L-6-v2"
DATABASE_PATH="./data/db/mediassist.db"
GROQ_KEY=""
```

---

## Running the Application

> ⚠️ All commands must be run from the **project root** (`RAG-MediBot/`).

### Start the Backend

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

On first startup, the app will:
1. Parse all PDF/Markdown files in `data/` using Docling
2. Embed and store chunks into Qdrant at `./db/mediassist_qdrant`
3. Initialize the Groq LLM and SQL database connection

> 💡 Subsequent restarts re-ingest everything (the current implementation always calls `store_chunks_to_qdrant` with `force_recreate=True`).

### Start the Frontend

In a separate terminal:

```bash
cd frontend
npm run dev
```

The app will be available at **http://localhost:3000**.

---

## Hardcoded Users & Roles

Authentication is handled with in-memory mock users defined in [`api/app/config.py`](api/app/config.py). There is no real authentication database.

| Username | Password | Role |
|---|---|---|
| `dr.mehta` | `doctor` | `doctor` |
| `nurse.priya` | `nurse` | `nurse` |
| `billing.ravi` | `billing_executive` | `billing_executive` |
| `admin.sys` | `admin` | `admin` |
| `tech.anand` | `technician` | `technician` |

> ⚠️ These are demo credentials only. Do not use in production.

---

## Role-Based Document Access

Each role can only retrieve documents from specific **collections**. This is enforced at the Qdrant query level using a payload filter (`metadata.collection`).

| Role | Accessible Collections |
|---|---|
| `admin` | general, clinical, nursing, billing, equipment |
| `doctor` | general, clinical, nursing |
| `nurse` | general, nursing |
| `billing_executive` | general, billing |
| `technician` | general, equipment |

If a user asks about a collection they do not have access to, the system returns:

```
As a [role], you do not have access to [restricted collections] documents.
I can only answer questions from the [accessible collections] collections.
```

Additionally, `admin` and `billing_executive` roles automatically fall back to the **SQL RAG** chain when the hybrid vector search returns no useful answer (e.g., for structured claims queries).

---

## Data Collections

Documents live in `data/<collection-name>/`. The subfolder name **determines the collection** and therefore **which roles can access it**.

| Collection | Subfolder | Source Files |
|---|---|---|
| `general` | `data/general/` | code_of_conduct.pdf, general_faqs.pdf, leave_policy.pdf, staff_handbook.pdf |
| `clinical` | `data/clinical/` | diagnostic_reference.pdf, drug_formulary.pdf, treatment_protocols.pdf |
| `nursing` | `data/nursing/` | icu_nursing_procedures.pdf, infection_control.pdf |
| `billing` | `data/billing/` | billing_codes.pdf, claim_submission_guide.md |
| `equipment` | `data/equipment/` | equipment_manual.pdf |

Structured claims data lives in `data/db/mediassist.db` (SQLite) and is queried via the SQL RAG chain.

---

## Request Flow

### Login Flow

```
User enters credentials
        │
        ▼
POST /login
        │
        ├─ Username exists in MOCK_USERS? → No → 401 User not found
        │
        ├─ Password matches? → No → 401 Invalid password
        │
        └─ Yes → return { message, role, username }
                         │
                         ▼
              Frontend stores role in state
              GET /collections/{role} → list of accessible collections
```

### Chat Flow

```
User sends message (with role in request)
        │
        ▼
POST /chat  { query, role }
        │
        ├─ Role valid? → No → 403 Forbidden
        │
        ▼
  Lookup accessible collections for role
  (e.g., doctor → ["general", "clinical", "nursing"])
        │
        ▼
  ┌─────────────────────────────────────────┐
  │          HYBRID RAG PIPELINE            │
  │                                         │
  │  1. Build Qdrant retriever              │
  │     Filter: metadata.collection         │
  │             in roles_for_user           │
  │                                         │
  │  2. Retrieve top-10 chunks              │
  │     (dense + sparse hybrid search)      │
  │                                         │
  │  3. Re-rank top-5 with cross-encoder    │
  │                                         │
  │  4. LLM generates answer from context   │
  └─────────────────────────────────────────┘
        │
        ├─ Answer found? → Yes → return { answer }
        │
        ├─ No answer ("I don't have that information.")
        │       │
        │       ├─ Role is admin or billing_executive?
        │       │       │
        │       │       ▼
        │       │  ┌───────────────────────────────┐
        │       │  │        SQL RAG PIPELINE        │
        │       │  │                                │
        │       │  │  1. LLM generates SQL query    │
        │       │  │  2. Execute SQL on SQLite DB   │
        │       │  │  3. LLM formats result as NL   │
        │       │  └───────────────────────────────┘
        │       │       │
        │       │       ├─ SQL answer found? → return { answer }
        │       │       │
        │       │       └─ No → fallback message
        │       │
        │       └─ Other roles → fallback message:
        │              "As a {role}, you do not have access
        │               to [{inaccessible}] documents..."
        │
        └─ return { answer }
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | None | Health check |
| `POST` | `/login` | None | Authenticate user, returns role |
| `GET` | `/collections/{role}` | None | List collections accessible to a role |
| `POST` | `/chat` | Role in body | Submit a query, returns RAG answer |

### POST /login

```json
// Request
{ "username": "dr.mehta", "password": "doctor" }

// Response
{ "message": "Success", "role": "doctor", "username": "dr.mehta" }
```

### POST /chat

```json
// Request
{ "query": "What are the diagnostic criteria for diabetes?", "role": "doctor" }

// Response
{ "answer": "The diagnostic criteria for diabetes are: FPG ≥ 126 mg/dL, ..." }
```

---

## RAG Pipeline Details

### Hybrid RAG (Document Collections)

1. **Ingestion** (`rag/hybrid/ingestion_chunking.py`)
   - Parses PDFs and Markdown using **Docling** `HierarchicalChunker`
   - Builds full heading breadcrumb for each chunk (`H1 > H2 > H3\n\nContent`)
   - Stores collection name, source document, access roles, section title, chunk type in metadata

2. **Embedding** (`rag/hybrid/embedding_store.py`)
   - **Dense**: HuggingFace `all-MiniLM-L6-v2` (semantic understanding)
   - **Sparse**: FastEmbed BM25 (keyword matching)
   - Stored in local Qdrant (`RetrievalMode.HYBRID`)

3. **Retrieval** (`rag/hybrid/hybrid_retriever.py`)
   - Qdrant filter: `metadata.collection` must be in the user's allowed collections
   - Returns top-K hybrid matches

4. **Re-ranking** (`rag/hybrid/reranker.py`)
   - `ContextualCompressionRetriever` with `CrossEncoderReranker`
   - Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
   - Reduces candidates to top-5

5. **Generation** (`rag/hybrid/invoke_llm.py` + `hybrid_prompt.py`)
   - Groq LLM with system prompt: "Answer using ONLY the provided context. If not in context, say 'I don't have that information.'"

### SQL RAG (Structured Claims Data)

1. **SQL Generation** (`rag/sql/sql_chain_cleanup_run.py`)
   - `create_sql_query_chain` generates a SQL query from natural language
   - SQL is cleaned (strips markdown fences, `SQLQuery:` prefixes)
   - Query is executed against `mediassist.db`

2. **Answer Generation** (`rag/sql/invoke_llm.py`)
   - Groq LLM formats raw SQL results into a human-readable narrative

---

## Notes

- The Qdrant vector DB is stored **locally on disk** — no external Qdrant server required.
- The first startup takes several minutes as it parses all documents and builds embeddings.
- To force re-ingestion (e.g. after adding new documents), restart the server — the store always recreates with `force_recreate=True`.
- CORS is configured to allow only `http://localhost:3000` (the frontend dev server).
