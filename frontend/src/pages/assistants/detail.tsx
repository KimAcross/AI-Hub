import * as React from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Bot,
  Settings,
  FileText,
  MessageSquare,
  Trash2,
} from 'lucide-react'
import { Header } from '@/components/layout/header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { FileUpload } from '@/components/file/file-upload'
import { FileList } from '@/components/file/file-list'
import { AssistantForm } from '@/components/assistant/assistant-form'
import { useAssistant, useUpdateAssistant, useDeleteAssistant } from '@/hooks/use-assistants'
import { useFiles, useUploadFile, useDeleteFile, useReprocessFile } from '@/hooks/use-files'
import { formatDate } from '@/lib/utils'
import type { AssistantUpdate } from '@/types'

export function AssistantDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = React.useState<'files' | 'settings'>('files')
  const [showDeleteDialog, setShowDeleteDialog] = React.useState(false)

  const { data: assistant, isLoading } = useAssistant(id!)
  const { data: files, isLoading: filesLoading } = useFiles(id!)
  const updateAssistant = useUpdateAssistant()
  const deleteAssistant = useDeleteAssistant()
  const uploadFile = useUploadFile(id!)
  const deleteFile = useDeleteFile(id!)
  const reprocessFile = useReprocessFile(id!)

  const handleUpdateAssistant = (data: AssistantUpdate) => {
    updateAssistant.mutate({ id: id!, data })
  }

  const handleDeleteAssistant = () => {
    deleteAssistant.mutate(id!, {
      onSuccess: () => navigate('/assistants'),
    })
  }

  const handleUpload = async (file: File) => {
    await uploadFile.mutateAsync({ file })
  }

  if (isLoading) {
    return (
      <div className="flex flex-col h-screen">
        <Header>
          <Skeleton className="h-8 w-48" />
        </Header>
        <div className="flex-1 p-6">
          <div className="max-w-4xl mx-auto">
            <Skeleton className="h-32 w-full mb-6" />
            <Skeleton className="h-64 w-full" />
          </div>
        </div>
      </div>
    )
  }

  if (!assistant) {
    return (
      <div className="flex flex-col h-screen">
        <Header title="Assistant Not Found" />
        <div className="flex-1 p-6 flex items-center justify-center">
          <div className="text-center">
            <p className="text-muted-foreground mb-4">This assistant doesn't exist</p>
            <Button asChild>
              <Link to="/assistants">Back to Assistants</Link>
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen">
      <Header>
        <Button variant="ghost" onClick={() => navigate('/assistants')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div className="flex-1" />
        <Button variant="outline" asChild>
          <Link to={`/chat?assistant=${id}`}>
            <MessageSquare className="h-4 w-4 mr-2" />
            Chat
          </Link>
        </Button>
      </Header>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto">
          {/* Assistant Header Card */}
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                  {assistant.avatar_url ? (
                    <img
                      src={assistant.avatar_url}
                      alt={assistant.name}
                      className="h-16 w-16 rounded-full object-cover"
                    />
                  ) : (
                    <Bot className="h-8 w-8 text-primary" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h1 className="text-2xl font-bold">{assistant.name}</h1>
                    {assistant.is_deleted && (
                      <Badge variant="destructive">Deleted</Badge>
                    )}
                  </div>
                  {assistant.description && (
                    <p className="text-muted-foreground mt-1">{assistant.description}</p>
                  )}
                  <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                    <span>Model: {assistant.model.split('/').pop()}</span>
                    <span>Created: {formatDate(assistant.created_at)}</span>
                    <span>{files?.length ?? 0} files</span>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-destructive"
                  onClick={() => setShowDeleteDialog(true)}
                >
                  <Trash2 className="h-5 w-5" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            <Button
              variant={activeTab === 'files' ? 'default' : 'outline'}
              onClick={() => setActiveTab('files')}
            >
              <FileText className="h-4 w-4 mr-2" />
              Knowledge Base
            </Button>
            <Button
              variant={activeTab === 'settings' ? 'default' : 'outline'}
              onClick={() => setActiveTab('settings')}
            >
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </div>

          {/* Tab Content */}
          {activeTab === 'files' && (
            <Card>
              <CardHeader>
                <CardTitle>Knowledge Base</CardTitle>
                <CardDescription>
                  Upload documents to give your assistant context
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileUpload onUpload={handleUpload} />
                <div className="mt-6">
                  {filesLoading ? (
                    <div className="space-y-4">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-16 w-full" />
                      ))}
                    </div>
                  ) : (
                    <FileList
                      files={files ?? []}
                      onDelete={(fileId) => deleteFile.mutate(fileId)}
                      onReprocess={(fileId) => reprocessFile.mutate(fileId)}
                      isDeleting={deleteFile.isPending ? deleteFile.variables : undefined}
                      isReprocessing={reprocessFile.isPending ? reprocessFile.variables : undefined}
                    />
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === 'settings' && (
            <Card>
              <CardHeader>
                <CardTitle>Assistant Settings</CardTitle>
                <CardDescription>
                  Configure your assistant's behavior
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AssistantForm
                  assistant={assistant}
                  onSubmit={handleUpdateAssistant}
                  onCancel={() => setActiveTab('files')}
                  isLoading={updateAssistant.isPending}
                />
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Delete Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Assistant</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{assistant.name}"? This will also remove all associated files.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteAssistant}
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
