import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  sidebarOpen: boolean
  selectedAssistantId: string | null
  theme: 'light' | 'dark' | 'system'

  // Actions
  setSidebarOpen: (open: boolean) => void
  toggleSidebar: () => void
  setSelectedAssistantId: (id: string | null) => void
  setTheme: (theme: 'light' | 'dark' | 'system') => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      selectedAssistantId: null,
      theme: 'system',

      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSelectedAssistantId: (id) => set({ selectedAssistantId: id }),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'ai-across-app',
      partialize: (state) => ({
        theme: state.theme,
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
)
