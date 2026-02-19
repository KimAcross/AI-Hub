import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { useCreateProviderKey, useUpdateProviderKey } from '@/hooks/use-admin'
import type { ProviderApiKey, APIKeyProvider } from '@/types'
import { Loader2 } from 'lucide-react'

interface ApiKeyDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  apiKey?: ProviderApiKey | null
  mode: 'create' | 'edit'
}

const providers: { value: APIKeyProvider; label: string }[] = [
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google AI' },
  { value: 'azure', label: 'Azure OpenAI' },
  { value: 'custom', label: 'Custom' },
]

export function ApiKeyDialog({ open, onOpenChange, apiKey, mode }: ApiKeyDialogProps) {
  const [provider, setProvider] = useState<APIKeyProvider>(
    mode === 'edit' && apiKey ? apiKey.provider : 'openrouter'
  )
  const [name, setName] = useState(mode === 'edit' && apiKey ? apiKey.name : '')
  const [key, setKey] = useState('')
  const [isDefault, setIsDefault] = useState(mode === 'edit' && apiKey ? apiKey.is_default : false)

  const createKey = useCreateProviderKey()
  const updateKey = useUpdateProviderKey()

  const isLoading = createKey.isPending || updateKey.isPending

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (mode === 'create') {
      createKey.mutate(
        { provider, name, api_key: key, is_default: isDefault },
        {
          onSuccess: () => {
            onOpenChange(false)
          },
        }
      )
    } else if (apiKey) {
      updateKey.mutate(
        { keyId: apiKey.id, keyData: { name } },
        {
          onSuccess: () => {
            onOpenChange(false)
          },
        }
      )
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {mode === 'create' ? 'Add API Key' : 'Edit API Key'}
          </DialogTitle>
          <DialogDescription>
            {mode === 'create'
              ? 'Add a new AI provider API key.'
              : 'Update API key details.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="provider">Provider</Label>
            <Select
              value={provider}
              onValueChange={(v) => setProvider(v as APIKeyProvider)}
              options={providers}
              placeholder="Select provider"
              disabled={mode === 'edit'}
              id="provider"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Production Key"
              required
            />
          </div>

          {mode === 'create' && (
            <div className="space-y-2">
              <Label htmlFor="api-key">API Key</Label>
              <Input
                id="api-key"
                type="password"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="sk-..."
                required
              />
            </div>
          )}

          {mode === 'create' && (
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is-default"
                checked={isDefault}
                onChange={(e) => setIsDefault(e.target.checked)}
                className="h-4 w-4 rounded border-input"
              />
              <Label htmlFor="is-default" className="font-normal">
                Set as default key for this provider
              </Label>
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {mode === 'create' ? 'Add Key' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
