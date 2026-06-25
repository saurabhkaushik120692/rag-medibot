from langchain_groq import ChatGroq

def llm_groq_agent(groq_model):
    llm = ChatGroq(
        model=groq_model,
        temperature=0,
        max_tokens=None,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
    )
    return llm
