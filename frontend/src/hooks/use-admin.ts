import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  adminApi,
  usersApi,
  providerKeysApi,
  quotasApi,
  auditApi,
} from '@/lib/api'
import { useAdminStore } from '@/stores/admin-store'
import toast from 'react-hot-toast'
import type {
  UserRole,
  UserCreate,
  UserUpdate,
  ProviderApiKeyCreate,
  ProviderApiKeyUpdate,
  APIKeyProvider,
  QuotaUpdate,
  AuditLogQuery,
} from '@/types'

export const adminKeys = {
  all: ['admin'] as const,
  usage: () => [...adminKeys.all, 'usage'] as const,
  summary: () => [...adminKeys.usage(), 'summary'] as const,
  breakdown: () => [...adminKeys.usage(), 'breakdown'] as const,
  daily: (days: number) => [...adminKeys.usage(), 'daily', { days }] as const,
  health: () => [...adminKeys.all, 'health'] as const,
  // Users
  users: () => [...adminKeys.all, 'users'] as const,
  usersList: (params?: {
    search?: string
    role?: UserRole
    is_active?: boolean
    page?: number
    size?: number
  }) => [...adminKeys.users(), 'list', params] as const,
  user: (id: string) => [...adminKeys.users(), id] as const,
  // API Keys
  apiKeys: () => [...adminKeys.all, 'api-keys'] as const,
  apiKeysList: (provider?: APIKeyProvider) =>
    [...adminKeys.apiKeys(), 'list', provider] as const,
  apiKey: (id: string) => [...adminKeys.apiKeys(), id] as const,
  // Quotas
  quotas: () => [...adminKeys.all, 'quotas'] as const,
  globalQuota: () => [...adminKeys.quotas(), 'global'] as const,
  usageStatus: () => [...adminKeys.quotas(), 'usage-status'] as const,
  quotaAlerts: () => [...adminKeys.quotas(), 'alerts'] as const,
  // Audit
  audit: () => [...adminKeys.all, 'audit'] as const,
  auditLogs: (params?: AuditLogQuery) => [...adminKeys.audit(), 'logs', params] as const,
  auditRecent: (limit?: number) => [...adminKeys.audit(), 'recent', limit] as const,
  auditSummary: (days?: number) => [...adminKeys.audit(), 'summary', days] as const,
}

export function useAdminLogin() {
  const setToken = useAdminStore((state) => state.setToken)

  return useMutation({
    mutationFn: (password: string) => adminApi.login(password),
    onSuccess: (data) => {
      setToken(data.token, data.expires_at, data.csrf_token)
      toast.success('Logged in to admin dashboard')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Invalid password')
    },
  })
}

export function useAdminVerify() {
  const token = useAdminStore((state) => state.token)
  const logout = useAdminStore((state) => state.logout)

  return useQuery({
    queryKey: ['admin', 'verify', token],
    queryFn: async () => {
      if (!token) return false
      const valid = await adminApi.verify(token)
      if (!valid) {
        logout()
      }
      return valid
    },
    enabled: !!token,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  })
}

export function useUsageSummary() {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.summary(),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return adminApi.getUsageSummary(token)
    },
    enabled: !!token,
    staleTime: 60 * 1000, // 1 minute
  })
}

export function useUsageBreakdown() {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.breakdown(),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return adminApi.getUsageBreakdown(token)
    },
    enabled: !!token,
    staleTime: 60 * 1000, // 1 minute
  })
}

export function useDailyUsage(days = 30) {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.daily(days),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return adminApi.getDailyUsage(token, days)
    },
    enabled: !!token,
    staleTime: 60 * 1000, // 1 minute
  })
}

export function useSystemHealth() {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.health(),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return adminApi.getHealth(token)
    },
    enabled: !!token,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Auto-refresh every 30 seconds
  })
}

// ============ User Management Hooks ============

export function useUsers(params?: {
  search?: string
  role?: UserRole
  is_active?: boolean
  page?: number
  size?: number
}) {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.usersList(params),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return usersApi.list(token, params)
    },
    enabled: !!token,
    staleTime: 30 * 1000,
  })
}

export function useUser(userId: string) {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.user(userId),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return usersApi.get(token, userId)
    },
    enabled: !!token && !!userId,
    staleTime: 30 * 1000,
  })
}

export function useCreateUser() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: (userData: UserCreate) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return usersApi.create(token, csrfToken, userData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.users() })
      toast.success('User created successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create user')
    },
  })
}

export function useUpdateUser() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: ({ userId, userData }: { userId: string; userData: UserUpdate }) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return usersApi.update(token, csrfToken, userId, userData)
    },
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: adminKeys.users() })
      queryClient.invalidateQueries({ queryKey: adminKeys.user(userId) })
      toast.success('User updated successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update user')
    },
  })
}

export function useDisableUser() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: (userId: string) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return usersApi.disable(token, csrfToken, userId)
    },
    onSuccess: (_, userId) => {
      queryClient.invalidateQueries({ queryKey: adminKeys.users() })
      queryClient.invalidateQueries({ queryKey: adminKeys.user(userId) })
      toast.success('User disabled')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to disable user')
    },
  })
}

