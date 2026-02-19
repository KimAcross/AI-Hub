import * as React from 'react'
import {
  Settings,
  Key,
  Palette,
  Bot,
  HardDrive,
  Check,
  X,
  Eye,
  EyeOff,
  Loader2,
  Globe,
  Zap,
  Save,
} from 'lucide-react'
import { Header } from '@/components/layout/header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { Slider } from '@/components/ui/slider'
import { useSettings, useUpdateSettings, useTestApiKey, useModels } from '@/hooks'
import { useAppStore } from '@/stores/app-store'
import { useAuthStore } from '@/stores/auth-store'
import toast from 'react-hot-toast'

export function SettingsPage() {
  const { theme, setTheme } = useAppStore()
  const user = useAuthStore((state) => state.user)
  const isAdmin = user?.role === 'admin'
  const { data: settings, isLoading: isLoadingSettings } = useSettings()
  const { data: models, isLoading: isLoadingModels } = useModels()
  const updateSettings = useUpdateSettings()
  const testApiKey = useTestApiKey()

  // Local state for form inputs
  const [apiKey, setApiKey] = React.useState('')
  const [showApiKey, setShowApiKey] = React.useState(false)
  const [selectedModel, setSelectedModel] = React.useState('')
  const [selectedLanguage, setSelectedLanguage] = React.useState('')
  const [streamingEnabled, setStreamingEnabled] = React.useState(true)
  const [autoSaveInterval, setAutoSaveInterval] = React.useState(30)

  // Initialize settings from API
  React.useEffect(() => {
    if (settings?.default_model) {
      setSelectedModel(settings.default_model)
    }
    if (settings?.language) {
      setSelectedLanguage(settings.language)
    }
    if (settings?.streaming_enabled !== undefined) {
      setStreamingEnabled(settings.streaming_enabled)
    }
    if (settings?.auto_save_interval !== undefined) {
      setAutoSaveInterval(settings.auto_save_interval)
    }
  }, [settings])

  const handleSaveApiKey = async () => {
    if (!apiKey.trim()) {
      toast.error('Please enter an API key')
      return
    }

    await updateSettings.mutateAsync({ openrouter_api_key: apiKey })
    setApiKey('')
    setShowApiKey(false)
  }

  const handleClearApiKey = async () => {
    await updateSettings.mutateAsync({ openrouter_api_key: '' })
  }

  const handleTestApiKey = async () => {
    const result = await testApiKey.mutateAsync()
    if (result.valid) {
      toast.success('API key is valid')
    } else {
      toast.error(result.error || 'API key is invalid')
    }
  }

  const handleSaveDefaultModel = async () => {
    if (!selectedModel) return
    await updateSettings.mutateAsync({ default_model: selectedModel })
  }

  const handleSaveLanguage = async () => {
    if (!selectedLanguage) return
    await updateSettings.mutateAsync({ language: selectedLanguage })
  }

  const handleToggleStreaming = async () => {
    const newValue = !streamingEnabled
    setStreamingEnabled(newValue)
    await updateSettings.mutateAsync({ streaming_enabled: newValue })
  }

  const handleSaveAutoSaveInterval = async () => {
    await updateSettings.mutateAsync({ auto_save_interval: autoSaveInterval })
  }

  const themeOptions = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'system', label: 'System' },
  ]

  const modelOptions = React.useMemo(() => {
    if (!models) return []
    return models.map((m) => ({
      value: m.id,
      label: m.name,
    }))
  }, [models])

  const languageOptions = [
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Spanish' },
    { value: 'fr', label: 'French' },
    { value: 'de', label: 'German' },
    { value: 'it', label: 'Italian' },
    { value: 'pt', label: 'Portuguese' },
    { value: 'zh', label: 'Chinese' },
    { value: 'ja', label: 'Japanese' },
    { value: 'ko', label: 'Korean' },
    { value: 'ru', label: 'Russian' },
  ]

  return (
    <div className="flex flex-col h-screen">
      <Header title="Settings" />

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* API Key Configuration (Admin only) */}
          {isAdmin && <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Key className="h-5 w-5 text-muted-foreground" />
                <CardTitle>OpenRouter API Key</CardTitle>
              </div>
              <CardDescription>
                Configure your OpenRouter API key to enable AI model access. Get your API key from{' '}
                <a
                  href="https://openrouter.ai/keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  openrouter.ai/keys
                </a>
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {isLoadingSettings ? (
                <div className="space-y-3">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-10 w-full" />
                </div>
              ) : (
                <>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-muted-foreground">Status:</span>
                    {settings?.openrouter_api_key_set ? (
                      <span className="flex items-center gap-1 text-green-600">
                        <Check className="h-4 w-4" />
                        Configured
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-yellow-600">
                        <X className="h-4 w-4" />
                        Not configured
                      </span>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="api-key">
                      {settings?.openrouter_api_key_set ? 'Update API Key' : 'Enter API Key'}
                    </Label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Input
                          id="api-key"
                          type={showApiKey ? 'text' : 'password'}
                          value={apiKey}
                          onChange={(e) => setApiKey(e.target.value)}
                          placeholder="sk-or-v1-..."
                          className="pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowApiKey(!showApiKey)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        >
                          {showApiKey ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                      <Button
                        onClick={handleSaveApiKey}
                        disabled={!apiKey.trim() || updateSettings.isPending}
                      >
                        {updateSettings.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          'Save'
                        )}
                      </Button>
                    </div>
                  </div>

                  {settings?.openrouter_api_key_set && (
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleTestApiKey}
                        disabled={testApiKey.isPending}
                      >
                        {testApiKey.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        ) : (
                          <Check className="h-4 w-4 mr-2" />
                        )}
                        Test API Key
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleClearApiKey}
                        disabled={updateSettings.isPending}
                      >
                        <X className="h-4 w-4 mr-2" />
                        Clear API Key
                      </Button>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>}

          {/* Theme Settings */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Palette className="h-5 w-5 text-muted-foreground" />
                <CardTitle>Appearance</CardTitle>
              </div>
              <CardDescription>
                Customize the look and feel of the application
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="theme">Theme</Label>
                <Select
                  id="theme"
                  value={theme}
                  onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'system')}
                  options={themeOptions}
                />
                <p className="text-xs text-muted-foreground">
                  Select your preferred color theme. System will follow your OS settings.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Default Model (Admin only) */}
          {isAdmin && <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-muted-foreground" />
                <CardTitle>Default Model</CardTitle>
              </div>
              <CardDescription>
                Choose the default AI model for new conversations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {isLoadingSettings || isLoadingModels ? (
                <div className="space-y-3">
                  <Skeleton className="h-10 w-full" />
                </div>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="default-model">Model</Label>
                  <div className="flex gap-2">
                    <div className="flex-1">
                      <Select
                        id="default-model"
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        options={modelOptions}
                        placeholder="Select a model..."
                      />
                    </div>
                    <Button
                      onClick={handleSaveDefaultModel}
                      disabled={!selectedModel || selectedModel === settings?.default_model || updateSettings.isPending}
                    >
                      {updateSettings.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        'Save'
                      )}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Current: {settings?.default_model || 'Not set'}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>}

          {/* Language Settings */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-muted-foreground" />
                <CardTitle>Language</CardTitle>
              </div>
              <CardDescription>
                Choose your preferred language for the interface
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {isLoadingSettings ? (
                <div className="space-y-3">
                  <Skeleton className="h-10 w-full" />
                </div>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <div className="flex gap-2">
                    <div className="flex-1">
                      <Select
                        id="language"
                        value={selectedLanguage}
                        onChange={(e) => setSelectedLanguage(e.target.value)}
                        options={languageOptions}
                        placeholder="Select a language..."
                      />
                    </div>
                    <Button
                      onClick={handleSaveLanguage}
                      disabled={!selectedLanguage || selectedLanguage === settings?.language || updateSettings.isPending}
                    >
                      {updateSettings.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        'Save'
                      )}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    This setting affects system prompts and AI responses.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Chat Settings (Admin only) */}
          {isAdmin && <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-muted-foreground" />
                <CardTitle>Chat Settings</CardTitle>
              </div>
              <CardDescription>
                Configure how the chat interface behaves
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {isLoadingSettings ? (
                <div className="space-y-3">
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                </div>
              ) : (
                <>
                  {/* Streaming Toggle */}
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Streaming Responses</Label>
                      <p className="text-xs text-muted-foreground">
                        Display AI responses as they are generated
                      </p>
                    </div>
                    <Button
                      variant={streamingEnabled ? 'default' : 'outline'}
                      size="sm"
                      onClick={handleToggleStreaming}
                      disabled={updateSettings.isPending}
                    >
                      {streamingEnabled ? 'Enabled' : 'Disabled'}
                    </Button>
                  </div>

                  {/* Auto-save Interval */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Auto-save Interval</Label>
                        <p className="text-xs text-muted-foreground">
                          How often to auto-save conversations (0 to disable)
                        </p>
                      </div>
                      <span className="text-sm font-medium">
                        {autoSaveInterval === 0 ? 'Disabled' : `${autoSaveInterval}s`}
                      </span>
                    </div>
                    <div className="flex gap-4">
                      <div className="flex-1">
                        <Slider
                          value={autoSaveInterval}
                          onChange={setAutoSaveInterval}
                          max={300}
                          min={0}
                          step={5}
                        />
                      </div>
                      <Button
                        size="sm"
                        onClick={handleSaveAutoSaveInterval}
                        disabled={autoSaveInterval === settings?.auto_save_interval || updateSettings.isPending}
                      >
                        <Save className="h-4 w-4 mr-1" />
                        Save
                      </Button>
                    </div>
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Off</span>
                      <span>5 min</span>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>}

          {/* System Info */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <HardDrive className="h-5 w-5 text-muted-foreground" />
                <CardTitle>System Information</CardTitle>
              </div>
              <CardDescription>
                View system configuration and limits
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingSettings ? (
                <div className="space-y-2">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-4 w-40" />
                </div>
              ) : (
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Embedding Model</span>
                    <span className="font-mono">{settings?.embedding_model}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Max File Size</span>
                    <span>{settings?.max_file_size_mb} MB</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* About */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-muted-foreground" />
                <CardTitle>About AI-Across</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Version</span>
                  <span>1.0.0-beta</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Phase</span>
                  <span>6 - Polish & QA</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
