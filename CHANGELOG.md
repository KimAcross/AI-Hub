# Changelog

All notable changes to AI-Across will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Assistant cards now open chat directly via `/chat?assistant=<id>`, while keeping the 3-dot admin menu for edit/delete/restore actions.
- Chat page now initializes model by context:
  - Assistant chat uses `assistant.model`
  - General chat uses `settings.default_model`
- Frontend stream parser now supports backend SSE `done` events with `message_id`/`tokens_used` payloads.
- GitHub Actions CI workflow at `.github/workflows/ci.yml` with:
  - Parallel backend and frontend jobs.
  - Optional gated E2E smoke job (`main` pushes, nightly schedule, or manual dispatch).
- CI smoke test assets for Playwright:
  - `frontend/playwright.smoke.config.ts`
  - `frontend/e2e/smoke.spec.ts`
- New documentation files:
  - `docs/DEPLOYMENT.md`
  - `docs/BACKUP.md`
  - `CONTRIBUTING.md`
- Structured logging and request correlation support:
  - JSON logs with context fields (`request_id`, `user_id`, `conversation_id`, `assistant_id`)
  - `X-Request-ID` response header middleware
- Self-healing ingestion resilience:
  - retry metadata on `knowledge_files`
  - periodic ingestion reaper and exponential backoff retries
- Message feedback capture:
  - assistant thumbs up/down with optional reason
  - feedback context storage (model + retrieval doc IDs)
- Workspace schema groundwork:
  - `workspaces` table and `workspace_id` on assistants/conversations/knowledge_files
- Per-assistant RAG guardrails:
  - `max_retrieval_chunks`
  - `max_context_tokens`
- Backup and restore scripts:
  - `docker/scripts/backup.sh`
  - `docker/scripts/restore.sh`

### Changed
- `/api/v1/models` now resolves OpenRouter API key from database settings first, then environment fallback.
- Conversation dependency wiring now injects OpenRouter service with database-stored API key, enabling chat even when key is configured from Settings UI.
- Frontend CI install now uses `npm ci --legacy-peer-deps` due current React 19 / Testing Library peer dependency conflict.
- Documentation audit and synchronization across `README.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/HLD.md`, and `frontend/README.md`.
- Phase 8 tracking aligned to complete (`100%`) in roadmap and docs.
- Backend file-type dependency is now platform-specific in `backend/requirements.txt`:
  - `python-magic-bin` on Windows
  - `python-magic` on non-Windows environments

### Fixed
- Fixed multiple 500 errors caused by async lazy-loading serialization (`MissingGreenlet`) in auth and conversations paths.
- Fixed enum value/name mismatch for user/api-key/quota enums when reading from PostgreSQL.
- Fixed assistant files API handler method reference causing 500s.
- Fixed models endpoint behavior when OpenRouter is unavailable (returns empty list response instead of hard failure).
- Fixed frontend crashes from non-array API payloads by normalizing assistants/files/conversations/models responses.
- Fixed dashboard crash (`assistants?.filter is not a function`) and conversation sidebar crash (`forEach is not a function`).
- Fixed chat stream client error `"No final message received"` by robust SSE parsing and completion handling.
- Fixed React crash when rendering FastAPI validation error objects; validation errors are now stringified for UI display.
- Fixed `onValueChange` warnings in native `Select`/`Slider` wrappers.
- Fixed chat composer flow that could POST invalid new conversations without assistant context (422).
- Fixed assistant file count mapping (`file_count` -> `files_count`) in frontend normalization.
- Fixed chat layout center whitespace by making message list full-width in chat content area.
- Added fallback favicon to avoid repeated `/favicon.ico` 404 noise in development.
- Fixed missing internal documentation links (`docs/DEPLOYMENT.md`, `CONTRIBUTING.md`) by adding the referenced files.
- Fixed migration `003` enum creation flow so fresh PostgreSQL migrations no longer fail on duplicate enum types.
- Fixed SQLite test compatibility for JSON fields by using SQLAlchemy `JSON` with a PostgreSQL `JSONB` variant in models.

### Completed
- CI baseline stabilized for auth-protected endpoint expectations after Phase 10 hardening.
- Production hardening docs updated with SSL guidance, VPS flow, backup runbook, and troubleshooting.

---

## [0.9.0] - 2026-02-10

### Added

#### Security Hardening (10A)
- `SecurityHeadersMiddleware` — adds X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, Content-Security-Policy, and conditional HSTS to all responses
- Password strength validation (uppercase, lowercase, digit, special character) on `UserCreate` and `UserPasswordChange` schemas
- File upload MIME type validation using magic bytes (`python-magic` / `python-magic-bin`)
- File cleanup on failed uploads (delete orphaned physical files)
- Rate limiting on all admin CRUD endpoints (30/min reads, 10/min writes)

