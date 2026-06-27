# app/routes.py
from fastapi import APIRouter, HTTPException, Request
from typing import List
from api.app.models import LoginRequest, LoginResponse, ChatRequest, ChatResponse
from api.app.config import MOCK_USERS, ROLE_ACCESS_MAPPING
from rag.hybrid.hybrid_retriever import vector_hybrid_retriever
from rag.hybrid.reranker import rerank_compression_retriever, rerank_llminvoke
from rag.hybrid.invoke_llm import ask_hybrid
from rag.sql.invoke_llm import ask_sql
from rag.utils import is_analytical_question

router = APIRouter()

NO_INFO_PHRASE = "I don't have that information."
ALL_COLLECTIONS = {"general", "clinical", "nursing", "billing", "equipment"}

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "mediassist-rag-api"}

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    username = data.username
    password = data.password
    print(username)
    if username not in MOCK_USERS:
        raise HTTPException(status_code=401, detail="User not found")
    
    db_password, db_role = MOCK_USERS[username]

    if password != db_password:
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"message": "Success", "role": db_role, "username": username}

@router.get("/collections/{role}", response_model=List[str])
def get_collections(role: str):
    role_lower = role.lower()
    if role_lower not in ROLE_ACCESS_MAPPING:
        raise HTTPException(status_code=404, detail="Role not found")
        
    return ROLE_ACCESS_MAPPING[role_lower]

# Helper function to build sources list from retrieved documents
def build_sources(context: list) -> list:
    """Extract source metadata from retrieved LangChain Documents."""
    seen = set()
    sources = []
    for doc in context:
        key = (
            doc.metadata.get("source_document", ""),
            doc.metadata.get("collection", "")
        )
        if key not in seen:              # deduplicate by document + collection
            seen.add(key)
            sources.append({
                "source_document": doc.metadata.get("source_document", ""),
                "section_title":   doc.metadata.get("section_title", []),
                "collection":      doc.metadata.get("collection", ""),
            })
    return sources

@router.post("/chat", response_model=ChatResponse)
def chat(request: Request, data: ChatRequest):
    query = data.query
    role = data.role.lower()

    if role not in ROLE_ACCESS_MAPPING:
        raise HTTPException(status_code=403, detail="Invalid role permissions")

     # Pull initialized state
    rag = request.app.state.rag
    llm = rag["llm"]
    # sql_db = rag["sql_db"]
    vectorstore = rag["vectorstore"]
    prompt = rag["hybrid_prompt"]
    roles_for_user = ROLE_ACCESS_MAPPING[role]   # list of collections the role can access
    sql_rag_chain = rag["sql_rag_chain"]
    cross_encoder_model = rag["cross_encoder_model"]

     # Step 1: Classify the question FIRST
    if role in ["admin", "billing_executive"] and is_analytical_question(query, llm):
        # Route directly to SQL RAG — no vector search performed
        results = sql_rag_chain(query)
        sql_answer = ask_sql(query, results, llm)
        print("[debug] SQL RAG Answer → ", sql_answer)
        return {
            "answer":         sql_answer,
            "sources":        [],
            "retrieval_type": "sql_rag",
            "role":           role,
        }

    # ── Step 2: Otherwise, run Hybrid RAG + Reranking

    # vector hybrid retriever
    # Filter by access_roles (the role string stored per chunk), not by collection name
    hybrid_retriever = vector_hybrid_retriever(vectorstore, 5, role)

    reranker_retriever = rerank_compression_retriever(cross_encoder_model,3,hybrid_retriever)
    reranking_rag_chain = rerank_llminvoke(reranker_retriever, llm, prompt)

    answer = ask_hybrid(reranking_rag_chain, query)

    #  Fallback: empty context OR LLM couldn't answer from retrieved docs
    context_empty = not answer["context"]
    llm_has_no_info = NO_INFO_PHRASE.lower() in answer["answer"].lower()
    if context_empty or llm_has_no_info:
        # # if requestor role is admin or technician then we will call the sql rag as well to get the answer
        # if role in ["admin", "billing_executive"]:
        #     # results = sql_rag_chain(query, llm, sql_db)
        #     results = sql_rag_chain(query)
        #     sql_answer = ask_sql(query, results,llm)
        #     print("[debug] SQL RAG Answer → ", sql_answer)
        #     if sql_answer:
        #         return {
        #             "answer":         sql_answer,
        #             "sources":        [],             # SQL has no doc chunks
        #             "retrieval_type": "sql_rag",
        #             "role":           role,
        #         }

        accessible_str   = ", ".join(roles_for_user)
        inaccessible_str = ", ".join(sorted(ALL_COLLECTIONS - set(roles_for_user)))
        if not inaccessible_str:
            fallback = "I cannot answer your question based on the documents and database available."
        else:
            fallback = (
                f"As a {role}, you do not have access to [{inaccessible_str}] documents. "
                f"I can only answer questions from the {accessible_str} documents."
            )
        return {
            "answer":         fallback,
            "sources":        [],
            "retrieval_type": "none",
            "role":           role,
        }

    return {
        "answer":         answer["answer"],
        "sources":        build_sources(answer["context"]),
        "retrieval_type": "hybrid_rag",
        "role":           role,
    }
    
