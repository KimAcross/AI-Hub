// Assistant Types
export interface Assistant {
  id: string
  name: string
  description: string | null
  instructions: string
  model: string
  temperature: number
  max_tokens: number
  max_retrieval_chunks: number
  max_context_tokens: number
  avatar_url: string | null
  is_deleted: boolean
  created_at: string
  updated_at: string
  files_count?: number
}

export interface AssistantCreate {
  name: string
  description?: string | null
  instructions: string
  model?: string
  temperature?: number
  max_tokens?: number
  max_retrieval_chunks?: number
  max_context_tokens?: number
  avatar_url?: string | null
}

export interface AssistantUpdate {
  name?: string
  description?: string | null
  instructions?: string
  model?: string
  temperature?: number
  max_tokens?: number
  max_retrieval_chunks?: number
  max_context_tokens?: number
  avatar_url?: string | null
}

export interface AssistantTemplate {
  id: string
  name: string
  description: string
  instructions: string
  model: string
  temperature: number
  max_tokens: number
  category: string
}

// File Types
export type FileStatus = 'uploading' | 'processing' | 'indexing' | 'ready' | 'error'

export interface KnowledgeFile {
  id: string
  assistant_id: string
  filename: string
  file_type: string
  file_path: string
  size_bytes: number
  chunk_count: number | null
  status: FileStatus
  error_message: string | null
  created_at: string
  updated_at: string
}

// Conversation Types
export interface Conversation {
  id: string
  assistant_id: string | null
  title: string
  created_at: string
  updated_at: string
  messages?: Message[]
}

export interface ConversationCreate {
  assistant_id?: string
  title?: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  model: string | null
  tokens_used: {
    prompt_tokens?: number
    completion_tokens?: number
    total_tokens?: number
  } | null
  created_at: string
  feedback?: 'positive' | 'negative' | null
  feedback_reason?: string | null
}

export interface MessageCreate {
  content: string
  model?: string
}

// Model Types
export interface LLMModel {
  id: string
  name: string
  description: string
  context_length: number
  pricing: {
    prompt: number
    completion: number
  }
}

// Settings Types
export interface AppSettings {
  openrouter_api_key_set: boolean
  default_model: string
  embedding_model: string
  max_file_size_mb: number
  language: string
  streaming_enabled: boolean
  auto_save_interval: number
}

export interface SettingsUpdate {
  openrouter_api_key?: string | null
  default_model?: string | null
  language?: string | null
  streaming_enabled?: boolean | null
  auto_save_interval?: number | null
}

export interface ApiKeyTestResult {
  valid: boolean
  error?: string
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ApiError {
  detail: string
  status_code?: number
}

// Admin Types
export interface AdminLoginRequest {
  password: string
}

export interface AdminLoginResponse {
  token: string
  expires_at: string
  csrf_token: string
}

export interface UsageSummary {
  total_tokens: number
  total_prompt_tokens: number
  total_completion_tokens: number
  total_cost_usd: number
  total_conversations: number
  total_messages: number
  period_start: string
  period_end: string
}

export interface UsageByModel {
  model: string
  total_tokens: number
  prompt_tokens: number
  completion_tokens: number
  cost_usd: number
  message_count: number
}

export interface UsageByAssistant {
  assistant_id: string | null
  assistant_name: string | null
  total_tokens: number
  prompt_tokens: number
  completion_tokens: number
  cost_usd: number
  message_count: number
}

export interface UsageBreakdown {
  by_model: UsageByModel[]
  by_assistant: UsageByAssistant[]
}

export interface DailyUsage {
  date: string
  total_tokens: number
  prompt_tokens: number
  completion_tokens: number
  cost_usd: number
  message_count: number
}

export interface DailyUsageResponse {
  data: DailyUsage[]
  days: number
}

export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy'

export interface ComponentHealth {
  status: HealthStatus
  latency_ms?: number
  error?: string
}

export interface SystemHealth {
  database: ComponentHealth
  openrouter: ComponentHealth
  chromadb: ComponentHealth
  api_key_configured: boolean
  api_key_masked?: string
}

// User Management Types
export type UserRole = 'admin' | 'manager' | 'user'

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  is_active: boolean
  is_verified: boolean
  last_login_at: string | null
  created_at: string
  updated_at: string
}

