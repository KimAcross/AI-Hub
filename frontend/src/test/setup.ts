import '@testing-library/jest-dom'
import { afterEach, beforeAll, afterAll } from 'vitest'
import { cleanup } from '@testing-library/react'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

// Mock handlers for API requests
export const handlers = [
  // Settings API
  http.get('/api/v1/settings', () => {
    return HttpResponse.json({
      openrouter_api_key_set: false,
      default_model: 'anthropic/claude-3.5-sonnet',
      embedding_model: 'text-embedding-3-small',
      max_file_size_mb: 50,
    })
  }),

  // Models API
  http.get('/api/v1/models', () => {
    return HttpResponse.json([
      {
        id: 'anthropic/claude-3.5-sonnet',
        name: 'Claude 3.5 Sonnet',
        description: 'Fast and capable model',
        context_length: 200000,
        pricing: { prompt: 0.003, completion: 0.015 },
      },
      {
        id: 'anthropic/claude-3-haiku-20240307',
        name: 'Claude 3 Haiku',
        description: 'Fast and affordable model',
        context_length: 200000,
        pricing: { prompt: 0.00025, completion: 0.00125 },
      },
    ])
  }),

  // Assistants API
  http.get('/api/v1/assistants', () => {
    return HttpResponse.json([])
  }),

  http.get('/api/v1/assistants/templates', () => {
    return HttpResponse.json([
      {
        id: 'general',
        name: 'General Assistant',
        description: 'A general-purpose assistant',
        instructions: 'Be helpful',
        model: 'anthropic/claude-3.5-sonnet',
        temperature: 0.7,
        max_tokens: 4096,
        category: 'general',
      },
    ])
  }),

  // Conversations API
  http.get('/api/v1/conversations', () => {
    return HttpResponse.json([])
  }),
]

// Setup MSW server
export const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  cleanup()
  server.resetHandlers()
})
afterAll(() => server.close())
