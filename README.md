# LLMOps — Large Language Model Operations Platform

> Not a script that wraps API calls.  
> A production-grade LLM application backend — from knowledge base to Agent, from single-turn chat to multi-channel deployment.

---

## What Problem Does This Solve

The real challenge of taking LLMs from demo to production is never the model itself — it's the engineering infrastructure around it:

- Knowledge base documents can run hundreds of pages, vectorization is slow — **how do you keep the main flow non-blocking?**
- Repeated vectorization of the same content wastes API budget — **how do you eliminate redundant embedding calls?**
- Keyword search misses semantics; vector search misses exact terms — **how do you get the best of both?**
- Different scenarios need different tools (search, image generation, weather) — **how do you make Agent capabilities extensible instead of hardcoded?**
- The same Agent needs to serve a web app, an API, and WeChat simultaneously — **how do you unify multi-channel deployment without duplicating logic?**
- Business logic, AI logic, and data layer tangled together — **how do you keep the system testable, maintainable, and iterable?**

This project answers each of these questions with concrete engineering decisions.

---

## Platform Capabilities at a Glance

| Category | Capability |
| :--- | :--- |
| **Agent Engine** | FunctionCall + ReACT dual-mode, auto-selected at runtime by model feature detection |
| **Memory** | Short-term `TokenBufferMemory` + long-term rolling summary, both injected per turn |
| **Tool System** | Built-in tools + OpenAPI custom tools + Workflow-as-Tool, unified `BaseTool` interface |
| **RAG Pipeline** | 5-stage async indexing → dual-track index → 3-strategy hybrid retrieval |
| **Multi-Channel** | Debug / WebApp / OpenAPI / WeChat — one Agent config, four deployment channels |
| **Config Versioning** | Draft → Publish → History → Rollback, full lifecycle with snapshot isolation |
| **Observability** | Per-step AgentThought token/price/latency + 7-day trend dashboard with WoW comparison |
| **Auth** | JWT + GitHub OAuth + API Key, three authentication modes |
| **Storage** | Tencent Cloud COS + MD5 dedup + upload whitelist |
| **Voice** | Whisper STT + streaming TTS output |

---

## Six Core Engineering Decisions

### Decision 1: Async-First — All High-Latency AI Tasks Offloaded to a Task Queue

**Problem**: Document parsing, text chunking, and vectorization are inherently high-latency operations. Handling them synchronously blocks the API response directly.

**Decision**: Introduced **Celery + Redis** to build an async task layer. All document indexing and vector write operations are fully asynchronous. The indexing pipeline runs as a **5-stage state machine**: `WAITING → PARSING → SPLITTING → INDEXING → COMPLETED`, with each stage's timestamp and error state persisted — fully traceable and recoverable.

**Outcome**: Main flow response time is completely decoupled from document volume. The system handles large-scale knowledge bases without degradation.

---

### Decision 2: Redis Cache-Backed Embeddings — Eliminate Redundant API Calls

**Problem**: Calling the OpenAI Embedding API for the same content repeatedly wastes token budget. In a knowledge base system, document re-indexing and query-time embedding both risk hitting the same content multiple times.

**Decision**: Wrapped `OpenAIEmbeddings` with LangChain's **`CacheBackedEmbeddings`** backed by a **Redis store**. Every embedding result is persisted by content hash — identical text is never sent to the API twice. Additionally, a **content hash comparison** is applied on segment updates — the vector store is only updated when content actually changes.

```python
self._cache_backed_embeddings = CacheBackedEmbeddings.from_bytes_store(
    self._embeddings,   # OpenAIEmbeddings
    self._store,        # RedisStore
    namespace="embeddings",
)
```

| Approach | Repeated Content | Cost Behavior |
| :--- | :--- | :--- |
| Raw OpenAI Embedding API | Re-embeds every time | Scales linearly with calls |
| **Cache-Backed + Hash Check (this project)** | Cache hit + skip unchanged | Marginal cost drops to zero after first embed |

---

### Decision 3: Hybrid Retrieval + RRF Fusion — Semantic and Keyword, Best of Both

**Problem**: Pure vector search misses exact keyword matches; pure keyword search misses semantic similarity. Neither alone is sufficient for production RAG.

**Decision**: Built a **dual-track index** (Weaviate vector store + Jieba keyword inverted index) maintained in **strong consistency** — every segment create/update/delete synchronizes both indexes atomically. Three retrieval strategies are selectable at runtime:

- **Semantic Search** — dense vector similarity via Weaviate
- **Full-Text Search** — sparse keyword matching via Jieba-tokenized inverted index
- **Hybrid Search** — both tracks run in parallel, results fused via **Reciprocal Rank Fusion (RRF)**

Concurrent writes to the keyword index are protected by **Redis distributed locks** — no phantom data under parallel indexing.

**Outcome**: Retrieval quality adapts to query type. Dual-index strong consistency is maintained across all write paths.

---

### Decision 4: Unified Tool Layer — Three Tracks, One Interface

**Problem**: Hardcoded tool lists are the most common anti-pattern in Agent systems — every new tool requires changes to core code.

**Decision**: The tool layer uses a **three-track parallel** architecture, all exposing a unified `BaseTool` interface:

- **Built-in Tools**: Pre-configured tools (Google Serper, DuckDuckGo, Wikipedia, DALL-E 3, Gaode Weather, etc.) loaded via factory pattern — zero hardcoded dispatch
- **Custom API Tools**: Dynamic registration via OpenAPI Schema — parameters validated on ingestion, type-safe Pydantic model generated at runtime via `create_model()`
- **Workflow-as-Tool**: Published workflows are wrapped as `BaseTool` — the Agent calls a workflow exactly like any other tool, with no awareness of the underlying DAG

