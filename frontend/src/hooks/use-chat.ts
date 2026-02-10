import * as React from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { conversationsApi } from '@/lib/api'
import { conversationKeys } from './use-conversations'
import type { Message } from '@/types'
import toast from 'react-hot-toast'

interface UseChatOptions {
  conversationId: string
  model: string
  onMessageComplete?: (message: Message) => void
}

interface UseChatReturn {
  sendMessage: (content: string) => Promise<void>
  stopGeneration: () => void
  isStreaming: boolean
  streamingContent: string
  error: Error | null
}

export function useChat({
  conversationId,
  model,
  onMessageComplete,
}: UseChatOptions): UseChatReturn {
  const queryClient = useQueryClient()
  const [isStreaming, setIsStreaming] = React.useState(false)
  const [streamingContent, setStreamingContent] = React.useState('')
  const [error, setError] = React.useState<Error | null>(null)
  const abortControllerRef = React.useRef<AbortController | null>(null)

  const sendMessage = React.useCallback(
    async (content: string) => {
      if (!conversationId || isStreaming) return

      setError(null)
      setStreamingContent('')
      setIsStreaming(true)

      // Create new AbortController for this request
      abortControllerRef.current = new AbortController()

      try {
        const finalMessage = await conversationsApi.sendMessage(
          conversationId,
          { content, model },
          (chunk: string) => {
            setStreamingContent((prev) => prev + chunk)
          }
        )

        // Invalidate the conversation query to refetch messages
        queryClient.invalidateQueries({
          queryKey: conversationKeys.detail(conversationId),
        })

        onMessageComplete?.(finalMessage)
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          // User stopped generation, not an error
          return
        }

        const error = err instanceof Error ? err : new Error('Failed to send message')
        setError(error)
        toast.error(error.message)
      } finally {
        setIsStreaming(false)
        setStreamingContent('')
        abortControllerRef.current = null
      }
    },
    [conversationId, model, isStreaming, queryClient, onMessageComplete]
  )

  const stopGeneration = React.useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setIsStreaming(false)
      setStreamingContent('')
    }
  }, [])

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  return {
    sendMessage,
    stopGeneration,
    isStreaming,
    streamingContent,
    error,
  }
}
