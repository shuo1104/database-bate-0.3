/**
 * Agent task polling composable
 */
import { computed, ref, watch } from 'vue'
import { ElNotification } from 'element-plus'
import { createGlobalState, useIntervalFn } from '@vueuse/core'
import { getTaskStatusApi, type AgentTaskResponse, type AgentTaskStatus } from '@/api/agent'
import { useAgentStore } from '@/store'

const FAST_POLLING_INTERVAL = 3000
const SLOW_POLLING_INTERVAL = 10000

function shouldNotifyTransition(fromStatus: AgentTaskStatus | undefined, toStatus: AgentTaskStatus) {
  return (
    (fromStatus === 'pending' || fromStatus === 'running') &&
    (toStatus === 'succeeded' || toStatus === 'failed')
  )
}

function getTaskDisplayName(task: AgentTaskResponse) {
  const fileName = task.payload?.file_name
  if (typeof fileName === 'string' && fileName.trim()) {
    return fileName
  }

  return `#${task.task_id}`
}

export const useAgentTasks = createGlobalState(() => {
  const agentStore = useAgentStore()
  const isPollingNow = ref(false)
  const syncingTaskIds = ref<number[]>([])
  const taskStatusSnapshot = ref<Record<number, AgentTaskStatus>>({})

  const pollingInterval = computed(() => {
    return agentStore.panelVisible ? FAST_POLLING_INTERVAL : SLOW_POLLING_INTERVAL
  })

  async function syncTaskStatus(taskId: number) {
    if (syncingTaskIds.value.includes(taskId)) {
      return null
    }

    syncingTaskIds.value.push(taskId)
    try {
      const latestTask = await getTaskStatusApi(taskId)
      const previousStatus = taskStatusSnapshot.value[taskId]

      agentStore.upsertTask(latestTask)
      taskStatusSnapshot.value[taskId] = latestTask.status

      if (shouldNotifyTransition(previousStatus, latestTask.status)) {
        const taskName = getTaskDisplayName(latestTask)

        if (latestTask.status === 'succeeded') {
          ElNotification({
            title: 'Agent Task Completed',
            message: `Task ${taskName} completed successfully`,
            type: 'success',
            duration: 3000,
          })
        }

        if (latestTask.status === 'failed') {
          ElNotification({
            title: 'Agent Task Failed',
            message: latestTask.error_message || `Task ${taskName} failed`,
            type: 'error',
            duration: 5000,
          })
        }
      }

      return latestTask
    } catch (error) {
      console.error(`Failed to sync agent task #${taskId}:`, error)
      return null
    } finally {
      syncingTaskIds.value = syncingTaskIds.value.filter((id) => id !== taskId)
    }
  }

  async function pollRunningTasks() {
    if (isPollingNow.value) {
      return
    }

    const taskIds = agentStore.runningTasks.map((task) => task.task_id)
    if (!taskIds.length) {
      return
    }

    isPollingNow.value = true
    try {
      await Promise.allSettled(taskIds.map((taskId) => syncTaskStatus(taskId)))
    } finally {
      isPollingNow.value = false
    }
  }

  function addTask(task: AgentTaskResponse) {
    agentStore.upsertTask(task)
    taskStatusSnapshot.value[task.task_id] = task.status

    if (task.status === 'pending' || task.status === 'running') {
      startPolling()
    }
  }

  function initTaskSnapshot(tasks: AgentTaskResponse[]) {
    const nextSnapshot: Record<number, AgentTaskStatus> = {}
    for (const task of tasks) {
      nextSnapshot[task.task_id] = task.status
    }
    taskStatusSnapshot.value = nextSnapshot
  }

  const { resume, pause, isActive } = useIntervalFn(pollRunningTasks, pollingInterval, {
    immediate: false,
    immediateCallback: false,
  })

  function startPolling() {
    if (agentStore.runningTasks.length === 0) {
      return
    }

    if (!isActive.value) {
      resume()
    }
  }

  function stopPolling() {
    if (isActive.value) {
      pause()
    }
  }

  watch(
    () => agentStore.activeTasks,
    (tasks) => {
      initTaskSnapshot(tasks)
    },
    { deep: true, immediate: true }
  )

  watch(
    () => agentStore.runningTasks.length,
    (size) => {
      if (size > 0) {
        startPolling()
      } else {
        stopPolling()
      }
    },
    { immediate: true }
  )

  watch(
    () => agentStore.panelVisible,
    () => {
      if (agentStore.runningTasks.length > 0) {
        startPolling()
      }
    }
  )

  return {
    isPolling: isActive,
    pollRunningTasks,
    syncTaskStatus,
    addTask,
    startPolling,
    stopPolling,
  }
})
