<template>
  <div class="modern-sidebar">
    <!-- Logo 区域 -->
    <div class="sidebar-logo">
      <div class="logo-icon">
        <el-icon :size="28"><Grid /></el-icon>
      </div>
      <div class="logo-text">
        <div class="logo-title">Advanced</div>
        <div class="logo-subtitle">PhotoPolymer DB</div>
      </div>
    </div>

    <!-- 导航菜单 -->
    <div class="sidebar-menu">
      <!-- 数据库管理 -->
      <div class="menu-group">
        <div 
          class="menu-item expandable"
          :class="{ expanded: databaseExpanded }"
          @click="toggleDatabase"
        >
          <div class="menu-icon">
            <el-icon :size="20"><DataBoard /></el-icon>
          </div>
          <span class="menu-text">Database Management</span>
          <el-icon class="expand-icon" :class="{ rotated: databaseExpanded }">
            <ArrowDown />
          </el-icon>
        </div>
        
        <!-- Database Submenu -->
        <transition name="submenu">
          <div v-show="databaseExpanded" class="submenu-container">
            <router-link to="/projects" class="submenu-item" :class="{ active: activeMenu === '/projects' }">
              <el-icon :size="16"><Operation /></el-icon>
              <span>Projects</span>
            </router-link>
            <router-link to="/materials" class="submenu-item" :class="{ active: activeMenu === '/materials' }">
              <el-icon :size="16"><Box /></el-icon>
              <span>Materials</span>
            </router-link>
            <router-link to="/fillers" class="submenu-item" :class="{ active: activeMenu === '/fillers' }">
              <el-icon :size="16"><Box /></el-icon>
              <span>Fillers</span>
            </router-link>
            <router-link to="/formulas" class="submenu-item" :class="{ active: activeMenu === '/formulas' }">
              <el-icon :size="16"><List /></el-icon>
              <span>Formulas</span>
            </router-link>
            <router-link to="/test-results" class="submenu-item" :class="{ active: activeMenu === '/test-results' }">
              <el-icon :size="16"><DataAnalysis /></el-icon>
              <span>Test Results</span>
            </router-link>
          </div>
        </transition>
      </div>

      <!-- System Management (Admin) -->
      <div v-if="isAdmin" class="menu-group">
        <div 
          class="menu-item expandable"
          :class="{ expanded: systemExpanded }"
          @click="toggleSystem"
        >
          <div class="menu-icon">
            <el-icon :size="20"><Setting /></el-icon>
          </div>
          <span class="menu-text">System Management</span>
          <el-icon class="expand-icon" :class="{ rotated: systemExpanded }">
            <ArrowDown />
          </el-icon>
        </div>
        
        <!-- System Management Submenu -->
        <transition name="submenu">
          <div v-show="systemExpanded" class="submenu-container">
            <router-link to="/system/roles" class="submenu-item" :class="{ active: activeMenu === '/system/roles' }">
              <el-icon :size="16"><Stamp /></el-icon>
              <span>Roles</span>
            </router-link>
            <router-link to="/system/logs" class="submenu-item" :class="{ active: activeMenu === '/system/logs' }">
              <el-icon :size="16"><Document /></el-icon>
              <span>System Logs</span>
            </router-link>
          </div>
        </transition>
      </div>
    </div>

    <!-- 底部 -->
    <div class="sidebar-footer">
      <div class="footer-divider"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store'
import { 
  DataBoard,
  Operation,
  Box, 
  List,
  DataAnalysis,
  Setting,
  Stamp,
  Document,
  ArrowDown,
  Grid
} from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const databaseExpanded = ref(true) // Database management expand state
const systemExpanded = ref(false) // System management expand state

// Check if user is admin
const isAdmin = computed(() => {
  return userStore.userInfo?.role === 'admin'
})

// Toggle database management expand/collapse
const toggleDatabase = () => {
  databaseExpanded.value = !databaseExpanded.value
}

// Toggle system management expand/collapse
const toggleSystem = () => {
  systemExpanded.value = !systemExpanded.value
}
</script>

<style scoped lang="scss">
.modern-sidebar {
  width: 240px;
  height: 100vh;
  background: #fff;
  border-right: none;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  
  // Logo 区域
  .sidebar-logo {
    padding: 24px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: none;
    
    .logo-icon {
      width: 42px;
      height: 42px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      flex-shrink: 0;
    }
    
    .logo-text {
      flex: 1;
      
      .logo-title {
        font-size: 16px;
        font-weight: 600;
        color: #111827;
        line-height: 1.2;
      }
      
      .logo-subtitle {
        font-size: 11px;
        color: #9ca3af;
        margin-top: 2px;
        letter-spacing: 0.5px;
      }
    }
  }
  
  // 菜单区域
  .sidebar-menu {
    flex: 1;
    padding: 16px 12px;
    
    .menu-group {
      margin-bottom: 8px;
    }
    
    .menu-item {
      display: flex;
      align-items: center;
      padding: 12px 12px;
      margin-bottom: 4px;
      border-radius: 8px;
      cursor: pointer;
      text-decoration: none;
      color: #6b7280;
      transition: all 0.2s ease;
      position: relative;
      
      .menu-icon {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        flex-shrink: 0;
      }
      
      .menu-text {
        flex: 1;
        font-size: 14px;
        font-weight: 500;
      }
      
      .menu-badge {
        background: #ef4444;
        color: #fff;
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 10px;
        font-weight: 600;
        min-width: 18px;
        text-align: center;
      }
      
      .expand-icon {
        margin-left: auto;
        transition: transform 0.3s ease;
        font-size: 14px;
        
        &.rotated {
          transform: rotate(180deg);
        }
      }
      
      &:hover {
        background: #ffffff;
        color: #374151;
      }
      
      &.active {
        background: #ffffff;
        color: #7c3aed;
        
        .menu-icon {
          color: #7c3aed;
        }
        
        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 3px;
          height: 20px;
          background: #7c3aed;
          border-radius: 0 2px 2px 0;
        }
      }
      
      &.expandable {
        cursor: pointer;
        user-select: none;
        
        &.expanded {
          margin-bottom: 0;
        }
      }
    }
    
    // 子菜单
    .submenu-container {
      margin-left: 32px;
      margin-bottom: 8px;
      padding-left: 12px;
      border-left: none;
      
      .submenu-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        margin-bottom: 2px;
        border-radius: 6px;
        color: #9ca3af;
        font-size: 13px;
        text-decoration: none;
        transition: all 0.2s ease;
        
        &:hover {
          background: #ffffff;
          color: #6b7280;
        }
        
        &.active {
          background: #ffffff;
          color: #7c3aed;
          font-weight: 500;
        }
      }
    }
  }
  
  // 底部
  .sidebar-footer {
    padding: 16px 12px;
    
    .footer-divider {
      height: 0;
      background: transparent;
    }
  }
}

// 子菜单展开/收起动画
.submenu-enter-active,
.submenu-leave-active {
  transition: all 0.3s ease;
  max-height: 200px;
  overflow: hidden;
}

.submenu-enter-from,
.submenu-leave-to {
  max-height: 0;
  opacity: 0;
}

// 滚动条样式
.modern-sidebar::-webkit-scrollbar {
  width: 6px;
}

.modern-sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.modern-sidebar::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 3px;
  
  &:hover {
    background: #d1d5db;
  }
}
</style>

