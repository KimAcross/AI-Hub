import { create } from 'zustand'
import { persist } from 'zustand/middleware'

import type { User, UserRole } from '@/types'

interface AuthUser {
  id: string
  email: string
  name: string
  role: UserRole
}

interface AuthState {
  token: string | null
  user: AuthUser | null
  expiresAt: string | null
  csrfToken: string | null

  // Computed
  isAuthenticated: boolean

  // Actions
  login: (token: string, expiresAt: string, csrfToken: string, user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      expiresAt: null,
      csrfToken: null,

      get isAuthenticated() {
        const { token, expiresAt } = get()
        if (!token || !expiresAt) return false

        const expiry = new Date(expiresAt)
        return expiry > new Date()
      },

      login: (token, expiresAt, csrfToken, user) =>
        set({
          token,
          expiresAt,
          csrfToken,
          user: {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
          },
        }),

      logout: () =>
        set({
          token: null,
          user: null,
          expiresAt: null,
          csrfToken: null,
        }),
    }),
    {
      name: 'ai-across-auth',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        expiresAt: state.expiresAt,
        csrfToken: state.csrfToken,
      }),
    }
  )
)
