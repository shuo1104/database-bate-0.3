<template>
  <div class="agent-chat">
    <section class="chat-shell">
      <header class="shell-toolbar">
        <div class="toolbar-left">
          <el-icon class="toolbar-icon"><ChatDotRound /></el-icon>
          <span class="toolbar-title">AI Chat</span>
          <span class="toolbar-divider" />
          <span class="message-count">{{ messages.length }} messages</span>
        </div>

        <div class="toolbar-right">
          <span class="hotkey-tip">Enter to send · Shift + Enter for newline</span>
          <el-button text size="small" @click="handleClearMessages">Clear History</el-button>
        </div>
      </header>

      <main ref="messageContainerRef" class="shell-body">
        <div v-if="!messages.length && !chatLoading" class="empty-state">
          <div class="empty-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <h3>Start an AI Session</h3>
          <p>Ask directly, or attach a file for structured processing.</p>

          <div class="quick-prompts">
            <button
              v-for="prompt in quickPrompts"
              :key="prompt"
              type="button"
              class="prompt-chip"
              @click="applyQuickPrompt(prompt)"
            >
              {{ prompt }}
            </button>
          </div>
        </div>

        <div v-else class="messages-list">
          <ChatMessage
            v-for="item in messages"
            :key="item.id"
            :message="item"
          />
        </div>

        <div v-if="chatLoading" class="typing-indicator">
          <span class="dot" />
          <span class="dot" />
          <span class="dot" />
          <span class="text">Agent is thinking...</span>
        </div>
      </main>

      <footer class="shell-footer">
        <div v-if="selectedFile" class="selected-file">
          <span class="file-label">Attachment: {{ selectedFile.name }}</span>
          <el-button text size="small" @click="clearSelectedFile">Remove</el-button>
        </div>

        <el-input
          ref="inputRef"
          v-model="inputMessage"
          class="composer-input"
          type="textarea"
          :rows="3"
          maxlength="8000"
          show-word-limit
          resize="none"
          placeholder="Enter your question. You can attach one file (PDF/Image/CSV)."
          @keydown.enter.exact.prevent="handleSend"
        />

        <div class="composer-actions">
          <input
            ref="fileInputRef"
            class="hidden-input"
            type="file"
            accept=".pdf,.csv,image/*"
            @change="handleFileChange"
          />

          <el-button class="attach-btn" @click="openFilePicker">
            <el-icon><Paperclip /></el-icon>
            Add Attachment
          </el-button>

          <el-button
            type="primary"
            class="send-btn"
            :loading="chatLoading"
            :disabled="!canSend || chatLoading"
            @click="handleSend"
          >
            <el-icon><Promotion /></el-icon>
            Send
          </el-button>
        </div>
      </footer>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { ChatDotRound, Paperclip, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { sendChatMessageApi } from '@/api/agent'
import { useAgentTasks } from '@/composables/useAgentTasks'
import { useAgentStore } from '@/store'

const NOT_READY_MESSAGE = 'Agent chat is coming soon. Please try again later.'

const agentStore = useAgentStore()
const { addTask } = useAgentTasks()

const inputMessage = ref('')
const selectedFile = ref<File | null>(null)
const messageContainerRef = ref<HTMLElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const inputRef = ref<{ focus: () => void } | null>(null)

const quickPrompts = [
  'Count projects created in the last 30 days, grouped by project type.',
  'Read my uploaded file and extract project name, formula code, formulator, and date.',
  'List pending ingestion review records and sort them by confidence ascending.',
]

const messages = computed(() => agentStore.chatMessages)
const chatLoading = computed(() => agentStore.chatLoading)
const canSend = computed(() => {
  return Boolean(inputMessage.value.trim()) || Boolean(selectedFile.value)
})

function scrollToBottom() {
  nextTick(() => {
    const container = messageContainerRef.value
    if (!container) {
      return
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior: 'smooth',
    })
  })
}

function openFilePicker() {
  fileInputRef.value?.click()
}

function applyQuickPrompt(prompt: string) {
  inputMessage.value = prompt
  nextTick(() => {
    inputRef.value?.focus()
  })
}

function clearSelectedFile() {
  selectedFile.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) {
    return
  }

  const maxSize = 20 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.warning('Attachment size cannot exceed 20MB')
    clearSelectedFile()
    return
  }

  selectedFile.value = file
}

function handleClearMessages() {
  agentStore.clearChatMessages()
}

