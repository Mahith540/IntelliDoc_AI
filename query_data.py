from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

CHROMA_PATH = "chroma"

def query_rag(question: str):
    print(f"🤔 Question: {question}")
    # Load embeddings and database
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    retriever = db.as_retriever(search_kwargs={"k": 3})

    # Set up OpenAI LLM
    llm = ChatOpenAI(model="gpt-4o-mini")

    # Create RAG pipeline
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
    )

    # Get the answer
    result = qa_chain.invoke({"query": question})
    answer = result["result"]

    print(f"💬 Answer: {answer}\n")
    return answer

if __name__ == "__main__":
    while True:
        q = input("Ask me something (or type 'exit'): ")
        if q.lower() == "exit":
            break
        query_rag(q)
