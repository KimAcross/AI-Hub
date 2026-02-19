import * as React from 'react'
import { Link } from 'react-router-dom'
import { Bot, FileText, MoreVertical, Trash2, RotateCcw, Edit } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn, formatDate } from '@/lib/utils'
import type { Assistant } from '@/types'

interface AssistantCardProps {
  assistant: Assistant
  onEdit?: () => void
  onDelete?: () => void
  onRestore?: () => void
}

export const AssistantCard = React.memo(function AssistantCard({ assistant, onEdit, onDelete, onRestore }: AssistantCardProps) {
  const [menuOpen, setMenuOpen] = React.useState(false)

  return (
    <Card className={cn(
      "group relative transition-shadow hover:shadow-md",
      assistant.is_deleted && "opacity-60"
    )}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <Link to={`/chat?assistant=${assistant.id}`} className="flex items-center gap-3 flex-1">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
              {assistant.avatar_url ? (
                <img
                  src={assistant.avatar_url}
                  alt={assistant.name}
                  className="h-10 w-10 rounded-full object-cover"
                />
              ) : (
                <Bot className="h-5 w-5 text-primary" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold truncate">{assistant.name}</h3>
              <p className="text-sm text-muted-foreground truncate">
                {assistant.model.split('/').pop()}
              </p>
            </div>
          </Link>

          <div className="relative">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              <MoreVertical className="h-4 w-4" />
            </Button>

            {menuOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setMenuOpen(false)}
                />
                <div className="absolute right-0 top-8 z-20 w-40 rounded-md border bg-popover p-1 shadow-md">
                  {!assistant.is_deleted ? (
                    <>
                      <button
                        className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-accent"
                        onClick={() => {
                          setMenuOpen(false)
                          onEdit?.()
                        }}
                      >
                        <Edit className="h-4 w-4" />
                        Edit
                      </button>
                      <button
                        className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-destructive hover:bg-accent"
                        onClick={() => {
                          setMenuOpen(false)
                          onDelete?.()
                        }}
                      >
                        <Trash2 className="h-4 w-4" />
                        Delete
                      </button>
                    </>
                  ) : (
                    <button
                      className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-accent"
                      onClick={() => {
                        setMenuOpen(false)
                        onRestore?.()
                      }}
                    >
                      <RotateCcw className="h-4 w-4" />
                      Restore
                    </button>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {assistant.description && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {assistant.description}
          </p>
        )}

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <FileText className="h-3.5 w-3.5" />
            <span>{assistant.files_count ?? 0} files</span>
          </div>
          <span>{formatDate(assistant.created_at)}</span>
        </div>

        {assistant.is_deleted && (
          <Badge variant="destructive" className="mt-2">
            Deleted
          </Badge>
        )}
      </CardContent>
    </Card>
  )
})
