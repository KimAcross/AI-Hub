# AI-Across Development Roadmap

This document outlines the development phases, milestones, and future vision for AI-Across.

## Current Status

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Backend Foundation | Complete | 100% |
| Phase 2: File Processing & RAG | Complete | 100% |
| Phase 3: OpenRouter & Chat | Complete | 100% |
| Phase 4: Frontend - Assistant Management | Complete | 100% |
| Phase 5: Frontend - Chat Interface | Complete | 100% |
| Phase 6: Polish & QA | Complete | 100% |
| Phase 7: Admin Board | Complete | 100% |
| Phase 8: Production Deployment | In Progress | 40% |
| Phase 9: Admin Dashboard Enhancement | Complete | 100% |
| Phase 10: Security Hardening & User Auth | Complete | 100% |

---

## Phase 1: Backend Foundation

**Status:** Complete

### Deliverables

- [x] Project scaffolding (FastAPI + PostgreSQL)
- [x] Database models and migrations (Alembic)
- [x] Assistant CRUD API endpoints
- [x] Configuration management (Pydantic settings)
- [x] API documentation (Swagger/OpenAPI)
- [x] Custom exception handling
- [x] CORS configuration
- [x] Docker development environment

### API Endpoints Implemented

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/assistants` | POST | Create assistant |
| `GET /api/v1/assistants` | GET | List assistants |
| `GET /api/v1/assistants/{id}` | GET | Get assistant |
| `PATCH /api/v1/assistants/{id}` | PATCH | Update assistant |
| `DELETE /api/v1/assistants/{id}` | DELETE | Soft delete |
| `POST /api/v1/assistants/{id}/restore` | POST | Restore deleted |
| `GET /api/v1/assistants/templates` | GET | List templates |
| `POST /api/v1/assistants/from-template/{id}` | POST | Create from template |

---

## Phase 2: File Processing & RAG

**Status:** Complete

### Deliverables

- [x] File upload endpoint with multipart handling
- [x] PDF text extraction (PyMuPDF)
- [x] DOCX text extraction (python-docx)
- [x] TXT/Markdown support
- [x] Text chunking pipeline (512 tokens, 50 overlap)
- [x] ChromaDB integration for vector storage
- [x] Embedding service infrastructure
- [x] RAG retrieval service
- [x] File status tracking (processing → ready)
- [x] File reprocessing for failed uploads

### API Endpoints Implemented

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/assistants/{id}/files` | POST | Upload file |
| `GET /api/v1/assistants/{id}/files` | GET | List files |
| `GET /api/v1/assistants/{id}/files/{file_id}` | GET | Get file details |
| `DELETE /api/v1/assistants/{id}/files/{file_id}` | DELETE | Delete file |
| `POST /api/v1/assistants/{id}/files/{file_id}/reprocess` | POST | Reprocess file |

### Technical Specifications

- **Chunk Size:** 512 tokens
- **Chunk Overlap:** 50 tokens
- **Embedding Model:** text-embedding-3-small (1536 dimensions)
- **Vector Store:** ChromaDB (persistent, local)
- **Retrieval:** Top-5, similarity threshold 0.7
- **Max File Size:** 50MB

---

## Phase 3: OpenRouter & Chat

**Status:** Complete

### Deliverables

- [x] OpenRouter service integration
- [x] Model listing endpoint
- [x] Chat completion with SSE streaming
- [x] RAG context injection into prompts
- [x] Conversation CRUD operations
- [x] Message persistence
- [x] Token usage tracking

