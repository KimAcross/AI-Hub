import { Outlet } from 'react-router-dom'
import { Sidebar } from './sidebar'
import { useAppStore } from '@/stores/app-store'
import { cn } from '@/lib/utils'

export function MainLayout() {
  const { sidebarOpen } = useAppStore()

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <main
        className={cn(
          "min-h-screen transition-all duration-300",
          sidebarOpen ? "ml-64" : "ml-16"
        )}
      >
        <Outlet />
      </main>
    </div>
  )
}
