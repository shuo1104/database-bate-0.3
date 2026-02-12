<template>
  <div class="app-container">
    <div class="sidebar-container">
      <Sidebar />
    </div>
    <div class="main-container">
      <div class="navbar-container">
        <Navbar />
      </div>
      <div class="content-container">
        <router-view v-slot="{ Component, route }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'
import { useHeartbeat } from '@/composables/useHeartbeat'

// 可选：启动心跳监控
const { init: initHeartbeat, destroy: destroyHeartbeat } = useHeartbeat()

onMounted(() => {
  initHeartbeat()
})

onUnmounted(() => {
  destroyHeartbeat()
})
</script>

<style scoped lang="scss">
.app-container {
  display: flex;
  width: 100%;
  height: 100%;
  background: transparent;
}

.sidebar-container {
  width: 304px;
  height: 100%;
  background-color: var(--app-surface);
  border-right: 1px solid var(--app-border);
  transition: width $transitionDuration;
  overflow: hidden;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.navbar-container {
  position: relative;
  min-height: $navBarHeight;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  border-bottom: 1px solid var(--app-border);
  box-shadow: 0 6px 18px rgba(15, 33, 53, 0.06);
  margin-bottom: 48px; // 为标签栏留出空间
}

.content-container {
  flex: 1;
  padding: 20px;
  background-color: transparent;
  overflow-y: auto;
}

// 页面切换动画 (简化为淡入淡出)
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.22s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

