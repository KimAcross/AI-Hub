import { useState, useEffect } from 'react'
import type { FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Lock, Loader2, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAdminLogin } from '@/hooks/use-admin'
import { useAdminStore } from '@/stores/admin-store'

export function AdminLoginPage() {
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const adminLogin = useAdminLogin()
  const token = useAdminStore((state) => state.token)
  const expiresAt = useAdminStore((state) => state.expiresAt)

  // Redirect if already authenticated
  useEffect(() => {
    if (token && expiresAt) {
      const expiry = new Date(expiresAt)
      if (expiry > new Date()) {
        navigate('/admin', { replace: true })
      }
    }
  }, [token, expiresAt, navigate])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!password.trim()) return

    try {
      await adminLogin.mutateAsync(password)
      navigate('/admin', { replace: true })
    } catch {
      // Error is handled by the mutation
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card>
          <CardHeader className="space-y-1">
            <div className="flex items-center justify-center mb-4">
              <div className="p-3 rounded-full bg-primary/10">
                <Lock className="h-8 w-8 text-primary" />
              </div>
            </div>
            <CardTitle className="text-2xl text-center">Admin Dashboard</CardTitle>
            <CardDescription className="text-center">
              Enter your admin password to access the dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter admin password"
                  autoComplete="current-password"
                  autoFocus
                />
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={!password.trim() || adminLogin.isPending}
              >
                {adminLogin.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign in'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <Link
                to="/"
                className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-1"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Application
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
