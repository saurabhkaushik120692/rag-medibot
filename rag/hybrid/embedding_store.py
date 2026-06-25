from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_core.documents import Document

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