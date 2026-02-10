# AI-Across Architecture

This document provides a comprehensive overview of the AI-Across system architecture, design decisions, and technical implementation details.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Database Design](#database-design)
- [RAG Pipeline](#rag-pipeline)
- [API Design](#api-design)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)
- [Technology Decisions](#technology-decisions)

---

## System Overview

AI-Across is a self-hosted AI content platform built with a modern microservices-inspired architecture. The system follows a three-tier architecture pattern:

1. **Presentation Layer** - React SPA (Single Page Application)
2. **Application Layer** - FastAPI REST API
3. **Data Layer** - PostgreSQL + ChromaDB

### Key Architectural Principles

- **Separation of Concerns** - Clear boundaries between API, services, and data access
- **Async-First** - All I/O operations use async/await for performance
- **Schema-Driven** - Pydantic models enforce data contracts
- **Local-First** - Self-hosted with no external dependencies except LLM APIs (OpenRouter + direct providers)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                    │
│                         React + Vite + Tailwind                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Dashboard  │  │    Chat     │  │  Assistant  │  │  Settings   │   │
│  │  Component  │  │  Interface  │  │   Manager   │  │    Page     │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                              │                                          │
│                    React Query + Zustand                                │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │ HTTP/REST + SSE
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         NGINX (Production)                               │
│                    Reverse Proxy + SSL Termination                       │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              BACKEND                                     │
│                         Python + FastAPI                                 │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                         API Layer (v1)                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │ │
│  │  │  assistants  │  │    files     │  │conversations │             │ │
│  │  │    router    │  │    router    │  │    router    │             │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │ │
│  └─────────┼─────────────────┼─────────────────┼──────────────────────┘ │
│            │                 │                 │                        │
│  ┌─────────▼─────────────────▼─────────────────▼──────────────────────┐ │
│  │                       Service Layer                                 │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │ │
│  │  │   Assistant    │  │     File       │  │     Chat       │       │ │
│  │  │    Service     │  │   Processor    │  │    Service     │       │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘       │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │ │
│  │  │      RAG       │  │   Embedding    │  │    Chroma      │       │ │
│  │  │    Service     │  │    Service     │  │    Service     │       │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘       │ │
│  └─────────┬─────────────────┬─────────────────┬──────────────────────┘ │
│            │                 │                 │                        │
│  ┌─────────▼─────────────────▼─────────────────▼──────────────────────┐ │
│  │                        Data Layer                                   │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │ │
│  │  │   SQLAlchemy   │  │   ChromaDB     │  │  File System   │       │ │
│  │  │    Session     │  │    Client      │  │    Storage     │       │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PostgreSQL    │  │    ChromaDB     │  │   OpenRouter    │
│                 │  │   (Vectors)     │  │      API        │
│  • assistants   │  │                 │  │                 │
│  • conversations│  │  • embeddings   │  │  • 50+ models   │
│  • messages     │  │  • chunks       │  │  • streaming    │
│  • files meta   │  │  • collections  │  │  • embeddings   │
│  • users        │  │                 │  │                 │
│  • usage_logs   │  │                 │  │                 │
│  • api_keys     │  │                 │  │                 │
│  • audit_logs   │  │                 │  │                 │
│  • settings     │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Component Architecture

### Frontend Components

```
frontend/
├── src/
│   ├── lib/
│   │   └── api/                 # API client modules
│   │       ├── client.ts        # Axios instance with interceptors
│   │       ├── assistants.ts    # Assistant API calls
│   │       ├── conversations.ts # Conversation/message API calls
│   │       ├── files.ts         # File upload API calls
│   │       └── models.ts        # LLM models API calls
│   ├── hooks/                   # React Query hooks
│   │   ├── use-assistants.ts    # Assistant CRUD hooks
│   │   ├── use-conversations.ts # Conversation management hooks
│   │   ├── use-models.ts        # Model fetching hook
│   │   ├── use-chat.ts          # Streaming chat hook
│   │   ├── use-auth.ts          # User auth hooks (login, verify, logout)
│   │   ├── use-admin.ts         # Admin dashboard hooks
│   │   └── index.ts             # Barrel exports
│   ├── components/              # Shared UI components
│   │   ├── ui/                  # shadcn/ui primitives
│   │   ├── layout/              # Layout components (Sidebar, Header)
│   │   ├── auth-guard.tsx       # User route protection
│   │   ├── quota-display.tsx    # User quota/usage widget
│   │   ├── assistant/           # Assistant-specific components
│   │   ├── file/                # File upload components
│   │   ├── admin/               # Admin UI components
│   │   │   ├── admin-layout.tsx
│   │   │   ├── admin-sidebar.tsx
│   │   │   ├── admin-guard.tsx
│   │   │   └── ...
│   │   └── chat/                # Chat interface components
│   │       ├── chat-window.tsx         # Main chat container
│   │       ├── conversation-sidebar.tsx # Conversation list
│   │       ├── message-list.tsx        # Scrollable messages
│   │       ├── message-bubble.tsx      # Individual message
│   │       ├── message-input.tsx       # Input with send/stop
│   │       ├── model-selector.tsx      # Model dropdown
│   │       ├── streaming-message.tsx   # Real-time streaming
│   │       ├── code-block.tsx          # Syntax highlighting
│   │       ├── message-edit-dialog.tsx # Edit message dialog
│   │       └── index.ts                # Barrel exports
│   ├── pages/                   # Route pages
│   │   ├── dashboard.tsx        # Main dashboard
│   │   ├── assistants.tsx       # Assistant list (read-only for users)
│   │   ├── assistant-detail.tsx # Single assistant view
│   │   ├── chat.tsx             # Chat interface page
│   │   ├── login.tsx            # User login page
│   │   ├── settings.tsx         # Settings (role-aware)
│   │   └── admin/               # Admin pages
│   │       ├── login.tsx        # Admin login
│   │       ├── index.tsx        # Admin dashboard
│   │       ├── assistants.tsx   # Admin assistant CRUD
│   │       ├── users.tsx        # User management
│   │       ├── api-keys.tsx     # API key management
│   │       ├── usage.tsx        # Usage & quotas
│   │       ├── settings.tsx     # System settings
│   │       └── audit-logs.tsx   # Audit log viewer
│   ├── stores/                  # Zustand stores
│   │   ├── app-store.ts         # Global app state
│   │   ├── auth-store.ts        # User auth state
│   │   └── admin-store.ts       # Admin auth + sidebar state
│   ├── lib/                     # Utility functions
│   ├── types/                   # TypeScript types
│   └── App.tsx                  # Root component with routing
├── public/                      # Static assets
└── index.html                   # Entry HTML
```

### Backend Components

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Dependency injection + auth helpers
│   │   └── v1/
│   │       ├── router.py        # Route aggregation
│   │       ├── assistants.py    # Assistant endpoints (admin write, any read)
│   │       ├── files.py         # File upload endpoints (admin write, any read)
│   │       ├── conversations.py # Chat endpoints (user-isolated)
│   │       ├── models.py        # LLM models endpoint
│   │       ├── settings.py      # App settings (admin write, any read)
│   │       ├── users.py         # Auth endpoints (login, verify, me, usage)
│   │       ├── admin.py         # Admin dashboard endpoints
│   │       ├── api_keys.py      # API key management (admin only)
│   │       ├── quotas.py        # Quota management (admin only)
│   │       └── audit.py         # Audit log endpoints (admin only)
│   │
│   ├── core/
│   │   ├── config.py            # Pydantic settings
│   │   └── exceptions.py        # Custom exceptions
│   │
│   ├── db/
│   │   ├── base.py              # SQLAlchemy base model
│   │   └── session.py           # Async session factory
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── assistant.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── knowledge_file.py
│   │   ├── settings.py
│   │   ├── usage_log.py
│   │   ├── user.py
│   │   ├── api_key.py
│   │   ├── usage_quota.py
│   │   └── audit_log.py
│   │
│   ├── schemas/                 # Pydantic request/response
│   │   ├── assistant.py
│   │   ├── file.py
│   │   └── conversation.py
│   │
│   ├── services/                # Business logic
│   │   ├── assistant_service.py
│   │   ├── conversation_service.py
│   │   ├── file_processor.py
│   │   ├── chroma_service.py
│   │   ├── embedding_service.py
│   │   ├── openrouter_service.py
│   │   ├── rag_service.py
│   │   ├── admin_auth_service.py
│   │   ├── usage_log_service.py
│   │   ├── user_service.py
│   │   ├── user_auth_service.py
│   │   ├── api_key_service.py
│   │   ├── quota_service.py
│   │   └── audit_service.py
│   │
│   ├── utils/                   # Utilities
│   │   ├── chunker.py
│   │   └── file_extractors.py
│   │
│   └── main.py                  # FastAPI app entry
│
├── alembic/                     # Database migrations
├── data/                        # Persistent storage
│   ├── uploads/                 # Uploaded files
│   └── chroma/                  # Vector database
└── tests/                       # Test suite
```

### Service Layer Pattern

Each service encapsulates a specific domain:

```python
# Example: AssistantService
class AssistantService:
    """Handles all assistant-related business logic."""

    async def create(db: AsyncSession, data: AssistantCreate) -> Assistant
    async def get(db: AsyncSession, id: UUID) -> Assistant | None
    async def list(db: AsyncSession, include_deleted: bool) -> list[Assistant]
    async def update(db: AsyncSession, id: UUID, data: AssistantUpdate) -> Assistant
    async def delete(db: AsyncSession, id: UUID) -> None  # Soft delete
    async def restore(db: AsyncSession, id: UUID) -> Assistant
```

---

## Data Flow

### Assistant Creation Flow

```
User Request                API Layer              Service Layer           Database
     │                          │                       │                     │
     │  POST /assistants        │                       │                     │
     │ ─────────────────────────>                       │                     │
     │                          │                       │                     │
     │                          │  validate(data)       │                     │
     │                          │ ─────────────────────>│                     │
     │                          │                       │                     │
     │                          │                       │  INSERT assistant   │
     │                          │                       │ ────────────────────>
     │                          │                       │                     │
     │                          │                       │  <─ assistant_id ───│
     │                          │                       │                     │
     │                          │  <── Assistant ───────│                     │
     │                          │                       │                     │
     │  <── 201 Created ────────│                       │                     │
```

### RAG Query Flow

```
User Message          RAG Service         Embedding Service      ChromaDB        OpenRouter
     │                    │                      │                  │                │
     │  query(message)    │                      │                  │                │
     │ ──────────────────>│                      │                  │                │
     │                    │                      │                  │                │
     │                    │  embed(message)      │                  │                │
     │                    │ ─────────────────────>                  │                │
     │                    │                      │                  │                │
     │                    │                      │  POST /embeddings│                │
     │                    │                      │ ─────────────────────────────────>│
     │                    │                      │                  │                │
     │                    │  <── vector ─────────│                  │                │
     │                    │                      │                  │                │
     │                    │  similarity_search(vector)              │                │
     │                    │ ───────────────────────────────────────>│                │
     │                    │                      │                  │                │
     │                    │  <── relevant_chunks ───────────────────│                │
     │                    │                      │                  │                │
     │  <── context ──────│                      │                  │                │
```

### File Processing Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Upload  │────>│  Extract │────>│  Chunk   │────>│  Embed   │────>│  Store   │
│   File   │     │   Text   │     │   Text   │     │  Chunks  │     │ Vectors  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │                │
     │                │                │                │                │
     ▼                ▼                ▼                ▼                ▼
 uploading       processing       processing       indexing          ready
```

---

## Database Design

### Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│     assistants      │       │   knowledge_files   │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │──────<│ id (PK)             │
│ name                │       │ assistant_id (FK)   │
│ description         │       │ filename            │
│ instructions        │       │ file_type           │
│ model               │       │ file_path           │
│ temperature         │       │ size_bytes          │
│ max_tokens          │       │ chunk_count         │
│ avatar_url          │       │ status              │
│ is_deleted          │       │ error_message       │
│ created_at          │       │ created_at          │
│ updated_at          │       └─────────────────────┘
└─────────────────────┘
          │
          │
          ▼
┌─────────────────────┐       ┌─────────────────────┐
│   conversations     │       │      messages       │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │──────<│ id (PK)             │
│ assistant_id (FK)   │       │ conversation_id (FK)│
│ user_id (FK)        │       │ role                │
│ title               │       │ content             │
│ created_at          │       │ model               │
│ updated_at          │       │ tokens_used (JSONB) │
└─────────────────────┘       │                     │
                              │ created_at          │
                              └─────────────────────┘

┌─────────────────────┐
│      settings       │
├─────────────────────┤
│ key (PK)            │
│ value               │
│ updated_at          │
└─────────────────────┘

┌─────────────────────┐       ┌─────────────────────┐
│       users         │       │     usage_logs      │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ email (unique)      │       │ assistant_id (FK)   │
│ password_hash       │       │ conversation_id (FK)│
│ name                │       │ message_id          │
│ role (enum)         │       │ model               │
│ is_active           │       │ prompt_tokens       │
│ last_login_at       │       │ completion_tokens   │
│ created_at          │       │ total_tokens        │
│ updated_at          │       │ cost_usd            │
└─────────────────────┘       │ created_at          │
                              └─────────────────────┘

┌─────────────────────┐       ┌─────────────────────┐
│      api_keys       │       │    usage_quotas     │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ provider (enum)     │       │ scope (enum)        │
│ name                │       │ scope_id            │
│ encrypted_key       │       │ daily_cost_limit    │
│ is_default          │       │ monthly_cost_limit  │
│ is_active           │       │ daily_token_limit   │
│ last_used_at        │       │ monthly_token_limit │
│ created_at          │       │ requests_per_min    │
│ updated_at          │       │ requests_per_hour   │
└─────────────────────┘       │ alert_threshold     │
                              │ created_at          │
                              │ updated_at          │
                              └─────────────────────┘

┌─────────────────────┐
│     audit_logs      │
├─────────────────────┤
│ id (PK)             │
│ actor_id (FK)       │
│ actor_email         │
│ action              │
│ resource_type       │
│ resource_id         │
│ old_values (JSONB)  │
│ new_values (JSONB)  │
│ ip_address          │
│ user_agent          │
│ created_at          │
└─────────────────────┘
```

### Table Specifications

| Table | Primary Key | Indexes | Relationships |
|-------|-------------|---------|---------------|
| assistants | UUID | - | Has many: files, conversations |
| knowledge_files | UUID | assistant_id | Belongs to: assistant |
| conversations | UUID | assistant_id, user_id, created_at | Belongs to: assistant, user; Has many: messages |
| messages | UUID | conversation_id, created_at | Belongs to: conversation |
| settings | VARCHAR(100) | - | Standalone key-value |
| users | UUID | email (unique) | Has many: audit_logs |
| usage_logs | UUID | created_at | Belongs to: assistant, conversation |
| api_keys | UUID | provider | Standalone |
| usage_quotas | UUID | scope, scope_id | Standalone |
| audit_logs | UUID | created_at, actor_id | Belongs to: user |

---

## RAG Pipeline

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           RAG PIPELINE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    INDEXING PIPELINE                             │   │
│  │                                                                  │   │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │   │
│  │  │  File    │──>│   Text   │──>│  Chunk   │──>│  Store   │    │   │
│  │  │  Upload  │   │ Extract  │   │  (512)   │   │ ChromaDB │    │   │
│  │  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │   │
│  │       │              │              │              │           │   │
│  │       ▼              ▼              ▼              ▼           │   │
│  │    PDF/DOCX      Raw Text      512-token      Embeddings      │   │
│  │    TXT/MD                       chunks        + metadata       │   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    RETRIEVAL PIPELINE                            │   │
│  │                                                                  │   │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │   │
│  │  │  User    │──>│  Embed   │──>│ Semantic │──>│  Inject  │    │   │
│  │  │  Query   │   │  Query   │   │  Search  │   │ Context  │    │   │
│  │  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │   │
│  │       │              │              │              │           │   │
│  │       ▼              ▼              ▼              ▼           │   │
│  │   "Write PR"    1536-dim       Top-5 @ 0.7   System prompt    │   │
│  │                  vector         threshold    + retrieved      │   │
│  │                                               chunks          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| Chunk Size | 512 tokens | Optimal for semantic coherence |
| Chunk Overlap | 50 tokens | Preserves context at boundaries |
| Embedding Model | text-embedding-3-small | 1536 dimensions |
| Embedding Dimension | 1536 | OpenAI standard |
| Top-K | 5 | Number of chunks to retrieve |
| Similarity Threshold | 0.7 | Minimum relevance score |
| Distance Metric | Cosine | Vector similarity measure |

### Prompt Template

```
You are {assistant_name}.

{assistant_instructions}

Use the following reference materials to inform your response. Only use
information from these materials when relevant:

---
{retrieved_chunks}
---

If the reference materials don't contain relevant information, rely on
your general knowledge but indicate this to the user.
```

---

## API Design

### RESTful Conventions

| Operation | HTTP Method | URL Pattern | Success Code |
|-----------|-------------|-------------|--------------|
| Create | POST | /resources | 201 Created |
| List | GET | /resources | 200 OK |
| Get | GET | /resources/{id} | 200 OK |
| Update | PATCH | /resources/{id} | 200 OK |
| Delete | DELETE | /resources/{id} | 204 No Content |

### API Versioning

- URL-based versioning: `/api/v1/...`
- Breaking changes require new version (`/api/v2/...`)

### Response Formats

**Success Response:**
```json
{
  "id": "uuid",
  "name": "Assistant Name",
  "created_at": "2026-01-20T10:30:00Z"
}
```

**Error Response:**
```json
{
  "error": "ValidationError",
  "message": "Name must be between 3 and 50 characters"
}
```

**List Response:**
```json
{
  "assistants": [...],
  "total": 10
}
```

### Streaming (SSE)

Chat responses use Server-Sent Events:

```
POST /api/v1/conversations/{id}/messages
Accept: text/event-stream

data: {"type": "start", "message_id": "msg_123"}
data: {"type": "chunk", "content": "Hello"}
data: {"type": "chunk", "content": " world"}
data: {"type": "done", "usage": {"prompt_tokens": 10, "completion_tokens": 5}}
```

---

## Security Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Layer 1: Network Security                                  │ │
│  │  • HTTPS only (TLS 1.3)                                    │ │
│  │  • Nginx reverse proxy                                      │ │
│  │  • Docker network isolation                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Layer 2: Application Security                              │ │
│  │  • JWT authentication (access + refresh tokens)            │ │
│  │  • Role-based access control (Admin/Manager/User)          │ │
│  │  • CORS configuration                                       │ │
│  │  • Quota-based rate limiting                               │ │
│  │  • Input validation (Pydantic)                             │ │
│  │  • Audit logging for admin actions                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Layer 3: Data Security                                     │ │
│  │  • bcrypt password hashing                                  │ │
│  │  • Parameterized SQL queries                                │ │
│  │  • API keys encrypted at rest                               │ │
│  │  • File type validation                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Security Measures

| Concern | Mitigation |
|---------|------------|
| SQL Injection | SQLAlchemy parameterized queries |
| XSS | React auto-escaping, CSP headers |
| CSRF | SameSite cookies, token validation |
| File Upload | Type validation, size limits |
| API Key Exposure | Fernet encryption at rest, never sent to frontend |
| Authentication | bcrypt (cost 12), JWT with access/refresh tokens |
| Authorization | Role-based access control (RBAC) |
| Cost Control | Usage quotas with runtime enforcement |
| Accountability | Audit logging with actor, IP, user agent tracking |

---

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────────────────┐
│                    docker-compose.dev.yml                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   backend   │  │  frontend   │  │  postgres   │             │
│  │  :8000      │  │  :5173      │  │  :5432      │             │
│  │  (hot-reload)  │  (HMR)      │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                                  │                    │
│         └──────────────────────────────────┘                    │
│                        volumes                                   │
│                    (code, data, db)                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Production Environment

```
┌─────────────────────────────────────────────────────────────────┐
│                      docker-compose.yml                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                       nginx                               │   │
│  │                    :80, :443                              │   │
│  │              (SSL, reverse proxy)                         │   │
│  └───────────────────────┬───────────────────────────────────┘   │
│                          │                                       │
│         ┌────────────────┴────────────────┐                     │
│         │                                 │                      │
│  ┌──────▼──────┐                  ┌───────▼──────┐              │
│  │   backend   │                  │   frontend   │              │
│  │   :8000     │                  │   (static)   │              │
│  │  (gunicorn) │                  │              │              │
│  └──────┬──────┘                  └──────────────┘              │
│         │                                                        │
│  ┌──────▼──────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  postgres   │  │   chroma    │  │   uploads   │             │
│  │   :5432     │  │  (volume)   │  │  (volume)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Volume Strategy

| Volume | Purpose | Backup Required |
|--------|---------|-----------------|
| postgres_data | Database | Yes |
| chroma_data | Vector embeddings | Yes |
| uploads | User files | Yes |
| nginx_certs | SSL certificates | No (regenerate) |

---

## Technology Decisions

### Why FastAPI?

| Consideration | FastAPI | Flask | Django |
|--------------|---------|-------|--------|
| Async Support | Native | Extension | Limited |
| Performance | Excellent | Good | Good |
| Type Hints | Built-in | Optional | Limited |
| Auto Documentation | Yes | No | No |
| Learning Curve | Low | Low | High |

**Decision:** FastAPI for native async, automatic OpenAPI docs, and Pydantic integration.

### Why PostgreSQL?

| Consideration | PostgreSQL | MySQL | SQLite |
|--------------|------------|-------|--------|
| JSON Support | Excellent | Good | Limited |
| Concurrent Writes | Excellent | Good | Poor |
| Full-Text Search | Built-in | Plugin | Limited |
| Extensions | Many | Few | None |

**Decision:** PostgreSQL for JSONB support, reliability, and feature set.

### Why ChromaDB?

| Consideration | ChromaDB | Pinecone | Qdrant |
|--------------|----------|----------|--------|
| Self-Hosted | Yes | No | Yes |
| Setup Complexity | Low | None | Medium |
| Cost | Free | Paid | Free |
| Persistence | Local disk | Cloud | Local/Cloud |

**Decision:** ChromaDB for simplicity, local-first approach, and zero cost.

### Why OpenRouter?

| Consideration | OpenRouter | Direct APIs | LangChain |
|--------------|------------|-------------|-----------|
| Model Variety | 50+ | Per-provider | 50+ |
| Single API Key | Yes | No | No |
| Consistent Interface | Yes | No | Yes |
| Pricing | Passthrough | Direct | N/A |

**Decision:** OpenRouter for unified access to multiple LLM providers with single integration.

---

## Performance Considerations

### Optimization Strategies

1. **Async I/O** - All database and HTTP operations are async
2. **Connection Pooling** - SQLAlchemy async pool for PostgreSQL
   - Pool size: 10 connections
   - Max overflow: 20 connections
   - Connection recycling: 30 minutes
   - Pre-ping validation enabled
3. **Streaming Responses** - SSE for chat to reduce TTFB
4. **Chunked Uploads** - Large file handling without memory spikes
5. **Index Optimization** - Database indexes on foreign keys and timestamps
6. **API Response Caching** - In-memory TTL cache for models endpoint (5 min)
7. **React Optimizations**:
   - Component memoization with `React.memo()` (MessageBubble, CodeBlock, AssistantCard)
   - Route-based code splitting with `React.lazy()` and `Suspense`
   - Image lazy loading with `IntersectionObserver`

### Scalability Path

```
Single Server → Read Replicas → Horizontal Scaling
     │               │                │
  Current       PostgreSQL        Multiple API
   Phase         Replicas         Instances (if needed)
```

> Docker Compose is sufficient for ~50 users. No Kubernetes planned.

---

## Monitoring & Observability

### Planned Instrumentation

| Layer | Tool | Metrics |
|-------|------|---------|
| Application | Prometheus | Request latency, error rates |
| Database | pg_stat | Query performance, connections |
| Infrastructure | Docker stats | CPU, memory, disk |
| Logs | Structured JSON | Request traces, errors |

### Health Checks

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /api/v1/health` | Basic health check | `{"status": "healthy", "timestamp": "..."}` |
| `GET /api/v1/ready` | Readiness with DB check | `{"status": "ready", "database": "connected"}` |

### Testing Infrastructure

| Test Type | Tool | Coverage |
|-----------|------|----------|
| Backend Unit | pytest + pytest-asyncio | Services, utilities |
| Frontend Unit | Vitest + React Testing Library | Components, hooks |
| API Integration | pytest + httpx | Endpoint flows |
| E2E | Playwright | Critical user paths |
| Load | Locust | Concurrent user simulation |

### Load Testing User Types (Locust)

- **AIAcrossUser** - Normal user behavior simulation (1-3s wait)
- **APIStressUser** - High-frequency stress testing (0.1-0.5s wait)
- **ReadOnlyUser** - Cache effectiveness testing (0.5-1s wait)

---

---

## Future Architecture Considerations

> AI-Across is an internal MarketAcross tool (~50 employees). Architecture changes are driven by internal team needs, not SaaS scaling.

### Planned Architectural Changes

| Version | Architectural Change | Rationale |
|---------|---------------------|-----------|
| v0.8.0 | Multi-user auth + RBAC | ✅ Implemented — User management, roles |
| v0.8.0 | API key encryption | ✅ Implemented — Fernet for secure storage |
| v0.8.0 | Usage quota system | ✅ Implemented — Cost/token limits |
| v0.8.0 | Audit logging | ✅ Implemented — Action tracking |
| v0.9.0 | User auth + conversation isolation | ✅ Implemented — JWT auth on all endpoints, user_id on conversations |
| v0.9.0 | Security headers + MIME validation | ✅ Implemented — CSP, HSTS, magic byte validation |
| v1.1 | Direct provider API routing | Call Anthropic/Google/OpenAI directly, OpenRouter as fallback |
| v1.1 | Embedding-based conversation search | Semantic search across all conversations |
| v1.2 | Content quality scoring pipeline | AI-based output quality assessment |
| v1.3 | Telegram Bot API integration | Message routing between Telegram and assistants |

### Technical Debt Tracking

| Item | Priority | Migration Path |
|------|----------|----------------|
| ChromaDB → Qdrant | Medium | When vectors > 1M |
| Local storage → S3 | Low | Only if multi-instance needed |
| REST → WebSocket | Low | Real-time conversation sync |

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OpenRouter rate limits | High | Medium | Request queuing, backoff; v1.1 adds direct provider routing |
| ChromaDB scaling limits | Medium | Low | Monitor, plan Qdrant migration |
| LLM API cost overruns | High | Medium | Usage limits, alerts |
| Data loss | Critical | Low | Automated backups, testing |

### Mitigation Strategies

1. **Rate Limiting:** Implement exponential backoff and request queuing
2. **Vector Scaling:** Monitor embedding count, migrate to Qdrant at 500K+
3. **Cost Control:** ✅ Usage quotas with daily/monthly limits enforced at runtime
4. **Data Protection:** Daily backups, restore testing, replication
5. **Audit Trail:** ✅ All admin actions logged with actor, IP, and timestamp

---

## Further Reading

- [High-Level Design](HLD.md)
- [Development Roadmap](../ROADMAP.md)
- [API Reference](/docs endpoint)
- [Deployment Guide](DEPLOYMENT.md)
