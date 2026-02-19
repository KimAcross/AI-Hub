# Product Requirements Document (PRD)

## AI-Across
### By MarketAcross

**Version:** 1.0  
**Status:** Draft  
**Last Updated:** February 19, 2026  
**Document Owner:** MarketAcross Product Team

---

## 1. Executive Summary

> Implementation alignment note (February 18, 2026):
> - Assistant cards open chat directly with assistant context.
> - Assistant model defines initial model in assistant chat; global default model defines initial model in general chat.
> - Users can override model from chat dropdown before sending.

### 1.1 Product Vision
AI-Across is a production-ready, self-hosted AI content platform designed for MarketAcross's content agency operations. It enables content teams to create, manage, and deploy specialized AI assistants with custom instructions and knowledge bases, while maintaining the flexibility to switch between any LLM provider through OpenRouter integration.

### 1.2 Problem Statement
Content agencies face several challenges with existing AI tools:
- **Fragmented workflows:** Teams use multiple AI tools without unified knowledge bases
- **No institutional knowledge:** Each conversation starts from scratch without brand guidelines, style guides, or reference materials
- **Model lock-in:** Tied to a single AI provider, unable to leverage strengths of different models
- **No customization:** Generic AI assistants don't understand specific content types (press releases, article rewrites, etc.)
- **Lack of control:** Third-party platforms don't offer the security and customization agencies need

### 1.3 Solution
AI-Across provides:
- Centralized platform for creating specialized content assistants
- RAG-powered knowledge bases with PDF, DOCX, and TXT support
- Model-agnostic architecture via OpenRouter (50+ models)
- Production-ready deployment for team use
- Full data ownership and privacy

### 1.4 Success Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Assistant creation time | < 5 minutes | Time from start to first chat |
| Knowledge base indexing | < 2 minutes for 50 pages | Processing time |
| Response latency | < 3 seconds (excluding LLM) | API response time |
| Team adoption | 80% of content team | Weekly active users |
| Content output increase | 40% improvement | Content pieces per week |

---

## 2. Product Overview

### 2.1 Product Name
**AI-Across** — "AI Across all your content needs"

### 2.2 Tagline
*"Your content team's AI command center"*

### 2.3 Target Users

#### Primary Users
| Role | Needs | Usage Pattern |
|------|-------|---------------|
| Content Writers | Quick access to specialized assistants, brand-consistent output | Daily, 4-6 hours |
| Content Editors | Review, refine, and ensure quality | Daily, 2-3 hours |
| Content Managers | Create/configure assistants, manage knowledge bases | Weekly, 1-2 hours |

#### Secondary Users
| Role | Needs | Usage Pattern |
|------|-------|---------------|
| Account Managers | Generate client-specific content | As needed |
| Leadership | Overview of platform usage, ROI tracking | Monthly |

### 2.4 Core Value Propositions
1. **Specialized Assistants:** Pre-configured AI personas for specific content types
2. **Institutional Memory:** Knowledge bases that persist across all conversations
3. **Model Freedom:** Switch between GPT-4, Claude, Gemini, Llama, and 50+ models instantly
4. **Team Collaboration:** Shared assistants and knowledge bases across the organization
5. **Data Ownership:** Self-hosted, your data never leaves your infrastructure

---

## 3. Feature Specifications

### 3.1 Assistant Management

#### 3.1.1 Create Assistant
**Description:** Users can create new AI assistants with custom configurations.

**Fields:**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| Name | String | Yes | 3-50 characters |
| Description | String | Yes | 10-500 characters |
| Instructions | Text | Yes | 100-10,000 characters (system prompt) |
| Avatar | Image | No | PNG/JPG, max 1MB, 256x256px |
| Default Model | Select | Yes | From OpenRouter model list |
| Temperature | Slider | No | 0.0-2.0, default 0.7 |
| Max Tokens | Number | No | 100-128,000, default 4,096 |

**User Stories:**
- As a Content Manager, I want to create a "Press Release Writer" assistant with specific formatting instructions so my team produces consistent PR content.
- As a Content Manager, I want to set a default model for each assistant but allow users to switch models during conversations.

