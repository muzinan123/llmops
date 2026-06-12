# LLMOps — Large Language Model Operations Platform

> Not a script that wraps API calls. A production-grade LLM backend engineering framework.

---

## What Problem Does This Solve

The real challenge of taking LLMs from demo to production is never the model itself — it's the engineering infrastructure around it:

- Knowledge base documents can run hundreds of pages, vectorization is slow — **how do you keep the main flow non-blocking?**
- Repeated vectorization of the same content wastes API budget — **how do you eliminate redundant embedding calls?**
- Different scenarios need different tools (search, image generation, weather) — **how do you make Agent capabilities extensible instead of hardcoded?**
- Keyword search misses semantics; vector search misses exact terms — **how do you get the best of both?**
- Business logic, AI logic, and data layer tangled together — **how do you keep the system testable, maintainable, and iterable?**

This project answers each of these questions with concrete engineering decisions.

✅ Async document indexing & vectorization — zero blocking on the main flow  
✅ Redis Cache-Backed Embeddings — redundant vectorization calls eliminated  
✅ Hybrid Retrieval + RRF fusion — semantic + keyword, best of both  
✅ RAG-as-Tool — knowledge base plugged directly into Agent as a callable tool  
✅ Dynamic tool registration — Agent capabilities extensible at runtime  
✅ Clean Architecture 3-layer separation — fully testable end to end  

---

## Five Core Engineering Decisions

### Decision 1: Async-First — All High-Latency AI Tasks Offloaded to a Task Queue

**Problem**: Document parsing, text chunking, and vectorization are inherently high-latency operations. Handling them synchronously blocks the API response directly, resulting in a terrible user experience.

**Decision**: Introduced **Celery + Redis** to build an async task layer. All document indexing and vector write operations are fully asynchronous — the API layer only accepts requests and returns task status. The indexing pipeline runs as a 5-stage state machine: `WAITING → PARSING → SPLITTING → INDEXING → COMPLETED`.

**Outcome**: Main flow response time is completely decoupled from document volume. The system is engineered to handle large-scale knowledge bases without degradation.

---

### Decision 2: Redis Cache-Backed Embeddings — Eliminate Redundant API Calls

**Problem**: Calling the OpenAI Embedding API for the same content repeatedly wastes token budget and adds unnecessary latency. In a knowledge base system, document re-indexing and query-time embedding both risk hitting the same content multiple times.

**Decision**: Wrapped `OpenAIEmbeddings` with LangChain's **`CacheBackedEmbeddings`** backed by a **Redis store**. Every embedding result is persisted by content hash — identical text is never sent to the API twice.

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
| **Cache-Backed Embeddings (this project)** | Cache hit, zero API call | Marginal cost drops to zero after first embed |

---

### Decision 3: Hybrid Retrieval + RRF Fusion — Semantic and Keyword, Best of Both

**Problem**: Pure vector search misses exact keyword matches; pure keyword search misses semantic similarity. Neither alone is sufficient for production RAG.

**Decision**: Built a **dual-track index** (Weaviate vector store + Jieba keyword table) and implemented **three retrieval strategies** selectable at runtime:

- **Semantic Search** — dense vector similarity via Weaviate
- **Full-Text Search** — sparse keyword matching via Jieba-tokenized inverted index
- **Hybrid Search** — both tracks run in parallel, results fused via **Reciprocal Rank Fusion (RRF)**

RRF merges ranked lists without requiring score normalization — robust across heterogeneous retrieval sources.

**Outcome**: Retrieval quality adapts to query type. Exact-match queries and semantic queries both get optimal results from the same pipeline.

---

### Decision 4: Dual-Track Tool Layer — Agent Capabilities Dynamically Extensible

**Problem**: Hardcoded tool lists are the most common anti-pattern in Agent systems — every new tool requires changes to core code, making extension expensive and maintenance a nightmare.

**Decision**: The tool layer uses a **dual-track parallel** architecture:
- **Built-in Tools (BuiltinToolProvider)**: Pre-configured high-frequency tools ready out of the box — Google Serper, DuckDuckGo, Wikipedia, DALL-E 3, Gaode Weather, and more. Loaded via factory pattern at runtime — zero hardcoded dispatch.
- **Custom Tools (ApiTool)**: Supports dynamic registration of any external API via OpenAPI spec. Parameters are validated on ingestion, and a type-safe Pydantic model is generated at runtime via `create_model()` — zero changes to core code.

Both tracks expose a unified `BaseTool` interface to the Agent — the Agent has no awareness of which track a tool comes from.

**Outcome**: Agent tool capabilities are extensible at runtime. Core dispatch logic requires zero modification.

---

### Decision 5: Clean Architecture — 3-Layer Separation for Full Testability

**Problem**: LLM projects iterate fast in early stages. Mixing business logic, AI logic, and database operations is the norm — and it makes code nearly impossible to test or refactor.

**Decision**: Strictly enforced **Handler → Service → Core** 3-layer separation:
- **Handler Layer**: HTTP request parsing and input validation only (Marshmallow Schema) — no business logic, no DB access
- **Service Layer**: Pure business logic orchestration — no awareness of HTTP internals
- **Core Layer**: AI capability encapsulation (Embeddings, vector retrieval, tool dispatch, RAG-as-Tool) — independently testable

Infrastructure initialization (Celery, Redis, Weaviate, DB) is further isolated into a dedicated `extension/` layer — keeping startup lifecycle concerns out of business code entirely.

**Outcome**: The test suite can directly test Service and Core layer logic without starting Flask. CI efficiency is significantly improved.

---

## System Overview

```
┌──────────────────────────────────────────────────────────┐
│                      HTTP API Layer                      │
│   AppHandler  DatasetHandler  ToolHandler  FileHandler   │
└─────────────────────────┬────────────────────────────────┘
                           │
┌─────────────────────────▼────────────────────────────────┐
│                     Service Layer                        │
│   AppService  DatasetService  ToolService  CosService    │
└──────┬──────────────────┬──────────────────┬────────────┘
       │                  │                  │
┌──────▼──────┐  ┌────────▼───────┐  ┌───────▼───────────┐
│  Core AI    │  │  Data Layer    │  │  Async Task Layer  │
│  Embeddings │  │  PostgreSQL    │  │  Celery + Redis    │
│  (w/ Cache) │  │  SQLAlchemy    │  │  5-Stage Indexing  │
│  VectorDB   │  │  COS Storage   │  │  Pipeline          │
│  Hybrid RAG │  └────────────────┘  └───────────────────┘
│  Tools      │
└─────────────┘
```

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| Web Framework | Flask |
| Async Tasks | Celery + Redis |
| Vector Store | Weaviate |
| Embeddings | OpenAI Embeddings + Redis Cache-Backed Layer |
| Hybrid Retrieval | Weaviate (semantic) + Jieba (keyword) + RRF fusion |
| Local LLM | Ollama (chat models, e.g. Qwen2.5) |
| ORM & Migrations | SQLAlchemy + Alembic |
| Data Validation | Marshmallow |
| Chinese Tokenization | Jieba |
| Dependency Injection | Injector |
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

## 📝 Related Articles

📚 [Building Enterprise Agent Systems: Core Component Design and Optimization](https://dev.to/jamesli/building-enterprise-agent-systems-core-component-design-and-optimization-5h6c)

📚 [Agent Tool Development Guide: From Design to Optimization](https://dev.to/jamesli/agent-tool-development-guide-from-design-to-optimization-58l4)

📚 [Building an Agent Tool Management Platform: A Practical Architecture Guide](https://dev.to/jamesli/building-an-agent-tool-management-platform-a-practical-architecture-guide-1h2a)
