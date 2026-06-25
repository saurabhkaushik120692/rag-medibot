from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

def rerank_compression_retriever(crossencoder_model, top_n, hybrid_retriever):
    # Load cross-encoder model (downloads ~270MB on first run)
    cross_encoder = HuggingFaceCrossEncoder(
        model_name=crossencoder_model
    )

    reranker = CrossEncoderReranker(
        model=cross_encoder,
        top_n=top_n           # keep only top-3 after reranking
    )
    reranking_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=hybrid_retriever
    )
    return reranking_retriever

def rerank_llminvoke(reranking_retriever, llm, prompt):
    reranking_rag_chain = create_retrieval_chain(
        reranking_retriever,
        create_stuff_documents_chain(llm, prompt)
    )
    return reranking_rag_chain