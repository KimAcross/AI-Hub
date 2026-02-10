import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  MoreHorizontal,
  Pencil,
  RefreshCw,
  Star,
  Trash2,
  TestTube,
  Loader2,
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import type { ProviderApiKey, APIKeyStatus } from '@/types'

interface ApiKeyTableProps {
  keys: ProviderApiKey[]
  isLoading: boolean
  testingKeyId: string | null
  onEdit: (key: ProviderApiKey) => void
  onRotate: (key: ProviderApiKey) => void
  onTest: (key: ProviderApiKey) => void
  onSetDefault: (key: ProviderApiKey) => void
  onDelete: (key: ProviderApiKey) => void
}

function formatDate(dateString: string | null) {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function getStatusBadge(status: APIKeyStatus, error?: string | null) {
  switch (status) {
    case 'valid':
      return (
        <Badge variant="secondary" className="bg-green-500/10 text-green-600">
          Valid
        </Badge>
      )
    case 'invalid':
      return (
        <Badge
          variant="secondary"
          className="bg-red-500/10 text-red-600"
          title={error || undefined}
        >
          Invalid
        </Badge>
      )
    default:
      return (
        <Badge variant="secondary" className="bg-yellow-500/10 text-yellow-600">
          Untested
        </Badge>
      )
  }
}

const providerLabels: Record<string, string> = {
  openrouter: 'OpenRouter',
  openai: 'OpenAI',
  anthropic: 'Anthropic',
  google: 'Google AI',
  azure: 'Azure OpenAI',
  custom: 'Custom',
}

export function ApiKeyTable({
  keys,
  isLoading,
  testingKeyId,
  onEdit,
  onRotate,
  onTest,
  onSetDefault,
  onDelete,
}: ApiKeyTableProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    )
  }

  if (keys.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No API keys configured
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Provider</TableHead>
          <TableHead>Name</TableHead>
          <TableHead>Key</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Last Tested</TableHead>
          <TableHead>Last Used</TableHead>
          <TableHead className="w-[70px]"></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {keys.map((key) => (
          <TableRow key={key.id}>
            <TableCell>
              <div className="flex items-center gap-2">
                <span className="font-medium">
                  {providerLabels[key.provider] || key.provider}
                </span>
                {key.is_default && (
                  <Badge variant="outline" className="text-xs">
                    <Star className="h-3 w-3 mr-1" />
                    Default
                  </Badge>
                )}
              </div>
            </TableCell>
            <TableCell>{key.name}</TableCell>
            <TableCell className="font-mono text-sm text-muted-foreground">
              {key.key_masked}
            </TableCell>
            <TableCell>
              {testingKeyId === key.id ? (
                <Badge variant="secondary" className="bg-blue-500/10 text-blue-600">
                  <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                  Testing...
                </Badge>
              ) : (
                getStatusBadge(key.test_status, key.test_error)
              )}
            </TableCell>
            <TableCell className="text-sm text-muted-foreground">
              {formatDate(key.last_tested_at)}
            </TableCell>
            <TableCell className="text-sm text-muted-foreground">
              {formatDate(key.last_used_at)}
            </TableCell>
            <TableCell>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => onTest(key)}>
                    <TestTube className="mr-2 h-4 w-4" />
                    Test Connection
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onEdit(key)}>
                    <Pencil className="mr-2 h-4 w-4" />
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onRotate(key)}>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Rotate Key
                  </DropdownMenuItem>
                  {!key.is_default && (
                    <DropdownMenuItem onClick={() => onSetDefault(key)}>
                      <Star className="mr-2 h-4 w-4" />
                      Set as Default
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => onDelete(key)}
                    className="text-destructive focus:text-destructive"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
