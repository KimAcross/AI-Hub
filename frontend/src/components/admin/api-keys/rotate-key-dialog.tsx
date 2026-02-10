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
import { useRotateProviderKey } from '@/hooks/use-admin'
import { Loader2 } from 'lucide-react'

interface RotateKeyDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  keyId: string
  keyName: string
}

export function RotateKeyDialog({
  open,
  onOpenChange,
  keyId,
  keyName,
}: RotateKeyDialogProps) {
  const [newApiKey, setNewApiKey] = useState('')

  const rotateKey = useRotateProviderKey()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    rotateKey.mutate(
      { keyId, newApiKey },
      {
        onSuccess: () => {
          setNewApiKey('')
          onOpenChange(false)
        },
      }
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Rotate API Key</DialogTitle>
          <DialogDescription>
            Replace the API key for "{keyName}" with a new one.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="newApiKey">New API Key</Label>
            <Input
              id="newApiKey"
              type="password"
              value={newApiKey}
              onChange={(e) => setNewApiKey(e.target.value)}
              placeholder="Enter new API key"
              required
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={rotateKey.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={rotateKey.isPending || !newApiKey}>
              {rotateKey.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Rotate Key
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
