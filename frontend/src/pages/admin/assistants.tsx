import * as React from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Filter } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { AssistantCard } from '@/components/assistant/assistant-card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  useAssistants,
  useDeleteAssistant,
  useRestoreAssistant,
  useUpdateAssistant,
} from '@/hooks/use-assistants'
import { AssistantForm } from '@/components/assistant/assistant-form'
import { AdminLayout } from '@/components/admin/admin-layout'
import type { Assistant, AssistantUpdate } from '@/types'

function AdminAssistantsContent() {
  const [search, setSearch] = React.useState('')
  const [showDeleted, setShowDeleted] = React.useState(false)
  const [editingAssistant, setEditingAssistant] = React.useState<Assistant | null>(null)
  const [deletingAssistant, setDeletingAssistant] = React.useState<Assistant | null>(null)

  const { data: assistants, isLoading } = useAssistants(showDeleted)
  const deleteAssistant = useDeleteAssistant()
  const restoreAssistant = useRestoreAssistant()
  const updateAssistant = useUpdateAssistant()

  const filteredAssistants = React.useMemo(() => {
    if (!assistants) return []
    return assistants.filter((a) =>
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.description?.toLowerCase().includes(search.toLowerCase())
    )
  }, [assistants, search])

  const handleEdit = (assistant: Assistant) => {
    setEditingAssistant(assistant)
  }

  const handleEditSubmit = (data: AssistantUpdate) => {
    if (!editingAssistant) return
    updateAssistant.mutate(
      { id: editingAssistant.id, data },
      { onSuccess: () => setEditingAssistant(null) }
    )
  }

  const handleDelete = (assistant: Assistant) => {
    setDeletingAssistant(assistant)
  }

  const confirmDelete = () => {
    if (!deletingAssistant) return
    deleteAssistant.mutate(deletingAssistant.id, {
      onSuccess: () => setDeletingAssistant(null),
    })
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Manage Assistants</h1>
        <Button asChild>
          <Link to="/assistants/new">
            <Plus className="h-4 w-4 mr-2" />
            New Assistant
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search assistants..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button
          variant={showDeleted ? 'secondary' : 'outline'}
          size="sm"
          onClick={() => setShowDeleted(!showDeleted)}
        >
          <Filter className="h-4 w-4 mr-2" />
          {showDeleted ? 'Hide Deleted' : 'Show Deleted'}
        </Button>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i}>
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="flex-1">
                    <Skeleton className="h-4 w-32 mb-2" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-2/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredAssistants.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredAssistants.map((assistant) => (
            <AssistantCard
              key={assistant.id}
              assistant={assistant}
              onEdit={() => handleEdit(assistant)}
              onDelete={() => handleDelete(assistant)}
              onRestore={() => restoreAssistant.mutate(assistant.id)}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">
            {search ? 'No assistants match your search' : 'No assistants yet'}
          </p>
          <Button asChild>
            <Link to="/assistants/new">
              <Plus className="h-4 w-4 mr-2" />
              Create Assistant
            </Link>
          </Button>
        </div>
      )}

      {/* Edit Dialog */}
      <Dialog open={!!editingAssistant} onOpenChange={() => setEditingAssistant(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Assistant</DialogTitle>
            <DialogDescription>
              Update the assistant's configuration
            </DialogDescription>
          </DialogHeader>
          {editingAssistant && (
            <AssistantForm
              assistant={editingAssistant}
              onSubmit={handleEditSubmit}
              onCancel={() => setEditingAssistant(null)}
              isLoading={updateAssistant.isPending}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <Dialog open={!!deletingAssistant} onOpenChange={() => setDeletingAssistant(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Assistant</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{deletingAssistant?.name}"? This action can be undone later.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeletingAssistant(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDelete}
              disabled={deleteAssistant.isPending}
            >
              {deleteAssistant.isPending ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export function AdminAssistantsPage() {
  return (
    <AdminLayout>
      <AdminAssistantsContent />
    </AdminLayout>
  )
}
