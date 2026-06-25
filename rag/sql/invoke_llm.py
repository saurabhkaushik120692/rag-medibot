from rag.sql.sql_prompt import generate_prompt

def ask_sql(question: str, result: str, llm):
    prompt = generate_prompt(question, result)
    response = prompt | llm
    answer = response.invoke({"question": question, "result": result}).content
    print(f"[debug] SQL RAG Answer → {answer}")
    return answer
