import {
  Coins,
  MessageSquare,
  Users,
  TrendingUp,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { AdminLayout } from '@/components/admin/admin-layout'
import { StatsCard, StatsCardGrid } from '@/components/admin/stats-card'
import { UsageChart } from '@/components/admin/usage-chart'
import { HealthStatusCard } from '@/components/admin/health-status'
import {
  useUsageSummary,
  useUsageBreakdown,
  useDailyUsage,
  useSystemHealth,
} from '@/hooks/use-admin'

function AdminDashboardContent() {
  const { data: summary, isLoading: isLoadingSummary } = useUsageSummary()
  const { data: breakdown, isLoading: isLoadingBreakdown } = useUsageBreakdown()
  const { data: dailyUsage, isLoading: isLoadingDaily } = useDailyUsage(30)
  const { data: health, isLoading: isLoadingHealth } = useSystemHealth()

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    }).format(value)
  }

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US').format(value)
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="text-muted-foreground">Overview of system usage and health</p>
      </div>

      {/* Stats Cards */}
      <StatsCardGrid>
        <StatsCard
          title="Total Tokens"
          value={summary ? formatNumber(summary.total_tokens) : '-'}
          description="Last 30 days"
          icon={<TrendingUp className="h-4 w-4" />}
          isLoading={isLoadingSummary}
        />
        <StatsCard
          title="Total Cost"
          value={summary ? formatCurrency(Number(summary.total_cost_usd)) : '-'}
          description="Last 30 days"
          icon={<Coins className="h-4 w-4" />}
          isLoading={isLoadingSummary}
        />
        <StatsCard
          title="Conversations"
          value={summary ? formatNumber(summary.total_conversations) : '-'}
          description="Last 30 days"
          icon={<Users className="h-4 w-4" />}
          isLoading={isLoadingSummary}
        />
        <StatsCard
          title="Messages"
          value={summary ? formatNumber(summary.total_messages) : '-'}
          description="Last 30 days"
          icon={<MessageSquare className="h-4 w-4" />}
          isLoading={isLoadingSummary}
        />
      </StatsCardGrid>

      {/* Usage Chart */}
      <UsageChart data={dailyUsage?.data || []} isLoading={isLoadingDaily} />

      {/* Two Column Layout for Breakdown and Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Usage Breakdown */}
        <div className="lg:col-span-2 space-y-6">
          {/* By Model */}
          <Card>
            <CardHeader>
              <CardTitle>Usage by Model</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingBreakdown ? (
                <div className="space-y-2">
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                </div>
              ) : breakdown?.by_model && breakdown.by_model.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Model</TableHead>
                      <TableHead className="text-right">Tokens</TableHead>
                      <TableHead className="text-right">Cost</TableHead>
                      <TableHead className="text-right">Messages</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {breakdown.by_model.map((item) => (
                      <TableRow key={item.model}>
                        <TableCell className="font-medium">
                          {item.model}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatNumber(item.total_tokens)}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(Number(item.cost_usd))}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatNumber(item.message_count)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No usage data yet
                </p>
              )}
            </CardContent>
          </Card>

          {/* By Assistant */}
          <Card>
            <CardHeader>
              <CardTitle>Usage by Assistant</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingBreakdown ? (
                <div className="space-y-2">
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                </div>
              ) : breakdown?.by_assistant && breakdown.by_assistant.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Assistant</TableHead>
                      <TableHead className="text-right">Tokens</TableHead>
                      <TableHead className="text-right">Cost</TableHead>
                      <TableHead className="text-right">Messages</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {breakdown.by_assistant.map((item) => (
                      <TableRow key={item.assistant_id || 'unknown'}>
                        <TableCell className="font-medium">
                          {item.assistant_name || 'Unknown'}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatNumber(item.total_tokens)}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(Number(item.cost_usd))}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatNumber(item.message_count)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No usage data yet
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Health Status */}
        <div>
          <HealthStatusCard health={health} isLoading={isLoadingHealth} />
        </div>
      </div>
    </div>
  )
}

export function AdminDashboardPage() {
  return (
    <AdminLayout>
      <AdminDashboardContent />
    </AdminLayout>
  )
}
