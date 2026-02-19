import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { conversationsApi } from '@/lib/api'
import type { ConversationCreate } from '@/types'
import toast from 'react-hot-toast'

export const conversationKeys = {
  all: ['conversations'] as const,
  lists: () => [...conversationKeys.all, 'list'] as const,
  list: (assistantId?: string) => [...conversationKeys.lists(), { assistantId }] as const,
  details: () => [...conversationKeys.all, 'detail'] as const,
  detail: (id: string) => [...conversationKeys.details(), id] as const,
}

export function useConversations(assistantId?: string) {
  return useQuery({
    queryKey: conversationKeys.list(assistantId),
    queryFn: () => conversationsApi.list(assistantId),
    select: (data) => (Array.isArray(data) ? data : []),
  })
}

export function useConversation(id: string) {
  return useQuery({
    queryKey: conversationKeys.detail(id),
    queryFn: () => conversationsApi.get(id),
    enabled: !!id,
  })
}

export function useCreateConversation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: ConversationCreate) => conversationsApi.create(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: conversationKeys.lists() })
      if (variables.assistant_id) {
        queryClient.invalidateQueries({
          queryKey: conversationKeys.list(variables.assistant_id),
        })
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create conversation')
    },
  })
}

export function useUpdateConversation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, title }: { id: string; title: string }) =>
      conversationsApi.update(id, title),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: conversationKeys.lists() })
      queryClient.invalidateQueries({ queryKey: conversationKeys.detail(id) })
      toast.success('Conversation renamed')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to rename conversation')
    },
  })
}

export function useDeleteConversation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => conversationsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: conversationKeys.lists() })
      toast.success('Conversation deleted')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete conversation')
    },
  })
}

export function useExportConversation() {
  return useMutation({
    mutationFn: ({ id, format }: { id: string; format: 'json' | 'markdown' }) =>
      conversationsApi.export(id, format),
    onSuccess: (data, { format }) => {
      // Create a download link
      const blob = new Blob([data], {
        type: format === 'json' ? 'application/json' : 'text/markdown',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `conversation.${format === 'json' ? 'json' : 'md'}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      toast.success('Conversation exported')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to export conversation')
    },
  })
}
