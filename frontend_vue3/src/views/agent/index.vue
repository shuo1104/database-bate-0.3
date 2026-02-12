<template>
  <div class="agent-page">
    <header class="workspace-header">
      <div class="title-group">
        <h2 class="title">AI Workspace</h2>
      </div>
      <div class="header-tags">
        <el-tag type="success" effect="plain">Agent Online</el-tag>
        <el-tag type="warning" effect="plain">Preview</el-tag>
        <el-tag type="info" effect="plain">{{ activeTabLabel }}</el-tag>
      </div>
    </header>

    <section class="workspace-content">
      <AgentChat v-if="activeTab === 'chat'" />
      <AgentIngest v-else-if="activeTab === 'ingest'" />
      <AgentReview v-else />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AgentChat from '@/components/AgentPanel/AgentChat.vue'
import AgentIngest from '@/components/AgentPanel/AgentIngest.vue'
import AgentReview from '@/components/AgentPanel/AgentReview.vue'
import { useAgentTasks } from '@/composables/useAgentTasks'
import { useAgentStore, useUserStore, type AgentPanelTab } from '@/store'

const route = useRoute()
const router = useRouter()
const agentStore = useAgentStore()
const userStore = useUserStore()

useAgentTasks()

const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const activeTab = computed<AgentPanelTab>(() => {
  const tab = String(route.query.tab || 'chat')
  if (tab === 'ingest') {
    return 'ingest'
  }

  if (tab === 'review' && isAdmin.value) {
    return 'review'
  }

  return 'chat'
})

const activeTabLabel = computed(() => {
  if (activeTab.value === 'ingest') {
    return 'File Ingestion'
  }
  if (activeTab.value === 'review') {
    return 'Review Management'
  }
  return 'Chat'
})

onMounted(() => {
  agentStore.setPanelVisible(true)
  agentStore.setUnreadCount(0)
})

onUnmounted(() => {
  agentStore.setPanelVisible(false)
})

watch(
  () => activeTab.value,
  (tab) => {
    agentStore.setActiveTab(tab)

    if (tab === 'chat' && route.query.tab !== 'chat') {
      if (route.query.tab === undefined || route.query.tab === null || route.query.tab === '') {
        return
      }

      router.replace({
        path: '/agent',
        query: { tab: 'chat' },
      })
    }
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.agent-page {
  height: calc(100vh - 172px);
  min-height: 560px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.workspace-header {
  padding: 14px 16px;
  border: 1px solid #d9e6ef;
  border-radius: 12px;
  background: linear-gradient(180deg, #ffffff 0%, #f6fbff 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.title-group {
  .title {
    margin: 0;
    font-size: 20px;
    font-weight: 700;
    color: #1f3e53;
    line-height: 1.2;
  }
}

.header-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.workspace-content {
  height: 100%;
  min-height: 0;
  border-radius: 14px;
  overflow: hidden;
}

@media (max-width: 768px) {
  .agent-page {
    min-height: 500px;
    height: auto;
    gap: 10px;
  }

  .workspace-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 12px;
  }

  .workspace-content {
    min-height: 500px;
  }
}
</style>