#### User Authentication & Authorization (10B)
- Authentication on **all** user-facing API endpoints — no more public access
- `user_id` column on `conversations` table with foreign key to `users` and index
- Conversation user isolation — regular users see only their own conversations, admins see all
- `GET /api/v1/auth/verify` endpoint for frontend token validation
- `GET /api/v1/auth/usage` endpoint for user quota/usage display
- `GET /api/v1/admin/audit/export` endpoint for audit log CSV/JSON export

#### Frontend Authentication (10C)
- User auth Zustand store (`auth-store.ts`) with persistence to localStorage
- User login page (`/login`) with email + password form
- `AuthGuard` component for route protection with server-side token verification
- API client request interceptor for automatic `X-Admin-Token` header injection
- API client response interceptor for 401 logout + redirect
- Auth header injection on raw `fetch()` calls (streaming chat endpoint)
- React Query hooks: `useLogin`, `useVerifyAuth`, `useCurrentUser`, `useUserUsage`, `useLogout`

#### Role-Based UI (10D)
- Admin-only assistant management page (`/admin/assistants`) with inline edit/delete dialogs
- "Assistants" link added to admin sidebar navigation
- Assistants page: read-only browse for regular users, card click navigates to chat
- Settings page: admin-only sections (API Key, Default Model, Chat Settings) hidden for regular users
- Dashboard: role-aware content with user-specific quick actions and empty states
- User profile display + logout button in main sidebar

#### UX Improvements (10E)
- `QuotaDisplay` widget with color-coded progress bars (daily/monthly cost and token limits)
- Quota widget placed on user dashboard
- Improved API error messages: 403 → "You don't have permission", 429 → "Too many requests"
- Empty state guidance for no assistants ("Your administrator hasn't set up any assistants yet")

#### Admin Enhancements (10F)
- Audit log export buttons (CSV/JSON) on admin audit logs page
- Streaming file download with auth header for audit exports

### Changed

- **Breaking:** All user-facing API endpoints now require authentication (JWT token via `X-Admin-Token` header)
- `GET /auth/me` auth changed from `require_manager_role` to `require_any_role` (regular users can now access)
- Access token TTL reduced from 24 hours to 8 hours for security
- Assistant CRUD endpoints: reads require `require_any_role`, writes require `require_admin_role`
- Conversation endpoints: all require `require_any_role` with ownership checks
- File endpoints: upload/delete/reprocess require `require_admin_role`, read requires `require_any_role`
- Settings endpoints: GET requires `require_any_role`, PATCH requires `require_admin_role`
- Models endpoint: requires `require_any_role`
- Conversation service methods accept `user_id` and `is_admin` parameters for isolation
- Updated `APP_VERSION` in `.env.example` from 0.8.0 to 0.9.0
- Updated `ACCESS_TOKEN_EXPIRE_HOURS` in `.env.example` from 24 to 8
- Updated frontend package version from 0.6.0 to 0.9.0
- Extracted duplicate `_get_client_info()` helper to shared `get_client_info()` in `backend/app/api/deps.py`
- Replaced `print()` statement with proper `logger.error()` in `backend/app/api/v1/files.py`

### Removed
- Unused `MessageSquare` import from `frontend/src/pages/assistants/index.tsx`
- Unused `EmptyState` component (`frontend/src/components/ui/empty-state.tsx`)
- Unused `LazyImage` component (`frontend/src/components/ui/lazy-image.tsx`)
- Unused accordion keyframe animations from `frontend/tailwind.config.js`
- Duplicate `_get_client_info()` functions from `users.py`, `quotas.py`, and `api_keys.py`

### Technical Details

- **Auth Flow:** User login → JWT with `{ sub: user_id, email, name, role }` → stored in Zustand (persisted to localStorage) → `X-Admin-Token` header on all requests
- **Token Header:** Reuses `X-Admin-Token` for both admin and user tokens (backend `verify_user_token` handles both)
- **Conversation Ownership:** `WHERE user_id = :current_user_id` for regular users, no filter for admin
- **Security Headers:** CSP, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy strict-origin-when-cross-origin, Permissions-Policy (camera/microphone/geolocation denied), HSTS in production
- **MIME Validation:** `magic.from_buffer()` on first 8KB of uploaded file, compared against `ALLOWED_MIME_TYPES` mapping
- **Password Policy:** Min 8 chars, requires uppercase + lowercase + digit + special character

### Database Schema Changes

