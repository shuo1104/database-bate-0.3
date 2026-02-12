<template>
  <aside class="workspace-sidebar">
    <div class="primary-rail">
      <div class="brand-block">
        <img src="@/assets/images/logo.png" alt="Logo" class="brand-logo" />
      </div>

      <div class="primary-list">
        <button
          v-for="section in sections"
          :key="section.key"
          type="button"
          class="primary-item"
          :class="{ active: section.key === activeSectionKey }"
          :title="section.label"
          @click="handlePrimaryClick(section.key)"
        >
          <el-icon :size="20"><component :is="section.icon" /></el-icon>
        </button>
      </div>
    </div>

    <div class="secondary-rail">
      <div class="secondary-header">
        <h3 class="secondary-title">{{ activeSection?.label }}</h3>
        <p v-if="activeSection?.description" class="secondary-desc">{{ activeSection?.description }}</p>
      </div>

      <nav class="secondary-nav">
        <router-link
          v-for="item in visibleSecondaryItems"
          :key="item.key"
          class="secondary-item"
          :class="{ active: isItemActive(item) }"
          :to="buildItemRoute(item)"
        >
          <el-icon :size="16"><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter, type RouteLocationRaw } from 'vue-router'
import { useUserStore } from '@/store'
import {
  Box,
  Cpu,
  ChatDotRound,
  DataAnalysis,
  DataBoard,
  Document,
  EditPen,
  Grid,
  List,
  Operation,
  Setting,
  Stamp,
  UploadFilled,
} from '@element-plus/icons-vue'

type PrimaryKey = 'project' | 'master' | 'ai' | 'system'

interface SecondaryItem {
  key: string
  label: string
  icon: any
  path: string
  query?: Record<string, string>
  requiresAdmin?: boolean
}

interface PrimarySection {
  key: PrimaryKey
  label: string
  description: string
  icon: any
  items: SecondaryItem[]
  requiresAdmin?: boolean
}

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const sectionConfig = computed<PrimarySection[]>(() => {
  const baseSections: PrimarySection[] = [
    {
      key: 'project',
      label: 'Project Information',
      description: '项目配方与结果数据',
      icon: DataBoard,
      items: [
        { key: 'projects', label: 'Project Information', icon: Operation, path: '/projects' },
        { key: 'formulas', label: 'Formulation Composition', icon: List, path: '/formulas' },
        { key: 'test-results', label: 'Results', icon: DataAnalysis, path: '/test-results' },
      ],
    },
    {
      key: 'master',
      label: 'Master',
      description: '基础主数据维护',
      icon: Grid,
      items: [
        { key: 'materials', label: 'Ingredient Master', icon: Box, path: '/materials' },
        { key: 'fillers', label: 'Mineral Filler Master', icon: Box, path: '/fillers' },
      ],
    },
    {
      key: 'ai',
      label: 'AI Workspace',
      description: '',
      icon: Cpu,
      items: [
        {
          key: 'ai-chat',
          label: 'Chat',
          icon: ChatDotRound,
          path: '/agent',
          query: { tab: 'chat' },
        },
        {
          key: 'ai-ingest',
          label: 'File Ingestion',
          icon: UploadFilled,
          path: '/agent',
          query: { tab: 'ingest' },
        },
        {
          key: 'ai-review',
          label: 'Review Management',
          icon: EditPen,
          path: '/agent',
          query: { tab: 'review' },
          requiresAdmin: true,
        },
      ],
    },
    {
      key: 'system',
      label: 'System Management',
      description: '角色与系统日志管理',
      icon: Setting,
      requiresAdmin: true,
      items: [
        { key: 'roles', label: 'Roles', icon: Stamp, path: '/system/roles', requiresAdmin: true },
        { key: 'logs', label: 'System Logs', icon: Document, path: '/system/logs', requiresAdmin: true },
      ],
    },
  ]

  return baseSections.filter((section) => !section.requiresAdmin || isAdmin.value)
})

const activeSectionKey = computed<PrimaryKey>(() => {
  const path = route.path
  if (path.startsWith('/projects') || path.startsWith('/formulas') || path.startsWith('/test-results')) {
    return 'project'
  }
  if (path.startsWith('/materials') || path.startsWith('/fillers')) {
    return 'master'
  }
  if (path.startsWith('/agent')) {
    return 'ai'
  }
  if (path.startsWith('/system/')) {
    return 'system'
  }
  return 'project'
})

const sections = computed(() => sectionConfig.value)

const activeSection = computed(() => {
  return sections.value.find((section) => section.key === activeSectionKey.value) || sections.value[0]
})

const visibleSecondaryItems = computed(() => {
  return (activeSection.value?.items || []).filter((item) => !item.requiresAdmin || isAdmin.value)
})

function buildItemRoute(item: SecondaryItem): RouteLocationRaw {
  if (item.query) {
    return {
      path: item.path,
      query: item.query,
    }
  }

  return {
    path: item.path,
  }
}

function isItemActive(item: SecondaryItem) {
  if (route.path !== item.path) {
    return false
  }

  if (item.query?.tab) {
    return String(route.query.tab || 'chat') === item.query.tab
  }

  return true
}

function handlePrimaryClick(sectionKey: PrimaryKey) {
  const section = sections.value.find((item) => item.key === sectionKey)
  if (!section) {
    return
  }

  const firstItem = section.items.find((item) => !item.requiresAdmin || isAdmin.value)
  if (!firstItem) {
    return
  }

  router.push(buildItemRoute(firstItem))
}
</script>

<style scoped lang="scss">
.workspace-sidebar {
  width: 304px;
  height: 100vh;
  display: flex;
  border-right: 1px solid #d9e6ef;
  background: #f9fcfe;
}

.primary-rail {
  width: 60px;
  border-right: 1px solid #dde9f2;
  background: linear-gradient(180deg, #ffffff 0%, #f4f9fc 100%);
  display: flex;
  flex-direction: column;
}

.brand-block {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e1ecf4;
}

.brand-logo {
  width: 34px;
  height: 34px;
  object-fit: contain;
}

.primary-list {
  flex: 1;
  padding: 12px 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.primary-item {
  width: 44px;
  height: 44px;
  border: 1px solid transparent;
  background: transparent;
  border-radius: 12px;
  padding: 0;
  color: #678095;
  cursor: pointer;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 0;
  transition: all 0.2s ease;

  &:hover {
    border-color: #d2e4f1;
    background: #edf6fc;
    color: #34556c;
  }

  &.active {
    border-color: #b9d8ec;
    background: #e8f4fb;
    color: #0f82c5;
    box-shadow: inset 0 0 0 1px rgba(15, 130, 197, 0.08);
  }
}

.secondary-rail {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 16px 14px;
  background: linear-gradient(180deg, #fcfeff 0%, #f6fbff 100%);
}

.secondary-header {
  padding: 4px 4px 12px;
  border-bottom: 1px solid #dfeaf3;
}

.secondary-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #274357;
}

.secondary-desc {
  margin: 5px 0 0;
  font-size: 12px;
  color: #748fa3;
}

.secondary-nav {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.secondary-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  color: #5f788d;
  text-decoration: none;
  border: 1px solid transparent;
  transition: all 0.2s ease;

  &:hover {
    background: #edf6fc;
    border-color: #d2e4f1;
    color: #365972;
  }

  &.active {
    background: #e8f4fb;
    border-color: #bddbee;
    color: #0f82c5;
    font-weight: 600;
  }
}

@media (max-width: 1024px) {
  .workspace-sidebar {
    width: 276px;
  }

  .primary-rail {
    width: 56px;
  }
}
</style>
