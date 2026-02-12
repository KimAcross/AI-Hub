import * as React from 'react'
import { Bot, ChevronDown, Settings } from 'lucide-react'
import { Link } from 'react-router-dom'
import { MessageList } from './message-list'
import { MessageInput } from './message-input'
import { ModelSelector } from './model-selector'
import { Button } from '@/components/ui/button'
import type { Message, LLMModel, Assistant } from '@/types'

interface ChatWindowProps {
  messages: Message[]
  models: LLMModel[]
  selectedModel: string
  onModelChange: (modelId: string) => void
  onSendMessage: (content: string) => void
  onStopGeneration?: () => void
  onRegenerate?: (messageId: string) => void
  onEditMessage?: (messageId: string) => void
  onFeedback?: (messageId: string, feedback: 'positive' | 'negative', reason?: string) => void
  streamingContent?: string
  isStreaming?: boolean
  isLoadingMessages?: boolean
  isLoadingModels?: boolean
  assistant?: Assistant | null
  assistants?: Assistant[]
  onAssistantChange?: (assistantId: string) => void
  conversationTitle?: string
}

export function ChatWindow({
  messages,
  models,
  selectedModel,
  onModelChange,
  onSendMessage,
  onStopGeneration,
  onRegenerate,
  onEditMessage,
  onFeedback,
  streamingContent,
  isStreaming = false,
  isLoadingMessages = false,
  isLoadingModels = false,
  assistant,
  assistants = [],
  onAssistantChange,
  conversationTitle,
}: ChatWindowProps) {
  const [assistantMenuOpen, setAssistantMenuOpen] = React.useState(false)
  return (
    <div className="flex-1 flex flex-col h-full min-w-0">
      {/* Header */}
      <div className="border-b bg-background px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3 min-w-0">
          {assistant && (
            <>
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                {assistant.avatar_url ? (
                  <img
                    src={assistant.avatar_url}
                    alt={assistant.name}
                    className="h-8 w-8 rounded-full object-cover"
                  />
                ) : (
                  <Bot className="h-4 w-4 text-primary" />
                )}
              </div>
              <div className="min-w-0 relative">
                {onAssistantChange && assistants.length > 1 ? (
                  <button
                    className="flex items-center gap-1 hover:text-primary transition-colors"
                    onClick={() => setAssistantMenuOpen(!assistantMenuOpen)}
                  >
                    <h2 className="font-semibold truncate">{assistant.name}</h2>
                    <ChevronDown className="h-3.5 w-3.5 shrink-0 opacity-50" />
                  </button>
                ) : (
                  <h2 className="font-semibold truncate">{assistant.name}</h2>
                )}
                {conversationTitle && (
                  <p className="text-xs text-muted-foreground truncate">
                    {conversationTitle}
                  </p>
                )}

                {/* Assistant switcher dropdown */}
                {assistantMenuOpen && (
                  <>
                    <div className="fixed inset-0 z-10" onClick={() => setAssistantMenuOpen(false)} />
                    <div className="absolute left-0 top-full mt-1 z-20 w-64 max-h-80 overflow-auto rounded-md border bg-popover p-1 shadow-md">
                      {assistants.map((a) => (
                        <button
                          key={a.id}
                          className={`flex w-full items-center gap-2 rounded-sm px-2 py-2 text-sm hover:bg-accent ${
                            a.id === assistant.id ? 'bg-accent' : ''
                          }`}
                          onClick={() => {
                            setAssistantMenuOpen(false)
                            if (a.id !== assistant.id) {
                              onAssistantChange?.(a.id)
                            }
                          }}
                        >
                          <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10">
                            {a.avatar_url ? (
                              <img src={a.avatar_url} alt={a.name} className="h-7 w-7 rounded-full object-cover" />
                            ) : (
                              <Bot className="h-3.5 w-3.5 text-primary" />
                            )}
                          </div>
                          <div className="min-w-0 text-left">
                            <div className="font-medium truncate">{a.name}</div>
                            <div className="text-xs text-muted-foreground truncate">
                              {a.model.split('/').pop()}
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </>
          )}

          {!assistant && conversationTitle && (
            <h2 className="font-semibold truncate">{conversationTitle}</h2>
          )}

          {!assistant && !conversationTitle && (
            <h2 className="font-semibold">New Chat</h2>
          )}
        </div>

        <div className="flex items-center gap-2">
          <ModelSelector
            models={models}
            selectedModel={selectedModel}
            onSelect={onModelChange}
            isLoading={isLoadingModels}
            disabled={isStreaming}
          />

          {assistant && (
            <Link to={`/assistants/${assistant.id}`}>
              <Button variant="ghost" size="icon" title="Assistant settings">
                <Settings className="h-4 w-4" />
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Assistant context banner */}
      {assistant && messages.length === 0 && !isStreaming && (
        <div className="bg-muted/30 border-b px-4 py-6">
          <div className="max-w-2xl mx-auto text-center">
            <div className="flex h-16 w-16 mx-auto items-center justify-center rounded-full bg-primary/10 mb-4">
              {assistant.avatar_url ? (
                <img
                  src={assistant.avatar_url}
                  alt={assistant.name}
                  className="h-16 w-16 rounded-full object-cover"
                />
              ) : (
                <Bot className="h-8 w-8 text-primary" />
              )}
            </div>
            <h3 className="text-lg font-semibold mb-1">{assistant.name}</h3>
            {assistant.description && (
              <p className="text-sm text-muted-foreground mb-2">
                {assistant.description}
              </p>
            )}
            <p className="text-xs text-muted-foreground">
              {assistant.files_count
                ? `${assistant.files_count} files in knowledge base`
                : 'No knowledge base files'}
            </p>
          </div>
        </div>
      )}

      {/* Messages */}
      <MessageList
        messages={messages}
        isLoading={isLoadingMessages}
        streamingContent={streamingContent}
        isStreaming={isStreaming}
        onRegenerate={onRegenerate}
        onEditMessage={onEditMessage}
        onFeedback={onFeedback}
      />

      {/* Input */}
      <MessageInput
        onSend={onSendMessage}
        onStop={onStopGeneration}
        isLoading={isStreaming}
        disabled={isLoadingMessages}
      />
    </div>
  )
}
