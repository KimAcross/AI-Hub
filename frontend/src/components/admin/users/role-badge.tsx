import { Badge } from '@/components/ui/badge'
import { UserRole } from '@/types'

interface RoleBadgeProps {
  role: UserRole
}

const roleConfig: Record<UserRole, { label: string; variant: 'default' | 'secondary' | 'destructive' }> = {
  admin: { label: 'Admin', variant: 'destructive' },
  manager: { label: 'Manager', variant: 'default' },
  user: { label: 'User', variant: 'secondary' },
}

export function RoleBadge({ role }: RoleBadgeProps) {
  const config = roleConfig[role]
  return <Badge variant={config.variant}>{config.label}</Badge>
}
