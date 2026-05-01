from langchain_openai.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os

def get_embedding_function():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        raise ValueError("❌ OPENAI_API_KEY not found in .env file")

    return OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_api_key)
