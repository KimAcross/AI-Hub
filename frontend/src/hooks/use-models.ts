import { useQuery } from '@tanstack/react-query'
import { modelsApi } from '@/lib/api'

export const modelKeys = {
  all: ['models'] as const,
  list: () => [...modelKeys.all, 'list'] as const,
}

export function useModels() {
  return useQuery({
    queryKey: modelKeys.list(),
    queryFn: () => modelsApi.list(),
    select: (data) => (Array.isArray(data) ? data : []),
    staleTime: 5 * 60 * 1000, // Models don't change often, cache for 5 minutes
  })
}
