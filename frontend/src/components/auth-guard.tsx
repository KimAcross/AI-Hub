import { ReactNode, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth-store'
import { useVerifyAuth } from '@/hooks/use-auth'
import { Skeleton } from '@/components/ui/skeleton'

interface AuthGuardProps {
  children: ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const navigate = useNavigate()
  const token = useAuthStore((state) => state.token)
  const expiresAt = useAuthStore((state) => state.expiresAt)
  const logout = useAuthStore((state) => state.logout)

  const { data: isValid, isLoading } = useVerifyAuth()

  // Check if token is expired locally
  const isExpired = expiresAt ? new Date(expiresAt) <= new Date() : true

  useEffect(() => {
    // Redirect if no token or token is expired
    if (!token || isExpired) {
      logout()
      navigate('/login', { replace: true })
      return
    }

    // Redirect if token verification failed
    if (!isLoading && isValid === false) {
      logout()
      navigate('/login', { replace: true })
    }
  }, [token, isExpired, isValid, isLoading, logout, navigate])

  // Show loading while verifying
  if (isLoading) {
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

  // Don't render children if not authenticated
  if (!token || isExpired || !isValid) {
    return null
  }

  return <>{children}</>
}
