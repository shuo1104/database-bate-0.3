<template>
  <div class="navbar">
    <div class="navbar-left">
      <span class="page-title">{{ pageTitle }}</span>
    </div>

    <!-- Tags Bar - Embedded in Navbar -->
    <div class="tags-bar" v-if="showTagsBar">
      <div class="tags-wrapper">
        <div
          v-for="tag in tags"
          :key="tag.path"
          :class="{ 'active': currentPath === tag.path }"
          class="tag-item"
          @click="handleTagClick(tag)"
          @contextmenu.prevent="handleRightClick(tag, $event)"
        >
          {{ tag.title }}
          <span
            v-if="!tag.fixed"
            class="tag-close"
            @click.stop="handleCloseTag(tag)"
          >
            ×
          </span>
        </div>
      </div>
      
      <!-- Quick Action Buttons -->
      <div class="tags-actions">
        <el-tooltip :content="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'">
          <el-icon class="action-icon" @click="toggleTheme">
            <Sunny v-if="isDark" />
            <Moon v-else />
          </el-icon>
        </el-tooltip>
        <el-tooltip content="Refresh Current Page">
          <el-icon class="action-icon" @click="handleRefresh">
            <Refresh />
          </el-icon>
        </el-tooltip>
        <el-tooltip content="Close Other Tags">
          <el-icon class="action-icon" @click="handleCloseOthers">
            <Close />
          </el-icon>
        </el-tooltip>
        <el-tooltip content="Close All Tags">
          <el-icon class="action-icon" @click="handleCloseAll">
            <CircleClose />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <!-- Context Menu -->
    <ul v-show="contextMenuVisible" :style="contextMenuStyle" class="context-menu">
      <li @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
        Refresh Page
      </li>
      <li v-if="!selectedTag?.fixed" @click="handleCloseTag(selectedTag!)">
        <el-icon><Close /></el-icon>
        Close Tag
      </li>
      <li @click="handleCloseOthers">
        <el-icon><CircleClose /></el-icon>
        Close Others
      </li>
      <li @click="handleCloseAll">
        <el-icon><CircleClose /></el-icon>
        Close All
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import { ElMessage } from 'element-plus'
import { Refresh, Close, CircleClose, Sunny, Moon } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const pageTitle = computed(() => route.meta.title || '')
const currentPath = computed(() => route.path)

// 主题切换（使用 composable）
const { isDark, toggleTheme, initTheme, syncThemeAcrossTabs } = useTheme()

// 初始化主题
onMounted(() => {
  initTheme()
  syncThemeAcrossTabs()
})

// ===== Tags Bar Functionality =====
const showTagsBar = ref(true)

interface Tag {
  path: string
  title: string
  fixed?: boolean
}

const tags = ref<Tag[]>([
  { path: '/projects', title: 'Project Information', fixed: true }
])

// Add tag
const addTag = () => {
  const title = (route.meta?.title as string) || 'Untitled'
  const path = route.path
  
  if (path && path !== '/login' && !tags.value.some(t => t.path === path)) {
    tags.value.push({
      path,
      title,
      fixed: route.meta?.affix as boolean
    })
  }
}

// Click tag
const handleTagClick = (tag: Tag) => {
  if (route.path !== tag.path) {
    router.push(tag.path)
  }
}

// Close tag
const handleCloseTag = (tag: Tag) => {
  const index = tags.value.findIndex(t => t.path === tag.path)
  if (index > -1) {
    tags.value.splice(index, 1)
    
    // If closing current page, jump to previous tag
    if (route.path === tag.path && tags.value.length > 0) {
      const prevTag = tags.value[Math.max(0, index - 1)]
      router.push(prevTag.path)
    }
  }
}

// Watch route changes
watch(route, () => {
  addTag()
}, { immediate: true })

// Watch tags display settings
watch(() => localStorage.getItem('show-tags'), (val) => {
  showTagsBar.value = val !== 'false'
})

// Refresh page
const handleRefresh = () => {
  router.go(0)
}

// Close other tags
const handleCloseOthers = () => {
  tags.value = tags.value.filter(t => t.fixed || t.path === route.path)
  ElMessage.success('Other tags closed')
}

// Close all tags
const handleCloseAll = () => {
  tags.value = tags.value.filter(t => t.fixed)
  if (route.path !== '/projects') {
    router.push('/projects')
  }
  ElMessage.success('All tags closed')
}

