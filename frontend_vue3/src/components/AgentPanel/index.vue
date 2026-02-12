<template>
  <div class="agent-panel-root">
    <el-badge
      :value="badgeValue"
      :hidden="agentStore.unreadCount <= 0"
      class="agent-fab-badge"
    >
      <el-button
        class="agent-fab"
        :class="{ active: panelVisibleModel }"
        type="primary"
        circle
        @click="panelVisibleModel = true"
      >
        AI
      </el-button>
    </el-badge>

    <el-drawer
      v-model="panelVisibleModel"
      :size="drawerSize"
      :append-to-body="true"
      :destroy-on-close="false"
      direction="rtl"
      class="agent-drawer"
    >
      <template #header>
        <div class="drawer-header">
          <div class="drawer-title-row">
            <div class="drawer-title">Agent Assistant</div>
            <el-tag class="agent-status" size="small" type="success" effect="plain">
              Online
            </el-tag>
          </div>
          <div class="drawer-subtitle">
            Unified panel for chat, ingestion, and review
            <span v-if="runningTaskCount > 0" class="running-task-tip">
              · Running {{ runningTaskCount }}
            </span>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTabModel" class="panel-tabs" stretch>
        <el-tab-pane name="chat">
          <template #label>
            <span class="tab-label">
              <el-icon><ChatDotRound /></el-icon>
              <span>Chat</span>
            </span>
          </template>
          <AgentChat />
        </el-tab-pane>

        <el-tab-pane name="ingest">
          <template #label>
            <span class="tab-label">
              <el-icon><UploadFilled /></el-icon>
              <span>File Ingestion</span>
            </span>
          </template>
          <AgentIngest />
        </el-tab-pane>

        <el-tab-pane v-if="isAdmin" name="review">
          <template #label>
            <span class="tab-label">
              <el-icon><EditPen /></el-icon>
              <span>Review Management</span>
            </span>
          </template>
          <AgentReview />
        </el-tab-pane>

      </el-tabs>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useWindowSize } from '@vueuse/core'
import { ChatDotRound, EditPen, UploadFilled } from '@element-plus/icons-vue'
import { useAgentTasks } from '@/composables/useAgentTasks'
import { useAgentStore, useUserStore, type AgentPanelTab } from '@/store'
import AgentChat from './AgentChat.vue'
import AgentIngest from './AgentIngest.vue'
import AgentReview from './AgentReview.vue'

const agentStore = useAgentStore()
const userStore = useUserStore()
const { width } = useWindowSize()

useAgentTasks()

const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const panelVisibleModel = computed({
  get: () => agentStore.panelVisible,
  set: (visible: boolean) => agentStore.setPanelVisible(visible),
})

const activeTabModel = computed<AgentPanelTab>({
  get: () => {
    if (!isAdmin.value && agentStore.activeTab === 'review') {
      return 'chat'
    }

    return agentStore.activeTab
  },
  set: (tab) => {
    if (!isAdmin.value && tab === 'review') {
      agentStore.setActiveTab('chat')
      return
    }

    agentStore.setActiveTab(tab)
  },
})

const drawerSize = computed(() => {
  return width.value <= 768 ? '100%' : '480px'
})

const badgeValue = computed(() => {
  if (agentStore.unreadCount > 99) {
    return '99+'
  }

  return agentStore.unreadCount
})

const runningTaskCount = computed(() => agentStore.runningTasks.length)

watch(
  () => isAdmin.value,
  (admin) => {
    if (!admin && agentStore.activeTab === 'review') {
      agentStore.setActiveTab('chat')
    }
  }
)
</script>

<style scoped lang="scss">
.agent-panel-root {
  position: fixed;
  right: 18px;
  bottom: 22px;
  z-index: 1800;
}

.agent-fab-badge {
  :deep(.el-badge__content) {
    border: none;
    box-shadow: 0 2px 10px rgba(24, 76, 112, 0.28);
  }
}

.agent-fab {
  width: 52px;
  height: 52px;
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.5px;
  border: 1px solid #2a95d6;
  box-shadow: 0 10px 24px rgba(13, 113, 178, 0.28);
  background: linear-gradient(135deg, #0f82c5 0%, #2aa3df 100%);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 28px rgba(13, 113, 178, 0.32);
  }

  &.active {
    box-shadow: 0 0 0 3px rgba(34, 146, 213, 0.2), 0 12px 26px rgba(13, 113, 178, 0.32);
  }
}

.drawer-header {
  padding: 2px 0 6px;

  .drawer-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }

  .drawer-title {
    font-size: 18px;
    font-weight: 700;
    color: #1f3e53;
  }

  .agent-status {
    border-color: #86cc9a;
    color: #2f7d49;
  }

  .drawer-subtitle {
    margin-top: 3px;
    font-size: 12px;
    color: #67859b;

    .running-task-tip {
      color: #0f82c5;
      font-weight: 600;
    }
  }
}

.panel-tabs {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;

  :deep(.el-tabs__content) {
    flex: 1;
    overflow: hidden;
  }

  :deep(.el-tab-pane) {
    height: 100%;
  }

  :deep(.el-tabs__nav-wrap::after) {
    background-color: #d7e4ee;
  }

  :deep(.el-tabs__item) {
    font-weight: 600;
    color: #5d7488;
  }

  :deep(.el-tabs__item.is-active) {
    color: #0f82c5;
  }
}

.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

@media (max-width: 768px) {
  .agent-panel-root {
    right: 12px;
    bottom: 16px;
  }

  .agent-fab {
    width: 48px;
    height: 48px;
    font-size: 13px;
  }

  .panel-tabs {
    height: calc(100vh - 104px);
  }
}
</style>

<!-- Drawer is teleported to body via append-to-body; use non-scoped styles for override -->
<style lang="scss">
.agent-drawer .el-drawer__header {
  margin-bottom: 8px;
  padding-bottom: 0;
  border-bottom: 1px solid #dce7ef;
}

.agent-drawer .el-drawer__body {
  padding-top: 0;
  background: linear-gradient(180deg, #fdfefe 0%, #f7fbff 100%);
}
</style>
