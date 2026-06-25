from langchain_core.prompts import ChatPromptTemplate

def generate_prompt(question, result):
    # Prompt template
    SYSTEM_PROMPT = """You are a medical assistant.
    Given a user question and the SQL query result from our mediassist database,
    provide a clear, concise natural language answer.
    Be specific with numbers and facts from the data."""

    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Question: {question}\nSQL Result: {result}\n\nAnswer:"),
    ])

    return answer_prompt