```sql
-- New column on conversations table
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
| `frontend/src/pages/admin/assistants.tsx` | Admin assistant management page |
| `frontend/src/components/quota-display.tsx` | User quota/usage widget |

### New Dependencies

**Backend:**
- `python-magic-bin>=0.4.14` — MIME type detection via magic bytes (Windows)
- `python-magic>=0.4.27` — MIME type detection (Linux/Docker, replaces python-magic-bin)
- `libmagic1` — System library required by python-magic (Docker)

**Frontend:**
- No new dependencies

---

## [0.8.0] - 2026-02-04

### Added

#### User Management
- `User` database model with roles (Admin, Manager, User)
- User CRUD API endpoints (`/admin/users`)
- Password hashing with bcrypt (cost factor 12)
- JWT authentication with access tokens (15 min) and refresh tokens (7 days)
- Role-based access control (RBAC) with Admin > Manager > User hierarchy
- User management UI with create/edit/disable/delete functionality
- Password reset functionality for admins

#### API Key Management
- `APIKey` database model supporting multiple providers
- Support for OpenRouter, OpenAI, Anthropic, Google, and Azure providers
- Fernet encryption for secure API key storage at rest
- API key CRUD endpoints (`/admin/api-keys`)
- Test connectivity endpoint for validating keys
- Key rotation endpoint for security updates
- Default key selection per provider
- API key management UI with provider filtering and status display

#### Usage Quotas & Limits
- `UsageQuota` database model for cost and token limits
- Global quota settings (daily/monthly cost limits, daily/monthly token limits)
- Per-user quota support (scope-based configuration)
- Alert threshold configuration (percentage-based, default 80%)
- Rate limiting support (requests per minute/hour)
- Runtime quota enforcement before AI API calls
- Graceful handling when quota check fails (log warning, don't block)
- Quota management UI with progress bars and configuration dialog
- Real-time alerts for approaching limits

#### Audit Logging
- `AuditLog` database model for tracking all admin actions
- Automatic logging of CRUD operations with actor information
- Old/new value comparison storage (JSONB)
- IP address and user agent tracking
- Audit log query API with filters (action, resource type, actor, date range)
- Recent activity endpoint for quick access
- Audit log viewer UI with search, filters, and detail dialog

#### Admin Dashboard Enhancement
- Admin sidebar navigation with collapsible state
- Admin layout wrapper with header (logout, refresh, alerts badge)
- Users page with table, search, role filter, status filter, pagination
- API Keys page with provider cards and action buttons
- Usage & Quotas page with summary stats and configuration
- Settings page with system health and current configuration
- Audit Logs page with searchable log viewer

#### API Endpoints
- `POST /api/v1/admin/users` - Create user (Admin only)
- `GET /api/v1/admin/users` - List users with filters
- `GET /api/v1/admin/users/{id}` - Get user details
- `PATCH /api/v1/admin/users/{id}` - Update user
- `DELETE /api/v1/admin/users/{id}` - Delete user
- `POST /api/v1/admin/users/{id}/disable` - Disable user
- `POST /api/v1/admin/users/{id}/enable` - Enable user
- `POST /api/v1/admin/users/{id}/reset-password` - Reset password
- `GET /api/v1/admin/api-keys` - List provider API keys
- `POST /api/v1/admin/api-keys` - Add new API key
- `PATCH /api/v1/admin/api-keys/{id}` - Update API key
- `DELETE /api/v1/admin/api-keys/{id}` - Delete API key
- `POST /api/v1/admin/api-keys/{id}/test` - Test connectivity
- `POST /api/v1/admin/api-keys/{id}/rotate` - Rotate key
- `POST /api/v1/admin/api-keys/{id}/set-default` - Set as default
- `GET /api/v1/admin/quotas/global` - Get global quota
- `PATCH /api/v1/admin/quotas/global` - Update global quota
- `GET /api/v1/admin/quotas/usage` - Current usage status
- `GET /api/v1/admin/quotas/alerts` - Get quota alerts
- `GET /api/v1/admin/audit` - Query audit logs
- `GET /api/v1/admin/audit/recent` - Recent activity

#### Frontend Components
- `AdminLayout` - Layout wrapper with sidebar and header
- `AdminSidebar` - Navigation sidebar with route highlighting
- `UserTable` - User list with actions dropdown
- `UserDialog` - Create/edit user modal
- `DropdownMenu` - Custom dropdown menu component
- Extended `use-admin.ts` hooks for all admin operations

### Changed

- Updated `ConversationService.send_message()` to check quota before proceeding
- Added `QuotaService.check_quota()` integration with graceful error handling
- Updated `App.tsx` with new admin page routes
- Refactored admin dashboard to use new `AdminLayout` component
- Updated app version to 0.8.0

### Technical Details

- **Password Hashing:** bcrypt with cost factor 12
- **API Key Encryption:** Fernet symmetric encryption (32-byte key)
- **JWT Tokens:** Access token (15 min expiry) + Refresh token (7 days expiry)
- **RBAC:** Admin > Manager > User hierarchy with route-level enforcement
- **Quota Enforcement:** Pre-check before AI API calls, warning log on failure
- **Audit Logging:** Automatic on all admin CRUD operations

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

### New Dependencies

**Backend:**
- `bcrypt` - Password hashing
- `cryptography` - Fernet encryption for API keys
- `python-jose[cryptography]` - JWT token handling

**Frontend:**
- No new dependencies (uses existing shadcn/ui components)

---

## [0.7.0] - 2026-01-25

### Added

#### Admin Dashboard
- Admin login page with password authentication
- Usage overview stats (total tokens, cost, conversations, messages)
- Usage breakdown tables by model and assistant
- Daily usage trends chart (last 30 days) with recharts
- System health indicators (Database, OpenRouter, ChromaDB)
- API key status display (masked) with connectivity test
- Real-time health status with auto-refresh

#### Usage Tracking & Cost Calculation
- `UsageLog` database model for tracking tokens per message
- Automatic usage logging on every chat completion
- Cost calculation based on OpenRouter model pricing
- Pricing cache with 24-hour TTL for efficiency
- Daily, by-model, and by-assistant usage aggregations

#### Admin Authentication
- Password stored in environment variable (`ADMIN_PASSWORD`)
- HMAC-based session tokens with 24-hour expiry
- Token stored in localStorage with expiry checking
- Protected admin routes with `AdminGuard` component

#### API Endpoints
- `POST /api/v1/admin/login` - Verify password, return token
- `GET /api/v1/admin/verify` - Check if token is valid
- `GET /api/v1/admin/usage/summary` - Totals for last 30 days
- `GET /api/v1/admin/usage/breakdown` - By assistant and model
- `GET /api/v1/admin/usage/daily` - Daily totals (configurable days)
- `GET /api/v1/admin/health` - All component statuses

#### Frontend Components
- `AdminGuard` - Route protection with auth check
- `StatsCard` - Reusable metric display card
- `StatsCardGrid` - Responsive grid for stats
- `UsageChart` - Line chart for daily trends
- `HealthStatusCard` - System health display
- `Table` - Data table component

### Changed

- Updated `ConversationService.send_message()` to log usage after completion
- Added `get_model_pricing()` to `OpenRouterService` with caching
- Added `check_connectivity()` to `OpenRouterService` for health checks
- Updated app version to 0.7.0

### Technical Details

- **Token Format:** Base64 encoded `{expiry}:{nonce}:{signature}`
- **Cost Precision:** Decimal with 6 decimal places (USD)
- **Pricing Cache:** 24-hour TTL, refreshed on first access
- **Database Migration:** New `usage_logs` table with indexes

### Database Schema

```sql
usage_logs
├── id (UUID, PK)
├── assistant_id (FK → assistants, SET NULL)
├── conversation_id (FK → conversations, SET NULL)
├── message_id (UUID, nullable)
├── model (VARCHAR 100)
├── prompt_tokens (INTEGER)
├── completion_tokens (INTEGER)
├── total_tokens (INTEGER)
├── cost_usd (DECIMAL 10,6)
├── created_at (TIMESTAMP, indexed)
```

### New Dependencies

- `recharts` - React charting library for usage visualization

---

## [0.6.0] - 2026-01-20

### Added

#### Offline Detection & Connectivity
- `useOnlineStatus` hook for detecting network status
- `ConnectionStatus` component with reconnection banner
- Automatic query invalidation on reconnect
- Periodic connectivity checks via health endpoint

#### Enhanced Settings
- Language preference setting (10 languages supported)
- Streaming responses enable/disable toggle
- Auto-save interval configuration (0-300 seconds)
- Settings persisted to database

#### Performance Optimizations
- React component memoization (`React.memo`) for:
  - `MessageBubble` - Prevents re-renders of message list
  - `CodeBlock` - Prevents syntax highlighting recalculation
  - `AssistantCard` - Prevents re-renders of assistant list
- Lazy loading images with `LazyImage` component
- Route-based code splitting with `React.lazy` and `Suspense`
- API response caching for models endpoint (5 minute TTL)
- Database connection pooling optimization:
  - Pool size: 10 connections
  - Max overflow: 20 connections
  - Connection recycling: 30 minutes
  - Pre-ping validation

#### Health Endpoints
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/ready` - Readiness check with database validation

