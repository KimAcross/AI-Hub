import * as React from 'react'
import {
  MessageSquare,
  Plus,
  Search,
  MoreVertical,
  Trash2,
  Pencil,
  Download,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import type { Conversation } from '@/types'

interface ConversationSidebarProps {
  conversations: Conversation[]
  selectedId?: string
  onSelect: (id: string) => void
  onNewChat: () => void
  onDelete: (id: string) => void
  onRename: (id: string, title: string) => void
  onExport: (id: string) => void
  isLoading?: boolean
}

export function ConversationSidebar({
  conversations,
  selectedId,
  onSelect,
  onNewChat,
  onDelete,
  onRename,
  onExport,
  isLoading = false,
}: ConversationSidebarProps) {
  const [search, setSearch] = React.useState('')
  const [editingId, setEditingId] = React.useState<string | null>(null)
  const [editTitle, setEditTitle] = React.useState('')
  const [menuOpenId, setMenuOpenId] = React.useState<string | null>(null)

  const filteredConversations = React.useMemo(() => {
    if (!search) return conversations

    const query = search.toLowerCase()
    return conversations.filter((c) =>
      c.title.toLowerCase().includes(query)
    )
  }, [conversations, search])

  // Group conversations by date
  const groupedConversations = React.useMemo(() => {
    const groups: Record<string, Conversation[]> = {
      Today: [],
      Yesterday: [],
      'Previous 7 Days': [],
      'Previous 30 Days': [],
      Older: [],
    }

    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)

    filteredConversations.forEach((conv) => {
      const date = new Date(conv.updated_at)

      if (date >= today) {
        groups['Today'].push(conv)
      } else if (date >= yesterday) {
        groups['Yesterday'].push(conv)
      } else if (date >= weekAgo) {
        groups['Previous 7 Days'].push(conv)
      } else if (date >= monthAgo) {
        groups['Previous 30 Days'].push(conv)
      } else {
        groups['Older'].push(conv)
      }
    })

    return groups
  }, [filteredConversations])

  const handleStartEdit = (id: string, currentTitle: string) => {
    setEditingId(id)
    setEditTitle(currentTitle)
    setMenuOpenId(null)
  }

  const handleSaveEdit = () => {
    if (editingId && editTitle.trim()) {
      onRename(editingId, editTitle.trim())
    }
    setEditingId(null)
    setEditTitle('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSaveEdit()
    } else if (e.key === 'Escape') {
      setEditingId(null)
      setEditTitle('')
    }
  }

  if (isLoading) {
    return (
      <div className="w-64 border-r bg-muted/30 flex flex-col">
        <div className="p-4 border-b">
          <Skeleton className="h-9 w-full" />
        </div>
        <div className="flex-1 p-2 space-y-2">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="w-64 border-r bg-muted/30 flex flex-col">
      <div className="p-3 border-b space-y-3">
        <Button onClick={onNewChat} className="w-full gap-2">
          <Plus className="h-4 w-4" />
          New Chat
        </Button>

        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search conversations..."
            className="pl-8 h-9"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {Object.entries(groupedConversations).map(
          ([group, convs]) =>
            convs.length > 0 && (
              <div key={group} className="mb-4">
                <div className="px-2 py-1 text-xs font-medium text-muted-foreground">
                  {group}
                </div>
                <div className="space-y-1">
                  {convs.map((conv) => (
                    <div
                      key={conv.id}
                      className={cn(
                        "group relative rounded-lg",
                        selectedId === conv.id && "bg-accent"
                      )}
                    >
                      {editingId === conv.id ? (
                        <Input
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onBlur={handleSaveEdit}
                          onKeyDown={handleKeyDown}
                          autoFocus
                          className="h-9 text-sm"
                        />
                      ) : (
                        <button
                          className={cn(
                            "w-full flex items-center gap-2 px-2 py-2 text-sm text-left hover:bg-accent rounded-lg transition-colors"
                          )}
                          onClick={() => onSelect(conv.id)}
                        >
                          <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
                          <span className="flex-1 truncate">{conv.title}</span>
                        </button>
                      )}

                      {editingId !== conv.id && (
                        <div className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            className="p-1 rounded hover:bg-background"
                            onClick={(e) => {
                              e.stopPropagation()
                              setMenuOpenId(menuOpenId === conv.id ? null : conv.id)
                            }}
                          >
                            <MoreVertical className="h-4 w-4 text-muted-foreground" />
                          </button>

                          {menuOpenId === conv.id && (
                            <>
                              <div
                                className="fixed inset-0 z-10"
                                onClick={() => setMenuOpenId(null)}
                              />
                              <div className="absolute right-0 top-full mt-1 z-20 w-36 rounded-md border bg-popover p-1 shadow-md">
                                <button
                                  className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-accent"
                                  onClick={() => handleStartEdit(conv.id, conv.title)}
                                >
                                  <Pencil className="h-4 w-4" />
                                  Rename
                                </button>
                                <button
                                  className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-accent"
                                  onClick={() => {
                                    onExport(conv.id)
                                    setMenuOpenId(null)
                                  }}
                                >
                                  <Download className="h-4 w-4" />
                                  Export
                                </button>
                                <button
                                  className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-destructive hover:bg-accent"
                                  onClick={() => {
                                    onDelete(conv.id)
                                    setMenuOpenId(null)
                                  }}
                                >
                                  <Trash2 className="h-4 w-4" />
                                  Delete
                                </button>
                              </div>
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )
        )}

        {filteredConversations.length === 0 && (
          <div className="text-center py-8 text-sm text-muted-foreground">
            {search ? 'No conversations found' : 'No conversations yet'}
          </div>
        )}
      </div>
    </div>
  )
}
