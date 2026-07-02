# 🛡️ Aegis Legal AI

**A production-grade, AI-Powered Legal Document Assistant designed to ingest, analyze, and draft legal contracts with high precision.**

## 🚀 Key Highlights
*   **AI-Powered Interactive Redlining:** Automatically drafts, modifies, and visually tracks changes to legal clauses based strictly on uploaded contracts.
*   **High-Precision Hybrid Search:** Combines vector embeddings and keyword algorithms (ChromaDB + RankBM25) fused via Reciprocal Rank Fusion (RRF) to instantly retrieve the exact legal context.
*   **Automated Compliance Auditing:** Features a secondary AI agent that scans drafts in real-time to detect, badge, and fix legal liability risks.

## 🏗️ Architecture Stack
*   **Frontend:** Next.js 14 (React), TypeScript, Tailwind CSS (Premium Glassmorphism Dark Mode), `react-diff-viewer-continued` for redlining.
*   **Backend:** FastAPI (Python), Google Gemini Pro API, LangChain, ChromaDB, Sentence-Transformers (`all-MiniLM-L6-v2`), PyPDF, python-docx.
*   **Evaluation:** Custom LLM-as-a-judge RAG evaluation suite measuring Faithfulness, Relevance, and Recall metrics.
*   **DevOps:** Multi-stage Dockerfiles, Docker Compose, PII-redacted structured JSON logging.

## 🛠️ Getting Started (Local Development)

### 1. Prerequisites
Ensure you have [Python 3.10+](https://www.python.org/downloads/) and [Node.js](https://nodejs.org/) installed.

### 2. API Keys
1. Create `.env.production` and `backend/.env` files based on `.env.example`.
2. Add your Google Gemini API Key to the `GEMINI_API_KEY` variable.

### 3. Run the Backend (FastAPI)
```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*API Documentation will be available at `http://localhost:8000/docs`*

### 4. Run the Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
*The UI Workspace will be available at `http://localhost:3000`*

## 🐳 Docker Deployment
To run the entire suite in isolated containers using Docker Compose:
```bash
docker-compose up --build -d
```

## 🔒 Security & Privacy
*   **PII Masking:** Built-in scrubbing of emails, phone numbers, and full names before logging or processing.
*   **Zero-Hallucination Guardrails:** The GenAI pipeline returns strict warnings if the provided reference context is missing or insufficient to draft a legally binding clause.