#### Testing Infrastructure
- API integration tests for assistants, conversations, and settings
- Playwright E2E test configuration
- E2E tests for dashboard, assistants, and settings pages
- Locust load testing configuration:
  - `AIAcrossUser` - Normal user behavior simulation
  - `APIStressUser` - High-frequency stress testing
  - `ReadOnlyUser` - Cache effectiveness testing

### Changed

- Updated `App.tsx` to use lazy-loaded page components
- Improved `session.py` with optimized connection pooling
- Enhanced settings API to support new configuration options

### Technical Details

- **Caching:** In-memory TTL cache with async support
- **Connection Pool:** AsyncAdaptedQueuePool with 10+20 connections
- **Code Splitting:** Page-level splits for Dashboard, Assistants, Chat, Settings
- **E2E Tests:** Playwright with Chrome, Firefox, WebKit, and mobile
- **Load Tests:** Locust with multiple user types

### Testing Coverage

| Test Type | Tool | Files |
|-----------|------|-------|
| API Integration | pytest + httpx | 3 test files |
| E2E | Playwright | 3 spec files |
| Load | Locust | 4 user classes |

---

## [0.5.0] - 2026-01-20

### Added

#### Chat Interface
- Complete chat window component with message display
- Real-time streaming responses via Server-Sent Events (SSE)
- Markdown rendering with react-markdown and remark-gfm
- Code syntax highlighting with rehype-highlight and highlight.js
- Copy-to-clipboard for messages and code blocks
- Stop generation button with AbortController support

