# Enterprise Agentic Workflow Engine

> A production-grade AI orchestration platform that lets you define natural-language goals, select tools, and watch autonomous agents execute them in real time — streamed live to a professional dark-mode dashboard.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (React 18)                        │
│                                                                   │
│  WorkflowBuilder ──POST──► api.js (Axios) ──► LiveDashboard      │
│       │                                           │               │
│  WorkflowList                            EventTimeline           │
│  DataVault (upload)              MarkdownResult (final output)   │
│  LogsPage                                         │               │
│                                         useWorkflowWebSocket      │
└───────────────────────────────────────────────────┼─────────────┘
                                                    WS (JSON events)
                                                    │
┌───────────────────────────────────────────────────▼─────────────┐
│                      FASTAPI BACKEND (Python)                     │
│                                                                   │
│  POST /api/v1/workflows ──► BackgroundTask ──► WorkflowService   │
│  GET  /api/v1/workflows/{id}                       │              │
│  GET  /api/v1/tools                        EnterpriseAgent        │
│  POST /api/v1/documents/upload                     │              │
│  GET  /api/v1/logs/{workflow_id}           ┌───────▼──────┐      │
│  WS   /ws/execution/{workflow_id}          │ LangChain     │      │
│                                            │ AgentExecutor │      │
│  Middleware Stack:                         │ + Tools       │      │
│  • CORS                                    └───────┬──────┘      │
│  • slowapi rate limiting (60 req/min)              │              │
│  • Structured JSON logging (structlog)     WebSocketCallback      │
│  • Global exception handlers              TokenUsageTracker       │
└────────────────────────────────────────────────────┼─────────────┘
                                                     │
              ┌──────────────────────────────────────▼──────────────┐
              │                  TOOL REGISTRY                        │
              │                                                        │
              │  Tool Set A (Web)         Tool Set B (File)           │
              │  • web_search             • read_json_file            │
              │    (DuckDuckGo)           • write_json_file           │
              │  • scrape_webpage         • read_csv_file             │
              │    (httpx + BS4)          • write_text_file           │
              │                                                        │
              │  Tool Set C (Knowledge)                               │
              │  • query_knowledge_base (FAISS similarity search)     │
              └──────────────────────────────────────────────────────┘
                                                     │
              ┌──────────────────────────────────────▼──────────────┐
              │                PERSISTENCE LAYER                      │
              │                                                        │
              │  SQLite (aiosqlite / SQLAlchemy 2.0 async)           │
              │  ├── workflows      (goal, status, result, cost)      │
              │  ├── tasks          (step-by-step breakdown)          │
              │  ├── execution_logs (typed events, metadata JSON)     │
              │  └── chat_history   (LangChain message history)       │
              │                                                        │
              │  FAISS Vector Store  (HuggingFace all-MiniLM-L6-v2)  │
              │  └── Persistent index for uploaded documents          │
              └──────────────────────────────────────────────────────┘
```

---

## Feature Highlights

| Category | Feature |
|---|---|
| **Orchestration** | LangChain `AgentExecutor` with `create_openai_tools_agent`; up to 15 tool-calling iterations |
| **LLM Support** | OpenAI (GPT-4o, GPT-4o-mini, GPT-4-turbo) + Ollama (Llama 3, local GPU) |
| **Tools** | Web search (DuckDuckGo), webpage scraping, JSON/CSV/text file I/O, FAISS vector search |
| **Memory** | `ConversationBufferWindowMemory` (k=10) backed by SQLite for cross-session persistence |
| **Vector Store** | FAISS with HuggingFace `all-MiniLM-L6-v2` embeddings; supports PDF, TXT, CSV, JSON, DOCX |
| **Real-time UI** | FastAPI WebSocket → typed JSON event stream → React timeline (token/tool_start/tool_end/agent_finish) |
| **Cost Tracking** | Per-run token accounting + USD cost estimation; displayed on dashboard |
| **Resilience** | Async exponential backoff retry (3 attempts, full jitter) for LLM API calls |
| **Observability** | structlog JSON logging, per-workflow execution log DB table, Swagger UI at `/api/docs` |
| **Frontend** | Pure React 18 + Webpack 5 + Tailwind CSS 3; no Next.js/Vite; dark-mode-first |
| **API Safety** | slowapi rate limiting, CORS, MIME-type guards on uploads, path-traversal prevention on file tools |

---

## Local Setup

### Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | bundled with Node |
| Git | any | — |

An **OpenAI API key** is required for cloud inference. For fully local inference, install [Ollama](https://ollama.ai) and pull `llama3`.

---

### 1 — Clone & configure

```bash
git clone https://github.com/AhmedIrfan7/Enterprise_Agentic_Workflow_Engine.git
cd Enterprise_Agentic_Workflow_Engine