### API Endpoints Implemented

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/v1/models` | GET | List available models |
| `POST /api/v1/conversations` | POST | Create conversation |
| `GET /api/v1/conversations` | GET | List conversations |
| `GET /api/v1/conversations/{id}` | GET | Get conversation |
| `PATCH /api/v1/conversations/{id}` | PATCH | Update conversation |
| `DELETE /api/v1/conversations/{id}` | DELETE | Delete conversation |
| `POST /api/v1/conversations/{id}/messages` | POST | Send message (streaming) |
| `PATCH /api/v1/conversations/{id}/messages/{msg_id}` | PATCH | Edit message |
| `GET /api/v1/conversations/{id}/export` | GET | Export conversation |

### Success Criteria

- Chat works with Claude 3.5 Sonnet via OpenRouter
- Model switching works mid-conversation
- Streaming responses display token-by-token
- Knowledge base context is included in prompts

---

## Phase 4: Frontend - Assistant Management

**Status:** Complete

### Deliverables

- [x] React + Vite project setup
- [x] TailwindCSS + shadcn/ui configuration
- [x] Sidebar navigation component
- [x] Dashboard with assistant cards
- [x] Assistant list view
- [x] Create assistant form with validation
- [x] Edit assistant modal
- [x] Delete assistant confirmation dialog
- [x] File upload interface with drag-and-drop
- [x] File processing status indicators
- [x] React Query for API integration
- [x] Zustand for client state
- [x] Docker frontend configuration

### Technical Implementation

- **Framework:** React 18 + TypeScript + Vite 7
- **Styling:** TailwindCSS v3 with custom design system
- **State Management:** Zustand (persisted app state) + React Query (server state)
- **Routing:** React Router v7
- **Components:** Custom UI component library (shadcn/ui patterns)
- **Forms:** React Hook Form
- **File Upload:** react-dropzone with progress tracking

### Success Criteria

- Full assistant CRUD from UI
- File upload with real-time progress
- Responsive design (mobile, tablet, desktop)

---

## Phase 5: Frontend - Chat Interface

**Status:** Complete

### Deliverables

- [x] Chat window component
- [x] Message list with markdown rendering
- [x] Code syntax highlighting (highlight.js)
- [x] Streaming response display with SSE
- [x] Model selector dropdown with provider grouping
- [x] Conversation sidebar with search
- [x] Copy message to clipboard
- [x] Regenerate response button
- [x] Stop generation button (AbortController)
- [x] Message editing with history
- [x] Conversation export (Markdown/JSON)
- [x] Keyboard shortcuts (Ctrl + Enter to send)
- [x] Auto-scroll with smart pause on user scroll
- [x] Typing indicators

### Technical Implementation

- **Markdown Rendering:** react-markdown with remark-gfm
- **Code Highlighting:** rehype-highlight or Prism.js
- **Streaming:** EventSource API for SSE consumption
- **State Management:** React Query for conversations + Zustand for UI state
- **Virtualization:** react-window for long conversation lists

### Component Structure

```
src/
├── components/
│   └── chat/
│       ├── ChatWindow.tsx          # Main chat container
│       ├── MessageList.tsx         # Virtualized message list
│       ├── MessageBubble.tsx       # Individual message component
│       ├── MessageInput.tsx        # Input with submit button
│       ├── ModelSelector.tsx       # Model dropdown
│       ├── ConversationSidebar.tsx # Conversation list
│       ├── StreamingMessage.tsx    # Handles SSE display
│       └── CodeBlock.tsx           # Syntax-highlighted code
```

### Success Criteria

- Full chat functionality
- Real-time streaming display
- Model switching preserves conversation
- Conversation history persists
- Smooth scrolling and responsive UI
- < 100ms input latency

---

## Phase 6: Polish & QA

**Status:** Complete (100%)

### Delivered

#### Error Handling & UX
- [x] Global error boundary with fallback UI
- [x] API error interceptors with retry logic
- [x] Offline detection and reconnection handling
- [x] Loading states and skeleton screens
- [x] Toast notifications (react-hot-toast)
- [x] Empty states for all list views

#### Settings Page
- [x] OpenRouter API key configuration (database storage)
- [x] Default model selection
- [x] Theme toggle (dark/light/system)
- [x] Language preference
- [x] Streaming enable/disable
- [x] Auto-save interval configuration

#### Performance Optimization
- [x] React component memoization
- [x] Image lazy loading
- [x] Bundle splitting and code splitting
- [x] API response caching
- [x] Database query optimization
- [x] Connection pooling tuning

#### Testing
- [x] Backend unit tests (pytest)
- [x] Frontend unit tests (Vitest + React Testing Library)
- [x] API integration tests
- [x] End-to-end tests (Playwright)
- [x] Load testing (Locust)

### Testing Strategy

| Layer | Tool | Coverage Target |
|-------|------|-----------------|
| Backend Unit | pytest + pytest-asyncio | 80% |
| Frontend Unit | Vitest + RTL | 70% |
| API Integration | pytest + httpx | Key flows |
| E2E | Playwright | Critical paths |
| Load | Locust | 50 concurrent users |

### Success Criteria

- No critical bugs
- < 3s response time (excluding LLM)
- Smooth UX throughout application
- Test coverage > 70%
- Lighthouse score > 90
- Zero accessibility violations (axe-core)

---

## Phase 7: Admin Board

**Status:** Complete

### Overview

A simple Admin Board for monitoring token usage/costs and system health. Single-admin model with password protection. No multi-user system needed for v1.

### Deliverables

#### Admin Authentication (Simple)
- [x] Password stored in environment variable (`ADMIN_PASSWORD`)
- [x] Simple session token in localStorage after login
- [x] No database session model needed

#### Usage Tracking & Cost Calculation
- [x] UsageLog database model (tracks tokens per message)
- [x] Integrate usage logging into ConversationService
- [x] Cost calculation based on OpenRouter model pricing
- [x] Usage summary endpoint (totals: tokens, cost, conversations)
- [x] Usage breakdown by assistant and model
- [x] Daily usage trends (last 30 days)

#### Admin Dashboard (Single Page)
- [x] Admin login page with password form
- [x] Dashboard with usage overview stats
- [x] Usage breakdown tables (by model, by assistant)
- [x] System health indicators (Database, OpenRouter, ChromaDB)
- [x] API key status display (masked) with connectivity test
- [x] Link back to main application

### Database Schema

```sql
usage_logs
├── id (UUID, PK)
├── assistant_id (FK → assistants, SET NULL, nullable)
├── conversation_id (FK → conversations, SET NULL, nullable)
├── message_id (UUID, nullable)
├── model (VARCHAR 100)
├── prompt_tokens (INTEGER)
├── completion_tokens (INTEGER)
├── total_tokens (INTEGER)
├── cost_usd (DECIMAL 10,6)
├── created_at (TIMESTAMP, indexed)
```

### Technical Implementation

- **Token Format:** Base64 encoded `{expiry}:{nonce}:{signature}`
- **Token Expiry:** 24 hours
- **Cost Precision:** Decimal with 6 decimal places (USD)
- **Pricing Cache:** 24-hour TTL, refreshed on first access
- **Usage Aggregations:** SQL GROUP BY queries with proper indexes

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/admin/login` | POST | Verify password, return token |
| `GET /api/v1/admin/verify` | GET | Check if token valid |
| `GET /api/v1/admin/usage/summary` | GET | Totals: tokens, cost, conversations |
| `GET /api/v1/admin/usage/breakdown` | GET | By assistant and model |
| `GET /api/v1/admin/usage/daily` | GET | Last 30 days daily totals |
| `GET /api/v1/admin/health` | GET | All component statuses |