// 右键菜单
const contextMenuVisible = ref(false)
const contextMenuStyle = ref({ left: '0px', top: '0px' })
const selectedTag = ref<Tag | null>(null)

const handleRightClick = (tag: Tag, event: MouseEvent) => {
  selectedTag.value = tag
  contextMenuVisible.value = true
  contextMenuStyle.value = {
    left: event.clientX + 'px',
    top: event.clientY + 'px'
  }
}

// 点击其他地方关闭右键菜单
const closeContextMenu = () => {
  contextMenuVisible.value = false
}

onMounted(() => {
  document.addEventListener('click', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
})
</script>

<style scoped lang="scss">
.navbar {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
  color: var(--app-text-primary);
}

.navbar-left {
  .page-title {
    font-size: 19px;
    font-weight: 600;
    letter-spacing: 0.2px;
    color: var(--app-text-primary);
  }
}

.settings-content {
  padding: 10px 0;

  .setting-group {
    padding: 0 20px;
    margin-bottom: 20px;

    h4 {
      font-size: 14px;
      color: #303133;
      margin: 0 0 15px 0;
      font-weight: 600;
    }

    .setting-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      span {
        font-size: 14px;
        color: #606266;
      }
    }
  }
}

.tags-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  transform: translateY(100%);
  height: 48px;
  background: linear-gradient(180deg, #ffffff 0%, #f9fcfe 100%);
  border-top: 1px solid #e1ebf2;
  box-shadow: 0 8px 20px rgba(15, 33, 53, 0.06);
  display: flex;
  align-items: center;
  z-index: 10;
}

.tags-wrapper {
  display: flex;
  gap: 8px;
  padding: 0 20px;
  overflow-x: auto;
  width: 100%;
  
  &::-webkit-scrollbar {
    height: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #c6d7e4;
    border-radius: 2px;
  }
}

.tag-item {
  display: inline-flex;
  align-items: center;
  padding: 0 16px;
  height: 32px;
  font-size: 13px;
  border: 1px solid #deebf3;
  border-radius: 16px;
  background: #f7fbfe;
  color: #51657b;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
  user-select: none;
  box-shadow: 0 1px 2px rgba(15, 33, 53, 0.04);

  &:hover {
    color: var(--el-color-primary);
    background: #ecf6fc;
    border-color: #c9e2f4;
    box-shadow: 0 3px 10px rgba(15, 130, 197, 0.12);
  }

  &.active {
    background: linear-gradient(135deg, #0f82c5 0%, #1b9cd8 100%);
    border-color: transparent;
    color: #ffffff;
    box-shadow: 0 6px 14px rgba(15, 130, 197, 0.28);
    font-weight: 500;

    .tag-close {
      color: #ffffff;
    }
  }

  .tag-close {
    margin-left: 8px;
    font-size: 12px;
    font-weight: bold;
    width: 16px;
    height: 16px;
    line-height: 16px;
    text-align: center;
    border-radius: 50%;
    color: #89a0b7;

    &:hover {
      background: rgba(22, 48, 73, 0.2);
      color: #fff;
      transform: scale(1.1);
    }
  }
}

.tags-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
  margin-left: auto;

  .action-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    font-size: 16px;
    border-radius: 50%;
    background: #f1f8fc;
    color: #567087;
    cursor: pointer;
    transition: all 0.25s ease;
    box-shadow: 0 1px 2px rgba(15, 33, 53, 0.05);

    &:hover {
      color: var(--el-color-primary);
      background: #e8f4fc;
      box-shadow: 0 3px 10px rgba(15, 130, 197, 0.14);
      transform: rotate(90deg);
    }
  }
}

.context-menu {
  position: fixed;
  background: #ffffff;
  border: 1px solid #dbe7ef;
  border-radius: 10px;
  box-shadow: 0 12px 28px rgba(15, 33, 53, 0.14);
  z-index: 3000;
  list-style: none;
  padding: 6px 0;
  margin: 0;
  min-width: 136px;

  li {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    font-size: 14px;
    color: var(--app-text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background-color: #edf6fc;
      color: var(--el-color-primary);
    }

    .el-icon {
      font-size: 14px;
    }
  }
}
</style>

