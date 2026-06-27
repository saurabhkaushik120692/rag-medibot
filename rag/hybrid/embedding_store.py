from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_core.documents import Document
from qdrant_client import QdrantClient

def collection_exists(qdrant_path: str, collection_name: str) -> bool:
    """Returns True if the Qdrant collection is already built on disk."""
    try:
        client = QdrantClient(path=qdrant_path)
        existing = [c.name for c in client.get_collections().collections]
        return collection_name in existing
    except Exception:
        return False

def load_existing_vectorstore(embed_model: str, qdrant_path: str, collection_name: str):
    """Connect to an already-built Qdrant collection — no re-ingestion."""
    dense_embeddings = HuggingFaceEmbeddings(
        model_name=embed_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25", batch_size=32)
    client = QdrantClient(path=qdrant_path)
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=dense_embeddings,
        sparse_embedding=sparse_embeddings,
        retrieval_mode=RetrievalMode.HYBRID,
    )
    return vectorstore

def store_chunks_to_qdrant(embed_model: str, qdrant_path: str, collection_name: str , chunks: list):
    # Dense embeddings — semantic understanding
    dense_embeddings = HuggingFaceEmbeddings(
        model_name=embed_model,
        model_kwargs={"device": "cpu"},      # change to "cuda" if you have a GPU
        encode_kwargs={"normalize_embeddings": True}
    )

    # Sparse embeddings — BM25 keyword matching (via FastEmbed)
    sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25", batch_size=32)

    # Convert the list of raw dictionaries into LangChain Document objects
    langchain_documents = [
        Document(
            page_content=chunk["page_content"],
            metadata=chunk["metadata"]
        )
        for chunk in chunks
    ]

    # RetrievalMode.HYBRID stores BOTH dense and sparse vectors
    vectorstore = QdrantVectorStore.from_documents(
        documents=langchain_documents,
        embedding=dense_embeddings,
        sparse_embedding=sparse_embeddings,
        path=qdrant_path,
        collection_name=collection_name,
        retrieval_mode=RetrievalMode.HYBRID,
        force_recreate=True,
    )
    return vectorstore