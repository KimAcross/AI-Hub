import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AdminState {
  token: string | null
  expiresAt: string | null
  csrfToken: string | null

  // Computed
  isAuthenticated: boolean

  // Actions
  setToken: (token: string, expiresAt: string, csrfToken: string) => void
  logout: () => void
}

export const useAdminStore = create<AdminState>()(
  persist(
    (set, get) => ({
      token: null,
      expiresAt: null,
      csrfToken: null,

      get isAuthenticated() {
        const { token, expiresAt } = get()
        if (!token || !expiresAt) return false

        // Check if token is expired
        const expiry = new Date(expiresAt)
        return expiry > new Date()
      },

      setToken: (token, expiresAt, csrfToken) =>
        set({
          token,
          expiresAt,
          csrfToken,
        }),

      logout: () =>
        set({
          token: null,
          expiresAt: null,
          csrfToken: null,
        }),
    }),
    {
      name: 'ai-across-admin',
      partialize: (state) => ({
        token: state.token,
        expiresAt: state.expiresAt,
        csrfToken: state.csrfToken,
      }),
    }
  )
)