export function useEnableUser() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: (userId: string) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return usersApi.enable(token, csrfToken, userId)
    },
    onSuccess: (_, userId) => {
      queryClient.invalidateQueries({ queryKey: adminKeys.users() })
      queryClient.invalidateQueries({ queryKey: adminKeys.user(userId) })
      toast.success('User enabled')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to enable user')
    },
  })
}

export function useDeleteUser() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: (userId: string) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return usersApi.delete(token, csrfToken, userId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.users() })
      toast.success('User deleted')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete user')
    },
  })
}

export function useResetUserPassword() {
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: ({ userId, newPassword }: { userId: string; newPassword: string }) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return usersApi.resetPassword(token, csrfToken, userId, newPassword)
    },
    onSuccess: () => {
      toast.success('Password reset successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to reset password')
    },
  })
}

// ============ Provider API Keys Hooks ============

export function useProviderKeys(provider?: APIKeyProvider) {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.apiKeysList(provider),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return providerKeysApi.list(token, provider)
    },
    enabled: !!token,
    staleTime: 30 * 1000,
  })
}

export function useProviderKey(keyId: string) {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.apiKey(keyId),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return providerKeysApi.get(token, keyId)
    },
    enabled: !!token && !!keyId,
    staleTime: 30 * 1000,
  })
}

export function useCreateProviderKey() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: (keyData: ProviderApiKeyCreate) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return providerKeysApi.create(token, csrfToken, keyData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.apiKeys() })
      toast.success('API key added successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to add API key')
    },
  })
}

export function useUpdateProviderKey() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: ({ keyId, keyData }: { keyId: string; keyData: ProviderApiKeyUpdate }) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return providerKeysApi.update(token, csrfToken, keyId, keyData)
    },
    onSuccess: (_, { keyId }) => {
      queryClient.invalidateQueries({ queryKey: adminKeys.apiKeys() })
      queryClient.invalidateQueries({ queryKey: adminKeys.apiKey(keyId) })
      toast.success('API key updated')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update API key')
    },
  })
}

export function useDeleteProviderKey() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: (keyId: string) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return providerKeysApi.delete(token, csrfToken, keyId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.apiKeys() })
      toast.success('API key deleted')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete API key')
    },
  })
}

export function useTestProviderKey() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)

  return useMutation({
    mutationFn: (keyId: string) => {
      if (!token) throw new Error('Not authenticated')
      return providerKeysApi.test(token, keyId)
    },
    onSuccess: (result, keyId) => {
      queryClient.invalidateQueries({ queryKey: adminKeys.apiKey(keyId) })
      queryClient.invalidateQueries({ queryKey: adminKeys.apiKeys() })
      if (result.valid) {
        toast.success(`API key is valid (${result.latency_ms}ms)`)
      } else {
        toast.error(result.error || 'API key test failed')
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to test API key')
    },
  })
}

export function useRotateProviderKey() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: ({ keyId, newApiKey }: { keyId: string; newApiKey: string }) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return providerKeysApi.rotate(token, csrfToken, keyId, newApiKey)
    },
    onSuccess: (_, { keyId }) => {
      queryClient.invalidateQueries({ queryKey: adminKeys.apiKeys() })
      queryClient.invalidateQueries({ queryKey: adminKeys.apiKey(keyId) })
      toast.success('API key rotated successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to rotate API key')
    },
  })
}

export function useSetDefaultProviderKey() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: (keyId: string) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return providerKeysApi.setDefault(token, csrfToken, keyId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.apiKeys() })
      toast.success('Default API key updated')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to set default API key')
    },
  })
}

// ============ Quota Hooks ============

export function useGlobalQuota() {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.globalQuota(),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return quotasApi.getGlobal(token)
    },
    enabled: !!token,
    staleTime: 60 * 1000,
  })
}

export function useUpdateGlobalQuota() {
  const queryClient = useQueryClient()
  const token = useAdminStore((state) => state.token)
  const csrfToken = useAdminStore((state) => state.csrfToken)

  return useMutation({
    mutationFn: (quotaData: QuotaUpdate) => {
      if (!token || !csrfToken) throw new Error('Not authenticated')
      return quotasApi.updateGlobal(token, csrfToken, quotaData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.quotas() })
      toast.success('Quota settings updated')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update quota')
    },
  })
}

export function useUsageStatus() {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.usageStatus(),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return quotasApi.getUsageStatus(token)
    },
    enabled: !!token,
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000, // Refresh every minute
  })
}

export function useQuotaAlerts() {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.quotaAlerts(),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return quotasApi.getAlerts(token)
    },
    enabled: !!token,
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000, // Refresh every minute
  })
}

// ============ Audit Log Hooks ============

export function useAuditLogs(params?: AuditLogQuery) {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.auditLogs(params),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return auditApi.query(token, params)
    },
    enabled: !!token,
    staleTime: 30 * 1000,
  })
}

export function useRecentAuditLogs(limit = 50) {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.auditRecent(limit),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return auditApi.getRecent(token, limit)
    },
    enabled: !!token,
    staleTime: 30 * 1000,
  })
}

export function useAuditSummary(days = 30) {
  const token = useAdminStore((state) => state.token)

  return useQuery({
    queryKey: adminKeys.auditSummary(days),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return auditApi.getSummary(token, days)
    },
    enabled: !!token,
    staleTime: 60 * 1000,
  })
}