#### Model Selector
- Model selector dropdown grouped by provider (Anthropic, OpenAI, Google, Meta, etc.)
- Displays model name, context length, and pricing info
- Model switching preserves conversation history

#### Conversation Management
- Conversation sidebar with search functionality
- Conversations grouped by date (Today, Yesterday, Previous 7 Days, etc.)
- Inline rename conversations
- Export conversations to Markdown
- Delete conversations with confirmation

#### Message Features
- Message bubbles with user/assistant avatars
- Timestamps and model info display
- Regenerate assistant responses
- Edit user messages with dialog
- Auto-scroll with smart pause on user scroll detection
- Typing indicators during streaming

#### React Hooks
- useConversations - CRUD operations for conversations
- useConversation - Single conversation with messages
- useModels - Fetch available LLM models
- useChat - Streaming message sending with abort support

### Technical Details
- **Markdown:** react-markdown + remark-gfm for GitHub-flavored markdown
- **Code Highlighting:** rehype-highlight with highlight.js (github-dark theme)
- **Streaming:** EventSource pattern with chunk aggregation
- **State:** React Query for server state, local state for UI
- **Abort:** AbortController for canceling in-flight requests

### Component Structure
```
src/components/chat/
├── chat-window.tsx         # Main chat container
├── conversation-sidebar.tsx # Conversation list with search
├── message-list.tsx        # Scrollable message list
├── message-bubble.tsx      # Individual message with markdown
├── message-input.tsx       # Input textarea with send/stop
├── model-selector.tsx      # Model dropdown grouped by provider
├── streaming-message.tsx   # Real-time streaming display
├── code-block.tsx          # Syntax-highlighted code
├── message-edit-dialog.tsx # Edit message dialog
└── index.ts                # Barrel exports
```

---

## [0.4.0] - 2026-01-20

### Added

#### Frontend Application
- React 19 + TypeScript + Vite 7 project setup
- TailwindCSS v3 with custom design system
- shadcn/ui component library integration
- React Router v7 for client-side routing

#### Dashboard & Navigation
- Sidebar navigation component with collapsible sections
- Dashboard with assistant cards and quick stats
- Responsive layout (mobile, tablet, desktop)

#### Assistant Management UI
- Assistant list view with search and filters
- Create assistant form with validation (React Hook Form)
- Edit assistant modal with real-time updates
- Delete assistant confirmation dialog with soft delete
- Assistant templates quick-create

#### File Upload Interface
- Drag-and-drop file upload (react-dropzone)
- Multi-file upload with progress tracking
- File processing status indicators (processing → ready)
- File list with metadata and delete actions
- Reprocess failed files functionality

#### State Management
- Zustand for client-side state (persisted to localStorage)
- React Query for server state and caching
- Optimistic updates for better UX

#### Docker Configuration
- Development Dockerfile with hot-reload
- Production multi-stage Dockerfile
- Docker Compose integration

### Technical Details
- **Framework:** React 19 + TypeScript
- **Build Tool:** Vite 7
- **Styling:** TailwindCSS v3 + CSS variables for theming
- **State:** Zustand (client) + React Query (server)
- **Routing:** React Router v7
- **Forms:** React Hook Form + Zod validation
- **HTTP Client:** Axios with interceptors
- **File Upload:** react-dropzone

