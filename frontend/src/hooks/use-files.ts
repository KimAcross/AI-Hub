import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { filesApi } from '@/lib/api'
import toast from 'react-hot-toast'

export const fileKeys = {
  all: ['files'] as const,
  lists: () => [...fileKeys.all, 'list'] as const,
  list: (assistantId: string) => [...fileKeys.lists(), assistantId] as const,
  details: () => [...fileKeys.all, 'detail'] as const,
  detail: (assistantId: string, fileId: string) =>
    [...fileKeys.details(), assistantId, fileId] as const,
}

export function useFiles(assistantId: string) {
  return useQuery({
    queryKey: fileKeys.list(assistantId),
    queryFn: () => filesApi.list(assistantId),
    enabled: !!assistantId,
    refetchInterval: (query) => {
      // Refetch every 3s if any file is still processing
      const hasProcessingFiles = query.state.data?.some(
        (file) => file.status === 'processing' || file.status === 'indexing' || file.status === 'uploading'
      )
      return hasProcessingFiles ? 3000 : false
    },
  })
}

export function useFile(assistantId: string, fileId: string) {
  return useQuery({
    queryKey: fileKeys.detail(assistantId, fileId),
    queryFn: () => filesApi.get(assistantId, fileId),
    enabled: !!assistantId && !!fileId,
  })
}

export function useUploadFile(assistantId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ file, onProgress }: { file: File; onProgress?: (progress: number) => void }) =>
      filesApi.upload(assistantId, file, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fileKeys.list(assistantId) })
      toast.success('File uploaded successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to upload file')
    },
  })
}

export function useDeleteFile(assistantId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (fileId: string) => filesApi.delete(assistantId, fileId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fileKeys.list(assistantId) })
      toast.success('File deleted successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete file')
    },
  })
}

export function useReprocessFile(assistantId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (fileId: string) => filesApi.reprocess(assistantId, fileId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fileKeys.list(assistantId) })
      toast.success('File reprocessing started')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to reprocess file')
    },
  })
}
