import * as React from 'react'
import { ChevronDown, Check, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { LLMModel } from '@/types'

interface ModelSelectorProps {
  models: LLMModel[]
  selectedModel: string
  onSelect: (modelId: string) => void
  isLoading?: boolean
  disabled?: boolean
}

export function ModelSelector({
  models,
  selectedModel,
  onSelect,
  isLoading = false,
  disabled = false,
}: ModelSelectorProps) {
  const [open, setOpen] = React.useState(false)
  const dropdownRef = React.useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Group models by provider
  const groupedModels = React.useMemo(() => {
    const groups: Record<string, LLMModel[]> = {}

    models.forEach((model) => {
      const provider = model.id.split('/')[0] || 'Other'
      if (!groups[provider]) {
        groups[provider] = []
      }
      groups[provider].push(model)
    })

    return groups
  }, [models])

  const selectedModelData = models.find((m) => m.id === selectedModel)
  const displayName = selectedModelData?.name || selectedModel.split('/').pop() || 'Select model'

  return (
    <div className="relative" ref={dropdownRef}>
      <Button
        variant="outline"
        size="sm"
        className="gap-2 min-w-[180px] justify-between"
        onClick={() => setOpen(!open)}
        disabled={disabled || isLoading}
      >
        <div className="flex items-center gap-2 truncate">
          <Sparkles className="h-4 w-4 shrink-0 text-muted-foreground" />
          <span className="truncate">{displayName}</span>
        </div>
        <ChevronDown
          className={cn(
            "h-4 w-4 shrink-0 transition-transform text-muted-foreground",
            open && "rotate-180"
          )}
        />
      </Button>

      {open && (
        <div className="absolute left-0 top-full mt-1 z-50 w-80 rounded-md border bg-popover shadow-lg">
          <div className="max-h-80 overflow-y-auto p-1">
            {Object.entries(groupedModels).map(([provider, providerModels]) => (
              <div key={provider}>
                <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  {provider}
                </div>
                {providerModels.map((model) => (
                  <button
                    key={model.id}
                    className={cn(
                      "flex w-full items-center justify-between gap-2 rounded-sm px-2 py-2 text-sm hover:bg-accent",
                      selectedModel === model.id && "bg-accent"
                    )}
                    onClick={() => {
                      onSelect(model.id)
                      setOpen(false)
                    }}
                  >
                    <div className="flex-1 min-w-0 text-left">
                      <div className="font-medium truncate">{model.name}</div>
                      <div className="text-xs text-muted-foreground truncate">
                        {model.context_length.toLocaleString()} tokens
                        {model.pricing && (
                          <> · ${model.pricing.prompt}/1K in</>
                        )}
                      </div>
                    </div>
                    {selectedModel === model.id && (
                      <Check className="h-4 w-4 shrink-0 text-primary" />
                    )}
                  </button>
                ))}
              </div>
            ))}

            {models.length === 0 && (
              <div className="p-4 text-center text-sm text-muted-foreground">
                {isLoading ? 'Loading models...' : 'No models available'}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
