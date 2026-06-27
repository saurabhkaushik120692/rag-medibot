from qdrant_client.models import Filter, FieldCondition, MatchAny

def vector_hybrid_retriever(vectorstore, top_k: int, role: str):
    """
    Build a Qdrant-backed hybrid retriever that enforces RBAC at the
    vector-store level by filtering on the 'access_roles' metadata field.

    Each stored chunk carries  metadata.access_roles = ["doctor", "admin", ...]
    We filter so that only chunks whose access_roles list contains the
    requesting user's role are ever returned — matching the assignment spec.
    """
    hybrid_retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": top_k,
            "filter": Filter(
                must=[
                    FieldCondition(
                        key="metadata.access_roles",
                        match=MatchAny(any=[role])  # role = e.g. "doctor"
                    )
                ]
            )
        }
    )
    return hybrid_retriever