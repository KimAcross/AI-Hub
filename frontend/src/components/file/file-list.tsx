import {
  FileText,
  Trash2,
  RefreshCw,
  Loader2,
  CheckCircle,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn, formatBytes, formatDateTime } from '@/lib/utils'
import type { KnowledgeFile, FileStatus } from '@/types'

interface FileListProps {
  files: KnowledgeFile[]
  onDelete: (fileId: string) => void
  onReprocess: (fileId: string) => void
  isDeleting?: string
  isReprocessing?: string
}

const statusConfig: Record<FileStatus, {
  label: string
  icon: typeof CheckCircle
  variant: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning'
}> = {
  uploading: { label: 'Uploading', icon: Loader2, variant: 'secondary' },
  processing: { label: 'Processing', icon: Loader2, variant: 'secondary' },
  indexing: { label: 'Indexing', icon: Loader2, variant: 'secondary' },
  ready: { label: 'Ready', icon: CheckCircle, variant: 'success' },
  error: { label: 'Error', icon: AlertCircle, variant: 'destructive' },
}

export function FileList({
  files,
  onDelete,
  onReprocess,
  isDeleting,
  isReprocessing,
}: FileListProps) {
  if (files.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
        <p>No files uploaded yet</p>
        <p className="text-sm">Upload files to add to the knowledge base</p>
      </div>
    )
  }

  return (
    <div className="divide-y">
      {files.map((file) => {
        const status = statusConfig[file.status]
        const StatusIcon = status.icon
        const isProcessing = ['uploading', 'processing', 'indexing'].includes(file.status)

        return (
          <div key={file.id} className="flex items-center gap-4 py-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
              <FileText className="h-5 w-5 text-muted-foreground" />
            </div>

            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{file.filename}</p>
              <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
                <span>{formatBytes(file.size_bytes)}</span>
                {file.chunk_count && (
                  <span>{file.chunk_count} chunks</span>
                )}
                <span>{formatDateTime(file.created_at)}</span>
              </div>
              {file.error_message && (
                <p className="text-xs text-destructive mt-1">{file.error_message}</p>
              )}
            </div>

            <Badge variant={status.variant} className="shrink-0">
              <StatusIcon
                className={cn("h-3 w-3 mr-1", isProcessing && "animate-spin")}
              />
              {status.label}
            </Badge>

            <div className="flex items-center gap-1">
              {file.status === 'error' && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => onReprocess(file.id)}
                  disabled={isReprocessing === file.id}
                >
                  {isReprocessing === file.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4" />
                  )}
                </Button>
              )}
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-destructive hover:text-destructive"
                onClick={() => onDelete(file.id)}
                disabled={isDeleting === file.id}
              >
                {isDeleting === file.id ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