### Developer Experience
- ESLint 9 with TypeScript-aware rules
- Path aliases (@/) for clean imports
- Component co-location pattern
- Consistent code formatting

---

## [0.3.0] - 2026-01-20

### Added

#### OpenRouter Integration
- OpenRouter service for LLM chat completions (`app/services/openrouter_service.py`)
- Support for all OpenRouter models (Claude, GPT-4, Gemini, Llama, Mistral, etc.)
- Featured models sorting for popular models
- Model listing endpoint (`GET /api/v1/models`)

#### Chat & Conversations
- Conversation CRUD API
  - Create conversation (`POST /api/v1/conversations`)
  - List conversations (`GET /api/v1/conversations`)
  - Get conversation with messages (`GET /api/v1/conversations/{id}`)
  - Update conversation (`PATCH /api/v1/conversations/{id}`)
  - Delete conversation (`DELETE /api/v1/conversations/{id}`)
- Send message with streaming response (`POST /api/v1/conversations/{id}/messages`)
- Edit message (`PATCH /api/v1/conversations/{id}/messages/{msg_id}`)
- Export conversation (`GET /api/v1/conversations/{id}/export`)

#### Streaming Responses
- Server-Sent Events (SSE) for real-time streaming
- Token-by-token response display
- Token usage tracking per message

#### RAG Context Injection
- Automatic RAG context retrieval for chat messages
- Knowledge base integration in chat responses
- System prompt augmentation with relevant document chunks

### Technical Details
- Conversation service with full CRUD operations
- Message persistence with role and token tracking
- Model switching per message
- Automatic conversation title generation

---

## [0.2.0] - 2026-01-20

### Added

#### File Upload System
- Multi-file upload endpoint (`POST /api/v1/assistants/{id}/files`)
- Support for PDF, DOCX, TXT, and Markdown files
- File size limit of 50MB per file
- Async file processing with status tracking

#### RAG Pipeline
- Text extraction from all supported file formats
- PyMuPDF integration for PDF processing
- python-docx integration for Word documents
- Intelligent text chunking (512 tokens, 50 token overlap)
- Embedding service infrastructure
- ChromaDB integration for vector storage
- RAG retrieval service with similarity search

#### File Management
- List files per assistant (`GET /api/v1/assistants/{id}/files`)
- Get file details (`GET /api/v1/assistants/{id}/files/{file_id}`)
- Delete files (`DELETE /api/v1/assistants/{id}/files/{file_id}`)
- Reprocess failed files (`POST /api/v1/assistants/{id}/files/{file_id}/reprocess`)
- File status tracking: `uploading` → `processing` → `indexing` → `ready`/`error`

#### Utilities
- `chunker.py` - Token-based text chunking with tiktoken
- `file_extractors.py` - Document text extraction utilities

### Technical Details
- Chunk size: 512 tokens
- Chunk overlap: 50 tokens
- Embedding dimensions: 1536 (text-embedding-3-small)
- Retrieval: Top-5 results with 0.7 similarity threshold
- Vector store: ChromaDB with persistent disk storage

---

## [0.1.0] - 2026-01-20

### Added

#### Project Foundation
- FastAPI application scaffolding
- Project structure with clean architecture
- Configuration management via Pydantic settings
- Environment variable support with `.env` files

#### Database
- PostgreSQL database integration
- SQLAlchemy 2.x async ORM setup
- Alembic migrations configuration
- Initial schema migration

#### Models
- `Assistant` - AI assistant configurations
- `Conversation` - Chat conversation groupings
- `Message` - Individual chat messages
- `KnowledgeFile` - Uploaded file metadata
- `Settings` - Application settings key-value store

#### Assistant Management API
- Create assistant (`POST /api/v1/assistants`)
- List assistants (`GET /api/v1/assistants`)
- Get assistant (`GET /api/v1/assistants/{id}`)
- Update assistant (`PATCH /api/v1/assistants/{id}`)
- Delete assistant (`DELETE /api/v1/assistants/{id}`) - soft delete
- Restore assistant (`POST /api/v1/assistants/{id}/restore`)
- List templates (`GET /api/v1/assistants/templates`)
- Create from template (`POST /api/v1/assistants/from-template/{id}`)

#### Pre-built Assistant Templates
1. **Press Release Writer** - AP style press releases
2. **Article Rewriter** - Plagiarism-free content rewriting
3. **Blog Post Creator** - Engaging blog content
4. **Social Media Manager** - Platform-specific social posts
5. **Email Copywriter** - Conversion-focused email copy
6. **SEO Content Optimizer** - Search-optimized content

