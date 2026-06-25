def ask_hybrid(rag_chain, question: str):
    response = rag_chain.invoke({"input": question})
    print("\nQUESTION:\n", question)
    print("\nRESPONSE:\n", response["answer"])
    print(f"-------------------Context---------------------")
    print(f"\nSources retrieved:")
    for i, doc in enumerate(response["context"], 1):
        # Access the correct keys from your metadata schema
        src = doc.metadata.get("source_document", "unknown")
        coll = doc.metadata.get("collection", "unknown")
        chunk_idx = doc.metadata.get("chunk_index", "N/A")
        headings = doc.metadata.get("section_title", "N/A")
        chunk_type = doc.metadata.get("chunk_type", "N/A")
        print(f"  [{i}] source={src} | collection={coll} | chunk={chunk_idx} | headings={headings} | chunk_type={chunk_type}")
        print(f"Document Content:\n{doc.page_content}")
    print("-" * 60)
    return {"answer": response["answer"], "context": response["context"]}