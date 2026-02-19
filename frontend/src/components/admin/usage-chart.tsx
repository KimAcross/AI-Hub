import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { DailyUsage } from '@/types'

interface UsageChartProps {
  data: DailyUsage[]
  isLoading?: boolean
}

export function UsageChart({ data, isLoading }: UsageChartProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    )
  }

  // Format data for the chart
  const chartData = data.map((item) => ({
    date: formatDate(item.date),
    tokens: item.total_tokens,
    cost: Number(item.cost_usd),
    messages: item.message_count,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Daily Usage (Last 30 Days)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
              />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
                tickFormatter={(value) => `$${value.toFixed(2)}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                }}
                formatter={(value: number | string | undefined, name: string | undefined) => {
                  const numericValue =
                    typeof value === 'number' ? value : Number(value ?? 0)
                  if (name === 'cost') {
                    return [`$${numericValue.toFixed(4)}`, 'Cost']
                  }
                  if (name === 'tokens') {
                    return [numericValue.toLocaleString(), 'Tokens']
                  }
                  return [numericValue, name]
                }}
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="tokens"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={false}
                name="Tokens"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="cost"
                stroke="hsl(142.1 76.2% 36.3%)"
                strokeWidth={2}
                dot={false}
                name="Cost (USD)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