#### Infrastructure
- Docker development environment
- Docker Compose for multi-container setup
- Multi-stage production Dockerfile
- Development Dockerfile with hot reload
- CORS middleware configuration
- Custom exception handling

#### API Documentation
- Swagger UI at `/docs`
- ReDoc at `/redoc`
- OpenAPI schema generation

#### Health Checks
- Root endpoint (`GET /`)
- Health check endpoint (`GET /health`)

### Technical Details
- Python 3.11+
- FastAPI 0.109+
- SQLAlchemy 2.x with async support
- Pydantic 2.x for validation
- asyncpg for PostgreSQL driver
- UUID primary keys
- Timezone-aware timestamps

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 0.9.0 | 2026-02-10 | Phase 10 complete: Security hardening, user auth, role-based UI, conversation isolation |
| 0.8.0 | 2026-02-04 | Phase 9 complete: Multi-user, API key management, quotas, audit logging |
| 0.7.0 | 2026-01-25 | Phase 7 complete: Admin dashboard, usage tracking, cost calculation |
| 0.6.0 | 2026-01-20 | Phase 6 complete: offline detection, settings, performance, testing |
| 0.5.0 | 2026-01-20 | Chat interface, streaming, markdown, model selector |
| 0.4.0 | 2026-01-20 | Frontend app, assistant management UI, file upload |
| 0.3.0 | 2026-01-20 | OpenRouter integration, chat API, SSE streaming |
| 0.2.0 | 2026-01-20 | File upload, RAG pipeline, ChromaDB |
| 0.1.0 | 2026-01-20 | Initial release, assistant CRUD, templates |

---

## Upgrade Notes

### 0.8.0 → 0.9.0

**This release has breaking changes.** All user-facing API endpoints now require authentication. Unauthenticated requests will receive 401 responses.

**New backend dependency:**
- `python-magic-bin>=0.4.14` — MIME type detection (Windows)
- Docker uses `python-magic>=0.4.27` + system `libmagic1` instead

**Changed environment variables:**
- `ACCESS_TOKEN_EXPIRE_HOURS` — Default changed from 24 to 8

**Database migration required:**
```bash
cd backend
alembic upgrade head
```

This migration:
- Deletes all existing conversations and messages (pre-production data cleanup)
- Adds `user_id` column to `conversations` table with foreign key to `users`
- Creates index `ix_conversations_user_id`

**New files:**
- `frontend/src/pages/login.tsx` — User login page
- `frontend/src/stores/auth-store.ts` — User auth state
- `frontend/src/components/auth-guard.tsx` — Route protection
- `frontend/src/hooks/use-auth.ts` — Auth React Query hooks
- `frontend/src/pages/admin/assistants.tsx` — Admin assistant management
- `frontend/src/components/quota-display.tsx` — Usage quota widget

To upgrade:
```bash
# Install new backend dependency
cd backend && pip install python-magic-bin>=0.4.14

# Run migrations (WARNING: deletes existing conversations)
alembic upgrade head

# Rebuild frontend
cd frontend && npm run build

# Restart services
docker-compose down && docker-compose up -d
```

**Post-upgrade steps:**
1. All users must now log in at `/login` to access the application
2. Admin creates user accounts via `/admin/users` (no self-registration)
3. Admin manages assistants via `/admin/assistants`
4. Regular users browse assistants and chat at `/assistants` and `/chat`

---

### 0.7.0 → 0.8.0

This release adds comprehensive admin features. No breaking changes to existing functionality.

**New environment variables:**
- `API_KEY_ENCRYPTION_KEY` - Fernet key for API key encryption (auto-generated if not set)

**New dependencies (backend):**
- `bcrypt` - Password hashing
- `cryptography` - Fernet encryption
- `python-jose[cryptography]` - JWT handling

**Database migration required:**
```bash
cd backend
alembic upgrade head
```

This creates the following new tables:
- `users` - User accounts with roles
- `api_keys` - Multi-provider API key storage
- `usage_quotas` - Cost and token limits
- `audit_logs` - Admin action tracking

**New files:**
- `backend/app/models/user.py` - User model
- `backend/app/models/api_key.py` - API key model
- `backend/app/models/usage_quota.py` - Quota model
- `backend/app/models/audit_log.py` - Audit log model
- `backend/app/services/user_service.py` - User CRUD
- `backend/app/services/user_auth_service.py` - JWT authentication
- `backend/app/services/api_key_service.py` - API key management
- `backend/app/services/quota_service.py` - Quota enforcement
- `backend/app/services/audit_service.py` - Audit logging
- `backend/app/api/v1/users.py` - User endpoints
- `backend/app/api/v1/api_keys.py` - API key endpoints
- `backend/app/api/v1/quotas.py` - Quota endpoints
- `backend/app/api/v1/audit.py` - Audit endpoints
- `frontend/src/pages/admin/users.tsx` - User management page
- `frontend/src/pages/admin/api-keys.tsx` - API key management page
- `frontend/src/pages/admin/usage.tsx` - Usage & quotas page
- `frontend/src/pages/admin/settings.tsx` - System settings page
- `frontend/src/pages/admin/audit-logs.tsx` - Audit log viewer
- `frontend/src/components/admin/admin-layout.tsx` - Admin layout
- `frontend/src/components/admin/admin-sidebar.tsx` - Admin navigation

