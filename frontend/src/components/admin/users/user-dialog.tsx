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
import { useCreateUser, useUpdateUser } from '@/hooks/use-admin'
import type { User, UserRole } from '@/types'
import { Loader2 } from 'lucide-react'

interface UserDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  user?: User | null
  mode: 'create' | 'edit'
}

export function UserDialog({ open, onOpenChange, user, mode }: UserDialogProps) {
  const [name, setName] = useState(mode === 'edit' && user ? user.name : '')
  const [email, setEmail] = useState(mode === 'edit' && user ? user.email : '')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<UserRole>(mode === 'edit' && user ? user.role : 'user')

  const createUser = useCreateUser()
  const updateUser = useUpdateUser()

  const isLoading = createUser.isPending || updateUser.isPending

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (mode === 'create') {
      createUser.mutate(
        { name, email, password, role },
        {
          onSuccess: () => {
            onOpenChange(false)
          },
        }
      )
    } else if (user) {
      updateUser.mutate(
        { userId: user.id, userData: { name, email, role } },
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
            {mode === 'create' ? 'Create New User' : 'Edit User'}
          </DialogTitle>
          <DialogDescription>
            {mode === 'create'
              ? 'Add a new user to the system.'
              : 'Update user information.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="john@example.com"
              required
            />
          </div>

          {mode === 'create' && (
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter a strong password"
                required
                minLength={8}
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Select
              value={role}
              onValueChange={(v) => setRole(v as UserRole)}
              options={[
                { value: 'user', label: 'User' },
                { value: 'manager', label: 'Manager' },
                { value: 'admin', label: 'Admin' },
              ]}
              placeholder="Select role"
              id="role"
            />
          </div>

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
              {mode === 'create' ? 'Create User' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
