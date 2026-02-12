<template>
  <div class="agent-ingest">
    <el-upload
      drag
      action="#"
      :show-file-list="false"
      :before-upload="beforeUpload"
      :http-request="handleUploadRequest"
      accept=".pdf,.csv,image/*"
      class="ingest-upload"
    >
      <div class="upload-body">
        <div class="upload-title">Drag a file here or click to upload</div>
        <div class="upload-desc">Supports PDF / image / CSV, up to 20MB per file</div>
      </div>
    </el-upload>

    <div class="tasks-header">
      <div class="tasks-title">
        <span>Task Status</span>
        <el-tag size="small" type="info">{{ tasks.length }}</el-tag>
        <el-tag v-if="runningCount > 0" size="small" type="warning">
          Running {{ runningCount }}
        </el-tag>
      </div>
      <el-button text size="small" @click="pollRunningTasks">Refresh</el-button>
    </div>

    <div v-if="tasks.length" class="task-list">
      <div
        v-for="task in tasks"
        :key="task.task_id"
        class="task-card"
        :class="`status-${task.status}`"
      >
        <div class="task-row">
          <div class="task-name">{{ getTaskName(task) }}</div>
          <el-tag :type="statusTagType(task.status)" size="small">
            {{ statusLabel(task.status) }}
          </el-tag>
        </div>

        <div class="task-meta">
          <span>ID: #{{ task.task_id }}</span>
          <span>{{ formatDateTime(task.created_at) }}</span>
        </div>

        <div v-if="task.status === 'running' || task.status === 'pending'" class="running-line">
          <span class="pulse" />
          <span>Task is processing, please wait...</span>
        </div>

        <div v-if="task.status === 'succeeded'" class="result-line success-line">
          <span>Completed</span>
          <span v-if="getConfidence(task) !== null">
            Confidence: {{ getConfidence(task) }}
          </span>
        </div>

        <div v-if="task.status === 'failed'" class="result-line fail-line">
          {{ task.error_message || 'Processing failed. Please try again later.' }}
        </div>
      </div>
    </div>

    <el-empty v-else :image-size="70" description="No tasks yet. Upload a file to see progress." />
  </div>
</template>

<script setup lang="ts">
import type { UploadProps, UploadRequestOptions } from 'element-plus'
import { ElMessage } from 'element-plus'
import { computed } from 'vue'
import { submitIngestApi, type AgentTaskResponse, type AgentTaskStatus } from '@/api/agent'
import { useAgentTasks } from '@/composables/useAgentTasks'
import { useAgentStore } from '@/store'

const agentStore = useAgentStore()
const { addTask, syncTaskStatus, pollRunningTasks } = useAgentTasks()

const tasks = computed(() => {
  return [...agentStore.activeTasks].sort((left, right) => {
    return new Date(right.created_at).getTime() - new Date(left.created_at).getTime()
  })
})

const runningCount = computed(() => {
  return tasks.value.filter((item) => item.status === 'pending' || item.status === 'running').length
})

function statusLabel(status: AgentTaskStatus) {
  if (status === 'pending') {
    return 'Pending'
  }
  if (status === 'running') {
    return 'Running'
  }
  if (status === 'succeeded') {
    return 'Succeeded'
  }
  return 'Failed'
}

function statusTagType(status: AgentTaskStatus) {
  if (status === 'pending') {
    return 'info'
  }
  if (status === 'running') {
    return 'warning'
  }
  if (status === 'succeeded') {
    return 'success'
  }
  return 'danger'
}

function formatDateTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return '-'
  }

  return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
}

function getTaskName(task: AgentTaskResponse) {
  const fileName = task.payload?.file_name
  if (typeof fileName === 'string' && fileName.trim()) {
    return fileName
  }

  return `Task #${task.task_id}`
}

function getConfidence(task: AgentTaskResponse) {
  const fromResult = task.result?.overall_confidence
  const fromPayload = task.payload?.overall_confidence
  const raw = typeof fromResult === 'number' ? fromResult : (typeof fromPayload === 'number' ? fromPayload : null)

  if (raw === null) {
    return null
  }

  return `${Math.round(raw * 100)}%`
}

