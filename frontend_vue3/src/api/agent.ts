/**
 * Agent API
 */
import { request } from '@/utils/request'

export type AgentTaskStatus = 'pending' | 'running' | 'succeeded' | 'failed'

export type AgentReviewStatus = 'pending_review' | 'approved' | 'rejected' | 'modified'

export type AgentReviewAction = 'approved' | 'rejected' | 'modified'

export type AgentChatIntent =
  | 'ingest'
  | 'query'
  | 'mutate_domain'
  | 'mutate_bulk'
  | 'admin_ops'
  | 'clarify'
  | 'general'

export type AgentChatMode = 'sync' | 'async_task' | 'follow_up'

export interface AgentTaskSubmitResponse {
  task_id: number
  task_type: string
  status: AgentTaskStatus
  file_name: string
  file_path: string
  created_at: string
}

export interface AgentTaskResponse {
  task_id: number
  task_type: string
  status: AgentTaskStatus
  payload?: Record<string, any> | null
  result?: Record<string, any> | null
  error_message?: string | null
  created_at: string
  started_at?: string | null
  finished_at?: string | null
}

export interface AgentReviewRecord {
  record_id: number
  task_id?: number | null
  source_file_path: string
  source_file_name?: string | null
  extracted_data: Record<string, any>
  field_confidences?: Record<string, number> | null
  overall_confidence?: number | null
  review_status: AgentReviewStatus
  reviewed_by_user_id?: number | null
  reviewed_at?: string | null
  trace_meta?: Record<string, any> | null
  created_at: string
}

export interface AgentReviewListResponse {
  items: AgentReviewRecord[]
  total: number
  page: number
  page_size: number
}

export interface AgentReviewListParams {
  page?: number
  page_size?: number
  review_status?: AgentReviewStatus
  task_id?: number
  file_type?: string
  start_time?: string
  end_time?: string
}

export interface AgentReviewUpdateRequest {
  action: AgentReviewAction
  modified_data?: Record<string, any>
  comment?: string
}

export interface AgentReviewUpdateResponse {
  record_id: number
  review_status: AgentReviewStatus
  reviewed_by_user_id?: number | null
  reviewed_at: string
  task_id?: number | null
}

export interface AgentToolTrace {
  tool_name: string
  status: 'ok' | 'failed' | 'skipped'
  tool_input?: Record<string, any> | null
  tool_output?: Record<string, any> | null
  error?: string | null
  duration_ms?: number | null
}

export interface AgentChatRequest {
  message: string
  top_k?: number
  project_scope?: number[]
  file?: File
}

export interface AgentChatResponse {
  mode: AgentChatMode
  intent: AgentChatIntent
  reply: string
  follow_up_question?: string | null
  task_id?: number | null
  query_result?: Record<string, any> | null
  tool_traces: AgentToolTrace[]
  degraded: boolean
  retryable: boolean
  audit_id?: number | null
}

/**
 * Submit ingestion task
 */
export function submitIngestApi(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request<AgentTaskSubmitResponse>({
    url: '/api/v1/agent/ingest',
    method: 'post',
    data: formData,
  })
}

/**
 * Query task status
 */
export function getTaskStatusApi(taskId: number) {
  return request<AgentTaskResponse>({
    url: `/api/v1/agent/tasks/${taskId}`,
    method: 'get',
    timeout: 10000, // Polling should be fast; fail quickly to avoid request queue buildup
  })
}

/**
 * Get review list
 */
export function getReviewListApi(params?: AgentReviewListParams) {
  return request<AgentReviewListResponse>({
    url: '/api/v1/agent/review',
    method: 'get',
    params,
  })
}

/**
 * Review record
 */
export function reviewRecordApi(recordId: number, data: AgentReviewUpdateRequest) {
  return request<AgentReviewUpdateResponse>({
    url: `/api/v1/agent/review/${recordId}`,
    method: 'put',
    data,
  })
}

/**
 * Agent chat
 */
export function sendChatMessageApi(data: AgentChatRequest) {
  const formData = new FormData()
  formData.append('message', data.message)
  formData.append('top_k', String(data.top_k ?? 100))

  if (data.project_scope?.length) {
    formData.append('project_scope', JSON.stringify(data.project_scope))
  }

  if (data.file) {
    formData.append('file', data.file)
  }

  return request<AgentChatResponse>({
    url: '/api/v1/agent/chat',
    method: 'post',
    data: formData,
    timeout: 120000, // Agent chat involves multiple LLM calls, needs longer timeout
  })
}
