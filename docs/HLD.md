# AI-Across High-Level Design (HLD)

**Document Version:** 1.5
**Last Updated:** February 19, 2026
**Status:** Active

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Context](#2-system-context)
3. [Design Goals](#3-design-goals)
4. [System Architecture](#4-system-architecture)
5. [Component Design](#5-component-design)
6. [Data Design](#6-data-design)
7. [Integration Design](#7-integration-design)
8. [Security Design](#8-security-design)
9. [Deployment Design](#9-deployment-design)
10. [Non-Functional Requirements](#10-non-functional-requirements)

---

## 1. Introduction

### 1.1 Purpose

This High-Level Design document describes the architecture and design of AI-Across, a self-hosted AI content platform. It serves as a reference for developers, architects, and stakeholders to understand the system's structure and design decisions.

### 1.2 Scope

This document covers:
- System architecture and component interactions
- Data models and storage strategies
- Integration with external services (OpenRouter)
- Security and deployment considerations
- Non-functional requirements

### 1.3 Definitions

| Term | Definition |
|------|------------|
| **Assistant** | A configured AI persona with specific instructions and knowledge base |
| **Knowledge Base** | Collection of documents used for RAG retrieval |
| **RAG** | Retrieval-Augmented Generation - injecting relevant context into LLM prompts |
| **Chunk** | A segment of text (512 tokens) stored as a vector embedding |
| **OpenRouter** | API gateway providing unified access to multiple LLM providers |

### 1.4 References

- [Product Requirements Document](../ai-across-prd.md)
- [Architecture Overview](ARCHITECTURE.md)
- [OpenRouter API Documentation](https://openrouter.ai/docs)

---

## 2. System Context

### 2.1 Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM CONTEXT                                 │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │    Content Team     │
                    │      (Users)        │
                    └──────────┬──────────┘
                               │
                         Web Browser
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                           AI-ACROSS                                      │
│                                                                          │
│    Self-hosted AI content platform for creating specialized              │
│    assistants with custom knowledge bases and multi-model support        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               │                               │
               ▼                               ▼
     ┌─────────────────┐             ┌─────────────────┐
     │   OpenRouter    │             │   File System   │
     │      API        │             │    (Local)      │
     │                 │             │                 │
     │  • LLM Access   │             │  • Uploads      │
     │  • 50+ Models   │             │  • Vectors      │
     │  • Embeddings   │             │  • Database     │
     └─────────────────┘             └─────────────────┘
```

### 2.2 Actors

| Actor | Description | Interactions |
|-------|-------------|--------------|
| Content Writer (User) | Creates content using AI assistants | Chat, view assistants, view own conversations |
| Admin | Creates/configures assistants, manages knowledge bases, manages users, monitors usage/costs | CRUD assistants, upload files, admin dashboard, user management |
| System Admin | Deploys and maintains the platform | Server configuration, monitoring |

### 2.3 External Systems

| System | Purpose | Protocol |
|--------|---------|----------|
| OpenRouter | LLM API gateway | HTTPS REST |
| PostgreSQL | Relational data storage | TCP/SQL |
| ChromaDB | Vector storage | Local Python API |

### 2.4 Current Runtime Behavior (Implementation Alignment)

- Assistant card click opens chat with assistant context (`/chat?assistant=<id>`).
- New general chat starts from `settings.default_model`.
- Assistant chat starts from assistant-level configured model.
- Chat model dropdown remains user-overridable per conversation/message flow.
- OpenRouter API key is resolved from database settings first, then environment fallback.

---

## 3. Design Goals

### 3.1 Primary Goals

| Goal | Description | Priority |
|------|-------------|----------|
| **Simplicity** | Easy to deploy and use for non-technical users | High |
| **Flexibility** | Support multiple LLM providers through OpenRouter | High |
| **Privacy** | Self-hosted with no data leaving infrastructure | High |
| **Performance** | Sub-3-second response times (excluding LLM) | Medium |
| **Extensibility** | Easy to add new features and integrations | Medium |

### 3.2 Design Principles

1. **Separation of Concerns** - Clear boundaries between layers
2. **Schema-First** - Pydantic models define all data contracts
3. **Async-First** - Non-blocking I/O for all operations
4. **Convention over Configuration** - Sensible defaults, optional customization
5. **Local-First** - No cloud dependencies except LLM API

### 3.3 Constraints

| Constraint | Description |
|------------|-------------|
| Single Instance | Initial design supports single deployment |
| OpenRouter Dependency | Requires OpenRouter API key for LLM access |
| Local Storage | File storage on local filesystem |
| No Multi-Tenancy | Single team/organization use |

---

## 4. System Architecture

### 4.1 Architecture Style

AI-Across follows a **Layered Architecture** with clear separation:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                                │
│                                                                          │
│  React SPA with component-based UI                                      │
│  • Dashboard, Chat Interface, Assistant Manager                         │
│  • State: React Query (server) + Zustand (client)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                              REST API / SSE
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                                │
│                                                                          │
│  FastAPI with versioned endpoints                                       │
│  • Request validation (Pydantic)                                        │
│  • Authentication/Authorization (JWT)                                   │
│  • Error handling                                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                            Service Calls
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                          BUSINESS LAYER                                  │
│                                                                          │
│  Domain Services                                                         │
│  • AssistantService, ChatService, RAGService                            │
│  • FileProcessor, EmbeddingService                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                          Data Access
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                     │
│                                                                          │
│  • SQLAlchemy ORM (PostgreSQL)                                          │
│  • ChromaDB Client (Vectors)                                            │
│  • File System (Uploads)                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         COMPONENT DIAGRAM                                │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐     ┌─────────────────────┐
│      Frontend       │     │       Nginx         │
│   (React + Vite)    │────>│  (Reverse Proxy)    │
└─────────────────────┘     └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │      Backend        │
                            │     (FastAPI)       │
                            └──────────┬──────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
         ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
         │   PostgreSQL    │ │    ChromaDB     │ │   OpenRouter    │
         │   (Database)    │ │   (Vectors)     │ │     (LLMs)      │
         └─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## 5. Component Design

### 5.1 Frontend Components

| Component | Responsibility | Dependencies | Status |
|-----------|---------------|--------------|--------|
| Dashboard | Main landing page, assistant cards | React Query | Complete |
| AssistantManager | CRUD operations for assistants | API client | Complete |
| ChatWindow | Main chat container, message display | SSE client, React Query | Complete |
| MessageList | Scrollable message list with auto-scroll | Local state | Complete |
| MessageBubble | Individual message with markdown rendering | react-markdown | Complete |
| MessageInput | Input textarea with send/stop buttons | Local state | Complete |
| StreamingMessage | Real-time streaming response display | SSE client | Complete |
| CodeBlock | Syntax-highlighted code with copy | highlight.js | Complete |
| MessageEditDialog | Edit user messages dialog | Dialog UI | Complete |
| FileUploader | Drag-drop upload, progress tracking | API client | Complete |
| ModelSelector | LLM model dropdown grouped by provider | API client | Complete |
| ConversationSidebar | Conversation list with search/rename | React Query | Complete |
| SettingsPage | Application configuration | Zustand | Complete |
| ConnectionStatus | Offline/reconnecting banner | useOnlineStatus hook | Complete |
| AdminLoginPage | Admin authentication form | Admin store | Complete |
| AdminDashboardPage | Usage stats, charts, health | React Query | Complete |
| AdminGuard | Route protection for admin | Admin store | Complete |
| StatsCard | Reusable metric display | - | Complete |
| UsageChart | Daily usage line chart | recharts | Complete |
| HealthStatusCard | System health indicators | React Query | Complete |
| AdminLayout | Admin page wrapper with sidebar | Admin store | Complete |
| AdminSidebar | Navigation sidebar with routes | React Router | Complete |
| UserTable | User list with actions | React Query | Complete |
| UserDialog | Create/edit user modal | React Hook Form | Complete |
| ApiKeyTable | API key list by provider | React Query | Complete |
| ApiKeyDialog | Create/edit API key modal | React Hook Form | Complete |
| QuotaConfig | Quota configuration dialog | React Hook Form | Complete |
| AuditLogTable | Audit log viewer with filters | React Query | Complete |
| UserLoginPage | User authentication form | Auth store | Complete |
| AuthGuard | Route protection for user routes | Auth store | Complete |
| QuotaDisplay | User quota/usage widget with progress bars | React Query | Complete |
| AdminAssistantsPage | Admin assistant management (CRUD, templates, files) | React Query | Complete |

### Frontend Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| Framework | React | 19.x | UI library |
| Language | TypeScript | 5.x | Type safety |
| Build Tool | Vite | 7.x | Fast builds, HMR |
| Styling | TailwindCSS | 3.x | Utility-first CSS |
| Components | shadcn/ui | Latest | Accessible UI primitives |
| Client State | Zustand | 5.x | Lightweight state |
| Server State | React Query | 5.x | Data fetching, caching |
| Routing | React Router | 7.x | Client-side routing |
| Forms | React Hook Form | 7.x | Form management |
| Validation | Zod | 3.x | Schema validation |
| HTTP | Axios | 1.x | HTTP client |

### 5.2 Backend Services

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│  AssistantService   │  CRUD operations for AI assistants
│                     │  • create, get, list, update, delete
│                     │  • template management
└──────────┬──────────┘
           │
           │ uses
           ▼
┌─────────────────────┐
│   FileProcessor     │  Document upload and processing
│                     │  • validate, extract, chunk
│                     │  • status management
└──────────┬──────────┘
           │
           │ uses
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│   RAGService        │────>│  EmbeddingService   │
│                     │     │                     │
│ • retrieve context  │     │ • generate vectors  │
│ • inject into prompt│     │ • OpenRouter API    │
└──────────┬──────────┘     └─────────────────────┘
           │
           │ uses
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│   ChromaService     │     │ ConversationService │
│                     │     │                     │
│ • store embeddings  │     │ • conversation mgmt │
│ • similarity search │     │ • streaming chat    │
└─────────────────────┘     └─────────────────────┘

┌─────────────────────┐
│ OpenRouterService   │
│                     │
│ • model listing     │
│ • chat completions  │
│ • streaming SSE     │
│ • model pricing     │
│ • connectivity check│
└─────────────────────┘

┌─────────────────────┐     ┌─────────────────────┐
│ AdminAuthService    │     │  UsageLogService    │
│                     │     │                     │
│ • password verify   │     │ • log usage         │
│ • token generation  │     │ • calculate cost    │
│ • token validation  │     │ • get summary       │
└─────────────────────┘     │ • get breakdown     │
                            │ • get daily usage   │
                            └─────────────────────┘

┌─────────────────────┐     ┌─────────────────────┐
│   UserService       │     │  UserAuthService    │
│                     │     │                     │
│ • create user       │     │ • verify password   │
│ • get/list users    │     │ • generate JWT      │
│ • update user       │     │ • verify JWT        │
│ • disable/enable    │     │ • refresh token     │
│ • reset password    │     │ • role-based access │
└─────────────────────┘     └─────────────────────┘

┌─────────────────────┐     ┌─────────────────────┐
│  APIKeyService      │     │   QuotaService      │
│                     │     │                     │
│ • create/list keys  │     │ • get/set quotas    │
│ • update/delete     │     │ • check quota       │
│ • encrypt/decrypt   │     │ • get usage status  │
│ • test connectivity │     │ • get alerts        │
│ • rotate key        │     │ • enforce limits    │
└─────────────────────┘     └─────────────────────┘

┌─────────────────────┐
│   AuditService      │
│                     │
│ • log action        │
│ • query logs        │
│ • get recent        │
│ • filter by actor   │
└─────────────────────┘
```

### 5.3 Service Interfaces

#### AssistantService

```python
class AssistantService:
    async def create(db: AsyncSession, data: AssistantCreate) -> Assistant
    async def get(db: AsyncSession, id: UUID) -> Assistant | None
    async def list(db: AsyncSession, include_deleted: bool = False) -> list[Assistant]
    async def update(db: AsyncSession, id: UUID, data: AssistantUpdate) -> Assistant
    async def delete(db: AsyncSession, id: UUID) -> None
    async def restore(db: AsyncSession, id: UUID) -> Assistant
    def get_templates() -> list[AssistantTemplate]
    async def create_from_template(db: AsyncSession, template_id: str) -> Assistant
```

#### RAGService

```python
class RAGService:
    async def retrieve_context(
        assistant_id: UUID,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> list[RetrievedChunk]

    def build_prompt(
        assistant: Assistant,
        query: str,
        context: list[RetrievedChunk]
    ) -> str
```

#### FileProcessor

```python
class FileProcessor:
    async def process_file(
        db: AsyncSession,
        file: UploadFile,
        assistant_id: UUID
    ) -> KnowledgeFile

    async def reprocess_file(
        db: AsyncSession,
        file_id: UUID
    ) -> KnowledgeFile
```

#### ConversationService

```python
class ConversationService:
    async def create_conversation(data: ConversationCreate) -> Conversation
    async def get_conversation(conversation_id: UUID) -> Conversation
    async def list_conversations(assistant_id: UUID | None, limit: int, offset: int) -> list[Conversation]
    async def update_conversation(conversation_id: UUID, data: ConversationUpdate) -> Conversation
    async def delete_conversation(conversation_id: UUID) -> None
    async def add_message(conversation_id: UUID, role: str, content: str) -> Message
    async def send_message(conversation_id: UUID, content: str) -> AsyncIterator[dict]
    async def export_conversation(conversation_id: UUID) -> ConversationExport
```

#### OpenRouterService

```python
class OpenRouterService:
    async def list_models() -> list[dict]
    async def chat_completion(messages: list, model: str, temperature: float) -> dict
    async def stream_chat_completion(messages: list, model: str) -> AsyncIterator[dict]
    async def get_model_pricing(model_id: str) -> dict[str, float]
    async def check_connectivity() -> tuple[bool, int | None, str | None]
```

#### AdminAuthService

```python
class AdminAuthService:
    def verify_password(password: str) -> bool
    def generate_token() -> tuple[str, datetime]
    def verify_token(token: str) -> bool
```

#### UsageLogService

```python
class UsageLogService:
    async def log_usage(
        assistant_id: UUID,
        conversation_id: UUID,
        message_id: UUID,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> UsageLog
    async def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> Decimal
    async def get_summary(period_start: datetime, period_end: datetime) -> dict
    async def get_breakdown_by_model() -> list[dict]
    async def get_breakdown_by_assistant() -> list[dict]
    async def get_daily_usage(days: int = 30) -> list[dict]
```

#### UserService

```python
class UserService:
    async def create_user(data: UserCreate) -> User
    async def get_user(user_id: UUID) -> User | None
    async def get_user_by_email(email: str) -> User | None
    async def list_users(role: str | None, is_active: bool | None, limit: int, offset: int) -> tuple[list[User], int]
    async def update_user(user_id: UUID, data: UserUpdate) -> User
    async def disable_user(user_id: UUID) -> User
    async def enable_user(user_id: UUID) -> User
    async def delete_user(user_id: UUID) -> None
    async def reset_password(user_id: UUID, new_password: str) -> User
```

#### UserAuthService

```python
class UserAuthService:
    def hash_password(password: str) -> str
    def verify_password(plain: str, hashed: str) -> bool
    def create_access_token(user_id: UUID, email: str, role: str) -> str
    def create_refresh_token(user_id: UUID) -> str
    def verify_token(token: str) -> dict | None
    async def authenticate(email: str, password: str) -> tuple[User, str, str] | None
```

#### APIKeyService

```python
class APIKeyService:
    async def create_api_key(data: APIKeyCreate) -> APIKey
    async def list_api_keys(provider: str | None) -> list[APIKey]
    async def get_api_key(key_id: UUID) -> APIKey | None
    async def update_api_key(key_id: UUID, data: APIKeyUpdate) -> APIKey
    async def delete_api_key(key_id: UUID) -> None
    async def test_api_key(key_id: UUID) -> tuple[bool, str | None]
    async def rotate_api_key(key_id: UUID, new_key: str) -> APIKey
    async def set_default(key_id: UUID) -> APIKey
    def encrypt_key(plain_key: str) -> str
    def decrypt_key(encrypted_key: str) -> str
```

#### QuotaService

```python
class QuotaService:
    async def get_global_quota() -> UsageQuota | None
    async def get_or_create_global_quota() -> UsageQuota
    async def update_global_quota(
        daily_cost_limit_usd: Decimal | None,
        monthly_cost_limit_usd: Decimal | None,
        daily_token_limit: int | None,
        monthly_token_limit: int | None,
        alert_threshold_percent: int | None
    ) -> UsageQuota
    async def get_current_usage(user_id: UUID | None) -> dict
    async def check_quota(user_id: UUID | None) -> QuotaCheckResult
    async def get_alerts(user_id: UUID | None) -> list[QuotaAlert]
    async def get_usage_status(user_id: UUID | None) -> dict
```

#### AuditService

```python
class AuditService:
    async def log_action(
        actor_id: UUID | None,
        actor_email: str,
        action: str,
        resource_type: str,
        resource_id: str | None,
        old_values: dict | None,
        new_values: dict | None,
        ip_address: str | None,
        user_agent: str | None
    ) -> AuditLog
    async def get_logs(
        action: str | None,
        resource_type: str | None,
        actor_id: UUID | None,
        start_date: datetime | None,
        end_date: datetime | None,
        limit: int,
        offset: int
    ) -> tuple[list[AuditLog], int]
    async def get_recent(limit: int = 50) -> list[AuditLog]
```

---

## 6. Data Design

### 6.1 Entity Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ENTITY MODEL                                    │
└─────────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────┐
                        │    Assistant    │
                        ├─────────────────┤
                        │ id: UUID        │
                        │ name: string    │
                        │ description     │
                        │ instructions    │
                        │ model: string   │
                        │ temperature     │
                        │ max_tokens      │
                        │ avatar_url      │
                        │ is_deleted      │
                        │ created_at      │
                        │ updated_at      │
                        └────────┬────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   │                           │
                   ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │ KnowledgeFile   │         │  Conversation   │
        ├─────────────────┤         ├─────────────────┤
        │ id: UUID        │         │ id: UUID        │
        │ assistant_id    │         │ assistant_id    │
        │ filename        │         │ user_id (FK)    │
        │ file_type       │         │ title           │
        │ file_path       │         │ created_at      │
        │ size_bytes      │         │ updated_at      │
        │ chunk_count     │         └────────┬────────┘
        │ chunk_count     │                  │
        │ status          │                  │
        │ error_message   │                  ▼
        │ created_at      │         ┌─────────────────┐
        └─────────────────┘         │    Message      │
                                    ├─────────────────┤
                                    │ id: UUID        │
                                    │ conversation_id │
                                    │ role            │
                                    │ content         │
                                    │ model           │
                                    │ tokens_used     │
                                    │ created_at      │
                                    └─────────────────┘

        ┌─────────────────┐
        │    Settings     │
        ├─────────────────┤
        │ key: string (PK)│
        │ value: string   │
        │ updated_at      │
        └─────────────────┘

        ┌─────────────────┐
        │   UsageLog      │
        ├─────────────────┤
        │ id: UUID        │
        │ assistant_id    │◄─── FK (SET NULL)
        │ conversation_id │◄─── FK (SET NULL)
        │ message_id      │
        │ model           │
        │ prompt_tokens   │
        │ completion_tokens│
        │ total_tokens    │
        │ cost_usd        │
        │ created_at      │
        └─────────────────┘

        ┌─────────────────┐
        │      User       │
        ├─────────────────┤
        │ id: UUID        │
        │ email           │ (unique, indexed)
        │ password_hash   │
        │ name            │
        │ role            │ (admin/manager/user)
        │ is_active       │
        │ last_login_at   │
        │ created_at      │
        │ updated_at      │
        └─────────────────┘

        ┌─────────────────┐
        │     APIKey      │
        ├─────────────────┤
        │ id: UUID        │
        │ provider        │ (openrouter/openai/etc)
        │ name            │
        │ encrypted_key   │
        │ is_default      │
        │ is_active       │
        │ last_used_at    │
        │ created_at      │
        │ updated_at      │
        └─────────────────┘

        ┌─────────────────┐
        │  UsageQuota     │
        ├─────────────────┤
        │ id: UUID        │
        │ scope           │ (global/user)
        │ scope_id        │
        │ daily_cost_limit│
        │ monthly_cost_limit│
        │ daily_token_limit│
        │ monthly_token_limit│
        │ requests_per_min│
        │ requests_per_hour│
        │ alert_threshold │
        │ created_at      │
        │ updated_at      │
        └─────────────────┘

        ┌─────────────────┐
        │   AuditLog      │
        ├─────────────────┤
        │ id: UUID        │
        │ actor_id        │◄─── FK (SET NULL)
        │ actor_email     │
        │ action          │
        │ resource_type   │
        │ resource_id     │
        │ old_values      │ (JSONB)
        │ new_values      │ (JSONB)
        │ ip_address      │
        │ user_agent      │
        │ created_at      │ (indexed)
        └─────────────────┘
```

### 6.2 Data Storage Strategy

| Data Type | Storage | Rationale |
|-----------|---------|-----------|
| Structured Data | PostgreSQL | ACID compliance, relationships |
| Vector Embeddings | ChromaDB | Optimized for similarity search |
| Uploaded Files | File System | Large binary storage |
| Sessions | Memory/JWT | Stateless authentication |

### 6.3 ChromaDB Collections

```
Collection: assistant_{assistant_id}
├── Embeddings: float[1536]
├── Documents: string (chunk text)
├── Metadata:
│   ├── file_id: UUID
│   ├── chunk_index: int
│   ├── source_filename: string
│   └── created_at: timestamp
└── IDs: string (chunk_{file_id}_{index})
```

---

## 7. Integration Design

### 7.1 OpenRouter Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      OPENROUTER INTEGRATION                              │
└─────────────────────────────────────────────────────────────────────────┘

AI-Across                                          OpenRouter API
    │                                                    │
    │  1. List Models                                    │
    │  GET /api/v1/models ─────────────────────────────>│
    │  <─────────────── [{id, name, context_length}] ───│
    │                                                    │
    │  2. Generate Embeddings                            │
    │  POST /api/v1/embeddings ────────────────────────>│
    │  {model: "text-embedding-3-small", input: "..."}  │
    │  <───────────────────── {embedding: float[1536]} ─│
    │                                                    │
    │  3. Chat Completion (Streaming)                    │
    │  POST /api/v1/chat/completions ──────────────────>│
    │  {model: "anthropic/claude-3.5-sonnet",           │
    │   messages: [...], stream: true}                   │
    │  <─────────────────── SSE: data: {content: "..."} │
    │  <─────────────────── SSE: data: {content: "..."} │
    │  <─────────────────── SSE: data: [DONE]           │
    │                                                    │
```

### 7.2 API Rate Limiting Strategy

| Endpoint Type | Rate Limit | Burst |
|--------------|------------|-------|
| Chat Completion | 60/min | 10 |
| Embeddings | 100/min | 20 |
| File Upload | 20/min | 5 |
| General API | 200/min | 50 |

### 7.3 Error Handling

| Error Source | Strategy |
|--------------|----------|
| OpenRouter 429 | Exponential backoff, retry 3x |
| OpenRouter 500 | Fail fast, return error to user |
| Database Connection | Connection pool retry |
| File Processing | Mark as error, allow reprocess |

---

## 8. Security Design

### 8.1 Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      AUTHENTICATION FLOW                                 │
└─────────────────────────────────────────────────────────────────────────┘

User                        Frontend                      Backend
 │                             │                             │
 │  1. Enter Password          │                             │
 │ ───────────────────────────>│                             │
 │                             │                             │
 │                             │  2. POST /auth/login        │
 │                             │  {password: "..."}          │
 │                             │ ───────────────────────────>│
 │                             │                             │
 │                             │                             │ 3. Verify bcrypt hash
 │                             │                             │
 │                             │  4. {token: "jwt..."}       │
 │                             │ <───────────────────────────│
 │                             │                             │
 │  5. Redirect to Dashboard   │                             │
 │ <───────────────────────────│                             │
 │                             │                             │
 │                             │  6. GET /api/v1/assistants  │
 │                             │  X-Admin-Token: <jwt>        │
 │                             │ ───────────────────────────>│
 │                             │                             │
 │                             │                             │ 7. Validate JWT
 │                             │                             │
 │                             │  8. {assistants: [...]}     │
 │                             │ <───────────────────────────│
```

### 8.2 Security Controls

| Control | Implementation |
|---------|----------------|
| Admin Password | Environment variable (`ADMIN_PASSWORD`) for legacy support |
| User Authentication | JWT access tokens (8 hours) + refresh tokens (7 days) |
| Password Storage | bcrypt with cost factor 12 |
| API Key Storage | Fernet symmetric encryption at rest |
| Role-Based Access | Admin > Manager > User hierarchy |
| Session Management | JWT with role claims, automatic refresh |
| API Authentication | `X-Admin-Token` header carrying JWT |
| CORS | Whitelist of allowed origins |
| Input Validation | Pydantic models for all inputs |
| SQL Injection | SQLAlchemy parameterized queries |
| File Upload | Type whitelist, size limits, path sanitization |
| Audit Logging | All admin actions logged with actor, IP, user agent |

### 8.3 Threat Model

| Threat | Mitigation |
|--------|------------|
| Unauthorized Access | Password protection + JWT |
| API Key Exposure | Server-side only, encrypted storage |
| Malicious File Upload | Type validation, sandboxed processing |
| Prompt Injection | Input sanitization, output filtering |
| Data Exfiltration | No external network calls except OpenRouter |

---

## 9. Deployment Design

### 9.1 Container Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CONTAINER ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          Docker Network                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐                                                    │
│  │     nginx       │  Exposed: 80, 443                                  │
│  │   (frontend)    │  Static files + reverse proxy                      │
│  └────────┬────────┘                                                    │
│           │                                                              │
│           ▼                                                              │
│  ┌─────────────────┐                                                    │
│  │    backend      │  Internal: 8000                                    │
│  │   (fastapi)     │  Gunicorn + Uvicorn workers                        │
│  └────────┬────────┘                                                    │
│           │                                                              │
│           ▼                                                              │
│  ┌─────────────────┐                                                    │
│  │   postgres      │  Internal: 5432                                    │
│  │  (database)     │  Persistent volume                                 │
│  └─────────────────┘                                                    │
│                                                                          │
│  Volumes:                                                                │
│  • postgres_data (persistent)                                           │
│  • chroma_data (persistent)                                             │
│  • uploads (persistent)                                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Environment Configuration

| Environment | Database | Debug | SSL |
|-------------|----------|-------|-----|
| Development | postgres:5432 | true | false |
| Production | postgres:5432 | false | true |

### 9.3 Scaling Strategy

**Current State (v1.0):** Single instance deployment

**Future Scaling Path (if needed):**
1. Vertical scaling (increase server resources)
2. PostgreSQL read replicas
3. Multiple API instances behind load balancer

> Note: AI-Across is an internal tool for ~50 users. Container orchestration (Kubernetes) is not planned. Docker Compose is sufficient for this scale.

---

## 10. Non-Functional Requirements

### 10.1 Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time | < 200ms | p95 excluding LLM |
| Chat First Token | < 500ms | Time to first SSE chunk |
| File Processing | < 2min/50 pages | PDF indexing |
| Page Load | < 2s | Lighthouse Performance |
| Concurrent Users | 20 | Simultaneous active chats |

### 10.2 Availability Requirements

| Metric | Target |
|--------|--------|
| Uptime | 99% (excludes maintenance) |
| Recovery Time | < 1 hour |
| Backup Frequency | Daily |
| Backup Retention | 7 days |

### 10.3 Scalability Requirements

| Dimension | Initial | Maximum |
|-----------|---------|---------|
| Assistants | 50 | 500 |
| Files per Assistant | 20 | 100 |
| Total Storage | 10GB | 100GB |
| Conversations | 1000 | 10000 |

### 10.4 Maintainability Requirements

| Aspect | Requirement |
|--------|-------------|
| Code Coverage | > 70% |
| Documentation | All public APIs documented |
| Logging | Structured JSON logs |
| Monitoring | Health endpoints + metrics |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Chunk** | A segment of text (typically 512 tokens) stored as a vector |
| **Embedding** | Vector representation of text for similarity comparison |
| **RAG** | Retrieval-Augmented Generation |
| **SSE** | Server-Sent Events for streaming responses |
| **JWT** | JSON Web Token for authentication |

## Appendix B: Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-20 | Use ChromaDB over Pinecone | Local-first, zero cost |
| 2026-01-20 | Use OpenRouter over direct APIs | Unified access, single key |
| 2026-01-20 | Use FastAPI over Django | Async-native, auto-docs |
| 2026-01-20 | Use PostgreSQL over SQLite | Concurrent writes, features |
| 2026-01-25 | Simple admin auth over JWT | Single-admin use case, simpler implementation |
| 2026-01-25 | Usage tracking in UsageLog table | Historical data preservation, aggregation queries |
| 2026-01-25 | Pricing cache in memory | Reduce API calls, 24h TTL sufficient |
| 2026-02-04 | JWT over session-based auth | Stateless, scalable, standard |
| 2026-02-04 | bcrypt with cost 12 | Industry standard, good security/performance balance |
| 2026-02-04 | Fernet for API key encryption | Symmetric encryption, simple key management |
| 2026-02-04 | RBAC with 3 roles | Simple hierarchy covers most use cases |
| 2026-02-04 | JSONB for audit old/new values | Flexible schema, efficient storage |
| 2026-02-04 | Quota check before AI calls | Prevent overspending, graceful degradation |

## Appendix C: References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenRouter API](https://openrouter.ai/docs)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vite.dev/)
- [TailwindCSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)

---

## Appendix D: Development Roadmap Summary

> AI-Across is an internal MarketAcross tool (~50 employees), not a SaaS product.

### Current Progress

| Milestone | Status | Key Deliverables |
|-----------|--------|------------------|
| Alpha (Phase 3) | ✅ Complete | Backend APIs, RAG pipeline, chat streaming |
| Beta (Phase 5) | ✅ Complete | Full UI with chat interface, streaming, model selector |
| RC (Phase 6) | ✅ Complete | Testing, polish, performance, health endpoints |
| Admin Ready (Phase 7) | ✅ Complete | Admin dashboard, usage tracking, cost calculation |
| Admin Enhanced (Phase 9) | ✅ Complete | Multi-user, API keys, quotas, audit logs |
| Security (Phase 10) | ✅ Complete | User auth, RBAC, conversation isolation, security headers |
| v1.0 (Phase 8) | ✅ Complete | Production deployment hardening complete (CI, structured logging, ingestion resilience, backups, feedback, workspace groundwork, RAG guardrails) |

### Post-MVP Vision

| Version | Theme | Key Features |
|---------|-------|--------------|
| v1.1 | Team Productivity | Conversation sharing, folders/tags, smart search, direct provider API routing |
| v1.2 | Admin Power Features | Custom templates, assistant cloning, quality scoring, brand voice checker |
| v1.3 | Integrations | Telegram integration |

### Success Metrics

| Metric | v1.0 Target | Measurement |
|--------|-------------|-------------|
| Assistant creation | < 5 minutes | Time to first chat |
| File processing | < 2 min/50 pages | Processing time |
| API latency | < 200ms (p95) | Excluding LLM |
| Uptime | 99% | Monitoring |
| Test coverage | > 70% | pytest + Vitest |

---

## Appendix E: Risk Assessment

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OpenRouter rate limits | High | Medium | Request queuing, exponential backoff |
| ChromaDB scaling | Medium | Low | Monitor vectors, plan Qdrant migration |
| LLM API costs | High | Medium | Usage limits, cost alerts |
| Data loss | Critical | Low | Daily backups, recovery testing |
| Security breach | Critical | Low | Security audits, penetration testing |

### Business Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model API price changes | Medium | Multi-provider support; v1.1 adds direct API routing |
| Model deprecation | Medium | Graceful fallbacks |
| Team adoption | High | Training, documentation, intuitive UX |

### Mitigation Priorities

1. **Immediate:** Automated backups, rate limiting
2. **Short-term:** Usage monitoring, cost alerts
3. **Medium-term:** Security audit, load testing