### Frontend Structure

```
frontend/src/
├── pages/admin/
│   ├── login.tsx       # Password form
│   └── index.tsx       # Single dashboard page
├── components/admin/
│   ├── admin-guard.tsx # Route protection
│   └── stats-card.tsx  # Reusable stat card
├── hooks/
│   └── use-admin.ts    # Admin hooks
└── stores/
    └── admin-store.ts  # Auth token storage
```

### Dependencies

- **Frontend:** `recharts` for usage charts

### Success Criteria

- Usage logged for every chat message with cost calculation
- Admin can view total tokens and USD cost
- Admin can see breakdown by assistant and model
- System health status visible at a glance
- Simple password protection for admin access

---

## Phase 8: Production Deployment

**Status:** In Progress (40%)

### Deliverables

#### Production Infrastructure
- [x] Nginx reverse proxy configuration
- [ ] SSL/TLS certificate setup (Let's Encrypt / Certbot)
- [x] Production Docker Compose with optimizations
- [x] Health check endpoints (`/health`, `/ready`)
- [ ] Structured logging (JSON format)
- [ ] Log rotation and retention

#### Backup & Recovery
- [ ] PostgreSQL automated daily backups
- [ ] ChromaDB data backup strategy
- [ ] Uploaded files backup
- [ ] Backup to external storage (S3-compatible optional)
- [ ] Restore procedures and documentation
- [ ] Disaster recovery runbook

#### Documentation
- [ ] VPS deployment guide (Ubuntu 22.04+)
- [ ] Docker deployment guide
- [ ] Configuration reference
- [ ] Troubleshooting guide
- [ ] Security hardening checklist

### Production Architecture

```
                    ┌─────────────────┐
                    │   Cloudflare    │
                    │   (Optional)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     Nginx       │
                    │  (Port 80/443)  │
                    │  + Let's Encrypt│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌───────▼──────┐ ┌────▼─────┐
     │  Frontend  │  │   Backend    │ │  Static  │
     │   (Vite)   │  │  (FastAPI)   │ │  Files   │
     │  Port 5173 │  │  Port 8000   │ │          │
     └────────────┘  └───────┬──────┘ └──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌───────▼──────┐ ┌────▼─────┐
     │ PostgreSQL │  │   ChromaDB   │ │  Uploads │
     │  Port 5432 │  │  (Embedded)  │ │  Volume  │
     └────────────┘  └──────────────┘ └──────────┘
```

### Environment Configuration

```bash
# Production .env
APP_ENV=production
DEBUG=false
SECRET_KEY=<generate-secure-key>

# Database
DATABASE_URL=postgresql://aiacross:secure_pass@db:5432/aiacross

# Security
CORS_ORIGINS=https://your-domain.com
ALLOWED_HOSTS=your-domain.com

# SSL
SSL_CERT_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem
```

### Success Criteria

- Secure password protection
- One-command production deployment (`docker compose up -d`)
- HTTPS working with valid certificate
- Automated daily backup system
- < 30 second deployment rollback capability
- 99.9% uptime target

---

## Phase 9: Admin Dashboard Enhancement

**Status:** Complete

### Overview

Comprehensive admin features including multi-user support, API key management for multiple providers, usage quotas and limits, and audit logging. This phase implements features originally planned for v1.1 (Multi-User System).

### Deliverables

#### User Management
- [x] User model with roles (Admin, Manager, User)
- [x] User CRUD API endpoints
- [x] Password hashing with bcrypt (cost factor 12)
- [x] JWT authentication with access/refresh tokens
- [x] Role-based access control (RBAC)
- [x] User management UI (create, edit, disable, delete)
- [x] Password reset functionality

#### API Key Management
- [x] Multi-provider API key storage (OpenRouter, OpenAI, Anthropic, Google, Azure)
- [x] Fernet encryption for API keys at rest
- [x] API key CRUD endpoints
- [x] Test connectivity endpoint
- [x] Key rotation endpoint
- [x] Default key selection per provider
- [x] API key management UI with provider filtering

#### Usage Quotas & Limits
- [x] UsageQuota model (daily/monthly cost and token limits)
- [x] Global and per-user quota support
- [x] Alert threshold configuration (percentage-based)
- [x] Quota checking before AI API calls
- [x] Rate limiting support (requests per minute/hour)
- [x] Quota management UI with progress bars
- [x] Real-time alerts for approaching limits

#### Audit Logging
- [x] AuditLog model for tracking admin actions
- [x] Automatic logging of CRUD operations
- [x] Old/new value comparison storage
- [x] Audit log query API with filters
- [x] Recent activity endpoint
- [x] Audit log viewer UI with search

#### Admin UI Enhancement
- [x] Admin sidebar navigation
- [x] Admin layout with header (logout, refresh, alerts)
- [x] Users page with table and dialogs
- [x] API Keys page with provider cards
- [x] Usage & Quotas page with configuration
- [x] Settings page with system info
- [x] Audit Logs page with filters

### Database Schema

```sql
users
├── id (UUID, PK)
├── email (VARCHAR 255, unique, indexed)
├── password_hash (VARCHAR 255)
├── name (VARCHAR 255)
├── role (ENUM: admin, manager, user)
├── is_active (BOOLEAN, default true)
├── last_login_at (TIMESTAMP, nullable)
├── created_at (TIMESTAMP)
├── updated_at (TIMESTAMP)

api_keys
├── id (UUID, PK)
├── provider (ENUM: openrouter, openai, anthropic, google, azure)
├── name (VARCHAR 255)
├── encrypted_key (TEXT)
├── is_default (BOOLEAN)
├── is_active (BOOLEAN)
├── last_used_at (TIMESTAMP, nullable)
├── created_at (TIMESTAMP)
├── updated_at (TIMESTAMP)

usage_quotas
├── id (UUID, PK)
├── scope (ENUM: global, user)
├── scope_id (VARCHAR 255, nullable)
├── daily_cost_limit_usd (DECIMAL 10,2, nullable)
├── monthly_cost_limit_usd (DECIMAL 10,2, nullable)
├── daily_token_limit (INTEGER, nullable)
├── monthly_token_limit (INTEGER, nullable)
├── requests_per_minute (INTEGER, nullable)
├── requests_per_hour (INTEGER, nullable)
├── alert_threshold_percent (INTEGER, default 80)
├── created_at (TIMESTAMP)
├── updated_at (TIMESTAMP)

audit_logs
├── id (UUID, PK)
├── actor_id (UUID, nullable, FK → users)
├── actor_email (VARCHAR 255)
├── action (VARCHAR 50)
├── resource_type (VARCHAR 50)
├── resource_id (VARCHAR 255, nullable)
├── old_values (JSONB, nullable)
├── new_values (JSONB, nullable)
├── ip_address (VARCHAR 45, nullable)
├── user_agent (TEXT, nullable)
├── created_at (TIMESTAMP, indexed)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/admin/users` | POST | Create user (Admin only) |
| `GET /api/v1/admin/users` | GET | List users with filters |
| `GET /api/v1/admin/users/{id}` | GET | Get user details |
| `PATCH /api/v1/admin/users/{id}` | PATCH | Update user |
| `DELETE /api/v1/admin/users/{id}` | DELETE | Delete user |
| `POST /api/v1/admin/users/{id}/disable` | POST | Disable user |
| `POST /api/v1/admin/users/{id}/enable` | POST | Enable user |
| `POST /api/v1/admin/users/{id}/reset-password` | POST | Reset password |
| `GET /api/v1/admin/api-keys` | GET | List provider API keys |
| `POST /api/v1/admin/api-keys` | POST | Add new API key |
| `PATCH /api/v1/admin/api-keys/{id}` | PATCH | Update API key |
| `DELETE /api/v1/admin/api-keys/{id}` | DELETE | Delete API key |
| `POST /api/v1/admin/api-keys/{id}/test` | POST | Test connectivity |
| `POST /api/v1/admin/api-keys/{id}/rotate` | POST | Rotate key |
| `POST /api/v1/admin/api-keys/{id}/set-default` | POST | Set as default |
| `GET /api/v1/admin/quotas/global` | GET | Get global quota |
| `PATCH /api/v1/admin/quotas/global` | PATCH | Update global quota |
| `GET /api/v1/admin/quotas/usage` | GET | Current usage status |
| `GET /api/v1/admin/quotas/alerts` | GET | Get quota alerts |
| `GET /api/v1/admin/audit` | GET | Query audit logs |
| `GET /api/v1/admin/audit/recent` | GET | Recent activity |

### Frontend Structure

```
frontend/src/
├── pages/
│   ├── login.tsx              # User login (Phase 10)
│   └── admin/
│       ├── login.tsx          # Admin login
│       ├── index.tsx          # Dashboard
│       ├── assistants.tsx     # Assistant management (Phase 10)
│       ├── users.tsx          # User management
│       ├── api-keys.tsx       # API key management
│       ├── usage.tsx          # Usage & quotas
│       ├── settings.tsx       # System settings
│       └── audit-logs.tsx     # Audit log viewer
├── components/
│   ├── auth-guard.tsx         # User route protection (Phase 10)
│   ├── quota-display.tsx      # Usage quota widget (Phase 10)
│   └── admin/
│       ├── admin-layout.tsx   # Layout wrapper
│       ├── admin-sidebar.tsx  # Navigation sidebar
│       ├── admin-guard.tsx    # Route protection
│       ├── stats-card.tsx     # Stat display
│       ├── usage-chart.tsx    # Usage chart
│       ├── health-status.tsx  # Health indicators
│       └── users/
│           ├── user-table.tsx
│           └── user-dialog.tsx
├── hooks/
│   ├── use-admin.ts           # Admin hooks
│   └── use-auth.ts            # User auth hooks (Phase 10)
└── stores/
    ├── admin-store.ts         # Admin auth + sidebar state
    └── auth-store.ts          # User auth state (Phase 10)
```

### Technical Implementation

- **Password Hashing:** bcrypt with cost factor 12
- **API Key Encryption:** Fernet symmetric encryption
- **JWT Tokens:** Access (15 min) + Refresh (7 days)
- **RBAC:** Admin > Manager > User hierarchy
- **Quota Enforcement:** Check before AI API calls, log warning if check fails
- **Audit Logging:** Automatic on all admin CRUD operations

### Success Criteria

- Multi-user authentication working with JWT
- Role-based access control enforced
- API keys encrypted and securely stored
- Quota limits enforced at runtime
- All admin actions logged with actor info
- Admin UI fully functional for all operations

---

## Phase 10: Security Hardening & User Authentication

**Status:** Complete (100%)

### Overview

Comprehensive security hardening, user-facing authentication, role-based endpoint protection, and UI improvements identified through a full code-level inspection. This phase addresses critical security gaps and establishes proper user authentication flow. Key principle: **only admins** create assistants, choose models, and manage API keys. Admin creates user accounts (no self-registration).

### 10A: Security Hardening

- [x] Security headers middleware (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy)
- [x] File upload MIME type + magic byte validation (python-magic)
- [x] File cleanup on failed uploads (delete orphaned files)
- [x] Password strength validation (min 8 chars, mixed case, digits, special chars)
- [x] Rate limits on all admin CRUD endpoints (30/min read, 10/min write)

### 10B: User Authentication & Authorization (Backend)

- [x] Protect assistant endpoints: CRUD → `require_admin_role`, READ → `require_any_role`
- [x] Protect conversation endpoints with `require_any_role`
- [x] Add `user_id` column to conversations table (Alembic migration)
- [x] Conversation user isolation (users see only their own conversations)
- [x] Admin users bypass ownership checks (can see all conversations)
- [x] Protect file endpoints: upload/delete → `require_admin_role`, read → `require_any_role`
- [x] Protect settings endpoints: GET → `require_any_role`, PATCH → `require_admin_role`
- [x] Protect models endpoint: GET → `require_any_role`
- [x] Fix `GET /auth/me` to use `require_any_role` (currently `require_manager_role`)
- [x] Add `GET /auth/verify` endpoint for frontend token validation
- [x] Add `GET /auth/usage` endpoint for user quota/usage display

### 10C: User Authentication (Frontend)

- [x] User auth Zustand store (`auth-store.ts`, following `admin-store.ts` pattern)
- [x] User login page (`/login`) with email + password form
- [x] Auth guard component (following `AdminGuard` pattern)
- [x] Route protection: wrap all MainLayout routes with AuthGuard
- [x] API client auth integration (request/response interceptors)
- [x] User auth React Query hooks (`useLogin`, `useLogout`, `useVerifyAuth`)

### 10D: Role-Based UI

- [x] Remove assistant create/edit from regular user UI (read-only browse)
- [x] New admin assistant management page (`/admin/assistants`) with CRUD, templates, model selection, file management
- [x] Add "Assistants" link to admin sidebar navigation
- [x] Simplify user settings page (theme + language only, remove API key and model selection)
- [x] Update user dashboard (user's conversations, available assistants, usage widget)
- [x] Add user profile section + logout button to user sidebar/header

### 10E: UX Improvements

- [x] Verify conversation export works end-to-end (hook exists, check UI wiring)
- [x] User quota/usage display widget (progress bars, color-coded warnings)
- [x] Improved error messages with categories (auth/validation/rate-limit/server) and recovery suggestions
- [x] Empty state guidance ("Browse available assistants to start chatting")

### 10F: Admin Enhancements

- [x] Audit log export endpoint (`GET /admin/audit/export?format=csv|json`)
- [x] Audit log export button in frontend (CSV/JSON format selector)
- [x] Reduce admin token TTL from 24h to 8h

### Database Migration

```sql
-- Alembic migration for Phase 10
-- 1. Delete all existing conversations (pre-production data)
DELETE FROM messages;
DELETE FROM conversations;

-- 2. Add user_id to conversations
ALTER TABLE conversations ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE SET NULL;
CREATE INDEX ix_conversations_user_id ON conversations(user_id);
```

### New Files

| File | Purpose |
|------|---------|
| `frontend/src/pages/login.tsx` | User login page |
| `frontend/src/stores/auth-store.ts` | User auth Zustand store |
| `frontend/src/components/auth-guard.tsx` | Route protection component |
| `frontend/src/hooks/use-auth.ts` | User auth React Query hooks |
| `frontend/src/pages/admin/assistants.tsx` | Admin assistant management |
| `frontend/src/components/quota-display.tsx` | User quota/usage widget |

### Key Files Modified

| File | Changes |
|------|---------|
| `backend/app/main.py` | SecurityHeadersMiddleware |
| `backend/app/services/file_processor.py` | MIME validation + cleanup |
| `backend/app/schemas/user.py` | Password strength validator |
| `backend/app/api/v1/assistants.py` | Auth deps on all endpoints |
| `backend/app/api/v1/conversations.py` | Auth + user_id filtering |
| `backend/app/api/v1/files.py` | Auth deps |
| `backend/app/api/v1/settings.py` | Auth deps |
| `backend/app/api/v1/users.py` | Fix /auth/me, add /auth/verify |
| `backend/app/models/conversation.py` | Add user_id column |
| `frontend/src/App.tsx` | /login route, AuthGuard wrapper |
| `frontend/src/lib/api.ts` | Auth interceptors |
| `frontend/src/pages/settings.tsx` | Role-based section visibility |
| `frontend/src/pages/dashboard.tsx` | User-specific content |
| `frontend/src/components/admin/admin-sidebar.tsx` | Add Assistants link |

### Success Criteria

- All API endpoints require authentication (no public access except /login, /health)
- Regular users can only see their own conversations
- Assistant creation/edit/delete is admin-only (403 for regular users)
- Security headers present on all responses
- File uploads reject MIME type mismatches
- Weak passwords are rejected with specific error messages
- User login flow works: login → dashboard → chat → logout
- Admin assistant management page fully functional

---

## Post-MVP Roadmap

> **Scope note:** AI-Across is an internal MarketAcross tool (~50 employees), not a SaaS product. The roadmap below focuses exclusively on features that serve the internal content team.

### Previously Completed (v0.8–v0.9)

- [x] Multi-user accounts with roles (Admin, Manager, User) - *Phase 9*
- [x] User management interface (invite, deactivate, reset password) - *Phase 9*
- [x] Per-user usage tracking and cost attribution - *Phase 10*
- [x] Usage quotas with rate limits - *Phase 9*
- [x] Activity audit log - *Phase 9*
- [x] Budget limits and alerts per user - *Phase 9*
- [x] JWT authentication with RBAC - *Phase 9*
- [x] Conversation user isolation - *Phase 10*

---

### Version 1.1 - Team Productivity

**Theme:** Help the content team work faster and find things easily

- [ ] Conversation sharing (shareable links with expiry)
- [ ] Conversation folders and tags
- [ ] Smart search across all conversations (embedding-based semantic search)
- [ ] Direct provider API routing (call Anthropic, Google, OpenAI directly — fall back to OpenRouter)

**Technical Requirements:**
- Refactor `openrouter_service.py` into a generic `LLMGatewayService` with provider routing
- Embedding-based search index across conversations
- Shareable link generation with token-based access and TTL

---

### Version 1.2 - Admin Power Features

**Theme:** Make it easier for admins to manage and iterate on assistants

- [ ] Custom assistant templates (save your own configurations as reusable templates)
- [ ] Assistant cloning (duplicate an assistant with all settings)
- [ ] Content quality scoring (AI-based assessment of output quality)
- [ ] Brand voice consistency checker (verify output matches MarketAcross brand guidelines)

**Technical Requirements:**
- Template save/load from assistant configurations
- Quality scoring prompts and evaluation pipeline
- Brand voice reference corpus and comparison logic

---

### Version 1.3 - Integrations

**Theme:** Connect AI-Across to the tools MarketAcross already uses

- [ ] Telegram integration (bot for quick queries or notifications)

**Technical Requirements:**
- Telegram Bot API integration
- Message routing between Telegram and AI-Across assistants

---

## Milestones

| Milestone | Target | Description |
|-----------|--------|-------------|
| Alpha | Phase 3 Complete | Backend fully functional |
| Beta | Phase 5 Complete | Full application usable |
| Release Candidate | Phase 6 Complete | Production-ready quality |
| Admin Ready | Phase 7 Complete | Admin board with usage tracking |
| v0.8.0 | Phase 9 Complete | Admin dashboard enhancement (multi-user, quotas, audit) |
| v0.9.0 | Phase 10 Complete | Security hardening, user auth, role-based UI |
| v1.0 | Phase 8 Complete | Production deployment (secure, authenticated, backed up) |
| v1.1 | After v1.0 | Team productivity (sharing, search, direct API routing) |
| v1.2 | After v1.1 | Admin power features (templates, cloning, quality scoring) |
| v1.3 | After v1.2 | Telegram integration |

---

## Technical Debt & Maintenance

### Ongoing Maintenance Tasks

- [ ] Dependency updates (monthly security patches)
- [ ] Database index optimization (quarterly)
- [ ] Log analysis and cleanup
- [ ] Performance monitoring and alerting
- [ ] Security vulnerability scanning
- [ ] API deprecation handling

### Known Technical Debt

| Item | Priority | Description |
|------|----------|-------------|
| ChromaDB scaling | Medium | Consider migration to Qdrant/Pinecone for >1M vectors |
| File storage | Low | Move to S3-compatible storage for multi-instance |
| Real-time updates | Medium | Consider WebSocket for live conversation sync |
| Caching layer | Low | Add Redis for session/response caching |

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenRouter rate limits | High | Implement request queuing and backoff; v1.1 adds direct provider routing as fallback |
| ChromaDB performance at scale | Medium | Monitor and plan Qdrant migration |
| LLM API cost overruns | High | Implement usage limits and alerts |
| File processing failures | Low | Robust error handling and retry logic |

### Business Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model API price changes | Medium | Support multiple providers, easy switching |
| Model deprecation | Medium | Graceful fallback to alternatives |
| Data loss | Critical | Automated backups, recovery testing |

---

## Success Metrics

### v1.0 Launch Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Assistant creation | < 5 min | Time from start to first chat |
| File processing | < 2 min for 50 pages | Processing time |
| Response latency | < 3s (excluding LLM) | API response time |
| Uptime | 99.9% | Monitoring |
| Page load | < 2s | Lighthouse |

### Post-Launch KPIs

| Metric | Target | Cadence |
|--------|--------|---------|
| Daily active users | 80% of team | Weekly |
| Conversations per user | 5+ per week | Weekly |
| Content output increase | 40% | Monthly |
| User satisfaction | > 4.5/5 | Quarterly |
| System errors | < 0.1% of requests | Daily |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to AI-Across development.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

---

## Appendix: Technology Decisions

### Why These Technologies?

| Choice | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| FastAPI | Django, Flask | Async-first, auto-docs, modern Python |
| React | Vue, Svelte | Team familiarity, ecosystem size |
| PostgreSQL | MySQL, SQLite | JSON support, reliability, scaling |
| ChromaDB | Pinecone, Qdrant | Local-first, no external dependency for MVP |
| Zustand | Redux, MobX | Simple, minimal boilerplate |
| shadcn/ui | Material UI, Chakra | Customizable, accessible, modern design |
| Docker | VM, bare metal | Reproducible, portable deployments |

### Architecture Decision Records (ADRs)

Future significant technical decisions should be documented as ADRs in the `/docs/adr/` directory.
