import { describe, it, expect, beforeEach } from 'vitest'
import { useAppStore } from './app-store'

describe('AppStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAppStore.setState({
      sidebarOpen: true,
      selectedAssistantId: null,
      theme: 'system',
    })
  })

  describe('sidebar state', () => {
    it('has default sidebar open', () => {
      const state = useAppStore.getState()
      expect(state.sidebarOpen).toBe(true)
    })

    it('can set sidebar open state', () => {
      useAppStore.getState().setSidebarOpen(false)
      expect(useAppStore.getState().sidebarOpen).toBe(false)
    })

    it('can toggle sidebar', () => {
      expect(useAppStore.getState().sidebarOpen).toBe(true)

      useAppStore.getState().toggleSidebar()
      expect(useAppStore.getState().sidebarOpen).toBe(false)

      useAppStore.getState().toggleSidebar()
      expect(useAppStore.getState().sidebarOpen).toBe(true)
    })
  })

  describe('assistant selection', () => {
    it('has no selected assistant by default', () => {
      const state = useAppStore.getState()
      expect(state.selectedAssistantId).toBeNull()
    })

    it('can set selected assistant', () => {
      useAppStore.getState().setSelectedAssistantId('test-assistant-id')
      expect(useAppStore.getState().selectedAssistantId).toBe('test-assistant-id')
    })

    it('can clear selected assistant', () => {
      useAppStore.getState().setSelectedAssistantId('test-id')
      useAppStore.getState().setSelectedAssistantId(null)
      expect(useAppStore.getState().selectedAssistantId).toBeNull()
    })
  })

  describe('theme state', () => {
    it('has system theme by default', () => {
      const state = useAppStore.getState()
      expect(state.theme).toBe('system')
    })

    it('can set light theme', () => {
      useAppStore.getState().setTheme('light')
      expect(useAppStore.getState().theme).toBe('light')
    })

    it('can set dark theme', () => {
      useAppStore.getState().setTheme('dark')
      expect(useAppStore.getState().theme).toBe('dark')
    })

    it('can set system theme', () => {
      useAppStore.getState().setTheme('dark')
      useAppStore.getState().setTheme('system')
      expect(useAppStore.getState().theme).toBe('system')
    })
  })
})
