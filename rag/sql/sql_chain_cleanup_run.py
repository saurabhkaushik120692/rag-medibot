from langchain_classic.chains import create_sql_query_chain
import re

def clean_sql(raw: str) -> str:
    """Strip markdown fences and any preamble, leaving only the SQL statement."""
    raw = re.sub(r"```(?:sql)?", "", raw).strip("`").strip()
    # If the LLM prefixed with 'SQLQuery:' or 'Question: ...\nSQLQuery:', keep only what's after
    if "SQLQuery:" in raw:
        raw = raw.split("SQLQuery:")[-1].strip()
    return raw

def sql_rag_chain(question: str, llm, db):
    sql_query_chain = create_sql_query_chain(llm, db)
    raw_sql = sql_query_chain.invoke({"question": question})
    sql = clean_sql(raw_sql)
    print(f"[debug] cleaned SQL → {sql}")

    # Step 2: Execute the SQL against the database
    result = db.run(sql)
    print(f"[debug] SQL result → {result}")
    return result