import * as React from 'react'
import { MessageBubble } from './message-bubble'
import { StreamingMessage } from './streaming-message'
import { Skeleton } from '@/components/ui/skeleton'
import type { Message } from '@/types'

interface MessageListProps {
  messages: Message[]
  isLoading?: boolean
  streamingContent?: string
  isStreaming?: boolean
  onRegenerate?: (messageId: string) => void
  onEditMessage?: (messageId: string) => void
}

export function MessageList({
  messages,
  isLoading = false,
  streamingContent,
  isStreaming = false,
  onRegenerate,
  onEditMessage,
}: MessageListProps) {
  const messagesEndRef = React.useRef<HTMLDivElement>(null)
  const containerRef = React.useRef<HTMLDivElement>(null)
  const [autoScroll, setAutoScroll] = React.useState(true)

  // Auto-scroll to bottom when new messages arrive
  React.useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, streamingContent, autoScroll])

  // Detect user scroll to pause auto-scroll
  const handleScroll = () => {
    if (!containerRef.current) return

    const { scrollTop, scrollHeight, clientHeight } = containerRef.current
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100

    setAutoScroll(isNearBottom)
  }

  if (isLoading) {
    return (
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="h-8 w-8 rounded-full shrink-0" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-16 w-full" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <p className="text-lg font-medium">Start a conversation</p>
          <p className="text-sm">Send a message to begin chatting with the assistant</p>
        </div>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto"
      onScroll={handleScroll}
    >
      <div className="max-w-4xl mx-auto divide-y divide-border">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onRegenerate={
              message.role === 'assistant'
                ? () => onRegenerate?.(message.id)
                : undefined
            }
            onEdit={
              message.role === 'user'
                ? () => onEditMessage?.(message.id)
                : undefined
            }
          />
        ))}

        {isStreaming && streamingContent !== undefined && (
          <StreamingMessage content={streamingContent} />
        )}
      </div>

      <div ref={messagesEndRef} />
    </div>
  )
}
