import { Bot, Settings } from 'lucide-react'
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
  streamingContent?: string
  isStreaming?: boolean
  isLoadingMessages?: boolean
  isLoadingModels?: boolean
  assistant?: Assistant | null
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
  streamingContent,
  isStreaming = false,
  isLoadingMessages = false,
  isLoadingModels = false,
  assistant,
  conversationTitle,
}: ChatWindowProps) {
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
              <div className="min-w-0">
                <h2 className="font-semibold truncate">{assistant.name}</h2>
                {conversationTitle && (
                  <p className="text-xs text-muted-foreground truncate">
                    {conversationTitle}
                  </p>
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