export interface UserCreate {
  email: string
  password: string
  name: string
  role?: UserRole
}

export interface UserUpdate {
  email?: string
  name?: string
  role?: UserRole
}

export interface UserListResponse {
  users: User[]
  total: number
  page: number
  size: number
  pages: number
}

export interface UserLoginRequest {
  email: string
  password: string
}

export interface UserLoginResponse {
  token: string
  expires_at: string
  csrf_token: string
  user: User
}

// User API Key Types
export interface UserApiKey {
  id: string
  name: string
  key_prefix: string
  last_used_at: string | null
  expires_at: string | null
  is_active: boolean
  created_at: string
}

export interface UserApiKeyCreate {
  name: string
  expires_in_days?: number
}

export interface UserApiKeyCreateResponse extends UserApiKey {
  key: string
}

// Provider API Key Types
export type APIKeyProvider = 'openrouter' | 'openai' | 'anthropic' | 'google' | 'azure' | 'custom'
export type APIKeyStatus = 'valid' | 'invalid' | 'untested'

export interface ProviderApiKey {
  id: string
  provider: APIKeyProvider
  name: string
  key_masked: string
  is_active: boolean
  is_default: boolean
  last_used_at: string | null
  last_tested_at: string | null
  test_status: APIKeyStatus
  test_error: string | null
  created_at: string
  updated_at: string
}

export interface ProviderApiKeyCreate {
  provider: APIKeyProvider
  name: string
  api_key: string
  is_default?: boolean
}

export interface ProviderApiKeyUpdate {
  name?: string
  is_active?: boolean
}

export interface ProviderApiKeyTestResult {
  valid: boolean
  error?: string
  latency_ms?: number
}

export interface ProviderApiKeyListResponse {
  keys: ProviderApiKey[]
  total: number
}

// Quota Types
export type QuotaScope = 'global' | 'user'

export interface UsageQuota {
  id: string
  scope: QuotaScope
  scope_id: string | null
  daily_cost_limit_usd: number | null
  monthly_cost_limit_usd: number | null
  daily_token_limit: number | null
  monthly_token_limit: number | null
  requests_per_minute: number | null
  requests_per_hour: number | null
  alert_threshold_percent: number
}

export interface QuotaUpdate {
  daily_cost_limit_usd?: number | null
  monthly_cost_limit_usd?: number | null
  daily_token_limit?: number | null
  monthly_token_limit?: number | null
  requests_per_minute?: number | null
  requests_per_hour?: number | null
  alert_threshold_percent?: number
}

export interface UsageStatus {
  daily_cost_used: number
  daily_cost_limit: number | null
  daily_cost_percent: number | null
  monthly_cost_used: number
  monthly_cost_limit: number | null
  monthly_cost_percent: number | null
  daily_tokens_used: number
  daily_token_limit: number | null
  daily_token_percent: number | null
  monthly_tokens_used: number
  monthly_token_limit: number | null
  monthly_token_percent: number | null
}

export interface QuotaAlert {
  alert_type: 'cost' | 'tokens'
  period: 'daily' | 'monthly'
  current_value: number
  limit_value: number
  percent_used: number
  threshold_percent: number
  is_exceeded: boolean
}

// Audit Log Types
export interface AuditLog {
  id: string
  action: string
  resource_type: string
  resource_id: string | null
  actor: string
  actor_id: string | null
  ip_address: string | null
  user_agent: string | null
  details: Record<string, unknown> | null
  old_values: Record<string, unknown> | null
  new_values: Record<string, unknown> | null
  created_at: string
}

export interface AuditLogListResponse {
  items: AuditLog[]
  total: number
  limit: number
  offset: number
}

export interface AuditLogQuery {
  action?: string
  resource_type?: string
  resource_id?: string
  actor?: string
  start_date?: string
  end_date?: string
  limit?: number
  offset?: number
}

export interface AuditLogSummary {
  action: string
  count: number
}
