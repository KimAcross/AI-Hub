import { AdminLayout } from '@/components/admin/admin-layout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { HealthStatusCard } from '@/components/admin/health-status'
import { useSystemHealth, useGlobalQuota } from '@/hooks/use-admin'
import { Shield, Database, Cpu, Server } from 'lucide-react'

function SettingsPageContent() {
  const { data: health, isLoading: isLoadingHealth } = useSystemHealth()
  const { data: quota, isLoading: isLoadingQuota } = useGlobalQuota()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">System Settings</h1>
        <p className="text-muted-foreground">
          View system configuration and health status
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <HealthStatusCard health={health} isLoading={isLoadingHealth} />

        {/* Current Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              Current Configuration
            </CardTitle>
            <CardDescription>Active system settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoadingQuota ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : quota ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <span className="text-sm text-muted-foreground">Daily Cost Limit</span>
                  <span className="font-medium">
                    {quota.daily_cost_limit_usd
                      ? `$${quota.daily_cost_limit_usd.toFixed(2)}`
                      : 'No limit'}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <span className="text-sm text-muted-foreground">Monthly Cost Limit</span>
                  <span className="font-medium">
                    {quota.monthly_cost_limit_usd
                      ? `$${quota.monthly_cost_limit_usd.toFixed(2)}`
                      : 'No limit'}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <span className="text-sm text-muted-foreground">Rate Limit (per minute)</span>
                  <span className="font-medium">
                    {quota.requests_per_minute
                      ? `${quota.requests_per_minute} requests`
                      : 'No limit'}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <span className="text-sm text-muted-foreground">Alert Threshold</span>
                  <span className="font-medium">{quota.alert_threshold_percent}%</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No configuration data</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* System Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5" />
            System Information
          </CardTitle>
          <CardDescription>Application details and versions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg border bg-card">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Shield className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Application</p>
                  <p className="font-medium">AI-Across</p>
                </div>
              </div>
            </div>
            <div className="p-4 rounded-lg border bg-card">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <Server className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Version</p>
                  <p className="font-medium">1.0.0</p>
                </div>
              </div>
            </div>
            <div className="p-4 rounded-lg border bg-card">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-500/10 rounded-lg">
                  <Database className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Database</p>
                  <Badge variant="secondary" className="bg-green-500/10 text-green-600">
                    {health?.database.status || 'Unknown'}
                  </Badge>
                </div>
              </div>
            </div>
            <div className="p-4 rounded-lg border bg-card">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-500/10 rounded-lg">
                  <Cpu className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Vector DB</p>
                  <Badge
                    variant="secondary"
                    className={
                      health?.chromadb.status === 'healthy'
                        ? 'bg-green-500/10 text-green-600'
                        : 'bg-yellow-500/10 text-yellow-600'
                    }
                  >
                    {health?.chromadb.status || 'Unknown'}
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Settings Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Security Configuration
          </CardTitle>
          <CardDescription>Current security settings (read-only)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">Authentication</span>
              <Badge variant="secondary">JWT + CSRF</Badge>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">Password Hashing</span>
              <Badge variant="secondary">bcrypt (cost 12)</Badge>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">API Key Encryption</span>
              <Badge variant="secondary">Fernet (AES-128)</Badge>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">Rate Limiting</span>
              <Badge variant="secondary">Enabled</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export function AdminSettingsPage() {
  return (
    <AdminLayout>
      <SettingsPageContent />
    </AdminLayout>
  )
}
