import { ReactNode, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAdminStore } from '@/stores/admin-store'
import { useAdminVerify } from '@/hooks/use-admin'
import { Skeleton } from '@/components/ui/skeleton'

interface AdminGuardProps {
  children: ReactNode
}

export function AdminGuard({ children }: AdminGuardProps) {
  const navigate = useNavigate()
  const token = useAdminStore((state) => state.token)
  const expiresAt = useAdminStore((state) => state.expiresAt)
  const logout = useAdminStore((state) => state.logout)

  const { data: isValid, isLoading } = useAdminVerify()

  // Check if token is expired locally
  const isExpired = expiresAt ? new Date(expiresAt) <= new Date() : true

  useEffect(() => {
    // Redirect if no token or token is expired
    if (!token || isExpired) {
      logout()
      navigate('/admin/login', { replace: true })
      return
    }

    // Redirect if token verification failed
    if (!isLoading && isValid === false) {
      logout()
      navigate('/admin/login', { replace: true })
    }
  }, [token, isExpired, isValid, isLoading, logout, navigate])

  // Show loading while verifying
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          <Skeleton className="h-8 w-48" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </div>
          <Skeleton className="h-64" />
        </div>
      </div>
    )
  }

  // Don't render children if not authenticated
  if (!token || isExpired || !isValid) {
    return null
  }

  return <>{children}</>
}