async function handleSend() {
  if (chatLoading.value) {
    return
  }

  const text = inputMessage.value.trim()
  const file = selectedFile.value

  if (!text && !file) {
    ElMessage.warning('Please enter a message or add an attachment')
    return
  }

  const requestMessage = text || `Please process attachment: ${file?.name || 'unnamed file'}`

  agentStore.addChatMessage({
    role: 'user',
    content: text || '[Attachment only] Please process this file.',
    file_name: file?.name,
  })

  inputMessage.value = ''
  clearSelectedFile()
  agentStore.setChatLoading(true)

  try {
    const response = await sendChatMessageApi({
      message: requestMessage,
      file: file || undefined,
    })

    agentStore.addChatMessage({
      role: 'agent',
      content: response.reply || 'Request received.',
    })

    if (response.follow_up_question) {
      agentStore.addChatMessage({
        role: 'system',
        content: response.follow_up_question,
      })
    }

    if (response.mode === 'async_task' && response.task_id) {
      addTask({
        task_id: response.task_id,
        task_type: response.intent || 'ingest',
        status: 'pending',
        payload: {
          file_name: file?.name,
        },
        result: null,
        error_message: null,
        created_at: new Date().toISOString(),
        started_at: null,
        finished_at: null,
      })

      agentStore.addChatMessage({
        role: 'system',
        content: `Async task #${response.task_id} created. Check progress in the "File Ingestion" tab.`,
      })
    }
  } catch (error) {
    console.error('Agent chat failed:', error)
    agentStore.addChatMessage({
      role: 'system',
      content: NOT_READY_MESSAGE,
      failed: true,
    })
  } finally {
    agentStore.setChatLoading(false)
    scrollToBottom()
  }
}

watch(
  () => [messages.value.length, chatLoading.value],
  () => {
    scrollToBottom()
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.agent-chat {
  height: 100%;
}

.chat-shell {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #d8e5ef;
  border-radius: 14px;
  overflow: hidden;
  background: #ffffff;
}

.shell-toolbar {
  min-height: 50px;
  padding: 0 14px;
  border-bottom: 1px solid #deebf3;
  background: #f7fbfe;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.toolbar-left {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  .toolbar-icon {
    color: #0f82c5;
  }

  .toolbar-title {
    font-size: 13px;
    font-weight: 700;
    color: #274357;
  }

  .toolbar-divider {
    width: 1px;
    height: 14px;
    background: #c8dbe8;
  }

  .message-count {
    color: #6f8ba0;
    font-size: 12px;
  }
}

.toolbar-right {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  .hotkey-tip {
    color: #8199ad;
    font-size: 11px;
  }
}

.shell-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 14px;
  background: linear-gradient(180deg, #fcfeff 0%, #f5f9fd 100%);
}

.messages-list {
  display: flex;
  flex-direction: column;
}

.empty-state {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 12px;

  .empty-icon {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: #0f82c5;
    background: #e3f1fa;
    border: 1px solid #c7deee;
    margin-bottom: 10px;
  }

  h3 {
    margin: 0;
    font-size: 18px;
    color: #274357;
  }

  p {
    margin: 8px 0 0;
    color: #708ca1;
    font-size: 13px;
  }
}

.quick-prompts {
  margin-top: 16px;
  width: 100%;
  max-width: 760px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.prompt-chip {
  border: 1px solid #caddea;
  background: #ffffff;
  color: #335a74;
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 12px;
  line-height: 1.35;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #9ec9e3;
    color: #215272;
    background: #f3fafe;
  }
}

.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  padding: 8px 10px;
  border-radius: 10px;
  background: #eff6fb;
  border: 1px solid #d7e5ef;
  color: #4d6a7f;
  font-size: 12px;

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #5583a6;
    animation: typing-bounce 1.2s infinite ease-in-out;

    &:nth-child(2) {
      animation-delay: 0.12s;
    }

    &:nth-child(3) {
      animation-delay: 0.24s;
    }
  }

  .text {
    margin-left: 2px;
  }
}

.shell-footer {
  border-top: 1px solid #deebf3;
  padding: 10px 12px;
  background: #ffffff;
}

.selected-file {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 6px 10px;
  border-radius: 8px;
  background: #f4f9fc;
  border: 1px dashed #c3d9e8;

  .file-label {
    color: #34566f;
    font-size: 12px;
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.composer-input {
  :deep(.el-textarea__inner) {
    border-radius: 10px;
    background: #fbfdff;
  }
}

.composer-actions {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;

  .attach-btn {
    color: #406179;
    border-color: #c6d9e7;
    background: #f7fbfe;
  }

  .send-btn {
    min-width: 86px;
  }
}

.hidden-input {
  display: none;
}

@keyframes typing-bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.55;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .shell-toolbar {
    min-height: auto;
    padding: 8px 10px;
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-right {
    width: 100%;
    justify-content: space-between;
  }

  .shell-body {
    padding: 10px;
  }

  .shell-footer {
    padding: 8px;
  }

  .composer-actions {
    justify-content: space-between;
  }
}
</style>
