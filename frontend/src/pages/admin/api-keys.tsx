import { useState } from 'react'
import { AdminLayout } from '@/components/admin/admin-layout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import { ApiKeyTable } from '@/components/admin/api-keys/api-key-table'
import { ApiKeyDialog } from '@/components/admin/api-keys/api-key-dialog'
import { RotateKeyDialog } from '@/components/admin/api-keys/rotate-key-dialog'
import {
  useProviderKeys,
  useTestProviderKey,
  useSetDefaultProviderKey,
  useDeleteProviderKey,
} from '@/hooks/use-admin'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Plus, Loader2, Key } from 'lucide-react'
import type { ProviderApiKey, APIKeyProvider } from '@/types'

const providers: { value: APIKeyProvider | 'all'; label: string }[] = [
  { value: 'all', label: 'All Providers' },
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google AI' },
  { value: 'azure', label: 'Azure OpenAI' },
  { value: 'custom', label: 'Custom' },
]

function ApiKeysPageContent() {
  const [providerFilter, setProviderFilter] = useState<APIKeyProvider | 'all'>('all')

  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create')
  const [selectedKey, setSelectedKey] = useState<ProviderApiKey | null>(null)

  const [rotateDialogOpen, setRotateDialogOpen] = useState(false)
  const [keyToRotate, setKeyToRotate] = useState<ProviderApiKey | null>(null)

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [keyToDelete, setKeyToDelete] = useState<ProviderApiKey | null>(null)

  const [testingKeyId, setTestingKeyId] = useState<string | null>(null)

  const { data, isLoading } = useProviderKeys(
    providerFilter !== 'all' ? providerFilter : undefined
  )

  const testKey = useTestProviderKey()
  const setDefaultKey = useSetDefaultProviderKey()
  const deleteKey = useDeleteProviderKey()

  const handleAddKey = () => {
    setSelectedKey(null)
    setDialogMode('create')
    setDialogOpen(true)
  }

  const handleEditKey = (key: ProviderApiKey) => {
    setSelectedKey(key)
    setDialogMode('edit')
    setDialogOpen(true)
  }

  const handleRotateKey = (key: ProviderApiKey) => {
    setKeyToRotate(key)
    setRotateDialogOpen(true)
  }

  const handleTestKey = (key: ProviderApiKey) => {
    setTestingKeyId(key.id)
    testKey.mutate(key.id, {
      onSettled: () => {
        setTestingKeyId(null)
      },
    })
  }

  const handleSetDefault = (key: ProviderApiKey) => {
    setDefaultKey.mutate(key.id)
  }

  const handleDeleteClick = (key: ProviderApiKey) => {
    setKeyToDelete(key)
    setDeleteDialogOpen(true)
  }

  const handleConfirmDelete = () => {
    if (keyToDelete) {
      deleteKey.mutate(keyToDelete.id, {
        onSuccess: () => {
          setDeleteDialogOpen(false)
          setKeyToDelete(null)
        },
      })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">API Key Management</h1>
          <p className="text-muted-foreground">
            Manage AI provider API keys
          </p>
        </div>
        <Button onClick={handleAddKey}>
          <Plus className="mr-2 h-4 w-4" />
          Add API Key
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                Provider API Keys
              </CardTitle>
              <CardDescription>
                Configure API keys for different AI providers
              </CardDescription>
            </div>
            <Select
              value={providerFilter}
              onValueChange={(v) => setProviderFilter(v as APIKeyProvider | 'all')}
              options={providers}
              placeholder="Filter by provider"
              className="w-[180px]"
            />
          </div>
        </CardHeader>
        <CardContent>
          <ApiKeyTable
            keys={data?.keys || []}
            isLoading={isLoading}
            testingKeyId={testingKeyId}
            onEdit={handleEditKey}
            onRotate={handleRotateKey}
            onTest={handleTestKey}
            onSetDefault={handleSetDefault}
            onDelete={handleDeleteClick}
          />
        </CardContent>
      </Card>

      {/* Dialogs */}
      <ApiKeyDialog
        key={`${dialogMode}-${selectedKey?.id ?? 'new'}-${dialogOpen ? 'open' : 'closed'}`}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        apiKey={selectedKey}
        mode={dialogMode}
      />

      {keyToRotate && (
        <RotateKeyDialog
          open={rotateDialogOpen}
          onOpenChange={setRotateDialogOpen}
          keyId={keyToRotate.id}
          keyName={keyToRotate.name}
        />
      )}

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete API Key</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{keyToDelete?.name}"? This action
              cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={deleteKey.isPending}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={deleteKey.isPending}
            >
              {deleteKey.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export function AdminApiKeysPage() {
  return (
    <AdminLayout>
      <ApiKeysPageContent />
    </AdminLayout>
  )
}
