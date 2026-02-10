import * as React from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, CheckCircle, Loader2 } from 'lucide-react'
import { cn, formatBytes } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>
  accept?: Record<string, string[]>
  maxSize?: number
  disabled?: boolean
}

interface UploadingFile {
  file: File
  progress: number
  status: 'uploading' | 'success' | 'error'
  error?: string
}

export function FileUpload({
  onUpload,
  accept = {
    'application/pdf': ['.pdf'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'text/plain': ['.txt'],
    'text/markdown': ['.md'],
  },
  maxSize = 50 * 1024 * 1024, // 50MB
  disabled = false,
}: FileUploadProps) {
  const [uploadingFiles, setUploadingFiles] = React.useState<UploadingFile[]>([])

  const onDrop = React.useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      const uploadingFile: UploadingFile = {
        file,
        progress: 0,
        status: 'uploading',
      }

      setUploadingFiles((prev) => [...prev, uploadingFile])

      try {
        await onUpload(file)
        setUploadingFiles((prev) =>
          prev.map((f) =>
            f.file === file ? { ...f, progress: 100, status: 'success' } : f
          )
        )
        // Remove successful upload after 2 seconds
        setTimeout(() => {
          setUploadingFiles((prev) => prev.filter((f) => f.file !== file))
        }, 2000)
      } catch (error) {
        setUploadingFiles((prev) =>
          prev.map((f) =>
            f.file === file
              ? { ...f, status: 'error', error: (error as Error).message }
              : f
          )
        )
      }
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize,
    disabled,
    multiple: true,
  })

  const removeFile = (file: File) => {
    setUploadingFiles((prev) => prev.filter((f) => f.file !== file))
  }

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
          isDragActive
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-primary/50",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        <input {...getInputProps()} />
        <Upload className="h-10 w-10 mx-auto text-muted-foreground mb-4" />
        {isDragActive ? (
          <p className="text-primary font-medium">Drop files here...</p>
        ) : (
          <>
            <p className="font-medium mb-1">Drag & drop files here</p>
            <p className="text-sm text-muted-foreground mb-2">
              or click to browse
            </p>
            <p className="text-xs text-muted-foreground">
              Supported: PDF, DOCX, TXT, MD (max {formatBytes(maxSize)})
            </p>
          </>
        )}
      </div>

      {uploadingFiles.length > 0 && (
        <div className="space-y-2">
          {uploadingFiles.map((uploadingFile, index) => (
            <div
              key={index}
              className="flex items-center gap-3 p-3 rounded-lg border bg-card"
            >
              <FileText className="h-8 w-8 text-muted-foreground shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {uploadingFile.file.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatBytes(uploadingFile.file.size)}
                </p>
                {uploadingFile.status === 'uploading' && (
                  <Progress value={uploadingFile.progress} className="mt-2 h-1" />
                )}
                {uploadingFile.status === 'error' && (
                  <p className="text-xs text-destructive mt-1">
                    {uploadingFile.error}
                  </p>
                )}
              </div>
              <div className="shrink-0">
                {uploadingFile.status === 'uploading' && (
                  <Loader2 className="h-5 w-5 animate-spin text-primary" />
                )}
                {uploadingFile.status === 'success' && (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
                {uploadingFile.status === 'error' && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => removeFile(uploadingFile.file)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
