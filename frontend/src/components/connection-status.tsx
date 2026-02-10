import { useOnlineStatus } from '@/hooks/use-online-status'
import { WifiOff, RefreshCw, Wifi } from 'lucide-react'
import { cn } from '@/lib/utils'

export function ConnectionStatus() {
  const { isOnline, isReconnecting } = useOnlineStatus()

  if (isOnline && !isReconnecting) {
    return null
  }

  return (
    <div
      className={cn(
        'fixed top-0 left-0 right-0 z-50 px-4 py-2 text-center text-sm font-medium transition-all duration-300',
        isReconnecting
          ? 'bg-green-500 text-white'
          : 'bg-yellow-500 text-yellow-900'
      )}
    >
      <div className="flex items-center justify-center gap-2">
        {isReconnecting ? (
          <>
            <Wifi className="h-4 w-4" />
            <span>Reconnected! Refreshing data...</span>
            <RefreshCw className="h-4 w-4 animate-spin" />
          </>
        ) : (
          <>
            <WifiOff className="h-4 w-4" />
            <span>You're offline. Some features may be unavailable.</span>
          </>
        )}
      </div>
    </div>
  )
}
