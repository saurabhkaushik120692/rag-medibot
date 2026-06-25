from langchain_core.prompts import ChatPromptTemplate

def generate_prompt():
    # Prompt template
    system_prompt = """You are a helpful medical expert.
    Answer the question using ONLY the information provided in the context below.
    If the answer is not in the context, say "I don't have that information."
    Keep answers concise and professional.
    Context:
    {context}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    return prompt