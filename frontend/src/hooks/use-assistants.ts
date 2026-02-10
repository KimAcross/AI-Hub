import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { assistantsApi } from '@/lib/api'
import type { AssistantCreate, AssistantUpdate } from '@/types'
import toast from 'react-hot-toast'

export const assistantKeys = {
  all: ['assistants'] as const,
  lists: () => [...assistantKeys.all, 'list'] as const,
  list: (includeDeleted: boolean) => [...assistantKeys.lists(), { includeDeleted }] as const,
  details: () => [...assistantKeys.all, 'detail'] as const,
  detail: (id: string) => [...assistantKeys.details(), id] as const,
  templates: () => [...assistantKeys.all, 'templates'] as const,
  template: (id: string) => [...assistantKeys.templates(), id] as const,
}

export function useAssistants(includeDeleted = false) {
  return useQuery({
    queryKey: assistantKeys.list(includeDeleted),
    queryFn: () => assistantsApi.list(includeDeleted),
  })
}

export function useAssistant(id: string) {
  return useQuery({
    queryKey: assistantKeys.detail(id),
    queryFn: () => assistantsApi.get(id),
    enabled: !!id,
  })
}

export function useAssistantTemplates() {
  return useQuery({
    queryKey: assistantKeys.templates(),
    queryFn: () => assistantsApi.getTemplates(),
  })
}

export function useCreateAssistant() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: AssistantCreate) => assistantsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assistantKeys.lists() })
      toast.success('Assistant created successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create assistant')
    },
  })
}

export function useUpdateAssistant() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AssistantUpdate }) =>
      assistantsApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: assistantKeys.lists() })
      queryClient.invalidateQueries({ queryKey: assistantKeys.detail(id) })
      toast.success('Assistant updated successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update assistant')
    },
  })
}

export function useDeleteAssistant() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => assistantsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assistantKeys.lists() })
      toast.success('Assistant deleted successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete assistant')
    },
  })
}

export function useRestoreAssistant() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => assistantsApi.restore(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assistantKeys.lists() })
      toast.success('Assistant restored successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to restore assistant')
    },
  })
}

export function useCreateFromTemplate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ templateId, name }: { templateId: string; name?: string }) =>
      assistantsApi.createFromTemplate(templateId, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assistantKeys.lists() })
      toast.success('Assistant created from template')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create from template')
    },
  })
}
