from qdrant_client.models import Filter, FieldCondition, MatchAny

# def vector_hybrid_retriever(vectorstore, top_k: int, roles: list):
#     hybrid_retriever = vectorstore.as_retriever(
#         search_kwargs={
#             "k": top_k,       # retrieve top-5 docs
#             "query_filter": {"must": [{"key": "access_roles", "match": {"any": roles}}]} # e.g., restrict by role
#         }
#     )
#     return hybrid_retriever

def vector_hybrid_retriever(vectorstore, top_k: int, roles: list):
    hybrid_retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": top_k,
            "filter": Filter(
                must=[
                    FieldCondition(
                        key="metadata.collection",
                        match=MatchAny(any=roles)  # roles = e.g. ["general", "clinical", "nursing"]
                    )
                ]
            )
        }
    )
    return hybrid_retriever