**Acceptance Criteria:**
- [ ] Form validates all required fields before submission
- [ ] Assistant is immediately available after creation
- [ ] Instructions support markdown formatting
- [ ] Preview mode shows how the assistant will appear to users

#### 3.1.2 Edit Assistant
**Description:** Modify existing assistant configurations.

**Behavior:**
- All fields editable except ID
- Changes take effect immediately
- Active conversations continue with previous settings until refreshed
- Version history tracked (last 10 versions)

#### 3.1.3 Delete Assistant
**Description:** Remove an assistant from the platform.

**Behavior:**
- Soft delete (archived, recoverable for 30 days)
- Associated conversations preserved but marked as orphaned
- Knowledge base files preserved (can be reassigned)
- Confirmation modal required

#### 3.1.4 Assistant Templates
**Description:** Pre-built assistant configurations for common content types.

**Default Templates:**
| Template | Description | Key Instructions |
|----------|-------------|------------------|
| Press Release Writer | Generates professional press releases | AP style, inverted pyramid, quote formatting |
| Article Rewriter | Rewrites articles while preserving meaning | Plagiarism-free, tone matching, SEO optimization |
| Blog Post Creator | Creates engaging blog content | Hook writing, subheadings, CTA inclusion |
| Social Media Manager | Crafts platform-specific posts | Character limits, hashtag strategy, engagement hooks |
| Email Copywriter | Writes marketing emails | Subject lines, preview text, conversion focus |
| SEO Content Optimizer | Optimizes content for search | Keyword integration, meta descriptions, headers |

---

### 3.2 Knowledge Base System

#### 3.2.1 File Upload
**Description:** Upload documents to create a searchable knowledge base for each assistant.

**Supported Formats:**
| Format | Extension | Max Size | Processing |
|--------|-----------|----------|------------|
| PDF | .pdf | 50MB | Text extraction, OCR for scanned |
| Word | .docx | 25MB | Full text extraction |
| Text | .txt | 10MB | Direct indexing |
| Markdown | .md | 10MB | Rendered then indexed |

**Upload Interface:**
- Drag-and-drop zone
- Multi-file upload (up to 10 files at once)
- Progress indicator per file
- Processing status (Uploading → Processing → Indexing → Ready)

#### 3.2.2 RAG Pipeline
**Description:** Retrieval-Augmented Generation system for injecting relevant knowledge into conversations.

**Technical Specifications:**
| Component | Implementation | Details |
|-----------|---------------|---------|
| Chunking | Recursive text splitter | 512 tokens, 50 token overlap |
| Embedding Model | OpenAI text-embedding-3-small | Via OpenRouter, 1536 dimensions |
| Vector Store | ChromaDB (local) / Qdrant (production) | Cosine similarity |
| Retrieval | Top-K similarity search | K=5, threshold 0.7 |
| Context Injection | System prompt prepend | Retrieved chunks added before user message |

**RAG Prompt Template:**
```
You are {assistant_name}.

{assistant_instructions}

Use the following reference materials to inform your response. Only use information from these materials when relevant:

---
{retrieved_chunks}
---

If the reference materials don't contain relevant information, rely on your general knowledge but indicate this to the user.
```

#### 3.2.3 Knowledge Base Management
**Features:**
- View all files per assistant
- File metadata (name, size, upload date, chunk count)
- Delete individual files
- Re-process files (if processing failed)
- Search within knowledge base
- Preview indexed chunks

---

### 3.3 Chat Interface

#### 3.3.1 Chat Window
**Description:** Primary interface for interacting with assistants.

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [Assistant Avatar] Assistant Name          [Model ▼]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Assistant: Hello! I'm your Press Release        │   │
│  │ Writer. What announcement would you like to     │   │
│  │ create today?                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ User: We need a PR for our new product launch   │   │
│  │ next week...                                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Assistant: I'd be happy to help craft that      │   │
│  │ press release! Let me ask a few questions...    │   │
│  │                                                 │   │
│  │ [Copy] [Regenerate]                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐ [Send] │
│ │ Type your message...                        │        │
│ └─────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

