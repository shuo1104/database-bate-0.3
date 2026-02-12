/**
 * Agent panel store
 */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { AgentTaskResponse } from '@/api/agent'

export type AgentPanelTab = 'chat' | 'ingest' | 'review'

export type AgentMessageRole = 'user' | 'agent' | 'system'

export interface AgentChatMessage {
  id: string
  role: AgentMessageRole
  content: string
  created_at: string
  file_name?: string
  pending?: boolean
  failed?: boolean
}

const MAX_CHAT_MESSAGES = 200

function createMessageId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

export const useAgentStore = defineStore(
  'agent',
  () => {
    const panelVisible = ref(false)
    const activeTab = ref<AgentPanelTab>('chat')
    const chatMessages = ref<AgentChatMessage[]>([])
    const chatLoading = ref(false)
    const activeTasks = ref<AgentTaskResponse[]>([])
    const unreadCount = ref(0)

    const runningTasks = computed(() => {
      return activeTasks.value.filter((task) => task.status === 'pending' || task.status === 'running')
    })

    function setPanelVisible(visible: boolean) {
      panelVisible.value = visible
      if (visible) {
        unreadCount.value = 0
      }
    }

    function setActiveTab(tab: AgentPanelTab) {
      activeTab.value = tab
    }

    function setChatLoading(loading: boolean) {
      chatLoading.value = loading
    }

    function addChatMessage(message: Omit<AgentChatMessage, 'id' | 'created_at'> & Partial<Pick<AgentChatMessage, 'id' | 'created_at'>>) {
      const next: AgentChatMessage = {
        id: message.id || createMessageId(),
        role: message.role,
        content: message.content,
        created_at: message.created_at || new Date().toISOString(),
        file_name: message.file_name,
        pending: message.pending,
        failed: message.failed,
      }

      chatMessages.value.push(next)

      if (chatMessages.value.length > MAX_CHAT_MESSAGES) {
        chatMessages.value = chatMessages.value.slice(chatMessages.value.length - MAX_CHAT_MESSAGES)
      }

      if (!panelVisible.value && next.role !== 'user') {
        unreadCount.value += 1
      }

      return next
    }

    function updateChatMessage(messageId: string, patch: Partial<AgentChatMessage>) {
      const index = chatMessages.value.findIndex((item) => item.id === messageId)
      if (index === -1) {
        return
      }

      chatMessages.value[index] = {
        ...chatMessages.value[index],
        ...patch,
      }
    }

    function clearChatMessages() {
      chatMessages.value = []
      unreadCount.value = 0
    }

    function setActiveTasks(tasks: AgentTaskResponse[]) {
      activeTasks.value = tasks
    }

    function upsertTask(task: AgentTaskResponse) {
      const index = activeTasks.value.findIndex((item) => item.task_id === task.task_id)
      if (index === -1) {
        activeTasks.value.unshift(task)
      } else {
        activeTasks.value[index] = task
      }
    }

    function removeTask(taskId: number) {
      activeTasks.value = activeTasks.value.filter((item) => item.task_id !== taskId)
    }

    function setUnreadCount(count: number) {
      unreadCount.value = Math.max(0, count)
    }

    function incrementUnreadCount(step = 1) {
      unreadCount.value += Math.max(0, step)
    }

    return {
      panelVisible,
      activeTab,
      chatMessages,
      chatLoading,
      activeTasks,
      unreadCount,
      runningTasks,
      setPanelVisible,
      setActiveTab,
      setChatLoading,
      addChatMessage,
      updateChatMessage,
      clearChatMessages,
      setActiveTasks,
      upsertTask,
      removeTask,
      setUnreadCount,
      incrementUnreadCount,
    }
  },
  {
    persist: {
      key: 'agent-store',
      storage: localStorage,
      pick: ['panelVisible', 'activeTab', 'chatMessages'],
    },
  }
)
