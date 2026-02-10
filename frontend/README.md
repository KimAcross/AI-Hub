# AI-Across Frontend

React frontend application for AI-Across - a self-hosted AI content platform.

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.x | UI framework |
| TypeScript | 5.x | Type safety |
| Vite | 7.x | Build tool with HMR |
| TailwindCSS | 3.x | Utility-first styling |
| shadcn/ui | Latest | Accessible UI components |
| React Router | 7.x | Client-side routing |
| React Query | 5.x | Server state management |
| Zustand | 5.x | Client state management |
| React Hook Form | 7.x | Form handling |
| Zod | 3.x | Schema validation |
| Axios | 1.x | HTTP client |
| react-markdown | 10.x | Markdown rendering |
| rehype-highlight | 7.x | Code syntax highlighting |
| highlight.js | 11.x | Syntax highlighting themes |
| Playwright | Latest | E2E testing |

## Project Structure

```
src/
├── api/                    # API client and React Query hooks
│   ├── client.ts           # Axios instance with interceptors
│   └── hooks/              # Custom hooks for data fetching
│       ├── useAssistants.ts
│       └── useFiles.ts
├── components/             # React components
│   ├── ui/                 # shadcn/ui primitives
│   ├── layout/             # Layout components
│   │   ├── Sidebar.tsx
│   │   └── Header.tsx
│   ├── assistants/         # Assistant-specific components
│   │   ├── AssistantCard.tsx
│   │   ├── AssistantForm.tsx
│   │   └── AssistantList.tsx
│   └── files/              # File management components
│       ├── FileUploader.tsx
│       └── FileList.tsx
├── pages/                  # Route pages (lazy-loaded)
│   ├── dashboard.tsx
│   ├── assistants.tsx
│   ├── chat.tsx
│   └── settings.tsx
├── hooks/                  # Custom React hooks
│   ├── use-assistants.ts
│   ├── use-conversations.ts
│   ├── use-models.ts
│   ├── use-chat.ts
│   └── use-online-status.ts
├── stores/                 # Zustand stores
│   └── appStore.ts
├── lib/                    # Utility functions
│   └── utils.ts
├── types/                  # TypeScript type definitions
│   └── index.ts
├── App.tsx                 # Root component with routing
├── main.tsx                # Application entry point
└── index.css               # Global styles and Tailwind imports
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Linting

```bash
# Run ESLint
npm run lint
```

## Docker Development

The frontend is configured to run in Docker for development:

```bash
# From project root
docker-compose -f docker-compose.dev.yml up frontend
```

This provides:
- Hot Module Replacement (HMR)
- Volume mounting for live code updates
- Automatic connection to backend API

## Environment Variables

Create a `.env` file for local development:

```env
# API URL (defaults to localhost:8000)
VITE_API_URL=http://localhost:8000
```

## Component Library

This project uses [shadcn/ui](https://ui.shadcn.com/) for UI components. These are copied into `src/components/ui/` and can be customized.

### Adding Components

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add dialog
```

## State Management

### Server State (React Query)

Used for data that comes from the API:
- Assistants list and details
- Files and upload status
- Conversations and messages

### Client State (Zustand)

Used for UI state and preferences:
- Sidebar collapsed state
- Theme preference (dark/light/system)
- Language preference
- Streaming responses toggle
- Auto-save interval

## Performance Optimizations

The app implements several performance optimizations:

- **React.memo** - Components like `MessageBubble`, `CodeBlock`, and `AssistantCard` are memoized
- **Lazy Loading** - Route pages are lazy-loaded with `React.lazy()` and `Suspense`
- **Image Lazy Loading** - `LazyImage` component uses `IntersectionObserver`
- **Code Splitting** - Vite automatically splits bundles by route

## API Integration

API hooks are located in `src/api/hooks/`. Example usage:

```tsx
import { useAssistants, useCreateAssistant } from '@/api/hooks/useAssistants';

function AssistantList() {
  const { data: assistants, isLoading } = useAssistants();
  const createMutation = useCreateAssistant();

  const handleCreate = (data) => {
    createMutation.mutate(data);
  };

  // ...
}
```

## Styling

### Tailwind Configuration

Custom theme values are defined in `tailwind.config.js`:
- Colors based on design system
- Custom spacing and breakpoints
- Dark mode support via CSS variables

### CSS Variables

Theme colors use CSS variables for dark/light mode:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  /* ... */
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... */
}
```

## Testing

### Unit Tests (Vitest)

```bash
# Run unit tests
npm run test

# Run tests with coverage
npm run test:coverage
```

### End-to-End Tests (Playwright)

```bash
# Install Playwright browsers (first time)
npx playwright install

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run E2E tests in headed mode
npm run test:e2e:headed
```

E2E tests are located in the `e2e/` directory and cover:
- Dashboard navigation
- Assistant management (create, edit, delete)
- Settings page functionality

## Contributing

See the main project [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Related Documentation

- [Main README](../README.md)
- [Architecture](../docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)
- [Development Roadmap](../ROADMAP.md)