**Features:**
| Feature | Description |
|---------|-------------|
| Streaming responses | Real-time token display |
| Markdown rendering | Headers, lists, code blocks, tables |
| Code syntax highlighting | All major languages |
| Copy message | One-click copy to clipboard |
| Regenerate | Re-run last request with same/different model |
| Stop generation | Cancel in-progress responses |
| Message editing | Edit and resubmit user messages |

#### 3.3.2 Model Selector
**Description:** Dropdown to switch between AI models mid-conversation.

**Behavior:**
- Displays current model with provider icon
- Grouped by provider (Anthropic, OpenAI, Google, Meta, etc.)
- Shows model capabilities (context window, vision support)
- Switching models preserves conversation history
- Assistant instructions and knowledge base remain unchanged

**Default Model:** `anthropic/claude-3.5-sonnet` (via OpenRouter)

**Model Display Format:**
```
┌─────────────────────────────────┐
│ 🟣 Claude 3.5 Sonnet        ▼  │
├─────────────────────────────────┤
│ ANTHROPIC                       │
│   🟣 Claude 3.5 Sonnet    ✓    │
│   🟣 Claude 3 Opus             │
│   🟣 Claude 3 Haiku            │
│ OPENAI                          │
│   🟢 GPT-4o                    │
│   🟢 GPT-4 Turbo               │
│   🟢 GPT-3.5 Turbo             │
│ GOOGLE                          │
│   🔵 Gemini 1.5 Pro            │
│   🔵 Gemini 1.5 Flash          │
│ META                            │
│   🟠 Llama 3.1 405B            │
│   🟠 Llama 3.1 70B             │
│ MOONSHOT                        │
│   ⚪ Kimi K2                    │
└─────────────────────────────────┘
```

#### 3.3.3 Conversation Management
**Features:**
| Feature | Description |
|---------|-------------|
| Auto-save | Conversations saved automatically |
| Conversation list | Sidebar with recent conversations |
| Search conversations | Full-text search across all chats |
| Rename conversation | Custom titles for organization |
| Delete conversation | Remove with confirmation |
| Export conversation | Download as Markdown or JSON |

---

### 3.4 Dashboard

#### 3.4.1 Main Dashboard
**Description:** Landing page after login showing overview and quick actions.

**Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│ AI-Across                                    [Settings] [User]  │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                   │
│ ASSISTANTS   │  Welcome back, [User]!                           │
│              │                                                   │
│ + New        │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│              │  │ 📝          │ │ 📰          │ │ ✍️          ││
│ 📝 Press     │  │ Press       │ │ Article     │ │ Blog Post   ││
│    Release   │  │ Release     │ │ Rewriter    │ │ Creator     ││
│              │  │ Writer      │ │             │ │             ││
│ 📰 Article   │  │ [Start Chat]│ │ [Start Chat]│ │ [Start Chat]││
│    Rewriter  │  └─────────────┘ └─────────────┘ └─────────────┘│
│              │                                                   │
│ ✍️ Blog Post │  RECENT CONVERSATIONS                            │
│    Creator   │  ┌───────────────────────────────────────────────┤
│              │  │ "Q1 Product Launch PR" - Press Release - 2h   │
│ 📱 Social    │  │ "Blog: AI Trends 2026" - Blog Post - 5h       │
│    Media     │  │ "Rewrite: TechCrunch Article" - Rewriter - 1d │
│              │  └───────────────────────────────────────────────┤
│ SETTINGS     │                                                   │
│              │  QUICK STATS                                      │
│ ⚙️ Settings  │  Conversations: 47 | Messages: 312 | This Week   │
│              │                                                   │
└──────────────┴──────────────────────────────────────────────────┘
```

---

### 3.5 Settings

#### 3.5.1 API Configuration
| Setting | Description | Default |
|---------|-------------|---------|
| OpenRouter API Key | Required for LLM access | None (must configure) |
| Default Model | Fallback model for new assistants | claude-3.5-sonnet |
| Embedding Model | Model for knowledge base embeddings | text-embedding-3-small |

#### 3.5.2 Application Settings
| Setting | Description | Default |
|---------|-------------|---------|
| Theme | Light / Dark / System | System |
| Language | Interface language | English |
| Response Streaming | Enable/disable streaming | Enabled |
| Auto-save Interval | Conversation save frequency | 30 seconds |

#### 3.5.3 Password Protection (Phase 7)
| Setting | Description |
|---------|-------------|
| Enable Password | Toggle password protection |
| Set Password | Configure access password |
| Session Duration | Auto-logout after inactivity (1h, 4h, 24h, Never) |

---

## 4. Technical Architecture

### 4.1 System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│                    React + Vite + Tailwind                       │
│              ┌─────────────────────────────────┐                │
│              │   Components:                    │                │
│              │   • AssistantManager            │                │
│              │   • ChatInterface               │                │
│              │   • KnowledgeBaseUploader       │                │
│              │   • ModelSelector               │                │
│              │   • ConversationHistory         │                │
│              └─────────────────────────────────┘                │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API + WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│                    Python + FastAPI                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ Assistants  │ │    Chat     │ │    Files    │               │
│  │   Router    │ │   Router    │ │   Router    │               │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘               │
│         │               │               │                       │
│  ┌──────▼───────────────▼───────────────▼──────┐               │
│  │              Service Layer                   │               │
│  │  • AssistantService                         │               │
│  │  • ChatService (streaming)                  │               │
│  │  • RAGService (retrieval)                   │               │
│  │  • FileProcessorService                     │               │
│  │  • OpenRouterService                        │               │
│  └──────┬───────────────┬───────────────┬──────┘               │
└─────────┼───────────────┼───────────────┼───────────────────────┘
          │               │               │
          ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │   ChromaDB   │ │  OpenRouter  │
│              │ │   (Vectors)  │ │     API      │
│ • Assistants │ │              │ │              │
│ • Convos     │ │ • Embeddings │ │ • 50+ Models │
│ • Files meta │ │ • Chunks     │ │ • Streaming  │
│ • Users      │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

### 4.2 Technology Stack

| Layer | Technology | Version | Justification |
|-------|------------|---------|---------------|
| **Frontend** | React | 18.x | Industry standard, large ecosystem |
| | Vite | 5.x | Fast builds, HMR |
| | Tailwind CSS | 3.x | Utility-first, rapid styling |
| | shadcn/ui | Latest | Beautiful, accessible components |
| | React Query | 5.x | Server state management |
| | Zustand | 4.x | Client state management |
| **Backend** | Python | 3.11+ | ML ecosystem, async support |
| | FastAPI | 0.100+ | Modern, fast, auto-docs |
| | SQLAlchemy | 2.x | ORM with async support |
| | Pydantic | 2.x | Data validation |
| | LangChain | 0.1+ | RAG pipeline utilities |
| **Databases** | PostgreSQL | 15+ | Reliable, feature-rich |
| | ChromaDB | 0.4+ | Simple vector store, local-first |
| **Infrastructure** | Docker | 24+ | Containerization |
| | Docker Compose | 2.x | Multi-container orchestration |
| | Nginx | 1.25+ | Reverse proxy (production) |

### 4.3 API Specifications

#### 4.3.1 Assistants API

**Create Assistant**
```
POST /api/v1/assistants
Content-Type: application/json

{
  "name": "Press Release Writer",
  "description": "Creates professional press releases in AP style",
  "instructions": "You are an expert PR writer...",
  "model": "anthropic/claude-3.5-sonnet",
  "temperature": 0.7,
  "max_tokens": 4096
}

Response: 201 Created
{
  "id": "ast_abc123",
  "name": "Press Release Writer",
  "description": "Creates professional press releases in AP style",
  "instructions": "You are an expert PR writer...",
  "model": "anthropic/claude-3.5-sonnet",
  "temperature": 0.7,
  "max_tokens": 4096,
  "file_count": 0,
  "created_at": "2026-01-20T10:30:00Z",
  "updated_at": "2026-01-20T10:30:00Z"
}
```

**List Assistants**
```
GET /api/v1/assistants

