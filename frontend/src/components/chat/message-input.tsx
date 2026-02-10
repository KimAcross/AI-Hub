import * as React from 'react'
import { Send, Square, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface MessageInputProps {
  onSend: (content: string) => void
  onStop?: () => void
  isLoading?: boolean
  disabled?: boolean
  placeholder?: string
}

export function MessageInput({
  onSend,
  onStop,
  isLoading = false,
  disabled = false,
  placeholder = "Type a message... (Ctrl+Enter to send)",
}: MessageInputProps) {
  const [content, setContent] = React.useState('')
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  React.useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    textarea.style.height = 'auto'
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`
  }, [content])

  // Focus on mount
  React.useEffect(() => {
    textareaRef.current?.focus()
  }, [])

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault()

    const trimmed = content.trim()
    if (!trimmed || isLoading || disabled) return

    onSend(trimmed)
    setContent('')

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl+Enter or Cmd+Enter to send
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleSubmit()
      return
    }

    // Enter without modifier inserts newline (default behavior)
  }

  return (
    <form onSubmit={handleSubmit} className="border-t bg-background p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex gap-2 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className={cn(
                "w-full resize-none rounded-lg border border-input bg-background px-4 py-3 pr-12",
                "text-sm placeholder:text-muted-foreground",
                "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                "disabled:cursor-not-allowed disabled:opacity-50",
                "min-h-[48px] max-h-[200px]"
              )}
            />
          </div>

          {isLoading ? (
            <Button
              type="button"
              variant="destructive"
              size="icon"
              className="h-12 w-12 shrink-0"
              onClick={onStop}
              title="Stop generating"
            >
              <Square className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              type="submit"
              size="icon"
              className="h-12 w-12 shrink-0"
              disabled={!content.trim() || disabled}
              title="Send message (Ctrl+Enter)"
            >
              {disabled ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>

        <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
          <span>Press Ctrl+Enter to send</span>
          <span>{content.length} characters</span>
        </div>
      </div>
    </form>
  )
}