# Backend env
cp backend/.env.example backend/.env
# Open backend/.env and set OPENAI_API_KEY=sk-...

# Frontend env (optional — defaults to localhost:8000)
cp frontend/.env.example frontend/.env
```

---

### 2 — Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- REST: `http://localhost:8000/api/v1/`
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

---

### 3 — Frontend

```bash
cd frontend

npm install
npm start        # Opens http://localhost:3000
```

---

### 4 — One-command startup (both services)

**Linux / macOS:**
```bash
chmod +x startup.sh
./startup.sh
```

**Windows:**
```bat
startup.bat
```

---

### 5 — Run tests

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

---

## Project Structure

```
Enterprise_Agentic_Workflow_Engine/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # health, workflows, documents, logs, tools, websocket
│   │   ├── core/
│   │   │   ├── agents/          # EnterpriseAgent, LLM factory, prompt templates,
│   │   │   │                    #   token tracker, WebSocket callback
│   │   │   ├── memory/          # ConversationBufferWindowMemory, FAISS vector store
│   │   │   └── tools/           # web_tools, file_tools, vector_tool, registry
│   │   ├── models/              # SQLAlchemy ORM: Workflow, Task, ExecutionLog
│   │   ├── schemas/             # Pydantic v2 request/response models
│   │   ├── services/            # workflow_service (execution loop), vector_service (ingestion)
│   │   ├── utils/               # CRUDBase, structured logging, exception hierarchy, retry
│   │   ├── config.py            # Pydantic BaseSettings (all config from .env)
│   │   ├── database.py          # SQLAlchemy async engine + Base
│   │   ├── dependencies.py      # FastAPI DI: get_db()
│   │   └── main.py              # Application factory (create_app)
│   ├── tests/                   # pytest: test_agent_core.py, test_api.py
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/          # Layout, Sidebar (collapsible), Topbar
│   │   │   ├── workflow/        # WorkflowBuilder, WorkflowList
│   │   │   ├── dashboard/       # LiveDashboard, EventTimeline, MarkdownResult
│   │   │   ├── vault/           # DataVault (upload + file list)
│   │   │   └── common/          # ErrorBoundary, Spinner
│   │   ├── context/             # Zustand stores (useWorkflowStore, useExecutionStore)
│   │   ├── hooks/               # useWorkflowWebSocket
│   │   ├── pages/               # WorkflowBuilderPage, DashboardPage, DataVaultPage, LogsPage
│   │   ├── services/            # api.js (Axios client, all endpoints + WS factory)
│   │   ├── App.js               # BrowserRouter + Routes
│   │   └── index.js             # React 18 createRoot entry point
│   ├── public/index.html
│   ├── webpack.config.js        # Webpack 5: code splitting, dev-server proxy, CSS pipeline
│   ├── babel.config.js
│   ├── tailwind.config.js       # Dark-mode, custom brand/surface palettes
│   └── package.json
│
├── startup.sh
├── startup.bat
└── README.md
```

---

## Environment Variables

All runtime configuration lives in `backend/.env`. See [`backend/.env.example`](backend/.env.example) for the full reference.

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required for OpenAI inference |
| `LLM_PROVIDER` | `openai` | `openai` or `ollama` |
| `LLM_MODEL` | `gpt-4o-mini` | Model name |
| `LLM_TEMPERATURE` | `0.2` | Sampling temperature |
| `DATABASE_URL` | `sqlite+aiosqlite:///./enterprise_workflows.db` | SQLAlchemy async URL |
| `VECTOR_STORE_PATH` | `./faiss_index` | FAISS persistence directory |
| `UPLOAD_DIR` | `./uploads` | Document upload directory |
| `RATE_LIMIT_PER_MINUTE` | `60` | API rate limit |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS allowed origins |

---

## Tech Stack

**Backend:** Python 3.11 · FastAPI 0.111 · LangChain 0.2 · LangGraph · SQLAlchemy 2.0 (async) · FAISS · HuggingFace Transformers · structlog · slowapi · Pydantic v2

**Frontend:** React 18 · Webpack 5 · Babel · Tailwind CSS 3 · Zustand · Axios · react-markdown · React Router v6

**Inference:** OpenAI API (GPT-4o family) · Ollama (local Llama 3)

---

*Built as a full-stack AI engineering capstone demonstrating production patterns: async orchestration, real-time streaming, vector retrieval, cost tracking, and enterprise UI/UX.*
