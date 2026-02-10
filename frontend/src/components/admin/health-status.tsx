import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import type { SystemHealth, ComponentHealth, HealthStatus } from '@/types'
import { cn } from '@/lib/utils'

interface HealthStatusProps {
  health: SystemHealth | undefined
  isLoading?: boolean
}

export function HealthStatusCard({ health, isLoading }: HealthStatusProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </CardContent>
      </Card>
    )
  }

  if (!health) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Health</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <HealthItem
          name="Database"
          health={health.database}
        />
        <HealthItem
          name="OpenRouter API"
          health={health.openrouter}
        />
        <HealthItem
          name="ChromaDB"
          health={health.chromadb}
        />
        <div className="border-t pt-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">API Key Status</span>
            {health.api_key_configured ? (
              <div className="text-right">
                <Badge variant="outline" className="text-green-600 border-green-600">
                  Configured
                </Badge>
                {health.api_key_masked && (
                  <p className="text-xs text-muted-foreground mt-1 font-mono">
                    {health.api_key_masked}
                  </p>
                )}
              </div>
            ) : (
              <Badge variant="outline" className="text-red-600 border-red-600">
                Not Configured
              </Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

interface HealthItemProps {
  name: string
  health: ComponentHealth
}

function HealthItem({ name, health }: HealthItemProps) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm font-medium">{name}</span>
      <div className="flex items-center gap-2">
        {health.latency_ms !== undefined && (
          <span className="text-xs text-muted-foreground">
            {health.latency_ms}ms
          </span>
        )}
        <StatusBadge status={health.status} />
      </div>
    </div>
  )
}

interface StatusBadgeProps {
  status: HealthStatus
}

function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig = {
    healthy: {
      label: 'Healthy',
      className: 'text-green-600 border-green-600 bg-green-50 dark:bg-green-950',
    },
    degraded: {
      label: 'Degraded',
      className: 'text-yellow-600 border-yellow-600 bg-yellow-50 dark:bg-yellow-950',
    },
    unhealthy: {
      label: 'Unhealthy',
      className: 'text-red-600 border-red-600 bg-red-50 dark:bg-red-950',
    },
  }

  const config = statusConfig[status]

  return (
    <Badge variant="outline" className={cn(config.className)}>
      {config.label}
    </Badge>
  )
}