To upgrade:
```bash
# Install new backend dependencies
cd backend && pip install bcrypt cryptography python-jose[cryptography]

# Run migrations
alembic upgrade head

# Install frontend deps (no new deps, but rebuild)
cd frontend && npm install && npm run build

# Restart services
docker-compose down && docker-compose up -d
```

**Post-upgrade steps:**
1. Navigate to `/admin` to access the enhanced admin dashboard
2. Configure global quotas via Usage & Quotas page
3. Add provider API keys via API Keys page
4. Create additional users if needed via Users page

---

### 0.6.0 → 0.7.0

No breaking changes. Admin dashboard and usage tracking are additive.

**New environment variables:**
- `ADMIN_PASSWORD` - Required for admin dashboard access

**New dependencies (frontend):**
- `recharts` - Chart library for usage visualization

**Database migration required:**
```bash
cd backend
alembic upgrade head
```

This creates the `usage_logs` table for tracking token usage and costs.

**New files:**
- `frontend/src/pages/admin/login.tsx` - Admin login page
- `frontend/src/pages/admin/index.tsx` - Admin dashboard
- `frontend/src/components/admin/` - Admin UI components
- `frontend/src/stores/admin-store.ts` - Admin auth state
- `frontend/src/hooks/use-admin.ts` - Admin React Query hooks
- `backend/app/models/usage_log.py` - UsageLog model
- `backend/app/services/admin_auth_service.py` - Admin authentication
- `backend/app/services/usage_log_service.py` - Usage tracking
- `backend/app/api/v1/admin.py` - Admin API endpoints

To upgrade:
```bash
# Update environment
echo 'ADMIN_PASSWORD=your-secure-password' >> .env

# Run migrations
cd backend && alembic upgrade head

# Install frontend deps
cd frontend && npm install

# Restart services
docker-compose down && docker-compose up -d
```

**Access admin dashboard:** Navigate to `/admin/login`

### 0.4.0 → 0.5.0

No breaking changes. Chat interface components added.

**New dependencies:**
- `react-markdown` - Markdown rendering
- `remark-gfm` - GitHub-flavored markdown support
- `rehype-highlight` - Code syntax highlighting
- `highlight.js` - Syntax highlighting themes

**New components:**
- `src/components/chat/` - Complete chat UI component library
- `src/hooks/use-conversations.ts` - Conversation management hooks
- `src/hooks/use-models.ts` - Model fetching hook
- `src/hooks/use-chat.ts` - Streaming chat hook

**Updated files:**
- `src/pages/chat.tsx` - Full chat page implementation
- `src/index.css` - Added highlight.js import and prose styles

To upgrade:
```bash
cd frontend && npm install
docker-compose down && docker-compose up -d
```

### 0.3.0 → 0.4.0

No breaking changes. Frontend application added.

**New services:**
- Frontend container (React + Vite)
- Nginx for production static serving

**Docker Compose changes:**
- Added `frontend` service
- Updated `nginx` configuration for SPA routing

To upgrade:
```bash
docker-compose down
docker-compose pull
docker-compose up -d
```

### 0.2.0 → 0.3.0

No breaking changes. Chat and OpenRouter features are additive.

**New environment variables:**
- `OPENROUTER_API_KEY` - Required for LLM access
- `OPENROUTER_BASE_URL` - OpenRouter API endpoint
- `DEFAULT_MODEL` - Default LLM model

### 0.1.0 → 0.2.0

No breaking changes. New file processing features are additive.

**New dependencies added:**
- `pymupdf` - PDF extraction
- `python-docx` - Word document extraction
- `chromadb` - Vector database
- `tiktoken` - Token counting

**New environment variables:**
- `CHROMA_PERSIST_DIR` - ChromaDB storage location
- `UPLOAD_DIR` - File upload storage location
- `MAX_FILE_SIZE_MB` - Maximum file size limit

Run database migrations after upgrade:
```bash
alembic upgrade head
```

---

## Links

- [Roadmap](ROADMAP.md)
- [Documentation](docs/)
- [API Reference](http://localhost:8000/docs)
