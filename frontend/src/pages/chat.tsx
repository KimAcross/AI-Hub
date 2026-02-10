import * as React from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { ChatWindow, ConversationSidebar, MessageEditDialog } from '@/components/chat'
import {
  useConversations,
  useConversation,
  useCreateConversation,
  useUpdateConversation,
  useDeleteConversation,
  useExportConversation,
  useModels,
  useAssistant,
  conversationKeys,
} from '@/hooks'
import { useAppStore } from '@/stores/app-store'
import { conversationsApi } from '@/lib/api'
import toast from 'react-hot-toast'
import type { Message } from '@/types'

const DEFAULT_MODEL = 'anthropic/claude-3.5-sonnet'

export function ChatPage() {
  const queryClient = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  const assistantIdParam = searchParams.get('assistant')
  const conversationIdParam = searchParams.get('conversation')

  // State
  const [selectedConversationId, setSelectedConversationId] = React.useState<string | null>(
    conversationIdParam
  )
  const [selectedModel, setSelectedModel] = React.useState(DEFAULT_MODEL)
  const [isStreaming, setIsStreaming] = React.useState(false)
  const [streamingContent, setStreamingContent] = React.useState('')
  const { selectedAssistantId } = useAppStore()
  const abortControllerRef = React.useRef<AbortController | null>(null)

  // Edit message state
  const [editingMessage, setEditingMessage] = React.useState<Message | null>(null)
  const [isEditSaving, setIsEditSaving] = React.useState(false)

  // Use assistant from URL param or global store
  const activeAssistantId = assistantIdParam || selectedAssistantId

  // Queries
  const { data: conversations = [], isLoading: isLoadingConversations } = useConversations(
    activeAssistantId || undefined
  )
  const { data: conversation, isLoading: isLoadingConversation } = useConversation(
    selectedConversationId || ''
  )
  const { data: models = [], isLoading: isLoadingModels } = useModels()
  const { data: assistant } = useAssistant(activeAssistantId || '')

  // Mutations
  const createConversation = useCreateConversation()
  const updateConversation = useUpdateConversation()
  const deleteConversation = useDeleteConversation()
  const exportConversation = useExportConversation()

  // Initialize model from assistant settings
  React.useEffect(() => {
    if (assistant?.model) {
      setSelectedModel(assistant.model)
    }
  }, [assistant])

  // Sync URL params
  React.useEffect(() => {
    const params = new URLSearchParams()
    if (activeAssistantId) params.set('assistant', activeAssistantId)
    if (selectedConversationId) params.set('conversation', selectedConversationId)
    setSearchParams(params, { replace: true })
  }, [activeAssistantId, selectedConversationId, setSearchParams])

  // Handle new chat
  const handleNewChat = async () => {
    setSelectedConversationId(null)
  }

  // Handle conversation selection
  const handleSelectConversation = (id: string) => {
    setSelectedConversationId(id)
  }

  // Handle conversation delete
  const handleDeleteConversation = async (id: string) => {
    await deleteConversation.mutateAsync(id)
    if (selectedConversationId === id) {
      setSelectedConversationId(null)
    }
  }

  // Handle conversation rename
  const handleRenameConversation = async (id: string, title: string) => {
    await updateConversation.mutateAsync({ id, title })
  }

  // Handle conversation export
  const handleExportConversation = async (id: string) => {
    await exportConversation.mutateAsync({ id, format: 'markdown' })
  }

  // Handle send message
  const handleSendMessage = async (content: string) => {
    let conversationId = selectedConversationId

    // Create conversation if needed
    if (!conversationId) {
      try {
        const newConversation = await createConversation.mutateAsync({
          assistant_id: activeAssistantId,
          title: content.slice(0, 50) + (content.length > 50 ? '...' : ''),
        })
        conversationId = newConversation.id
        setSelectedConversationId(conversationId)
      } catch {
        return
      }
    }

    // Start streaming
    setIsStreaming(true)
    setStreamingContent('')
    abortControllerRef.current = new AbortController()

    try {
      await conversationsApi.sendMessage(
        conversationId,
        { content, model: selectedModel },
        (chunk: string) => {
          setStreamingContent((prev) => prev + chunk)
        }
      )

      // Refresh conversation to get updated messages
      queryClient.invalidateQueries({
        queryKey: conversationKeys.detail(conversationId),
      })
      queryClient.invalidateQueries({
        queryKey: conversationKeys.lists(),
      })
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        toast.error(error.message || 'Failed to send message')
      }
    } finally {
      setIsStreaming(false)
      setStreamingContent('')
      abortControllerRef.current = null
    }
  }

  // Handle stop generation
  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setIsStreaming(false)
      setStreamingContent('')
    }
  }

  // Handle model change
  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId)
  }

  // Handle edit message - open dialog
  const handleEditMessage = (messageId: string) => {
    const message = messages.find((m) => m.id === messageId)
    if (message && message.role === 'user') {
      setEditingMessage(message)
    }
  }

  // Handle save edited message
  const handleSaveEditedMessage = async (newContent: string) => {
    if (!editingMessage || !selectedConversationId) return

    setIsEditSaving(true)

    try {
      // Edit the message via API
      await conversationsApi.editMessage(
        selectedConversationId,
        editingMessage.id,
        newContent
      )

      // Close the dialog
      setEditingMessage(null)

      // Refresh conversation to get updated messages
      queryClient.invalidateQueries({
        queryKey: conversationKeys.detail(selectedConversationId),
      })

      // Now regenerate the assistant response by sending the edited message
      setIsStreaming(true)
      setStreamingContent('')
      abortControllerRef.current = new AbortController()

      try {
        await conversationsApi.sendMessage(
          selectedConversationId,
          { content: newContent, model: selectedModel },
          (chunk: string) => {
            setStreamingContent((prev) => prev + chunk)
          }
        )

        // Refresh conversation
        queryClient.invalidateQueries({
          queryKey: conversationKeys.detail(selectedConversationId),
        })
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          toast.error(error.message || 'Failed to regenerate response')
        }
      } finally {
        setIsStreaming(false)
        setStreamingContent('')
        abortControllerRef.current = null
      }

      toast.success('Message updated')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to edit message')
    } finally {
      setIsEditSaving(false)
    }
  }

  // Handle regenerate response
  const handleRegenerate = async (messageId: string) => {
    if (!selectedConversationId || isStreaming) return

    // Find the user message before this assistant message
    const messageIndex = messages.findIndex((m) => m.id === messageId)
    if (messageIndex <= 0) return

    const userMessage = messages[messageIndex - 1]
    if (userMessage.role !== 'user') return

    // Resend the user message to regenerate
    setIsStreaming(true)
    setStreamingContent('')
    abortControllerRef.current = new AbortController()

    try {
      await conversationsApi.sendMessage(
        selectedConversationId,
        { content: userMessage.content, model: selectedModel },
        (chunk: string) => {
          setStreamingContent((prev) => prev + chunk)
        }
      )

      // Refresh conversation
      queryClient.invalidateQueries({
        queryKey: conversationKeys.detail(selectedConversationId),
      })
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        toast.error(error.message || 'Failed to regenerate response')
      }
    } finally {
      setIsStreaming(false)
      setStreamingContent('')
      abortControllerRef.current = null
    }
  }

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  // Messages from conversation
  const messages = conversation?.messages || []

  return (
    <div className="flex h-screen">
      {/* Conversation sidebar */}
      <ConversationSidebar
        conversations={conversations}
        selectedId={selectedConversationId || undefined}
        onSelect={handleSelectConversation}
        onNewChat={handleNewChat}
        onDelete={handleDeleteConversation}
        onRename={handleRenameConversation}
        onExport={handleExportConversation}
        isLoading={isLoadingConversations}
      />

      {/* Main chat area */}
      <ChatWindow
        messages={messages}
        models={models}
        selectedModel={selectedModel}
        onModelChange={handleModelChange}
        onSendMessage={handleSendMessage}
        onStopGeneration={handleStopGeneration}
        onRegenerate={handleRegenerate}
        onEditMessage={handleEditMessage}
        streamingContent={streamingContent}
        isStreaming={isStreaming}
        isLoadingMessages={isLoadingConversation}
        isLoadingModels={isLoadingModels}
        assistant={assistant}
        conversationTitle={conversation?.title}
      />

      {/* Edit message dialog */}
      <MessageEditDialog
        open={!!editingMessage}
        onOpenChange={(open) => !open && setEditingMessage(null)}
        initialContent={editingMessage?.content || ''}
        onSave={handleSaveEditedMessage}
        isLoading={isEditSaving}
      />
    </div>
  )
}