Response: 200 OK
{
  "assistants": [...],
  "total": 5
}
```

**Get Assistant**
```
GET /api/v1/assistants/{assistant_id}

Response: 200 OK
{
  "id": "ast_abc123",
  ...
}
```

**Update Assistant**
```
PATCH /api/v1/assistants/{assistant_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "instructions": "Updated instructions..."
}

Response: 200 OK
```

**Delete Assistant**
```
DELETE /api/v1/assistants/{assistant_id}

Response: 204 No Content
```

#### 4.3.2 Files API

**Upload File**
```
POST /api/v1/assistants/{assistant_id}/files
Content-Type: multipart/form-data

file: [binary]

Response: 202 Accepted
{
  "id": "file_xyz789",
  "filename": "brand_guidelines.pdf",
  "status": "processing",
  "assistant_id": "ast_abc123"
}
```

**List Files**
```
GET /api/v1/assistants/{assistant_id}/files

Response: 200 OK
{
  "files": [
    {
      "id": "file_xyz789",
      "filename": "brand_guidelines.pdf",
      "file_type": "pdf",
      "size_bytes": 2048576,
      "chunk_count": 45,
      "status": "ready",
      "created_at": "2026-01-20T10:35:00Z"
    }
  ]
}
```

**Delete File**
```
DELETE /api/v1/assistants/{assistant_id}/files/{file_id}

Response: 204 No Content
```

#### 4.3.3 Chat API

**Create Conversation**
```
POST /api/v1/conversations
Content-Type: application/json

{
  "assistant_id": "ast_abc123"
}

Response: 201 Created
{
  "id": "conv_def456",
  "assistant_id": "ast_abc123",
  "title": "New Conversation",
  "created_at": "2026-01-20T11:00:00Z"
}
```

**Send Message (Streaming)**
```
POST /api/v1/conversations/{conversation_id}/messages
Content-Type: application/json

{
  "content": "Write a press release about our new AI product",
  "model": "anthropic/claude-3.5-sonnet"  // Optional override
}

Response: 200 OK (text/event-stream)
data: {"type": "start", "message_id": "msg_123"}
data: {"type": "chunk", "content": "FOR"}
data: {"type": "chunk", "content": " IMMEDIATE"}
data: {"type": "chunk", "content": " RELEASE"}
...
data: {"type": "done", "usage": {"prompt_tokens": 150, "completion_tokens": 450}}
```

**Get Conversation History**
```
GET /api/v1/conversations/{conversation_id}

Response: 200 OK
{
  "id": "conv_def456",
  "assistant_id": "ast_abc123",
  "title": "Q1 Product Launch PR",
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "Write a press release...",
      "created_at": "2026-01-20T11:00:00Z"
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "FOR IMMEDIATE RELEASE...",
      "model": "anthropic/claude-3.5-sonnet",
      "created_at": "2026-01-20T11:00:05Z"
    }
  ]
}
```

#### 4.3.4 Models API

**List Available Models**
```
GET /api/v1/models

Response: 200 OK
{
  "models": [
    {
      "id": "anthropic/claude-3.5-sonnet",
      "name": "Claude 3.5 Sonnet",
      "provider": "Anthropic",
      "context_length": 200000,
      "supports_vision": true,
      "pricing": {
        "prompt": 0.003,
        "completion": 0.015
      }
    },
    ...
  ]
}
```

### 4.4 Database Schema

```sql
-- Assistants table
CREATE TABLE assistants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    description VARCHAR(500) NOT NULL,
    instructions TEXT NOT NULL,
    model VARCHAR(100) NOT NULL DEFAULT 'anthropic/claude-3.5-sonnet',
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 4096,
    avatar_url VARCHAR(500),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge base files table
