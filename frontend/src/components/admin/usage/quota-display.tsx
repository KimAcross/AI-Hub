import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'

interface QuotaDisplayProps {
  label: string
  used: number
  limit: number | null
  percent: number | null
  unit: string
  format?: (value: number) => string
}

export function QuotaDisplay({
  label,
  used,
  limit,
  percent,
  unit,
  format = (v) => v.toLocaleString(),
}: QuotaDisplayProps) {
  const hasLimit = limit !== null && percent !== null

  const getStatusColor = (p: number) => {
    if (p >= 100) return 'text-destructive'
    if (p >= 80) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getProgressColor = (p: number) => {
    if (p >= 100) return 'bg-destructive'
    if (p >= 80) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className={cn('font-medium', hasLimit && getStatusColor(percent!))}>
          {format(used)} {unit}
          {hasLimit && ` / ${format(limit!)} ${unit}`}
        </span>
      </div>
      {hasLimit && (
        <div className="relative">
          <Progress value={Math.min(percent!, 100)} className="h-2" />
          <div
            className={cn(
              'absolute inset-0 h-2 rounded-full transition-all',
              getProgressColor(percent!)
            )}
            style={{ width: `${Math.min(percent!, 100)}%` }}
          />
        </div>
      )}
      {hasLimit && (
        <p className="text-xs text-muted-foreground text-right">
          {percent!.toFixed(1)}% used
        </p>
      )}
    </div>
  )
}
