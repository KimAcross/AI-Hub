import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { Suspense, lazy, useEffect } from 'react'
import { MainLayout } from '@/components/layout/main-layout'
import { AuthGuard } from '@/components/auth-guard'
import { useAppStore } from '@/stores/app-store'
import { ErrorBoundary } from '@/components/error-boundary'
import { ConnectionStatus } from '@/components/connection-status'
import { Skeleton } from '@/components/ui/skeleton'

// Lazy load pages for code splitting
const DashboardPage = lazy(() => import('@/pages/dashboard').then(m => ({ default: m.DashboardPage })))
const AssistantsPage = lazy(() => import('@/pages/assistants').then(m => ({ default: m.AssistantsPage })))
const NewAssistantPage = lazy(() => import('@/pages/assistants/new').then(m => ({ default: m.NewAssistantPage })))
const AssistantDetailPage = lazy(() => import('@/pages/assistants/detail').then(m => ({ default: m.AssistantDetailPage })))
const ChatPage = lazy(() => import('@/pages/chat').then(m => ({ default: m.ChatPage })))
const SettingsPage = lazy(() => import('@/pages/settings').then(m => ({ default: m.SettingsPage })))
const LoginPage = lazy(() => import('@/pages/login').then(m => ({ default: m.LoginPage })))

// Admin pages
const AdminLoginPage = lazy(() => import('@/pages/admin/login').then(m => ({ default: m.AdminLoginPage })))
const AdminDashboardPage = lazy(() => import('@/pages/admin/index').then(m => ({ default: m.AdminDashboardPage })))
const AdminUsersPage = lazy(() => import('@/pages/admin/users').then(m => ({ default: m.AdminUsersPage })))
const AdminApiKeysPage = lazy(() => import('@/pages/admin/api-keys').then(m => ({ default: m.AdminApiKeysPage })))
const AdminUsagePage = lazy(() => import('@/pages/admin/usage').then(m => ({ default: m.AdminUsagePage })))
const AdminSettingsPage = lazy(() => import('@/pages/admin/settings').then(m => ({ default: m.AdminSettingsPage })))
const AdminAuditLogsPage = lazy(() => import('@/pages/admin/audit-logs').then(m => ({ default: m.AdminAuditLogsPage })))
const AdminAssistantsPage = lazy(() => import('@/pages/admin/assistants').then(m => ({ default: m.AdminAssistantsPage })))

// Loading fallback component
function PageLoader() {
  return (
    <div className="flex flex-col h-screen">
      <div className="h-14 border-b flex items-center px-4">
        <Skeleton className="h-6 w-32" />
      </div>
      <div className="flex-1 p-6 space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    </div>
  )
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      retry: 1,
    },
  },
})

function ThemeInitializer() {
  const { theme } = useAppStore()

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else if (theme === 'light') {
      root.classList.remove('dark')
    } else {
      // System preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        root.classList.add('dark')
      } else {
        root.classList.remove('dark')
      }
    }
  }, [theme])

  return null
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ThemeInitializer />
          <ConnectionStatus />
          <Suspense fallback={<PageLoader />}>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />

              {/* Admin routes (outside main layout) */}
              <Route path="/admin/login" element={<AdminLoginPage />} />
              <Route path="/admin" element={<AdminDashboardPage />} />
              <Route path="/admin/users" element={<AdminUsersPage />} />
              <Route path="/admin/api-keys" element={<AdminApiKeysPage />} />
              <Route path="/admin/usage" element={<AdminUsagePage />} />
              <Route path="/admin/settings" element={<AdminSettingsPage />} />
              <Route path="/admin/audit-logs" element={<AdminAuditLogsPage />} />
              <Route path="/admin/assistants" element={<AdminAssistantsPage />} />

              {/* Main app routes (protected) */}
              <Route element={<AuthGuard><MainLayout /></AuthGuard>}>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/assistants" element={<AssistantsPage />} />
                <Route path="/assistants/new" element={<NewAssistantPage />} />
                <Route path="/assistants/:id" element={<AssistantDetailPage />} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Route>
            </Routes>
          </Suspense>
          <Toaster
            position="bottom-right"
            toastOptions={{
              className: 'bg-card text-card-foreground border shadow-lg',
              duration: 4000,
            }}
          />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
