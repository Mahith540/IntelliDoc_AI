  # IntelliDoc AI 💠
**Next-Generation Document Intelligence & Analysis Hub**

IntelliDoc AI is a powerful, locally-hosted RAG (Retrieval-Augmented Generation) system designed to ingest, process, and analyze complex documents with cinematic precision. It features a modern, responsive web interface and a robust FastAPI backend.

## 🚀 Key Features
- **Smart Ingestion Pipeline**: Modular processing for PDF, TXT, and Markdown files.
- **Cinematic Command Center**: A sleek, dark-themed UI for real-time document interaction.
- **High-Precision Retrieval**: Powered by **Nomic V1.5 Embeddings** and **ChromaDB**.
- **Local Intelligence**: 100% private processing using **Mistral** via **Ollama**.
- **Flow Visualizer**: Non-intrusive status monitoring for knowledge acquisition.
- **Medical Intelligence (Beta)**: specialized pipeline for hospital bill ingestion and analysis (MedBill Checker).

## 🛠 Tech Stack
- **Backend**: FastAPI, LangChain, ChromaDB, Ollama.
- **Frontend**: Vanilla JS, Tailwind CSS, Space Grotesk Typography
- **AI Core**: Mistral (LLM), Nomic-Embed-Text (Embeddings).

## 📥 Setup & Installation

### 1. Prerequisites
- Python 3.9+
- [Ollama](https://ollama.ai/) installed and running.
- Pull the required models:
  ```bash
  ollama pull mistral
  ollama pull nomic-embed-text
  ```

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/Mahith540/IntelliDoc_AI.git
cd IntelliDoc_AI

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Launching the Hub
```bash
# Start the FastAPI server
python app.py
```
Open your browser and navigate to `http://localhost:8000`.

## 📖 Usage
1. **Ingest Documents**: Drag and drop mission files (PDF, TXT, MD) into the ingestion zone.
2. **Knowledge Acquisition**: Watch the "Flow Bar" at the bottom as the system reads, organizes, and learns from your data.
3. **Neural Query**: Ask complex questions in the interface.
4. **Context Trace**: Use the "Analyze Context" button to see exactly which document segments were used to generate the answer.

## ⚖️ License
MIT License - See [LICENSE](LICENSE) for details.
