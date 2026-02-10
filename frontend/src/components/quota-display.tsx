import { Coins, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useUserUsage } from '@/hooks/use-auth'
import { cn } from '@/lib/utils'

function ProgressBar({ value, className }: { value: number; className?: string }) {
  const color =
    value >= 90
      ? 'bg-destructive'
      : value >= 70
        ? 'bg-yellow-500'
        : 'bg-primary'

  return (
    <div className={cn('h-2 rounded-full bg-muted overflow-hidden', className)}>
      <div
        className={cn('h-full rounded-full transition-all', color)}
        style={{ width: `${Math.min(value, 100)}%` }}
      />
    </div>
  )
}

export function QuotaDisplay() {
  const { data: usage } = useUserUsage()

  if (!usage) return null

  const hasLimits =
    usage.daily_cost_limit != null ||
    usage.monthly_cost_limit != null ||
    usage.daily_token_limit != null ||
    usage.monthly_token_limit != null

  if (!hasLimits) return null

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium">Usage</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {usage.daily_cost_limit != null && (
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1 text-muted-foreground">
                <Coins className="h-3 w-3" />
                Daily Cost
              </span>
              <span>
                ${usage.daily_cost_used.toFixed(2)} / ${usage.daily_cost_limit.toFixed(2)}
              </span>
            </div>
            <ProgressBar value={usage.daily_cost_percent ?? 0} />
          </div>
        )}

        {usage.monthly_cost_limit != null && (
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1 text-muted-foreground">
                <Coins className="h-3 w-3" />
                Monthly Cost
              </span>
              <span>
                ${usage.monthly_cost_used.toFixed(2)} / ${usage.monthly_cost_limit.toFixed(2)}
              </span>
            </div>
            <ProgressBar value={usage.monthly_cost_percent ?? 0} />
          </div>
        )}

        {usage.daily_token_limit != null && (
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1 text-muted-foreground">
                <Zap className="h-3 w-3" />
                Daily Tokens
              </span>
              <span>
                {(usage.daily_tokens_used / 1000).toFixed(1)}k / {(usage.daily_token_limit / 1000).toFixed(1)}k
              </span>
            </div>
            <ProgressBar value={usage.daily_token_percent ?? 0} />
          </div>
        )}

        {usage.monthly_token_limit != null && (
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1 text-muted-foreground">
                <Zap className="h-3 w-3" />
                Monthly Tokens
              </span>
              <span>
                {(usage.monthly_tokens_used / 1000).toFixed(1)}k / {(usage.monthly_token_limit / 1000).toFixed(1)}k
              </span>
            </div>
            <ProgressBar value={usage.monthly_token_percent ?? 0} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
