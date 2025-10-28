<template>
  <div class="tags-view-container">
    <div class="tags-view-wrapper">
      <router-link
        v-for="tag in visitedViews"
        :key="tag.path"
        :to="{ path: tag.path }"
        :class="{ active: isActive(tag) }"
        class="tags-view-item"
      >
        {{ tag.title }}
        <span
          v-if="!isAffix(tag)"
          class="el-icon-close"
          @click.prevent.stop="closeSelectedTag(tag)"
        >
          ×
        </span>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

interface TagView {
  path: string
  title: string
  affix?: boolean
}

const visitedViews = ref<TagView[]>([])

// 判断是否为当前激活的标签
const isActive = (tag: TagView) => {
  return tag.path === route.path
}

// 判断是否为固定标签
const isAffix = (tag: TagView) => {
  return tag.affix || false
}

// 添加标签
const addTag = () => {
  const title = (route.meta?.title as string) || route.name as string || '未命名'
  const path = route.path
  
  if (path && !visitedViews.value.some(v => v.path === path)) {
    visitedViews.value.push({
      path,
      title,
      affix: route.meta?.affix as boolean
    })
  }
}

// 关闭标签
const closeSelectedTag = (view: TagView) => {
  const index = visitedViews.value.findIndex(v => v.path === view.path)
  if (index > -1) {
    visitedViews.value.splice(index, 1)
    
    if (isActive(view)) {
      const latestView = visitedViews.value[visitedViews.value.length - 1]
      if (latestView) {
        router.push(latestView.path)
      }
    }
  }
}

// 监听路由变化
watch(route, () => {
  addTag()
}, { immediate: true })
</script>

<style scoped lang="scss">
.tags-view-container {
  height: 34px;
  width: 100%;
  background: #fff;
  border-bottom: 1px solid #d8dce5;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.12);
  display: flex;
  align-items: center;
}

.tags-view-wrapper {
  display: flex;
  padding: 0 15px;
  gap: 5px;
  overflow-x: auto;
  overflow-y: hidden;
  
  &::-webkit-scrollbar {
    height: 0;
  }
}

.tags-view-item {
  display: inline-flex;
  align-items: center;
  position: relative;
  cursor: pointer;
  height: 26px;
  line-height: 26px;
  border: 1px solid #d8dce5;
  color: #495060;
  background: #fff;
  padding: 0 8px;
  font-size: 12px;
  text-decoration: none;
  transition: all 0.3s;

  &:hover {
    color: #409eff;
  }

  &.active {
    background-color: #409eff;
    color: #fff;
    border-color: #409eff;
  }

  .el-icon-close {
    margin-left: 5px;
    width: 14px;
    height: 14px;
    line-height: 14px;
    text-align: center;
    border-radius: 50%;
    font-size: 12px;
    
    &:hover {
      background-color: rgba(0, 0, 0, 0.2);
      color: #fff;
    }
  }
}
</style>
