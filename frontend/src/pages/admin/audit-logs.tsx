import { useState } from 'react'
import { AdminLayout } from '@/components/admin/admin-layout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { useAuditLogs, useAuditSummary } from '@/hooks/use-admin'
import { Search, FileText, ChevronLeft, ChevronRight, Download } from 'lucide-react'
import { useAdminStore } from '@/stores/admin-store'
import type { AuditLog, AuditLogQuery } from '@/types'

const actionColors: Record<string, string> = {
  create: 'bg-green-500/10 text-green-600',
  update: 'bg-blue-500/10 text-blue-600',
  delete: 'bg-red-500/10 text-red-600',
  login: 'bg-purple-500/10 text-purple-600',
  logout: 'bg-gray-500/10 text-gray-600',
  rotate: 'bg-orange-500/10 text-orange-600',
  test: 'bg-cyan-500/10 text-cyan-600',
  default: 'bg-gray-500/10 text-gray-600',
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function getActionColor(action: string): string {
  const key = Object.keys(actionColors).find((k) => action.toLowerCase().includes(k))
  return actionColors[key || 'default']
}

function AuditLogDetails({
  log,
  open,
  onOpenChange,
}: {
  log: AuditLog | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  if (!log) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Audit Log Details</DialogTitle>
          <DialogDescription>
            Action performed at {formatDate(log.created_at)}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Action</p>
              <Badge className={getActionColor(log.action)}>{log.action}</Badge>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Resource</p>
              <p className="font-medium">{log.resource_type}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Actor</p>
              <p className="font-medium">{log.actor}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Resource ID</p>
              <p className="font-mono text-sm">{log.resource_id || 'N/A'}</p>
            </div>
          </div>

          {log.ip_address && (
            <div>
              <p className="text-sm text-muted-foreground">IP Address</p>
              <p className="font-mono text-sm">{log.ip_address}</p>
            </div>
          )}

          {log.details && Object.keys(log.details).length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Details</p>
              <pre className="p-3 rounded-lg bg-muted text-sm overflow-auto max-h-40">
                {JSON.stringify(log.details, null, 2)}
              </pre>
            </div>
          )}

          {log.old_values && Object.keys(log.old_values).length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Previous Values</p>
              <pre className="p-3 rounded-lg bg-red-500/10 text-sm overflow-auto max-h-40">
                {JSON.stringify(log.old_values, null, 2)}
              </pre>
            </div>
          )}

          {log.new_values && Object.keys(log.new_values).length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">New Values</p>
              <pre className="p-3 rounded-lg bg-green-500/10 text-sm overflow-auto max-h-40">
                {JSON.stringify(log.new_values, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

function AuditLogsPageContent() {
  const [query, setQuery] = useState<AuditLogQuery>({
    limit: 50,
    offset: 0,
  })
  const [actionFilter, setActionFilter] = useState<string>('all')
  const [resourceFilter, setResourceFilter] = useState<string>('all')
  const [searchActor, setSearchActor] = useState('')

  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null)
  const [detailsOpen, setDetailsOpen] = useState(false)

  const { data: logsData, isLoading: isLoadingLogs } = useAuditLogs({
    ...query,
    action: actionFilter !== 'all' ? actionFilter : undefined,
    resource_type: resourceFilter !== 'all' ? resourceFilter : undefined,
    actor: searchActor || undefined,
  })

  const { data: summaryData } = useAuditSummary(30)

  const handleViewDetails = (log: AuditLog) => {
    setSelectedLog(log)
    setDetailsOpen(true)
  }

  const handlePageChange = (direction: 'prev' | 'next') => {
    const newOffset =
      direction === 'next'
        ? (query.offset || 0) + (query.limit || 50)
        : Math.max(0, (query.offset || 0) - (query.limit || 50))
    setQuery({ ...query, offset: newOffset })
  }

  const logs = logsData?.items || []
  const total = logsData?.total || 0
  const currentPage = Math.floor((query.offset || 0) / (query.limit || 50)) + 1
  const totalPages = Math.ceil(total / (query.limit || 50))

  // Get unique actions and resources from summary for filters
  const uniqueActions = summaryData?.summary.map((s) => s.action) || []
  const resourceTypes = ['user', 'api_key', 'quota', 'settings', 'auth']

  const token = useAdminStore((state) => state.token)

  const handleExport = (format: 'csv' | 'json') => {
    if (!token) return
    const params = new URLSearchParams({ format, limit: '10000' })
    if (actionFilter !== 'all') params.append('action', actionFilter)
    const url = `/api/v1/admin/audit/export?${params.toString()}`
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `audit-logs.${format}`)
    // Add auth header via fetch and create blob URL
    fetch(url, { headers: { 'X-Admin-Token': token } })
      .then((res) => res.blob())
      .then((blob) => {
        const blobUrl = URL.createObjectURL(blob)
        link.href = blobUrl
        link.click()
        URL.revokeObjectURL(blobUrl)
      })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Audit Logs</h1>
          <p className="text-muted-foreground">
            Track and review all administrative actions
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => handleExport('csv')}>
            <Download className="h-4 w-4 mr-2" />
            CSV
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('json')}>
            <Download className="h-4 w-4 mr-2" />
            JSON
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {summaryData?.summary.slice(0, 6).map((item) => (
          <Card key={item.action}>
            <CardContent className="pt-4">
              <div className="text-center">
                <Badge className={getActionColor(item.action)} variant="secondary">
                  {item.action}
                </Badge>
                <p className="text-2xl font-semibold mt-2">{item.count}</p>
                <p className="text-xs text-muted-foreground">Last 30 days</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Activity Log
          </CardTitle>
          <CardDescription>
            Complete history of administrative actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by actor..."
                value={searchActor}
                onChange={(e) => {
                  setSearchActor(e.target.value)
                  setQuery({ ...query, offset: 0 })
                }}
                className="pl-10"
              />
            </div>
            <Select
              value={actionFilter}
              onValueChange={(v) => {
                setActionFilter(v)
                setQuery({ ...query, offset: 0 })
              }}
            >
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Action" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Actions</SelectItem>
                {uniqueActions.map((action) => (
                  <SelectItem key={action} value={action}>
                    {action}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={resourceFilter}
              onValueChange={(v) => {
                setResourceFilter(v)
                setQuery({ ...query, offset: 0 })
              }}
            >
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Resource" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Resources</SelectItem>
                {resourceTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Table */}
          {isLoadingLogs ? (
            <div className="space-y-3">
              {Array.from({ length: 10 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No audit logs found
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Resource</TableHead>
                  <TableHead>Actor</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead className="w-[100px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                      {formatDate(log.created_at)}
                    </TableCell>
                    <TableCell>
                      <Badge className={getActionColor(log.action)} variant="secondary">
                        {log.action}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="font-medium">{log.resource_type}</span>
                      {log.resource_id && (
                        <span className="text-xs text-muted-foreground ml-2">
                          #{log.resource_id.slice(0, 8)}
                        </span>
                      )}
                    </TableCell>
                    <TableCell>{log.actor}</TableCell>
                    <TableCell className="font-mono text-sm text-muted-foreground">
                      {log.ip_address || '-'}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewDetails(log)}
                      >
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {/* Pagination */}
          {total > 0 && (
            <div className="flex items-center justify-between mt-6">
              <p className="text-sm text-muted-foreground">
                Showing {(query.offset || 0) + 1} to{' '}
                {Math.min((query.offset || 0) + (query.limit || 50), total)} of {total}{' '}
                entries
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange('prev')}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange('next')}
                  disabled={currentPage >= totalPages}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <AuditLogDetails
        log={selectedLog}
        open={detailsOpen}
        onOpenChange={setDetailsOpen}
      />
    </div>
  )
}

export function AdminAuditLogsPage() {
  return (
    <AdminLayout>
      <AuditLogsPageContent />
    </AdminLayout>
  )
}
