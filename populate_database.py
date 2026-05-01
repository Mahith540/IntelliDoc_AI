from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
import os
import shutil

CHROMA_PATH = "chroma"
DATA_FOLDERS = ["data_big", "data_text"]  # you can add more folders

def main():
    all_docs = []
    for folder in DATA_FOLDERS:
        all_docs.extend(load_documents(folder))

    if not all_docs:
        print(" No valid documents found! Please check your data folders.")
        return

    chunks = split_text(all_docs)
    save_to_chroma(chunks)


# Disable ChromaDB telemetry to prevent crashes
os.environ["ANONYMIZED_TELEMETRY"] = "False"

def process_new_file(file_path):
    """Processes a single new file and adds it to the Chroma database"""
    print(f"\n[INTERNAL] Ingesting file: {file_path}")
    
    try:
        # Step 1: Reading
        if file_path.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.lower().endswith((".txt", ".md")):
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {os.path.basename(file_path)}")

        docs = loader.load()
        if not docs:
            raise ValueError(f"Could not read any text from {os.path.basename(file_path)}")

        # Step 2: Organizing
        chunks = split_text(docs)

        # Step 3: Learning
        print(f"Updating Chroma database with Nomic Embeddings...")
        embedding_function = OllamaEmbeddings(model="nomic-embed-text")
        
        if os.path.exists(CHROMA_PATH):
            db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
            db.add_documents(chunks)
        else:
            db = Chroma.from_documents(
                chunks,
                embedding_function,
                persist_directory=CHROMA_PATH,
            )
        
        print(f"Ingestion complete for {file_path}")
        return {
            "num_chunks": len(chunks),
            "preview": docs[0].page_content[:200].replace("\n", " ") if docs else ""
        }

    except Exception as e:
        print(f"[ERROR] Failed to ingest {file_path}: {str(e)}")
        raise e


def load_documents(folder_path):
    """Loads PDFs or text files safely from a folder"""
    docs = []
    print(f"\n Loading documents from: {folder_path}")

    if not os.path.exists(folder_path):
        print(f" Folder not found: {folder_path}")
        return docs

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        try:
            if filename.lower().endswith(".pdf"):
                print(f"→ Loading PDF: {filename}")
                loader = PyPDFLoader(file_path)
            elif filename.lower().endswith((".txt", ".md")):
                print(f"→ Loading Text: {filename}")
                loader = TextLoader(file_path)
            else:
                print(f" Skipping unsupported file: {filename}")
                continue

            loaded = loader.load()
            if not loaded:
                print(f"️ Skipped empty file: {filename}")
                continue

            docs.extend(loaded)
        except Exception as e:
            print(f"Failed to load {filename}: {e}")

    print(f"---->Loaded {len(docs)} total documents from {folder_path}.")
    return docs


def split_text(documents):
    print("----> Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print(f"----> Split into {len(chunks)} chunks.")
    return chunks


def save_to_chroma(chunks):
    if not chunks:
        print(" No chunks to save, skipping Chroma creation.")
        return

    print("Updating Chroma database with Nomic Embeddings...")
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    
    # Check if database exists
    if os.path.exists(CHROMA_PATH):
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        db.add_documents(chunks)
    else:
        db = Chroma.from_documents(
            chunks,
            embedding_function,
            persist_directory=CHROMA_PATH,
        )
    print(" Database updated successfully!")


if __name__ == "__main__":
    main()

