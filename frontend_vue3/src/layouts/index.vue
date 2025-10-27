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
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'
import { useHeartbeat } from '@/composables/useHeartbeat'

// 启动心跳监控
useHeartbeat()
</script>

<style scoped lang="scss">
.app-container {
  display: flex;
  width: 100%;
  height: 100%;
}

.sidebar-container {
  width: $sideBarWidth;
  height: 100%;
  background-color: #304156;
  transition: width $transitionDuration;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.navbar-container {
  height: $navBarHeight;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.content-container {
  flex: 1;
  padding: 20px;
  background-color: #f0f2f5;
  overflow-y: auto;
}
</style>

