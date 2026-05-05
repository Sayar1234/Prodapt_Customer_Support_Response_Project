# AI Customer Support Response Generator

A minimalist AI-powered HR support response generator with hybrid retrieval, LlamaIndex, and LangServe integration.

## Features

- **Dual Modes**: Strict and Friendly response modes
- **Hybrid Retrieval**: BM25 keyword search + Pinecone semantic search
- **Auto-Reranking**: Intelligent document reranking for better context
- **Query Rewriting**: Automatic query optimization for retrieval
- **LangServe Integration**: REST API with interactive playground
- **LlamaIndex RAG**: Structured retrieval-augmented generation pipeline

## Tech Stack

- **Frontend**: React + TypeScript + TailwindCSS
- **Backend**: FastAPI + LlamaIndex + LangServe
- **LLM**: OpenRouter (GPT-4o-mini)
- **Vector DB**: Pinecone
- **Keyword Search**: BM25
- **Embeddings**: Sentence Transformers (MiniLM)

## Quick Setup

### 1. Backend Environment Variables

Create `backend/.env`:

```env
OPENROUTER_API_KEY=your_openrouter_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=hr-policy
```

### 2. Running the Backend

```bash
cd backend/

# Create and activate virtual environment
python -m venv venv
venv/Scripts/Activate.ps1          # Windows PowerShell
# source venv/bin/activate          # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

Backend runs at **http://localhost:8000**

### 3. Running the Frontend

```bash
cd frontend/

npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

## API Endpoints

### Legacy Endpoint (Backward Compatible)

- `POST /generate` - Original endpoint your frontend uses

### New LangServe Endpoints

- `POST /langserve/generate/invoke` - Full RAG pipeline (recommended)
- `POST /langserve/retrieve/invoke` - Document retrieval only
- `POST /langserve/rewrite/invoke` - Query rewriting
- `GET /langserve/generate/playground` - Interactive UI for testing
