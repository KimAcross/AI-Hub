import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsApi } from '@/lib/api'
import type { SettingsUpdate } from '@/types'
import toast from 'react-hot-toast'

export const settingsKeys = {
  all: ['settings'] as const,
  detail: () => [...settingsKeys.all, 'detail'] as const,
}

export function useSettings() {
  return useQuery({
    queryKey: settingsKeys.detail(),
    queryFn: settingsApi.get,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export function useUpdateSettings() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (settings: SettingsUpdate) => settingsApi.update(settings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: settingsKeys.all })
      toast.success('Settings saved')
    },
    onError: () => {
      toast.error('Failed to save settings')
    },
  })
}

export function useTestApiKey() {
  return useMutation({
    mutationFn: settingsApi.testApiKey,
  })
}
