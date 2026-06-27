def is_analytical_question(question: str, llm) -> bool:
    """
    Uses the LLM to classify whether the question is analytical/SQL-type
    (counts, sums, statistics, claims data) vs. document-based knowledge.
    Returns True if the question should be routed to SQL RAG.
    """
    classifier_prompt = (
        "You are a query router. Decide if the following question requires "
        "querying a structured database (counts, sums, trends, billing claims, "
        "maintenance tickets, statistics) or retrieving information from documents.\n\n"
        f"Question: {question}\n\n"
        "Reply with exactly one word — 'SQL' or 'DOCUMENT'."
    )
    response = llm.invoke(classifier_prompt)
    answer = response.content.strip().upper()
    print(f"[debug] Intent classifier → {answer}")
    return answer == "SQL"

# def is_analytical_question(question: str, llm=None) -> bool:
#     """Fast keyword-based classifier as a first pass."""
#     keywords = [
#         "how many", "count", "total", "sum", "average", "last month",
#         "last year", "claims", "submitted", "escalated", "tickets",
#         "statistics", "trend", "breakdown", "report", "billing"
#     ]
#     q = question.lower()
#     return any(kw in q for kw in keywords)
