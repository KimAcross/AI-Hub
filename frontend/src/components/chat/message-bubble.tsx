import * as React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { Bot, User, Copy, Check, RefreshCw, Pencil, ThumbsDown, ThumbsUp } from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'
import { CodeBlock } from './code-block'
import type { Message, MessageFeedback } from '@/types'

interface MessageBubbleProps {
  message: Message
  isStreaming?: boolean
  onCopy?: () => void
  onRegenerate?: () => void
  onEdit?: () => void
  onFeedback?: (feedback: MessageFeedback) => void
  showActions?: boolean
}

export const MessageBubble = React.memo(function MessageBubble({
  message,
  isStreaming = false,
  onCopy,
  onRegenerate,
  onEdit,
  onFeedback,
  showActions = true,
}: MessageBubbleProps) {
  const [copied, setCopied] = React.useState(false)
  const isUser = message.role === 'user'

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    onCopy?.()
    setTimeout(() => setCopied(false), 2000)
  }

  const handlePositiveFeedback = () => {
    onFeedback?.({ feedback: 'positive' })
  }

  const handleNegativeFeedback = () => {
    const reason = window.prompt('Optional: why was this response unhelpful?') || undefined
    onFeedback?.({ feedback: 'negative', feedback_reason: reason })
  }

  return (
    <div
      className={cn(
        "group flex gap-3 py-4 px-4",
        isUser ? "bg-background" : "bg-muted/30"
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      <div className="flex-1 min-w-0 space-y-2">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm">
            {isUser ? 'You' : 'Assistant'}
          </span>
          {message.model && !isUser && (
            <span className="text-xs text-muted-foreground">
              {message.model.split('/').pop()}
            </span>
          )}
          <span className="text-xs text-muted-foreground">
            {formatDate(message.created_at)}
          </span>
        </div>

        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight]}
            components={{
              code({ className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '')
                const isInline = !match && !className

                if (isInline) {
                  return (
                    <code
                      className="px-1.5 py-0.5 rounded bg-muted font-mono text-sm"
                      {...props}
                    >
                      {children}
                    </code>
                  )
                }

                return (
                  <CodeBlock language={match?.[1]}>
                    {String(children).replace(/\n$/, '')}
                  </CodeBlock>
                )
              },
              pre({ children }) {
                return <>{children}</>
              },
              a({ href, children }) {
                return (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    {children}
                  </a>
                )
              },
              table({ children }) {
                return (
                  <div className="overflow-x-auto my-4">
                    <table className="min-w-full divide-y divide-border">
                      {children}
                    </table>
                  </div>
                )
              },
            }}
          >
            {message.content}
          </ReactMarkdown>

          {isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-foreground animate-pulse" />
          )}
        </div>

        {showActions && !isStreaming && (
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCopy}
              className="p-1.5 rounded hover:bg-muted transition-colors"
              title="Copy message"
            >
              {copied ? (
                <Check className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4 text-muted-foreground" />
              )}
            </button>

            {isUser && onEdit && (
              <button
                onClick={onEdit}
                className="p-1.5 rounded hover:bg-muted transition-colors"
                title="Edit message"
              >
                <Pencil className="h-4 w-4 text-muted-foreground" />
              </button>
            )}

            {!isUser && onRegenerate && (
              <button
                onClick={onRegenerate}
                className="p-1.5 rounded hover:bg-muted transition-colors"
                title="Regenerate response"
              >
                <RefreshCw className="h-4 w-4 text-muted-foreground" />
              </button>
            )}

            {!isUser && onFeedback && (
              <>
                <button
                  onClick={handlePositiveFeedback}
                  className="p-1.5 rounded hover:bg-muted transition-colors"
                  title="Helpful response"
                >
                  <ThumbsUp
                    className={cn(
                      'h-4 w-4',
                      message.feedback === 'positive' ? 'text-green-600' : 'text-muted-foreground'
                    )}
                  />
                </button>
                <button
                  onClick={handleNegativeFeedback}
                  className="p-1.5 rounded hover:bg-muted transition-colors"
                  title="Unhelpful response"
                >
                  <ThumbsDown
                    className={cn(
                      'h-4 w-4',
                      message.feedback === 'negative' ? 'text-red-600' : 'text-muted-foreground'
                    )}
                  />
                </button>
              </>
            )}
          </div>
        )}

        {message.tokens_used && !isUser && (
          <div className="text-xs text-muted-foreground">
            {message.tokens_used.total_tokens?.toLocaleString()} tokens
          </div>
        )}
      </div>
    </div>
  )
})
