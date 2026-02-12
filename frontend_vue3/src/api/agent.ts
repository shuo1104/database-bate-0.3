/**
 * Agent API
 */
import { request } from '@/utils/request'
import { getToken } from '@/utils/auth'

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

export interface AgentReviewDeleteResponse {
  record_id: number
  task_id?: number | null
  review_status: AgentReviewStatus
  deleted_at: string
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

export interface AgentChatStreamCallbacks {
  onStart?: () => void
  onDelta?: (chunk: string) => void
  onDone?: (response: AgentChatResponse) => void
  onError?: (message: string) => void
}

type AgentChatStreamEvent =
  | { type: 'start' }
  | { type: 'delta'; content?: string }
  | { type: 'done'; response?: AgentChatResponse }
  | { type: 'error'; message?: string }

function createChatFormData(data: AgentChatRequest) {
  const formData = new FormData()
  formData.append('message', data.message)
  formData.append('top_k', String(data.top_k ?? 100))

  if (data.project_scope?.length) {
    formData.append('project_scope', JSON.stringify(data.project_scope))
  }

  if (data.file) {
    formData.append('file', data.file)
  }

  return formData
}

function parseStreamLines(buffer: string) {
  const lines = buffer.split('\n')
  const remain = lines.pop() || ''
  const parsedEvents: AgentChatStreamEvent[] = []

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) {
      continue
    }

    try {
      parsedEvents.push(JSON.parse(trimmed) as AgentChatStreamEvent)
    } catch {
      // Ignore malformed stream chunks and continue consuming
    }
  }

  return {
    remain,
    parsedEvents,
  }
}

async function processStreamEvent(
  event: AgentChatStreamEvent,
  callbacks?: AgentChatStreamCallbacks
) {
  if (event.type === 'start') {
    callbacks?.onStart?.()
    return null
  }

  if (event.type === 'delta') {
    callbacks?.onDelta?.(event.content || '')
    return null
  }

  if (event.type === 'error') {
    const message = event.message || 'Agent chat stream failed'
    callbacks?.onError?.(message)
    throw new Error(message)
  }

  const response = event.response
  if (!response) {
    throw new Error('Missing final response in stream event')
  }

  callbacks?.onDone?.(response)
  return response
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
 * Delete review record
 */
export function deleteReviewRecordApi(recordId: number) {
  return request<AgentReviewDeleteResponse>({
    url: `/api/v1/agent/review/${recordId}`,
    method: 'delete',
  })
}

/**
 * Agent chat
 */
export function sendChatMessageApi(data: AgentChatRequest) {
  const formData = createChatFormData(data)

  return request<AgentChatResponse>({
    url: '/api/v1/agent/chat',
    method: 'post',
    data: formData,
    timeout: 120000, // Agent chat involves multiple LLM calls, needs longer timeout
  })
}

/**
 * Agent chat stream (NDJSON)
 */
export async function sendChatMessageStreamApi(
  data: AgentChatRequest,
  callbacks?: AgentChatStreamCallbacks
) {
  const formData = createChatFormData(data)
  const headers: Record<string, string> = {
    Accept: 'application/x-ndjson',
  }

  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch('/api/v1/agent/chat/stream', {
    method: 'POST',
    headers,
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`Stream request failed with status ${response.status}`)
  }

  if (!response.body) {
    throw new Error('Empty stream body')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  let finalResponse: AgentChatResponse | null = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const { remain, parsedEvents } = parseStreamLines(buffer)
    buffer = remain

    for (const event of parsedEvents) {
      const maybeResponse = await processStreamEvent(event, callbacks)
      if (maybeResponse) {
        finalResponse = maybeResponse
      }
    }
  }

  buffer += decoder.decode()
  if (buffer.trim()) {
    const { parsedEvents } = parseStreamLines(`${buffer}\n`)
    for (const event of parsedEvents) {
      const maybeResponse = await processStreamEvent(event, callbacks)
      if (maybeResponse) {
        finalResponse = maybeResponse
      }
    }
  }

  if (!finalResponse) {
    throw new Error('Stream ended without final response')
  }

  return finalResponse
}
