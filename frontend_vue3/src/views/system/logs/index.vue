<template>
  <div class="app-container">
    <el-row :gutter="20">
      <!-- Left: Statistics Cards -->
      <el-col :span="12" class="left-section">
        <el-row :gutter="20" class="statistics-cards">
          <!-- First row: 3 cards -->
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <el-icon color="#409eff" :size="36"><User /></el-icon>
                <div class="stat-info">
                  <div class="stat-label">Total Users</div>
                  <div class="stat-value">{{ statistics.total_users || 0 }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <el-icon color="#67c23a" :size="36"><DataBoard /></el-icon>
                <div class="stat-info">
                  <div class="stat-label">Total Projects</div>
                  <div class="stat-value">{{ statistics.total_projects || 0 }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <el-icon color="#e6a23c" :size="36"><Box /></el-icon>
                <div class="stat-info">
                  <div class="stat-label">Total Materials</div>
                  <div class="stat-value">{{ statistics.total_materials || 0 }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <!-- Second row: 3 cards -->
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <el-icon color="#909399" :size="36"><Grid /></el-icon>
                <div class="stat-info">
                  <div class="stat-label">Total Fillers</div>
                  <div class="stat-value">{{ statistics.total_fillers || 0 }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <el-icon color="#f56c6c" :size="36"><Clock /></el-icon>
                <div class="stat-info">
                  <div class="stat-label">System Uptime</div>
                  <div class="stat-value">{{ statistics.system_uptime_days || 0 }} days</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <el-icon color="#1890ff" :size="36"><Calendar /></el-icon>
                <div class="stat-info">
                  <div class="stat-label">Logins Today</div>
                  <div class="stat-value">{{ statistics.total_logins_today || 0 }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <!-- Third row: 1 card -->
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-content">
                <el-icon color="#52c41a" :size="36"><UserFilled /></el-icon>
                <div class="stat-info">
                  <div class="stat-label">Active Users Today</div>
                  <div class="stat-value">{{ statistics.active_users_today || 0 }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-col>

      <!-- Right: Logs List -->
      <el-col :span="12" class="right-section">
        <el-card class="logs-card">
      <template #header>
        <div class="card-header">
          <span>System Logs</span>
        </div>
      </template>

      <!-- Tab Switching -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange as any">
        <el-tab-pane label="Login Logs" name="login">
          <!-- Search Bar -->
          <el-form :inline="true" :model="loginQuery" class="search-form">
            <el-form-item label="Username">
              <el-input
                v-model="loginQuery.username"
                placeholder="Enter username"
                clearable
                @keyup.enter="getLoginLogs"
              />
            </el-form-item>
            <el-form-item label="Date Range">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="to"
                start-placeholder="Start date"
                end-placeholder="End date"
                value-format="YYYY-MM-DD HH:mm:ss"
                @change="handleDateChange"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :icon="Search" @click="getLoginLogs">Search</el-button>
              <el-button :icon="Refresh" @click="handleReset">Reset</el-button>
            </el-form-item>
          </el-form>

          <!-- Login Logs Table -->
          <el-table
            v-loading="loginLoading"
            :data="loginLogs"
            stripe
            border
          >
            <el-table-column prop="log_id" label="Log ID" width="80" />
            <el-table-column prop="username" label="Username" width="150" />
            <el-table-column prop="login_ip" label="Login IP" width="150" />
            <el-table-column prop="user_agent" label="User Agent" min-width="200" show-overflow-tooltip />
            <el-table-column prop="login_time" label="Login Time" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.login_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="logout_time" label="Logout Time" width="180">
              <template #default="{ row }">
                {{ row.logout_time ? formatDateTime(row.logout_time) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="usage_duration" label="Duration (min)" width="140">
              <template #default="{ row }">
                {{ row.usage_duration ? Math.round(row.usage_duration) : '-' }}
              </template>
            </el-table-column>
          </el-table>

          <!-- Pagination -->
          <el-pagination
            v-model:current-page="loginQuery.page"
            v-model:page-size="loginQuery.page_size"
            :total="loginTotal"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="getLoginLogs"
            @current-change="getLoginLogs"
          />
        </el-tab-pane>

        <el-tab-pane label="Registration Logs" name="registration">
          <!-- Search Bar -->
          <el-form :inline="true" :model="regQuery" class="search-form">
            <el-form-item label="Username">
              <el-input
                v-model="regQuery.username"
                placeholder="Enter username"
                clearable
                @keyup.enter="getRegistrationLogs"
              />
            </el-form-item>
            <el-form-item label="Date Range">
              <el-date-picker
                v-model="regDateRange"
                type="daterange"
                range-separator="to"
                start-placeholder="Start date"
                end-placeholder="End date"
                value-format="YYYY-MM-DD HH:mm:ss"
                @change="handleRegDateChange"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :icon="Search" @click="getRegistrationLogs">Search</el-button>
              <el-button :icon="Refresh" @click="handleRegReset">Reset</el-button>
            </el-form-item>
          </el-form>

          <!-- Registration Logs Table -->
          <el-table
            v-loading="regLoading"
            :data="regLogs"
            stripe
            border
          >
            <el-table-column prop="log_id" label="Log ID" width="80" />
            <el-table-column prop="username" label="Username" width="150" />
            <el-table-column prop="real_name" label="Real Name" width="120" />
            <el-table-column prop="email" label="Email" width="200" />
            <el-table-column prop="registration_ip" label="Registration IP" width="150" />
            <el-table-column prop="user_agent" label="User Agent" min-width="200" show-overflow-tooltip />
            <el-table-column prop="registration_time" label="Registration Time" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.registration_time) }}
              </template>
            </el-table-column>
          </el-table>

          <!-- Pagination -->
          <el-pagination
            v-model:current-page="regQuery.page"
            v-model:page-size="regQuery.page_size"
            :total="regTotal"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="getRegistrationLogs"
            @current-change="getRegistrationLogs"
          />
        </el-tab-pane>
      </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, DataBoard, Clock, UserFilled, Search, Refresh, Box, Grid, Calendar } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/common'
import {
  getSystemStatisticsApi,
  getLoginLogsApi,
  getRegistrationLogsApi
} from '@/api/logs'

const activeTab = ref('login')
const loginLoading = ref(false)
const regLoading = ref(false)

// 统计数据
const statistics = ref<any>({})

// 登录日志
const loginLogs = ref<any[]>([])
const loginTotal = ref(0)
const loginQuery = reactive({
  page: 1,
  page_size: 20,
  username: '',
  start_date: '',
  end_date: ''
})
const dateRange = ref<any>(null)

// 注册日志
const regLogs = ref<any[]>([])
const regTotal = ref(0)
const regQuery = reactive({
  page: 1,
  page_size: 20,
  username: '',
  start_date: '',
  end_date: ''
})
const regDateRange = ref<any>(null)

// Get system statistics
async function getStatistics() {
  try {
    const res = await getSystemStatisticsApi()
    statistics.value = res
  } catch (error: any) {
    console.error('Failed to get system statistics:', error)
    ElMessage.error('Failed to get system statistics')
  }
}

// Get login logs
async function getLoginLogs() {
  loginLoading.value = true
  try {
    // Build query parameters, exclude empty strings
    const params: any = {
      page: loginQuery.page,
      page_size: loginQuery.page_size,
    }
    if (loginQuery.username) {
      params.username = loginQuery.username
    }
    if (loginQuery.start_date) {
      params.start_date = loginQuery.start_date
    }
    if (loginQuery.end_date) {
      params.end_date = loginQuery.end_date
    }
    
    const res = await getLoginLogsApi(params)
    loginLogs.value = res.items
    loginTotal.value = res.total
  } catch (error: any) {
    console.error('Failed to get login logs:', error)
    ElMessage.error('Failed to get login logs')
  } finally {
    loginLoading.value = false
  }
}

// Get registration logs
async function getRegistrationLogs() {
  regLoading.value = true
  try {
    // Build query parameters, exclude empty strings
    const params: any = {
      page: regQuery.page,
      page_size: regQuery.page_size,
    }
    if (regQuery.username) {
      params.username = regQuery.username
    }
    if (regQuery.start_date) {
      params.start_date = regQuery.start_date
    }
    if (regQuery.end_date) {
      params.end_date = regQuery.end_date
    }
    
    const res = await getRegistrationLogsApi(params)
    regLogs.value = res.items
    regTotal.value = res.total
  } catch (error: any) {
    console.error('Failed to get registration logs:', error)
    ElMessage.error('Failed to get registration logs')
  } finally {
    regLoading.value = false
  }
}

// Handle date range change
function handleDateChange(value: any) {
  if (value && value.length === 2) {
    loginQuery.start_date = value[0]
    loginQuery.end_date = value[1]
  } else {
    loginQuery.start_date = ''
    loginQuery.end_date = ''
  }
}

function handleRegDateChange(value: any) {
  if (value && value.length === 2) {
    regQuery.start_date = value[0]
    regQuery.end_date = value[1]
  } else {
    regQuery.start_date = ''
    regQuery.end_date = ''
  }
}

// Reset
function handleReset() {
  loginQuery.username = ''
  loginQuery.start_date = ''
  loginQuery.end_date = ''
  dateRange.value = null
  loginQuery.page = 1
  getLoginLogs()
}

function handleRegReset() {
  regQuery.username = ''
  regQuery.start_date = ''
  regQuery.end_date = ''
  regDateRange.value = null
  regQuery.page = 1
  getRegistrationLogs()
}

// Tab change
function handleTabChange(name: string) {
  if (name === 'login') {
    getLoginLogs()
  } else if (name === 'registration') {
    getRegistrationLogs()
  }
}

onMounted(() => {
  getStatistics()
  getLoginLogs()
})
</script>

<style scoped lang="scss">
.app-container {
  padding: 20px;
  min-height: calc(100vh - 100px);
  background-color: #ffffff !important;
  
  > .el-row {
    min-height: 100%;
  }
}

.left-section {
  height: 100%;
  overflow-y: auto;
  
  .statistics-cards {
    .stat-card {
      margin-bottom: 20px;
      
      :deep(.el-card__body) {
        padding: 18px;
      }
      
      .stat-content {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .stat-info {
          flex: 1;
          
          .stat-label {
            font-size: 13px;
            color: #909399;
            margin-bottom: 6px;
          }
          
          .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #303133;
          }
        }
      }
    }
  }
}

.right-section {
  height: 100%;
  
  .logs-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    
    :deep(.el-card__body) {
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    
    .card-header {
      font-size: 18px;
      font-weight: bold;
    }
    
    .el-tabs {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      
      :deep(.el-tabs__content) {
        flex: 1;
        overflow-y: auto;
      }
    }
    
    .search-form {
      margin-bottom: 16px;
    }
    
    .el-table {
      margin-bottom: 16px;
    }
    
    .el-pagination {
      justify-content: flex-end;
      margin-top: 16px;
    }
  }
}
</style>