CREATE TABLE knowledge_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID REFERENCES assistants(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    size_bytes BIGINT NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'processing',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID REFERENCES assistants(id) ON DELETE SET NULL,
    title VARCHAR(200) DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    model VARCHAR(100),
    tokens_used JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Settings table (key-value store)
CREATE TABLE settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_files_assistant ON knowledge_files(assistant_id);
CREATE INDEX idx_conversations_assistant ON conversations(assistant_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at);
```

---

## 5. User Interface Specifications

### 5.1 Design System

#### 5.1.1 Color Palette
| Name | Hex | Usage |
|------|-----|-------|
| Primary | #6366F1 | Buttons, links, accents |
| Primary Dark | #4F46E5 | Hover states |
| Secondary | #8B5CF6 | Secondary actions |
| Success | #10B981 | Success states, online |
| Warning | #F59E0B | Warnings, processing |
| Error | #EF4444 | Errors, delete actions |
| Background | #0F172A | Dark mode background |
| Surface | #1E293B | Cards, elevated surfaces |
| Text Primary | #F8FAFC | Primary text (dark mode) |
| Text Secondary | #94A3B8 | Secondary text |
| Border | #334155 | Borders, dividers |

#### 5.1.2 Typography
| Element | Font | Size | Weight |
|---------|------|------|--------|
| H1 | Inter | 32px | 700 |
| H2 | Inter | 24px | 600 |
| H3 | Inter | 20px | 600 |
| Body | Inter | 16px | 400 |
| Small | Inter | 14px | 400 |
| Code | JetBrains Mono | 14px | 400 |

#### 5.1.3 Component Library
Using **shadcn/ui** for all components:
- Button (primary, secondary, ghost, destructive)
- Input, Textarea
- Select, Dropdown
- Dialog, Modal
- Card
- Avatar
- Badge
- Tooltip
- Toast notifications
- Skeleton loaders

### 5.2 Responsive Breakpoints
| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, bottom nav |
| Tablet | 640px - 1024px | Collapsible sidebar |
| Desktop | > 1024px | Full sidebar, multi-column |

### 5.3 Accessibility Requirements
- WCAG 2.1 Level AA compliance
- Keyboard navigation support
- Screen reader compatibility
- Minimum contrast ratio 4.5:1
- Focus indicators on all interactive elements

---

## 6. Development Phases

### Phase 1: Backend Foundation (Week 1)
**Deliverables:**
- [ ] Project scaffolding (FastAPI + PostgreSQL)
- [ ] Database models and migrations
- [ ] Assistant CRUD API endpoints
- [ ] Basic configuration management
- [ ] API documentation (Swagger)

**Success Criteria:**
- All assistant endpoints functional
- Database properly initialized
- API docs accessible at /docs

---

### Phase 2: File Processing & RAG (Week 2)
**Deliverables:**
- [ ] File upload endpoint
- [ ] PDF, DOCX, TXT processors
- [ ] Text chunking pipeline
- [ ] ChromaDB integration
- [ ] Embedding generation
- [ ] Retrieval service

**Success Criteria:**
- Files upload and process successfully
- Embeddings stored in ChromaDB
- Retrieval returns relevant chunks

---

### Phase 3: OpenRouter & Chat (Week 3)
**Deliverables:**
- [ ] OpenRouter service integration
- [ ] Model listing endpoint
- [ ] Chat completion with streaming
- [ ] RAG context injection
- [ ] Conversation persistence

**Success Criteria:**
- Chat works with Claude 3.5 Sonnet
- Model switching works
- Streaming responses display correctly
- Knowledge base context included

---

### Phase 4: Frontend - Assistant Management (Week 4)
**Deliverables:**
- [ ] React project setup
- [ ] Sidebar navigation
- [ ] Assistant list view
- [ ] Create assistant form
- [ ] Edit assistant form
- [ ] Delete assistant confirmation
- [ ] File upload interface

**Success Criteria:**
- Full assistant CRUD from UI
- File upload with progress
- Responsive design

---

### Phase 5: Frontend - Chat Interface (Week 5)
**Deliverables:**
- [ ] Chat window component
- [ ] Message rendering (markdown)
- [ ] Streaming response display
- [ ] Model selector dropdown
- [ ] Conversation sidebar
- [ ] Copy/regenerate actions

**Success Criteria:**
- Full chat functionality
- Model switching in-conversation
- Conversation history works

---

### Phase 6: Polish & QA (Week 6)
**Deliverables:**
- [ ] Error handling throughout
- [ ] Loading states and skeletons
- [ ] Toast notifications
- [ ] Settings page
- [ ] Dark/light theme
- [ ] Performance optimization
- [ ] Bug fixes

**Success Criteria:**
- No critical bugs
- < 3s response time
- Smooth UX throughout

---

### Phase 7: Auth & Deployment (Week 7)
**Deliverables:**
- [ ] Password protection system
- [ ] Session management
- [ ] Docker configuration
- [ ] Docker Compose setup
- [ ] Nginx configuration
- [ ] VPS deployment guide
- [ ] Backup/restore procedures

**Success Criteria:**
- Secure password protection
- One-command deployment
- Production-ready

---

## 7. Security Considerations

### 7.1 Data Security
| Concern | Mitigation |
|---------|------------|
| API Key exposure | Stored encrypted in database, never sent to frontend |
| File uploads | Validated file types, size limits, virus scanning (future) |
| SQL injection | Parameterized queries via SQLAlchemy |
| XSS | React auto-escaping, CSP headers |

### 7.2 Authentication (Phase 7)
- Bcrypt password hashing (cost factor 12)
- JWT tokens with 24h expiry
- Secure HTTP-only cookies
- Rate limiting on auth endpoints

### 7.3 Infrastructure Security
- HTTPS only (TLS 1.3)
- Nginx reverse proxy
- Docker network isolation
- Regular security updates

---

## 8. Future Roadmap (Post-MVP)

> **Scope note:** AI-Across is an internal MarketAcross tool, not a SaaS product. Features below serve the internal content team only.

> Multi-user accounts, roles, usage analytics, cost tracking, and quotas were completed in Phases 9–10 (v0.8–v0.9).

### Version 1.1 — Team Productivity
- [ ] Conversation sharing (shareable links with expiry)
- [ ] Conversation folders and tags
- [ ] Smart search across all conversations
- [ ] Direct provider API routing (Anthropic, Google, OpenAI direct — OpenRouter fallback)

### Version 1.2 — Admin Power Features
- [ ] Custom assistant templates (save your own)
- [ ] Assistant cloning
- [ ] Content quality scoring
- [ ] Brand voice consistency checker

### Version 1.3 — Integrations
- [ ] Telegram integration (bot for queries/notifications)

---

## 9. Appendix

### 9.1 OpenRouter Model IDs
```
anthropic/claude-3.5-sonnet (DEFAULT)
anthropic/claude-3-opus
anthropic/claude-3-haiku
openai/gpt-4o
openai/gpt-4-turbo
openai/gpt-3.5-turbo
google/gemini-1.5-pro
google/gemini-1.5-flash
meta-llama/llama-3.1-405b-instruct
meta-llama/llama-3.1-70b-instruct
mistralai/mistral-large
moonshot/kimi-k2
```

### 9.2 Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/aiacross

# OpenRouter
OPENROUTER_API_KEY=sk-or-...
DEFAULT_MODEL=anthropic/claude-3.5-sonnet

# Embeddings
EMBEDDING_MODEL=text-embedding-3-small

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma

# File Storage
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE_MB=50

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_HOURS=24

# App
APP_NAME=AI-Across
APP_ENV=development
DEBUG=true
```

### 9.3 Glossary
| Term | Definition |
|------|------------|
| Assistant | A configured AI persona with specific instructions and knowledge |
| Knowledge Base | Collection of documents used for RAG retrieval |
| RAG | Retrieval-Augmented Generation - injecting relevant context into prompts |
| Chunking | Splitting documents into smaller pieces for embedding |
| Embedding | Vector representation of text for similarity search |
| OpenRouter | API gateway providing access to multiple LLM providers |

---

## 10. Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | | | |
| Tech Lead | | | |
| Design Lead | | | |
| QA Lead | | | |

---

*Document Version History:*
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-20 | AI-Across Team | Initial PRD |
