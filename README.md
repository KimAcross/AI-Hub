# AI-Across

> Your content team's AI command center

AI-Across is a self-hosted AI content platform designed for content agency operations. Create, manage, and deploy specialized AI assistants with custom instructions and knowledge bases, while maintaining the flexibility to switch between 50+ LLM providers through OpenRouter integration.

## Features

- **Specialized AI Assistants** - Pre-configured personas for press releases, article rewriting, blog posts, social media, and more
- **Knowledge Base (RAG)** - Upload PDFs, DOCX, TXT, and Markdown files to give assistants contextual knowledge, with per-assistant retrieval guardrails
- **Model Agnostic** - Switch between Claude, GPT-4, Gemini, Llama, and 50+ models via OpenRouter
- **Secure Multi-User** - JWT authentication, role-based access control (Admin/Manager/User), conversation isolation
- **Message Feedback** - Thumbs up/down on AI responses with optional reason capture for quality tracking
- **Self-Healing Ingestion** - Stuck file processing auto-recovers with exponential backoff retries
- **Structured Logging** - JSON logs with request correlation IDs (`X-Request-ID`) for end-to-end tracing
- **Backup & Restore** - Automated backup scripts with rotation and tested restore procedures
- **Full Data Ownership** - Self-hosted, your data never leaves your infrastructure
- **Modern Stack** - FastAPI backend, React frontend, PostgreSQL + ChromaDB

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenRouter API key ([get one here](https://openrouter.ai/keys))

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/marketacross/ai-across.git
   cd ai-across
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

3. **Start the development environment**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production Deployment

```bash
docker-compose up -d
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed production deployment instructions.

## Project Structure

```
ai-across/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Configuration & exceptions
│   │   ├── db/             # Database session & base
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Helpers (chunking, extractors)
│   ├── alembic/            # Database migrations
│   ├── data/               # Uploads & ChromaDB storage
│   └── tests/              # Test suite
├── frontend/               # React + Vite frontend
├── docker/                 # Docker configurations
│   ├── backend/
│   ├── frontend/
│   └── nginx/
├── docs/                   # Documentation
└── docker-compose.yml      # Production compose
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.x, Pydantic 2.x |
| **Frontend** | React 19, TypeScript, Vite 7, TailwindCSS, shadcn/ui |
| **State Management** | Zustand (client) + React Query (server) |
| **Database** | PostgreSQL 15, ChromaDB (vectors) |
| **LLM Gateway** | OpenRouter (50+ models) |
| **Infrastructure** | Docker, Docker Compose, Nginx |

## API Overview

> All endpoints except `/health`, `/ready`, and `/auth/login` require authentication via `X-Admin-Token` header (JWT).

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/login` | POST | Public | User login (email + password) |
| `/api/v1/auth/verify` | GET | Any | Validate user token |
| `/api/v1/auth/me` | GET | Any | Get current user profile |
| `/api/v1/auth/usage` | GET | Any | Get user's quota/usage status |
| `/api/v1/assistants` | GET | Any | List assistants |
| `/api/v1/assistants` | POST | Admin | Create assistant |
| `/api/v1/assistants/{id}` | GET | Any | Get assistant details |
| `/api/v1/assistants/{id}` | PATCH, DELETE | Admin | Update/delete assistant |
| `/api/v1/assistants/{id}/files` | GET | Any | List knowledge base files |
| `/api/v1/assistants/{id}/files` | POST | Admin | Upload knowledge base file |
| `/api/v1/assistants/templates` | GET | Any | List pre-built templates |
| `/api/v1/conversations` | GET, POST | Any | Manage conversations (user-isolated) |
| `/api/v1/conversations/{id}/messages` | POST | Any | Send message (streaming, ownership check) |
| `/api/v1/conversations/{id}/messages/{msg_id}/feedback` | POST | Any | Submit thumbs up/down feedback |
| `/api/v1/models` | GET | Any | List available LLM models |
| `/api/v1/settings` | GET | Any | Application settings |
| `/api/v1/settings` | PATCH | Admin | Update application settings |
| `/api/v1/health` | GET | Public | Health check endpoint |
| `/api/v1/ready` | GET | Public | Readiness check with DB validation |
| `/api/v1/admin/login` | POST | Public | Admin dashboard login |
| `/api/v1/admin/usage/*` | GET | Admin | Usage totals, breakdown, daily trends |
| `/api/v1/admin/health` | GET | Admin | System health status |
| `/api/v1/admin/users` | GET, POST | Admin | User management |
| `/api/v1/admin/users/{id}` | GET, PATCH, DELETE | Admin | Manage individual user |
| `/api/v1/admin/api-keys` | GET, POST | Admin | Provider API key management |
| `/api/v1/admin/api-keys/{id}/*` | PATCH, DELETE, POST | Admin | Manage/test/rotate API key |
| `/api/v1/admin/quotas/*` | GET, PATCH | Admin | Usage quota settings and alerts |
| `/api/v1/admin/audit` | GET | Admin | Query audit logs |
| `/api/v1/admin/audit/export` | GET | Admin | Export audit logs (CSV/JSON) |

Full API documentation available at `/docs` when running the server.

## Pre-built Assistant Templates

| Template | Description |
|----------|-------------|
| Press Release Writer | Professional press releases in AP style |
| Article Rewriter | Plagiarism-free rewrites with tone matching |
| Blog Post Creator | Engaging blog content with hooks and CTAs |
| Social Media Manager | Platform-specific posts with hashtag strategy |
| Email Copywriter | Marketing emails with conversion focus |
| SEO Content Optimizer | Keyword integration and meta descriptions |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `DEFAULT_MODEL` | Default LLM model | `anthropic/claude-3.5-sonnet` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `SECRET_KEY` | JWT signing key | Required |
| `ADMIN_PASSWORD` | Admin dashboard password | Required |
| `ACCESS_TOKEN_EXPIRE_HOURS` | JWT token expiry in hours | `8` |
| `API_KEY_ENCRYPTION_KEY` | Fernet key for API key encryption | Auto-generated |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./data/chroma` |
| `UPLOAD_DIR` | File upload path | `./data/uploads` |
| `MAX_FILE_SIZE_MB` | Max upload size | `50` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FORMAT` | Log format (`text` or `json`) | `text` |
| `BACKUP_DIR` | Backup storage directory | `/backups` |
| `BACKUP_RETENTION_DAYS` | Days to keep backups | `7` |

See [.env.example](.env.example) for all configuration options.

## Documentation

- [Product Requirements Document](ai-across-prd.md)
- [Development Roadmap](ROADMAP.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [High-Level Design](docs/HLD.md)
- [API Reference](http://localhost:8000/docs)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Backup & Restore](docs/BACKUP.md)
- [Changelog](CHANGELOG.md)

## Development Status

See [ROADMAP.md](ROADMAP.md) for development phases and [CHANGELOG.md](CHANGELOG.md) for version history.

**Current Status:** v1.0.0 — All phases complete, production-ready

| Phase | Status |
|-------|--------|
| Phase 1: Backend Foundation | ✅ Complete |
| Phase 2: File Processing & RAG | ✅ Complete |
| Phase 3: OpenRouter & Chat | ✅ Complete |
| Phase 4: Frontend - Assistant Management | ✅ Complete |
| Phase 5: Frontend - Chat Interface | ✅ Complete |
| Phase 6: Polish & QA | ✅ Complete |
| Phase 7: Admin Board | ✅ Complete |
| Phase 8: Production Deployment | ✅ Complete |
| Phase 9: Admin Dashboard Enhancement | ✅ Complete |
| Phase 10: Security Hardening & User Auth | ✅ Complete |

### v1.0.0 (Phase 8 Complete)

- **Structured Logging** - JSON logs with `X-Request-ID` correlation, contextvars for `request_id`/`user_id`/`conversation_id`/`assistant_id`
- **Self-Healing Ingestion** - Stuck file processing auto-detected and retried with exponential backoff (5→15→45 min), fails gracefully after 3 attempts
- **Backup & Restore** - `backup.sh`/`restore.sh` scripts with auto-rotation, full runbook in `docs/BACKUP.md`
- **Message Feedback** - ThumbsUp/ThumbsDown on assistant messages with optional reason, persisted with model context
- **Workspace Isolation** - `workspace_id` on core tables (future-proofing for v1.1 client isolation)
- **RAG Guardrails** - Per-assistant configurable retrieval limits (max chunks, max context tokens)
- **CI Pipeline** - GitHub Actions with parallel backend + frontend quality gates

### Previous (v0.9.0)

- **Full Authentication** - All API endpoints require JWT authentication
- **Conversation Isolation** - Users see only their own conversations
- **Role-Based UI** - Admin-only assistant management
- **Security Headers** - CSP, HSTS, MIME validation, password policy

## License

Proprietary - MarketAcross

## Support

For issues and feature requests, contact the MarketAcross development team.
