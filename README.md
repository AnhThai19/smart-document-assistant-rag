# Smart Document Assistant RAG

**Status:** Completed

Smart Document Assistant RAG is an AI-powered document question-answering system that allows users to upload documents and ask questions based on their content.

The project is designed as a practical RAG application for learning and demonstrating real-world AI engineering skills, including document ingestion, embeddings, vector search, LLM generation, chat history, short-term memory, question rewriting, evaluation, Docker, and Streamlit frontend development.

---

## Project Status

This project is currently **Completed as an MVP**.

### Completed

- FastAPI backend
- MongoDB integration for document metadata, chat sessions, and chat history
- Pinecone vector database integration
- Gemini Embedding API integration
- Groq LLM integration for answer generation and question rewriting
- TXT, PDF, and DOCX document upload
- Raw text ingestion
- Word-based chunking
- Document CRUD APIs
- Multi-document retrieval
- Source-grounded answer generation
- Chat sessions and chat history
- Short-term memory
- Follow-up question rewriting
- Retrieval evaluation script
- Docker backend setup
- Streamlit frontend demo
- User-facing document chat interface

---

## Features

### Document Processing

- Upload TXT files
- Upload PDF files
- Upload DOCX files
- Ingest raw text
- Extract text from documents
- Split document content into chunks
- Store document metadata in MongoDB
- Store document embeddings in Pinecone
- Delete documents and related vectors

### RAG Question Answering

- Generate embeddings for user questions
- Search relevant document chunks using Pinecone
- Generate grounded answers using Groq LLM
- Return sources used for each answer
- Support multi-document retrieval

### Chat and Memory

- Create chat sessions
- Continue previous chat sessions
- Store user and assistant messages
- Retrieve recent messages for short-term memory
- Rewrite follow-up questions into standalone questions before retrieval

Example:

```txt
User: Còn Pinecone thì sao?

Rewritten question:
Pinecone được dùng để làm gì trong hệ thống Smart Document Assistant RAG?
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Server | Uvicorn |
| Database | MongoDB |
| Vector Database | Pinecone |
| Embedding Model | Gemini Embedding API |
| LLM Generation | Groq API |
| PDF Parser | pypdf |
| DOCX Parser | python-docx |
| Frontend | Streamlit |
| Containerization | Docker, Docker Compose |
| Configuration | pydantic-settings |
| Validation | Pydantic |
| Language | Python |

---

## System Architecture

```txt
User
↓
Streamlit Frontend / Swagger UI
↓
FastAPI Backend
↓
Document Parser
↓
Chunking
↓
Gemini Embedding API
↓
Pinecone Vector Database
↓
Retriever
↓
Groq LLM
↓
Answer with Sources
```

MongoDB stores:

```txt
- Document metadata
- Chat sessions
- Chat messages
- Short-term conversation history
```

Pinecone stores:

```txt
- Chunk embeddings
- Chunk text
- Document ID
- User ID
- Chunk index
- Page metadata for PDF files
```

---

## RAG Pipeline

### 1. Document Ingestion

```txt
Upload document
↓
Extract text
↓
Split text into chunks
↓
Generate embeddings with Gemini Embedding API
↓
Store vectors in Pinecone
↓
Save document metadata in MongoDB
```

### 2. Question Answering

```txt
User question
↓
Load recent chat history
↓
Rewrite follow-up question
↓
Generate query embedding with Gemini
↓
Search similar chunks in Pinecone
↓
Build prompt with retrieved context
↓
Generate answer using Groq
↓
Save chat messages in MongoDB
```

---

## Project Structure

```txt
Smart-Document-Assistant-RAG/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   ├── documents.py
│   │   │   └── chat.py
│   │   │
│   │   ├── core/
│   │   │   └── config.py
│   │   │
│   │   ├── db/
│   │   │   ├── mongo.py
│   │   │   └── repositories/
│   │   │       ├── document_repo.py
│   │   │       └── chat_repo.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── document_schema.py
│   │   │   └── chat_schema.py
│   │   │
│   │   └── services/
│   │       ├── chunker.py
│   │       ├── embedder.py
│   │       ├── vector_store.py
│   │       ├── generator.py
│   │       ├── question_rewriter.py
│   │       ├── document_ingestion.py
│   │       ├── pdf_parser.py
│   │       └── docx_parser.py
│   │
│   ├── eval/
│   │   ├── test_questions.json
│   │   └── evaluate_retrieval.py
│   │
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── streamlit_app.py
│   └── requirements.txt
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## API Endpoints

### Health

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check backend health |

### Documents

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/documents/ingest-text` | Ingest raw text |
| POST | `/api/documents/upload-txt` | Upload and ingest TXT file |
| POST | `/api/documents/upload-pdf` | Upload and ingest PDF file |
| POST | `/api/documents/upload-docx` | Upload and ingest DOCX file |
| GET | `/api/documents` | List documents |
| GET | `/api/documents/{document_id}` | Get document detail |
| DELETE | `/api/documents/{document_id}` | Delete document and related vectors |

### Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat/test` | Test RAG chat without saving chat history |
| POST | `/api/chat/sessions` | Create chat session |
| GET | `/api/chat/sessions` | List chat sessions |
| GET | `/api/chat/sessions/{session_id}` | Get session detail and messages |
| POST | `/api/chat/sessions/{session_id}/messages` | Send message in a chat session |
| DELETE | `/api/chat/sessions/{session_id}` | Delete chat session and messages |

---

## Environment Variables

Create a `.env` file inside the `backend/` directory.

Use `backend/.env.example` as a template.

```env
APP_NAME=Smart Document Assistant RAG
APP_ENV=development

GEMINI_API_KEY=your_gemini_api_key
GEMINI_EMBEDDING_MODEL=gemini-embedding-001

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_groq_model

PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=smart-document-assistant-test

MONGODB_URI=your_mongodb_connection_string
MONGODB_DB_NAME=smart_document_assistant
```

---

## How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/smart-document-assistant-rag.git
cd smart-document-assistant-rag/backend
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Create a `.env` file inside the `backend/` folder and fill in your API keys.

```bash
cp .env.example .env
```

On Windows, you can manually copy `.env.example` and rename it to `.env`.

### 5. Run FastAPI Backend

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```txt
http://127.0.0.1:8000/docs
```

---

## Run with Docker

Make sure Docker Desktop is running.

From the project root:

```bash
docker compose build
docker compose up
```

Open:

```txt
http://127.0.0.1:8000/docs
```

Stop containers:

```bash
docker compose down
```

If you use MongoDB local with Docker, use:

```env
MONGODB_URI=mongodb://host.docker.internal:27017
```

If you use MongoDB Atlas, keep the normal `mongodb+srv://...` connection string.

---

## Example Usage

### Upload a Document

Use one of the following endpoints:

```txt
POST /api/documents/upload-txt
POST /api/documents/upload-pdf
POST /api/documents/upload-docx
```

The system returns a `document_id`.

### Ask a Question

Use:

```txt
POST /api/chat/test
```

Example request:

```json
{
  "question": "Pinecone được dùng để làm gì?",
  "document_id": "doc_xxx",
  "user_id": "demo_user",
  "top_k": 3
}
```

Example response:

```json
{
  "question": "Pinecone được dùng để làm gì?",
  "answer": "Pinecone được dùng để lưu vector embedding và thực hiện semantic search.",
  "sources": [
    {
      "document_id": "doc_xxx",
      "chunk_index": 1,
      "page": 1,
      "text": "Pinecone được dùng để lưu vector embedding..."
    }
  ]
}
```
