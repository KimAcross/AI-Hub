import { useState } from 'react'
import { AdminLayout } from '@/components/admin/admin-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { UserTable } from '@/components/admin/users/user-table'
import { UserDialog } from '@/components/admin/users/user-dialog'
import { PasswordResetDialog } from '@/components/admin/users/password-reset-dialog'
import {
  useUsers,
  useDisableUser,
  useEnableUser,
  useDeleteUser,
} from '@/hooks/use-admin'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Plus, Search, Loader2 } from 'lucide-react'
import type { User, UserRole } from '@/types'

function UsersPageContent() {
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState<UserRole | 'all'>('all')
  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'disabled'>('all')
  const [page, setPage] = useState(1)

  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create')
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

  const [passwordResetOpen, setPasswordResetOpen] = useState(false)
  const [passwordResetUser, setPasswordResetUser] = useState<User | null>(null)

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [userToDelete, setUserToDelete] = useState<User | null>(null)

  const { data, isLoading } = useUsers({
    search: search || undefined,
    role: roleFilter !== 'all' ? roleFilter : undefined,
    is_active: activeFilter === 'all' ? undefined : activeFilter === 'active',
    page,
    size: 20,
  })

  const disableUser = useDisableUser()
  const enableUser = useEnableUser()
  const deleteUser = useDeleteUser()

  const handleCreateUser = () => {
    setSelectedUser(null)
    setDialogMode('create')
    setDialogOpen(true)
  }

  const handleEditUser = (user: User) => {
    setSelectedUser(user)
    setDialogMode('edit')
    setDialogOpen(true)
  }

  const handleResetPassword = (user: User) => {
    setPasswordResetUser(user)
    setPasswordResetOpen(true)
  }

  const handleDisableUser = (user: User) => {
    disableUser.mutate(user.id)
  }

  const handleEnableUser = (user: User) => {
    enableUser.mutate(user.id)
  }

  const handleDeleteClick = (user: User) => {
    setUserToDelete(user)
    setDeleteDialogOpen(true)
  }

  const handleConfirmDelete = () => {
    if (userToDelete) {
      deleteUser.mutate(userToDelete.id, {
        onSuccess: () => {
          setDeleteDialogOpen(false)
          setUserToDelete(null)
        },
      })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">User Management</h1>
          <p className="text-muted-foreground">
            Manage user accounts and permissions
          </p>
        </div>
        <Button onClick={handleCreateUser}>
          <Plus className="mr-2 h-4 w-4" />
          Add User
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Users</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by name or email..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value)
                  setPage(1)
                }}
                className="pl-10"
              />
            </div>
            <Select
              value={roleFilter}
              onValueChange={(v) => {
                setRoleFilter(v as UserRole | 'all')
                setPage(1)
              }}
            >
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Roles</SelectItem>
                <SelectItem value="admin">Admin</SelectItem>
                <SelectItem value="manager">Manager</SelectItem>
                <SelectItem value="user">User</SelectItem>
              </SelectContent>
            </Select>
            <Select
              value={activeFilter}
              onValueChange={(v) => {
                setActiveFilter(v as 'all' | 'active' | 'disabled')
                setPage(1)
              }}
            >
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="disabled">Disabled</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Table */}
          <UserTable
            users={data?.users || []}
            isLoading={isLoading}
            onEdit={handleEditUser}
            onResetPassword={handleResetPassword}
            onDisable={handleDisableUser}
            onEnable={handleEnableUser}
            onDelete={handleDeleteClick}
          />

          {/* Pagination */}
          {data && data.pages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <p className="text-sm text-muted-foreground">
                Showing {(page - 1) * 20 + 1} to{' '}
                {Math.min(page * 20, data.total)} of {data.total} users
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={page >= data.pages}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialogs */}
      <UserDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        user={selectedUser}
        mode={dialogMode}
      />

      {passwordResetUser && (
        <PasswordResetDialog
          open={passwordResetOpen}
          onOpenChange={setPasswordResetOpen}
          userId={passwordResetUser.id}
          userName={passwordResetUser.name}
        />
      )}

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete User</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete {userToDelete?.name}? This action
              cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={deleteUser.isPending}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={deleteUser.isPending}
            >
              {deleteUser.isPending && (
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

export function AdminUsersPage() {
  return (
    <AdminLayout>
      <UsersPageContent />
    </AdminLayout>
  )
}
