import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

import { authApi } from '@/lib/api'
import { useAuthStore } from '@/stores/auth-store'
import type { UserLoginRequest, UsageStatus } from '@/types'

export const authKeys = {
  all: ['auth'] as const,
  verify: () => [...authKeys.all, 'verify'] as const,
  me: () => [...authKeys.all, 'me'] as const,
  usage: () => [...authKeys.all, 'usage'] as const,
}

export function useLogin() {
  const login = useAuthStore((state) => state.login)

  return useMutation({
    mutationFn: (credentials: UserLoginRequest) => authApi.login(credentials),
    onSuccess: (data) => {
      login(data.token, data.expires_at, data.csrf_token, data.user)
      toast.success('Logged in successfully')
    },
    onError: () => {
      // Error toast handled by API interceptor
    },
  })
}

export function useVerifyAuth() {
  const token = useAuthStore((state) => state.token)
  const logout = useAuthStore((state) => state.logout)

  return useQuery({
    queryKey: [...authKeys.verify(), token],
    queryFn: async () => {
      if (!token) return false
      const valid = await authApi.verify(token)
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

export function useCurrentUser() {
  const token = useAuthStore((state) => state.token)

  return useQuery({
    queryKey: authKeys.me(),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return authApi.me(token)
    },
    enabled: !!token,
    staleTime: 5 * 60 * 1000,
  })
}

export function useUserUsage() {
  const token = useAuthStore((state) => state.token)

  return useQuery<UsageStatus>({
    queryKey: authKeys.usage(),
    queryFn: () => {
      if (!token) throw new Error('Not authenticated')
      return authApi.usage(token)
    },
    enabled: !!token,
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000,
  })
}

export function useLogout() {
  const logout = useAuthStore((state) => state.logout)
  const navigate = useNavigate()

  return () => {
    logout()
    navigate('/login')
    toast.success('Logged out')
  }
}
