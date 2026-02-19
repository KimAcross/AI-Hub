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
      max_retrieval_chunks: assistant.max_retrieval_chunks,
      max_context_tokens: assistant.max_context_tokens,
    } : {
      name: '',
      description: '',
      instructions: '',
      model: 'anthropic/claude-3.5-sonnet',
      temperature: 0.7,
      max_tokens: 4096,
      max_retrieval_chunks: 5,
      max_context_tokens: 4000,
    },
  })

  const temperature = watch('temperature')
  const maxTokens = watch('max_tokens')
  const maxRetrievalChunks = watch('max_retrieval_chunks')
  const maxContextTokens = watch('max_context_tokens')

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

      <div className="space-y-4 rounded-md border p-4">
        <div>
          <h3 className="text-sm font-medium">Advanced: RAG Settings</h3>
          <p className="text-xs text-muted-foreground">
            Control retrieval breadth and context budget per assistant
          </p>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label>Max Retrieval Chunks</Label>
            <span className="text-sm text-muted-foreground">{maxRetrievalChunks}</span>
          </div>
          <Slider
            value={maxRetrievalChunks}
            min={1}
            max={20}
            step={1}
            onChange={(value) => setValue('max_retrieval_chunks', value)}
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label>Max Context Tokens</Label>
            <span className="text-sm text-muted-foreground">{maxContextTokens}</span>
          </div>
          <Slider
            value={maxContextTokens}
            min={512}
            max={16000}
            step={128}
            onChange={(value) => setValue('max_context_tokens', value)}
          />
        </div>
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
