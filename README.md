# AI-Across

> Your content team's AI command center

AI-Across is a self-hosted AI content platform designed for content agency operations. Create, manage, and deploy specialized AI assistants with custom instructions and knowledge bases, while maintaining the flexibility to switch between 50+ LLM providers through OpenRouter integration.

## Features

- **Specialized AI Assistants** - Pre-configured personas for press releases, article rewriting, blog posts, social media, and more
- **Knowledge Base (RAG)** - Upload PDFs, DOCX, TXT, and Markdown files to give assistants contextual knowledge
- **Model Agnostic** - Switch between Claude, GPT-4, Gemini, Llama, and 50+ models via OpenRouter
- **Secure Multi-User** - JWT authentication, role-based access control (Admin/Manager/User), conversation isolation
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

See [.env.example](.env.example) for all configuration options.

## Documentation

- [Product Requirements Document](ai-across-prd.md)
- [Development Roadmap](ROADMAP.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [High-Level Design](docs/HLD.md)
- [API Reference](http://localhost:8000/docs)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Changelog](CHANGELOG.md)

## Development Status

See [ROADMAP.md](ROADMAP.md) for development phases and [CHANGELOG.md](CHANGELOG.md) for version history.

**Current Status:** Phase 10 Complete (v0.9.0 - Security Hardening & User Authentication)

| Phase | Status |
|-------|--------|
| Phase 1: Backend Foundation | ✅ Complete |
| Phase 2: File Processing & RAG | ✅ Complete |
| Phase 3: OpenRouter & Chat | ✅ Complete |
| Phase 4: Frontend - Assistant Management | ✅ Complete |
| Phase 5: Frontend - Chat Interface | ✅ Complete |
| Phase 6: Polish & QA | ✅ Complete |
| Phase 7: Admin Board | ✅ Complete |
| Phase 8: Production Deployment | 🔄 In Progress (40%) |
| Phase 9: Admin Dashboard Enhancement | ✅ Complete |
| Phase 10: Security Hardening & User Auth | ✅ Complete |

### Recent Updates (v0.9.0)

- **Full Authentication** - All API endpoints now require JWT authentication (no public access)
- **User Login** - User login page with email/password, auth guard on all routes
- **Conversation Isolation** - Users see only their own conversations, admins see all
- **Role-Based UI** - Admin-only assistant management, simplified user settings
- **Security Headers** - CSP, X-Frame-Options, HSTS, and more on all responses
- **MIME Validation** - File uploads validated with magic bytes, not just extension
- **Password Policy** - Strength requirements (uppercase, lowercase, digit, special char)
- **Quota Display** - Color-coded progress bars for user usage limits
- **Audit Export** - CSV/JSON export for audit logs

### Previous (v0.8.0)

- **User Management** - Multi-user support with roles (Admin, Manager, User)
- **API Key Management** - Multi-provider key management (OpenRouter, OpenAI, Anthropic, Google, Azure)
- **Usage Quotas** - Daily/monthly cost and token limits with alerts
- **Audit Logging** - Complete action tracking with old/new value comparison

## License

Proprietary - MarketAcross

## Support

For issues and feature requests, contact the MarketAcross development team.
