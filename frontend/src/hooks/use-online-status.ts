import { useState, useEffect, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'

interface OnlineStatus {
  isOnline: boolean
  isReconnecting: boolean
  lastOnline: Date | null
}

export function useOnlineStatus(): OnlineStatus {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [isReconnecting, setIsReconnecting] = useState(false)
  const [lastOnline, setLastOnline] = useState<Date | null>(
    navigator.onLine ? new Date() : null
  )
  const queryClient = useQueryClient()

  const handleOnline = useCallback(() => {
    setIsOnline(true)
    setIsReconnecting(true)
    setLastOnline(new Date())

    // Invalidate queries to refetch fresh data after reconnecting
    queryClient.invalidateQueries()

    // Stop showing reconnecting state after a short delay
    setTimeout(() => {
      setIsReconnecting(false)
    }, 2000)
  }, [queryClient])

  const handleOffline = useCallback(() => {
    setIsOnline(false)
    setIsReconnecting(false)
  }, [])

  useEffect(() => {
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [handleOnline, handleOffline])

  // Periodically check actual connectivity by pinging the API
  useEffect(() => {
    if (!isOnline) return

    const checkConnectivity = async () => {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 5000)

        const response = await fetch('/api/v1/health', {
          method: 'GET',
          signal: controller.signal,
        })

        clearTimeout(timeoutId)

        if (!response.ok) {
          handleOffline()
        }
      } catch {
        // If we can't reach the API, we might be offline or server is down
        // Only mark as offline if browser also reports offline
        if (!navigator.onLine) {
          handleOffline()
        }
      }
    }

    // Check connectivity every 30 seconds
    const intervalId = setInterval(checkConnectivity, 30000)

    return () => clearInterval(intervalId)
  }, [isOnline, handleOffline])

  return { isOnline, isReconnecting, lastOnline }
}
