#  DocReader AI — Local RAG System

**DocReader AI** is an offline Retrieval-Augmented Generation (RAG) system that lets users query their own data using **Ollama + LangChain + ChromaDB** — no cloud dependencies.

##  Features
- Runs 100% locally with **Mistral** and **Ollama**
- Uses **Chroma** for vector storage
- Modular structure for easy extension
- Simple CLI interface for document Q&A
- Future-ready for PDF, TXT, or Markdown sources

##  Tech Stack
- Python 3.9+
- LangChain
- ChromaDB
- Ollama (Mistral model)
- dotenv

##  Setup
```bash
git clone https://github.com/<your-username>/DocReaderAI.git
cd DocReaderAI
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull mistral
python populate_database.py
python query_database.py


Example Queries
What are cutaneous receptors and what do they do?”
How much money does each player start with in Monopoly?
“Explain the function of nociceptors in the skin.”
“What is the role of muscle spindles in proprioception?”
📘 Author

Built with ❤️ by Mahith Bandaru

