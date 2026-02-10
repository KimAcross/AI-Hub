import * as React from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface MessageEditDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialContent: string
  onSave: (content: string) => void
  isLoading?: boolean
}

export function MessageEditDialog({
  open,
  onOpenChange,
  initialContent,
  onSave,
  isLoading = false,
}: MessageEditDialogProps) {
  const [content, setContent] = React.useState(initialContent)
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)

  // Reset content when dialog opens
  React.useEffect(() => {
    if (open) {
      setContent(initialContent)
      // Focus textarea after dialog opens
      setTimeout(() => textareaRef.current?.focus(), 0)
    }
  }, [open, initialContent])

  // Auto-resize textarea
  React.useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    textarea.style.height = 'auto'
    textarea.style.height = `${Math.min(textarea.scrollHeight, 300)}px`
  }, [content])

  const handleSave = () => {
    const trimmed = content.trim()
    if (trimmed && trimmed !== initialContent) {
      onSave(trimmed)
    } else {
      onOpenChange(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl+Enter to save
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleSave()
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Message</DialogTitle>
        </DialogHeader>

        <div className="py-4">
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            className={cn(
              "w-full resize-none rounded-lg border border-input bg-background px-3 py-2",
              "text-sm placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
              "disabled:cursor-not-allowed disabled:opacity-50",
              "min-h-[100px] max-h-[300px]"
            )}
          />
          <p className="text-xs text-muted-foreground mt-2">
            Press Ctrl+Enter to save
          </p>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={isLoading || !content.trim()}
          >
            {isLoading ? 'Saving...' : 'Save & Regenerate'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
