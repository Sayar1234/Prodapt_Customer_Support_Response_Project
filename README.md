# AI Customer Support Response Generator

A minimalist AI based customer support response generator that generates responses to the user query.

# Features

- Has two modes: Strict Mode and Friendly Mode
- Takes user query and generates suitable response based on selected mode.
- Also returns which chunks are related to sent query. (Buggy)

# Tech Used

- Frontend: React + TypeScript
- Styling: TailwindCSS
- Backend: FastAPI
- AI API: OpenRouter
- Vector Embeddings: Pinecone

# How to run?

Running the backend

```bash
# Go to backend folder
cd backend/

# Create a virtual environment
python -m venv venv

# Start off virtual environment
venv/Scripts/activate

# Install requirements
pip install -r requirements.txt

# Run the backend
uvicorn app.main:app --reload
```

Backend will be live at http://localhost:8000

Running the frontend

```bash
# Go to frontend folder
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

Frontend will be live at http://localhost:5173
