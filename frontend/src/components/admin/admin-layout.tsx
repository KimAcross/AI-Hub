import type { ReactNode } from 'react'
import { Outlet } from 'react-router-dom'
import { AdminGuard } from './admin-guard'
import { AdminSidebar } from './admin-sidebar'
import { LogOut, RefreshCw, Bell } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAdminStore } from '@/stores/admin-store'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { useQuotaAlerts } from '@/hooks/use-admin'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { useState } from 'react'

interface AdminLayoutProps {
  children?: ReactNode
}

function AlertsDialog({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const { data: alertsData } = useQuotaAlerts()
  const alerts = alertsData?.alerts || []

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Quota Alerts</DialogTitle>
          <DialogDescription>
            Current usage alerts and warnings
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-3 mt-4">
          {alerts.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No active alerts
            </p>
          ) : (
            alerts.map((alert, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${
                  alert.is_exceeded
                    ? 'bg-destructive/10 border-destructive'
                    : 'bg-yellow-500/10 border-yellow-500'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium capitalize">
                    {alert.period} {alert.alert_type}
                  </span>
                  <Badge variant={alert.is_exceeded ? 'destructive' : 'secondary'}>
                    {alert.percent_used.toFixed(1)}%
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {alert.current_value.toFixed(2)} / {alert.limit_value.toFixed(2)}
                  {alert.alert_type === 'cost' ? ' USD' : ' tokens'}
                </p>
              </div>
            ))
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

function AdminLayoutContent({ children }: AdminLayoutProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const logout = useAdminStore((state) => state.logout)
  const { data: alertsData } = useQuotaAlerts()
  const [alertsOpen, setAlertsOpen] = useState(false)

  const alertCount = alertsData?.alerts?.length || 0

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['admin'] })
  }

  const handleLogout = () => {
    logout()
    navigate('/admin/login')
  }

  return (
    <div className="min-h-screen bg-background">
      <AdminSidebar />

      {/* Main content area with left margin for sidebar */}
      <div className="ml-64">
        {/* Header */}
        <header className="sticky top-0 z-30 border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
          <div className="flex h-16 items-center justify-between px-6">
            <div />
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setAlertsOpen(true)}
                className="relative"
              >
                <Bell className="h-4 w-4" />
                {alertCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-destructive text-destructive-foreground text-xs flex items-center justify-center">
                    {alertCount}
                  </span>
                )}
              </Button>
              <Button variant="outline" size="sm" onClick={handleRefresh}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">{children || <Outlet />}</main>
      </div>

      <AlertsDialog open={alertsOpen} onOpenChange={setAlertsOpen} />
    </div>
  )
}

export function AdminLayout({ children }: AdminLayoutProps) {
  return (
    <AdminGuard>
      <AdminLayoutContent>{children}</AdminLayoutContent>
    </AdminGuard>
  )
}