The Agent has zero awareness of which track a tool comes from. Core dispatch logic requires zero modification to extend.

---

### Decision 5: Multi-Channel Deployment — One Agent Config, Four Channels

**Problem**: The same Agent logic needs to serve a developer API, an embedded web app, and WeChat simultaneously — duplicating execution logic per channel is unmaintainable.

**Decision**: All four channels converge on the same Agent execution core:

| Channel | Auth | User Model | Special Handling |
| :--- | :--- | :--- | :--- |
| Debug | Login session | Account | Draft config, no publish required |
| WebApp | App Token | Account | Model `features` exposed to drive frontend UI |
| OpenAPI | API Key | EndUser | Multi-tenant end-user isolation |
| WeChat | Signature verify | WechatEndUser | Thread + placeholder reply + follow-up polling to solve 5s timeout |

The WeChat channel deserves special mention: WeChat requires a response within 5 seconds, but Agent inference can take 10–30 seconds. The solution — return a placeholder reply immediately, run inference in a background thread, and persist the result once ready. The user triggers a follow-up message to check completion status and retrieve the answer — no timeout, no blocking wait.

---

### Decision 6: Clean Architecture — 3-Layer Separation for Full Testability

**Decision**: Strictly enforced **Handler → Service → Core** 3-layer separation across **30+ service classes**:

- **Handler Layer**: HTTP request parsing and input validation only (Marshmallow Schema) — no business logic, no DB access
- **Service Layer**: Pure business logic orchestration — no awareness of HTTP internals
- **Core Layer**: AI capability encapsulation (Embeddings, vector retrieval, tool dispatch, Agent execution) — independently testable

Infrastructure initialization (Celery, Redis, Weaviate, DB) is isolated into a dedicated `extension/` layer. **Dependency injection via `Injector`** eliminates manual wiring across all 30+ services.

**Outcome**: Service and Core layer logic is testable without starting Flask. CI efficiency is significantly improved.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Channel Access Layer               │
│         Debug │ WebApp │ OpenAPI │ WeChat (async push)      │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                    Agent Execution Core                     │
│         FunctionCallAgent ←→ ReACTAgent (auto-routed)       │
│    TokenBufferMemory + LongTerm Summary + ReviewConfig      │
│              AgentQueueManager (stream events)              │
└──────────┬──────────────────┬──────────────────┬───────────┘
           ↓                  ↓                  ↓
┌──────────────────┐ ┌────────────────┐ ┌────────────────────┐
│   Tool System    │ │  RAG Pipeline  │ │  Workflow Engine   │
│  BuiltinTool     │ │  Semantic      │ │  DAG Node Stream   │
│  ApiTool         │ │  FullText      │ │  Workflow-as-Tool  │
│  WorkflowTool    │ │  Hybrid (RRF)  │ │                    │
└──────────────────┘ └────────────────┘ └────────────────────┘
           ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│              Observability + Persistence Layer              │
│  AgentThought (token/price/latency) │ DatasetQuery Logs     │
│  Message History (soft delete)      │ Analysis Dashboard    │
│  Redis Cache │ Weaviate │ PostgreSQL │ Tencent COS          │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| Web Framework | Flask |
| Agent Framework | LangChain (LCEL, Tools, Memory) |
| Async Tasks | Celery + Redis |
| Vector Store | Weaviate |
| Embeddings | OpenAI Embeddings + Redis Cache-Backed Layer |
| Hybrid Retrieval | Weaviate (semantic) + Jieba (keyword) + RRF fusion |
| Local LLM | Ollama (e.g. Qwen2.5) |
| ORM & Migrations | SQLAlchemy + Alembic |
| Data Validation | Marshmallow |
| Chinese Tokenization | Jieba |
| Dependency Injection | Injector |
| Voice | OpenAI Whisper (STT) + TTS streaming |
| WeChat Integration | wechatpy |
| Object Storage | Tencent Cloud COS |
| Testing | Pytest |

---

## Getting Started

```bash
git clone https://github.com/muzinan123/llmops.git
cd llmops

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env  # Configure API Keys and database connection

# Start the main service
flask run

# Start the Celery worker (separate terminal)
celery -A app.celery worker --loglevel=info

# Run tests
pytest
```

---

## 📝 Engineering Articles

> The following article series document the core engineering philosophy and technical decisions behind this platform.

### 🤖 Agent Systems
📚 [Enterprise LLM Agent Systems Engineering](https://dev.to/jamesli/series/29494) *(7 articles — ReAct, Plan-and-Execute, Tool Design, OpenAI Assistants API)*

### ⛓️ LLM Chains & Orchestration
📚 [Complex LLM Chains Implementation Series](https://dev.to/jamesli/series/29491) *(5 articles — Multi-model routing, Conditional chains, Parallel processing, Context management)*

### 🔧 Framework Deep Dives
📚 [LangChain Development Guide](https://dev.to/jamesli/series/29453) *(5 articles — Runnable components, Memory, LCEL advanced patterns)*  
📚 [LangGraph Advanced Tutorial](https://dev.to/jamesli/series/29448) *(9 articles — Streaming, Subgraphs, Checkpoints, Human-in-the-loop)*

### 📚 RAG Pipeline
📚 [RAG Development & Optimization](https://dev.to/jamesli/series/29434) *(10 articles — Indexing strategy, Hybrid retrieval, Self-query, End-to-end optimization)*

### 🚀 Production Deployment
📚 [Enterprise-Level Deployment and Optimization of LLM Applications](https://dev.to/jamesli/enterprise-level-deployment-and-optimization-of-llm-applications-a-production-practice-guide-based-3jpg) *(Token management, Latency optimization, Cost control)*
