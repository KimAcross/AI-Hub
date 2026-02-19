import { useState } from 'react'
import { AdminLayout } from '@/components/admin/admin-layout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { QuotaDisplay } from '@/components/admin/usage/quota-display'
import { UsageChart } from '@/components/admin/usage-chart'
import {
  useGlobalQuota,
  useUpdateGlobalQuota,
  useUsageStatus,
  useDailyUsage,
  useUsageSummary,
} from '@/hooks/use-admin'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Settings, Loader2, TrendingUp, DollarSign, Hash, Clock } from 'lucide-react'
import type { QuotaUpdate } from '@/types'

function QuotaSettingsDialog({
  open,
  onOpenChange,
  currentQuota,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  currentQuota: QuotaUpdate | null
}) {
  const [dailyCostLimit, setDailyCostLimit] = useState<string>('')
  const [monthlyCostLimit, setMonthlyCostLimit] = useState<string>('')
  const [dailyTokenLimit, setDailyTokenLimit] = useState<string>('')
  const [monthlyTokenLimit, setMonthlyTokenLimit] = useState<string>('')
  const [requestsPerMinute, setRequestsPerMinute] = useState<string>('')
  const [requestsPerHour, setRequestsPerHour] = useState<string>('')
  const [alertThreshold, setAlertThreshold] = useState<string>('80')

  const updateQuota = useUpdateGlobalQuota()

  // Initialize form when dialog opens
  useState(() => {
    if (currentQuota && open) {
      setDailyCostLimit(currentQuota.daily_cost_limit_usd?.toString() || '')
      setMonthlyCostLimit(currentQuota.monthly_cost_limit_usd?.toString() || '')
      setDailyTokenLimit(currentQuota.daily_token_limit?.toString() || '')
      setMonthlyTokenLimit(currentQuota.monthly_token_limit?.toString() || '')
      setRequestsPerMinute(currentQuota.requests_per_minute?.toString() || '')
      setRequestsPerHour(currentQuota.requests_per_hour?.toString() || '')
      setAlertThreshold(currentQuota.alert_threshold_percent?.toString() || '80')
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const quotaData: QuotaUpdate = {
      daily_cost_limit_usd: dailyCostLimit ? parseFloat(dailyCostLimit) : null,
      monthly_cost_limit_usd: monthlyCostLimit ? parseFloat(monthlyCostLimit) : null,
      daily_token_limit: dailyTokenLimit ? parseInt(dailyTokenLimit) : null,
      monthly_token_limit: monthlyTokenLimit ? parseInt(monthlyTokenLimit) : null,
      requests_per_minute: requestsPerMinute ? parseInt(requestsPerMinute) : null,
      requests_per_hour: requestsPerHour ? parseInt(requestsPerHour) : null,
      alert_threshold_percent: alertThreshold ? parseInt(alertThreshold) : 80,
    }

    updateQuota.mutate(quotaData, {
      onSuccess: () => {
        onOpenChange(false)
      },
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Configure Quota Settings</DialogTitle>
          <DialogDescription>
            Set usage limits to control costs. Leave blank for no limit.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="dailyCostLimit">Daily Cost Limit (USD)</Label>
              <Input
                id="dailyCostLimit"
                type="number"
                step="0.01"
                min="0"
                value={dailyCostLimit}
                onChange={(e) => setDailyCostLimit(e.target.value)}
                placeholder="e.g., 10.00"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="monthlyCostLimit">Monthly Cost Limit (USD)</Label>
              <Input
                id="monthlyCostLimit"
                type="number"
                step="0.01"
                min="0"
                value={monthlyCostLimit}
                onChange={(e) => setMonthlyCostLimit(e.target.value)}
                placeholder="e.g., 100.00"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="dailyTokenLimit">Daily Token Limit</Label>
              <Input
                id="dailyTokenLimit"
                type="number"
                min="0"
                value={dailyTokenLimit}
                onChange={(e) => setDailyTokenLimit(e.target.value)}
                placeholder="e.g., 1000000"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="monthlyTokenLimit">Monthly Token Limit</Label>
              <Input
                id="monthlyTokenLimit"
                type="number"
                min="0"
                value={monthlyTokenLimit}
                onChange={(e) => setMonthlyTokenLimit(e.target.value)}
                placeholder="e.g., 10000000"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="requestsPerMinute">Requests per Minute</Label>
              <Input
                id="requestsPerMinute"
                type="number"
                min="0"
                value={requestsPerMinute}
                onChange={(e) => setRequestsPerMinute(e.target.value)}
                placeholder="e.g., 60"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="requestsPerHour">Requests per Hour</Label>
              <Input
                id="requestsPerHour"
                type="number"
                min="0"
                value={requestsPerHour}
                onChange={(e) => setRequestsPerHour(e.target.value)}
                placeholder="e.g., 1000"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="alertThreshold">Alert Threshold (%)</Label>
            <Input
              id="alertThreshold"
              type="number"
              min="0"
              max="100"
              value={alertThreshold}
              onChange={(e) => setAlertThreshold(e.target.value)}
              placeholder="80"
            />
            <p className="text-xs text-muted-foreground">
              Trigger alerts when usage exceeds this percentage of the limit
            </p>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={updateQuota.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={updateQuota.isPending}>
              {updateQuota.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Save Settings
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

function UsagePageContent() {
  const [settingsOpen, setSettingsOpen] = useState(false)

  const { data: quota } = useGlobalQuota()
  const { data: usageStatus, isLoading: isLoadingStatus } = useUsageStatus()
  const { data: dailyUsage, isLoading: isLoadingDaily } = useDailyUsage(30)
  const { data: summary, isLoading: isLoadingSummary } = useUsageSummary()

  const formatCurrency = (value: number) => `$${value.toFixed(2)}`
  const formatNumber = (value: number) => value.toLocaleString()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Usage & Quotas</h1>
          <p className="text-muted-foreground">
            Monitor usage and configure spending limits
          </p>
        </div>
        <Button onClick={() => setSettingsOpen(true)}>
          <Settings className="mr-2 h-4 w-4" />
          Configure Limits
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Tokens (30d)</p>
                {isLoadingSummary ? (
                  <Skeleton className="h-7 w-24 mt-1" />
                ) : (
                  <p className="text-2xl font-semibold">
                    {formatNumber(summary?.total_tokens || 0)}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-green-500/10 rounded-lg">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Cost (30d)</p>
                {isLoadingSummary ? (
                  <Skeleton className="h-7 w-24 mt-1" />
                ) : (
                  <p className="text-2xl font-semibold">
                    {formatCurrency(Number(summary?.total_cost_usd) || 0)}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <Hash className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Messages (30d)</p>
                {isLoadingSummary ? (
                  <Skeleton className="h-7 w-24 mt-1" />
                ) : (
                  <p className="text-2xl font-semibold">
                    {formatNumber(summary?.total_messages || 0)}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-orange-500/10 rounded-lg">
                <Clock className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Conversations (30d)</p>
                {isLoadingSummary ? (
                  <Skeleton className="h-7 w-24 mt-1" />
                ) : (
                  <p className="text-2xl font-semibold">
                    {formatNumber(summary?.total_conversations || 0)}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Current Usage vs Limits */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Cost Usage</CardTitle>
            <CardDescription>Current spending vs limits</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {isLoadingStatus ? (
              <div className="space-y-4">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : usageStatus ? (
              <>
                <QuotaDisplay
                  label="Daily Cost"
                  used={usageStatus.daily_cost_used}
                  limit={usageStatus.daily_cost_limit}
                  percent={usageStatus.daily_cost_percent}
                  unit="USD"
                  format={formatCurrency}
                />
                <QuotaDisplay
                  label="Monthly Cost"
                  used={usageStatus.monthly_cost_used}
                  limit={usageStatus.monthly_cost_limit}
                  percent={usageStatus.monthly_cost_percent}
                  unit="USD"
                  format={formatCurrency}
                />
              </>
            ) : (
              <p className="text-sm text-muted-foreground">No usage data available</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Token Usage</CardTitle>
            <CardDescription>Current token consumption vs limits</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {isLoadingStatus ? (
              <div className="space-y-4">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : usageStatus ? (
              <>
                <QuotaDisplay
                  label="Daily Tokens"
                  used={usageStatus.daily_tokens_used}
                  limit={usageStatus.daily_token_limit}
                  percent={usageStatus.daily_token_percent}
                  unit="tokens"
                  format={formatNumber}
                />
                <QuotaDisplay
                  label="Monthly Tokens"
                  used={usageStatus.monthly_tokens_used}
                  limit={usageStatus.monthly_token_limit}
                  percent={usageStatus.monthly_token_percent}
                  unit="tokens"
                  format={formatNumber}
                />
              </>
            ) : (
              <p className="text-sm text-muted-foreground">No usage data available</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Usage Chart */}
      <UsageChart data={dailyUsage?.data || []} isLoading={isLoadingDaily} />

      {/* Quota Settings Dialog */}
      <QuotaSettingsDialog
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
        currentQuota={quota || null}
      />
    </div>
  )
}

export function AdminUsagePage() {
  return (
    <AdminLayout>
      <UsagePageContent />
    </AdminLayout>
  )
}
