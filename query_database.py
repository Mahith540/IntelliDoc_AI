from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

CHROMA_PATH = "chroma"

def query_rag(question: str):
    # ✅ Use a more modern embedding model if available, else stick to mistral but nomic is preferred for RAG
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")

    # Load the local Chroma database
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    # Retrieve relevant documents with higher k for better context
    docs = db.similarity_search(question, k=5)
    
    # Context cleaning and formatting
    context_parts = []
    for i, doc in enumerate(docs):
        content = doc.page_content.strip()
        source = doc.metadata.get("source", "Unknown")
        context_parts.append(f"[Document {i+1} | Source: {source}]\n{content}")
    
    context_text = "\n\n---\n\n".join(context_parts)

    # Load local model for generation
    llm = Ollama(model="mistral")

    # Advanced prompt engineering for better quality
    prompt_template = """
    SYSTEM: You are IntelliDoc AI, a high-precision document intelligence engine. 
    Your goal is to provide accurate, concise, and professional answers based SOLELY on the provided context.

    RULES:
    1. If the answer is not contained within the context, state that you do not have enough information.
    2. Do not use outside knowledge.
    3. Use bullet points for complex information.
    4. Cite the [Document X] reference if possible.
    5. Be direct and avoid conversational filler.

    CONTEXT FROM INTELLIGENCE CORE:
    {context}

    USER QUERY: 
    {question}

    INTELLIDOC RESPONSE:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    final_prompt = prompt.format(context=context_text, question=question)

    # Invoke LLM
    answer = llm.invoke(final_prompt)
    
    response = {
        "answer": answer.strip(),
        "sources": list(set([doc.metadata.get("source") for doc in docs])),
        "context": context_text
    }
    return response

if __name__ == "__main__":
    while True:
        q = input("Ask me something (or type 'exit'): ")
        if q.lower() == "exit":
            break
        result = query_rag(q)
        print(f"\n🤔 Question: {q}\n")
        print(f"💡 Answer: {result['answer']}\n")
        print(f"📄 Sources: {', '.join(result['sources'])}\n")

