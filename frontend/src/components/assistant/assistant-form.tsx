import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import type { AssistantCreate, AssistantUpdate, Assistant } from '@/types'

const DEFAULT_MODELS = [
  { value: 'anthropic/claude-3.5-sonnet', label: 'Claude 3.5 Sonnet' },
  { value: 'anthropic/claude-3-opus', label: 'Claude 3 Opus' },
  { value: 'openai/gpt-4-turbo', label: 'GPT-4 Turbo' },
  { value: 'openai/gpt-4o', label: 'GPT-4o' },
  { value: 'google/gemini-pro-1.5', label: 'Gemini Pro 1.5' },
  { value: 'meta-llama/llama-3-70b-instruct', label: 'Llama 3 70B' },
]

interface AssistantFormProps {
  assistant?: Assistant
  onSubmit: (data: AssistantCreate | AssistantUpdate) => void
  onCancel: () => void
  isLoading?: boolean
}

export function AssistantForm({ assistant, onSubmit, onCancel, isLoading }: AssistantFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<AssistantCreate>({
    defaultValues: assistant ? {
      name: assistant.name,
      description: assistant.description ?? '',
      instructions: assistant.instructions,
      model: assistant.model,
      temperature: assistant.temperature,
      max_tokens: assistant.max_tokens,
    } : {
      name: '',
      description: '',
      instructions: '',
      model: 'anthropic/claude-3.5-sonnet',
      temperature: 0.7,
      max_tokens: 4096,
    },
  })

  const temperature = watch('temperature')
  const maxTokens = watch('max_tokens')

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">Name *</Label>
        <Input
          id="name"
          {...register('name', { required: 'Name is required' })}
          placeholder="My Assistant"
        />
        {errors.name && (
          <p className="text-sm text-destructive">{errors.name.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Input
          id="description"
          {...register('description')}
          placeholder="A brief description of what this assistant does"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="instructions">Instructions *</Label>
        <Textarea
          id="instructions"
          {...register('instructions', { required: 'Instructions are required' })}
          placeholder="You are a helpful assistant that..."
          rows={6}
        />
        {errors.instructions && (
          <p className="text-sm text-destructive">{errors.instructions.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="model">Model</Label>
        <Select
          id="model"
          {...register('model')}
          options={DEFAULT_MODELS}
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>Temperature</Label>
          <span className="text-sm text-muted-foreground">{temperature}</span>
        </div>
        <Slider
          value={temperature}
          min={0}
          max={2}
          step={0.1}
          onChange={(value) => setValue('temperature', value)}
        />
        <p className="text-xs text-muted-foreground">
          Higher values make output more random, lower values more deterministic
        </p>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>Max Tokens</Label>
          <span className="text-sm text-muted-foreground">{maxTokens}</span>
        </div>
        <Slider
          value={maxTokens}
          min={256}
          max={8192}
          step={256}
          onChange={(value) => setValue('max_tokens', value)}
        />
        <p className="text-xs text-muted-foreground">
          Maximum number of tokens in the response
        </p>
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : assistant ? 'Update' : 'Create'}
        </Button>
      </div>
    </form>
  )
}
