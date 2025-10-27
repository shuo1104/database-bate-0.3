<template>
  <div class="sidebar">
    <div class="logo">
      <span class="logo-title">配方管理系统</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      :default-openeds="['database']"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      :collapse="false"
      router
    >
      <!-- 数据库管理 -->
      <el-sub-menu index="database">
        <template #title>
          <el-icon><DataBoard /></el-icon>
          <span>数据库管理</span>
        </template>
        <el-menu-item index="/projects">
          <el-icon><Operation /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-menu-item index="/materials">
          <el-icon><Box /></el-icon>
          <span>原料管理</span>
        </el-menu-item>
        <el-menu-item index="/fillers">
          <el-icon><Box /></el-icon>
          <span>填料管理</span>
        </el-menu-item>
        <el-menu-item index="/formulas">
          <el-icon><List /></el-icon>
          <span>配方成分管理</span>
        </el-menu-item>
        <el-menu-item index="/test-results">
          <el-icon><DataAnalysis /></el-icon>
          <span>测试结果管理</span>
        </el-menu-item>
      </el-sub-menu>

      <!-- 系统管理 (仅管理员可见) -->
      <el-sub-menu v-if="isAdmin" index="system">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>系统管理</span>
        </template>
        <el-menu-item index="/system/roles">
          <el-icon><Stamp /></el-icon>
          <span>角色管理</span>
        </el-menu-item>
        <el-menu-item index="/system/logs">
          <el-icon><Document /></el-icon>
          <span>系统日志</span>
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store'
import { 
  Operation, 
  Box, 
  List, 
  DataAnalysis, 
  DataBoard,
  Setting,
  User,
  Stamp,
  Document
} from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

// 判断是否为管理员
const isAdmin = computed(() => {
  return userStore.userInfo?.role === 'admin'
})
</script>

<style scoped lang="scss">
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b2f3a;
  
  .logo-title {
    color: #fff;
    font-size: 16px;
    font-weight: bold;
  }
}

.el-menu {
  border-right: none;
}
</style>