const beforeUpload: UploadProps['beforeUpload'] = (rawFile) => {
  const fileName = rawFile.name.toLowerCase()
  const fileType = rawFile.type

  const isSupportedType =
    fileType === 'application/pdf' ||
    fileType === 'text/csv' ||
    fileType.startsWith('image/') ||
    fileName.endsWith('.pdf') ||
    fileName.endsWith('.csv')

  if (!isSupportedType) {
    ElMessage.warning('Only PDF / image / CSV files are supported')
    return false
  }

  const maxSize = 20 * 1024 * 1024
  if (rawFile.size > maxSize) {
    ElMessage.warning('File size cannot exceed 20MB')
    return false
  }

  return true
}

async function handleUploadRequest(options: UploadRequestOptions) {
  const file = options.file as File

  try {
    const submitResult = await submitIngestApi(file)

    const task: AgentTaskResponse = {
      task_id: submitResult.task_id,
      task_type: submitResult.task_type,
      status: submitResult.status,
      payload: {
        file_name: submitResult.file_name,
        file_path: submitResult.file_path,
      },
      result: null,
      error_message: null,
      created_at: submitResult.created_at,
      started_at: null,
      finished_at: null,
    }

    addTask(task)
    ElMessage.success(`Ingestion task #${submitResult.task_id} created`)

    await syncTaskStatus(submitResult.task_id)
  } catch (error) {
    console.error('Failed to submit ingest task:', error)
    ElMessage.error('Failed to submit ingestion task. Please try again later.')
  }
}
</script>

<style scoped lang="scss">
.agent-ingest {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ingest-upload {
  :deep(.el-upload-dragger) {
    border-radius: 14px;
    border-color: #bdd8eb;
    background: linear-gradient(180deg, #fafdff 0%, #f2f8fc 100%);
    transition: all 0.25s ease;
  }

  :deep(.el-upload-dragger:hover) {
    border-color: #7cb7dc;
    box-shadow: 0 10px 22px rgba(44, 99, 139, 0.12);
  }
}

.upload-body {
  padding: 14px 8px;

  .upload-title {
    font-size: 14px;
    font-weight: 700;
    color: #245271;
    margin-bottom: 5px;
  }

  .upload-desc {
    font-size: 12px;
    color: #66859b;
  }
}

.tasks-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2px;
  color: #274357;
  font-size: 14px;
  font-weight: 700;

  .tasks-title {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
}

.task-list {
  flex: 1;
  overflow-y: auto;
  padding: 2px;
}

.task-card {
  background: #ffffff;
  border: 1px solid #d6e5ef;
  border-radius: 12px;
  padding: 10px 12px;
  margin-bottom: 10px;
  box-shadow: 0 4px 12px rgba(20, 63, 95, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(20, 63, 95, 0.1);
  }

  &.status-running,
  &.status-pending {
    border-left: 4px solid #d79f32;
  }

  &.status-succeeded {
    border-left: 4px solid #4ea76e;
  }

  &.status-failed {
    border-left: 4px solid #d55252;
  }
}

.task-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;

  .task-name {
    font-size: 13px;
    font-weight: 700;
    color: #2f4659;
    word-break: break-word;
  }
}

.task-meta {
  margin-top: 6px;
  font-size: 12px;
  color: #6f8ba0;
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.running-line,
.result-line {
  margin-top: 8px;
  font-size: 12px;
  color: #4c6477;
}

.running-line {
  display: flex;
  align-items: center;
  gap: 8px;

  .pulse {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #d79f32;
    animation: pulse 1.2s infinite;
  }
}

.success-line {
  color: #3f8459;
  display: flex;
  justify-content: space-between;
}

.fail-line {
  color: #c44747;
}

@keyframes pulse {
  0% {
    transform: scale(0.85);
    opacity: 0.5;
  }
  65% {
    transform: scale(1.15);
    opacity: 1;
  }
  100% {
    transform: scale(0.85);
    opacity: 0.5;
  }
}
</style>
