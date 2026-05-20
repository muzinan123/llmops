# LLMOps — Large Language Model Operations Platform

> Not a script that wraps API calls. A production-grade LLM backend engineering framework.

---

## What Problem Does This Solve

The real challenge of taking LLMs from demo to production is never the model itself — it's the engineering infrastructure around it:

- Knowledge base documents can run hundreds of pages, vectorization is slow — **how do you keep the main flow non-blocking?**
- Different scenarios need different tools (search, image generation, weather) — **how do you make Agent capabilities extensible instead of hardcoded?**
- External Embedding APIs bring latency, cost, and data privacy risks — **how do you solve vectorization locally?**
- Business logic, AI logic, and data layer tangled together — **how do you keep the system testable, maintainable, and iterable?**

This project answers each of these questions with concrete engineering decisions.

✅ Async document indexing & vectorization — zero blocking on the main flow
✅ Locally deployed Nomic AI Embeddings — zero external dependency
✅ Dynamic tool registration — Agent capabilities extensible at runtime
✅ Clean Architecture 3-layer separation — fully testable end to end

---

## Four Core Engineering Decisions

### Decision 1: Async-First — All High-Latency AI Tasks Offloaded to a Task Queue

**Problem**: Document parsing, text chunking, and vectorization are inherently high-latency operations. Handling them synchronously blocks the API response directly, resulting in a terrible user experience.

**Decision**: Introduced **Celery + Redis** to build an async task layer. All document indexing and vector write operations are fully asynchronous — the API layer only accepts requests and returns task status.

**Outcome**: Main flow response time is completely decoupled from document volume. The system is engineered to handle large-scale knowledge bases without degradation.

---

### Decision 2: Locally Deployed Embedding Model Instead of External API

**Problem**: Calling the OpenAI Embedding API introduces three risks: unpredictable network latency, token costs that scale linearly with data volume, and compliance risks from sensitive documents leaving the network boundary.

**Decision**: Integrated **Nomic AI** embedding models for local deployment, including full tokenizer, vocabulary, and model snapshots. Vectorization is completed entirely within the service — zero external dependency.

| Approach | Latency | Cost | Data Privacy |
| :--- | :--- | :--- | :--- |
| OpenAI Embedding API | Network round-trip, unpredictable | Per-token billing | Data leaves boundary |
| **Nomic AI Local Deployment (this project)** | Local inference, stable low latency | One-time deploy, zero marginal cost | Data stays local |

---

### Decision 3: Dual-Track Tool Layer — Agent Capabilities Dynamically Extensible

**Problem**: Hardcoded tool lists are the most common anti-pattern in Agent systems — every new tool requires changes to core code, making extension expensive and maintenance a nightmare.

**Decision**: The tool layer uses a **dual-track parallel** architecture:
- **Built-in Tools (BuiltinToolProvider)**: Pre-configured high-frequency tools ready out of the box — Google Serper, DuckDuckGo, Wikipedia, DALL-E 3, Gaode Weather, and more
- **Custom Tools (ApiTool)**: Supports dynamic registration of any external API via OpenAPI spec, with zero changes to core code

**Outcome**: Agent tool capabilities are extensible at runtime. Core dispatch logic requires zero modification.

---

### Decision 4: Clean Architecture — 3-Layer Separation for Full Testability

**Problem**: LLM projects iterate fast in early stages. Mixing business logic, AI logic, and database operations is the norm — and it makes code nearly impossible to test or refactor.

**Decision**: Strictly enforced **Handler → Service → Core** 3-layer separation:
- **Handler Layer**: HTTP request parsing and input validation only (Marshmallow Schema)
- **Service Layer**: Pure business logic orchestration, no awareness of HTTP or database internals
- **Core Layer**: AI capability encapsulation (Embeddings, vector retrieval, tool dispatch) — independently testable

**Outcome**: The test suite can directly test Service and Core layer logic without starting Flask. CI efficiency is significantly improved.

---

## System Overview

```
┌─────────────────────────────────────────────────────┐
│                    HTTP API Layer                    │
│   AppHandler  DatasetHandler  ToolHandler  FileHandler│
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                   Service Layer                      │
│   AppService  DatasetService  ToolService  CosService│
└──────┬───────────────┬─────────────────┬────────────┘
       │               │                 │
┌──────▼──────┐ ┌──────▼──────┐ ┌───────▼────────────┐
│  Core AI    │ │  Data Layer │ │   Async Task Layer  │
│  Embeddings │ │  PostgreSQL │ │   Celery + Redis    │
│  VectorDB   │ │  SQLAlchemy │ │   Indexing / Embed  │
│  Tools      │ │  COS Storage│ │                    │
└─────────────┘ └─────────────┘ └────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| Web Framework | Flask |
| Async Tasks | Celery + Redis |
| Vector Embeddings | Nomic AI (local deployment) |
| ORM & Migrations | SQLAlchemy + Alembic |
| Data Validation | Marshmallow |
| Chinese Tokenization | Jieba |
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

