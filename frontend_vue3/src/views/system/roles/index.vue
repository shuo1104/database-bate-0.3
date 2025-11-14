<template>
  <div class="app-container">
    <!-- Statistics Cards -->
    <el-row :gutter="20" class="statistics-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card clickable" @click="handleCardClick('all')">
          <div class="stat-content-center">
            <el-icon color="#409eff" :size="40"><User /></el-icon>
            <div class="stat-label">Total Users</div>
            <div class="stat-value">{{ total }}</div>
          </div>
          <div class="card-footer">
            <span>Click to view user list</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card clickable" @click="handleCardClick('admin')">
          <div class="stat-content-center">
            <el-icon color="#67c23a" :size="40"><Avatar /></el-icon>
            <div class="stat-label">Administrators</div>
            <div class="stat-value">{{ adminCount }}</div>
          </div>
          <div class="card-footer">
            <span>Click to view user list</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card clickable" @click="handleCardClick('user')">
          <div class="stat-content-center">
            <el-icon color="#409eff" :size="40"><User /></el-icon>
            <div class="stat-label">Regular Users</div>
            <div class="stat-value">{{ normalUserCount }}</div>
          </div>
          <div class="card-footer">
            <span>Click to view user list</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card clickable" @click="handleAdd">
          <div class="stat-content-center">
            <el-icon color="#409eff" :size="40"><Plus /></el-icon>
            <div class="stat-label">Add User</div>
          </div>
          <div class="card-footer">
            <span>Click to add user</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- User List Dialog -->
    <el-dialog
      v-model="listDialogVisible"
      :title="listDialogTitle"
      width="80%"
      top="5vh"
    >
      <template #header>
        <div class="card-header">
          <span>{{ listDialogTitle }}</span>
          <el-button type="primary" :icon="Plus" @click="handleAdd">Add User</el-button>
        </div>
      </template>

      <!-- Search Bar -->
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="Username">
          <el-input
            v-model="queryParams.username"
            placeholder="Enter username"
            clearable
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">Search</el-button>
          <el-button :icon="Refresh" @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- Table -->
      <el-table
        v-loading="loading"
        :data="userList"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="user_id" label="User ID" width="80" />
        <el-table-column prop="username" label="Username" width="150" />
        <el-table-column prop="real_name" label="Real Name" width="120" />
        <el-table-column prop="position" label="Position" width="120" />
        <el-table-column prop="email" label="Email" width="200" />
        <el-table-column prop="role" label="Role" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'success' : 'info'">
              {{ row.role === 'admin' ? 'Admin' : 'User' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? 'Active' : 'Inactive' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Created Time" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">Edit</el-button>
            <el-button link type="primary" @click="handleResetPassword(row)">Reset Password</el-button>
            <el-button link type="danger" @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <el-pagination
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="getList"
        @current-change="getList"
      />
    </el-dialog>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" placeholder="Enter username" :disabled="!!form.user_id" />
        </el-form-item>
        <el-form-item v-if="!form.user_id" label="Password" prop="password">
          <el-input v-model="form.password" type="password" placeholder="Enter password" show-password />
        </el-form-item>
        <el-form-item label="Real Name" prop="real_name">
          <el-input v-model="form.real_name" placeholder="Enter real name" />
        </el-form-item>
        <el-form-item label="Position" prop="position">
          <el-input v-model="form.position" placeholder="Enter position" />
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" placeholder="Enter email" />
        </el-form-item>
        <el-form-item label="Role" prop="role">
          <el-select v-model="form.role" placeholder="Select role">
            <el-option label="Administrator" value="admin" />
            <el-option label="User" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Search, Refresh, User, Avatar } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/common'
import {
  getUserListApi,
  createUserApi,
  updateUserApi,
  deleteUserApi,
  resetUserPasswordApi,
  type UserInfo
} from '@/api/users'

const loading = ref(false)
const submitLoading = ref(false)
const userList = ref<any[]>([])
const total = ref(0)

const queryParams = reactive({
  page: 1,
  page_size: 10,
  username: '',
  role: ''
})

// Statistics data (calculate from all users fetched from backend)
const allUsers = ref<any[]>([])
const adminCount = computed(() => {
  return allUsers.value.filter(u => u.role === 'admin').length
})

const normalUserCount = computed(() => {
  return allUsers.value.filter(u => u.role === 'user').length
})

// List dialog
const listDialogVisible = ref(false)
const listDialogTitle = ref('User List')

const dialogVisible = ref(false)
const dialogTitle = ref('Add User')
const formRef = ref<FormInstance>()

const form = reactive<any>({
  user_id: null,
  username: '',
  password: '',
  real_name: '',
  position: '',
  email: '',
  role: 'user'
})

const rules: FormRules = {
  username: [
    { required: true, message: 'Please enter username', trigger: 'blur' },
    { min: 3, max: 50, message: 'Username length must be between 3 and 50 characters', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  role: [
    { required: true, message: 'Please select role', trigger: 'change' }
  ]
}

// Get all users (for statistics)
async function getAllUsers() {
  try {
    const res = await getUserListApi({ page: 1, page_size: 1000 })
    allUsers.value = res.items
    total.value = res.total
  } catch (error: any) {
    console.error('Failed to get user statistics:', error)
  }
}

// Get user list
async function getList() {
  loading.value = true
  try {
    const res = await getUserListApi(queryParams)
    userList.value = res.items
    total.value = res.total
  } catch (error: any) {
    console.error('Failed to get user list:', error)
    // Error is already handled by axios interceptor
  } finally {
    loading.value = false
  }
}

// Query
function handleQuery() {
  queryParams.page = 1
  getList()
}

// Reset
function handleReset() {
  queryParams.username = ''
  queryParams.role = ''
  handleQuery()
}

// Handle card click
function handleCardClick(type: string) {
  queryParams.page = 1
  queryParams.username = ''
  
  if (type === 'all') {
    queryParams.role = ''
    listDialogTitle.value = 'All Users'
  } else if (type === 'admin') {
    queryParams.role = 'admin'
    listDialogTitle.value = 'Administrator List'
  } else if (type === 'user') {
    queryParams.role = 'user'
    listDialogTitle.value = 'Regular User List'
  }
  
  listDialogVisible.value = true
  getList()
}

// Add
function handleAdd() {
  dialogTitle.value = 'Add User'
  dialogVisible.value = true
}

// Edit
function handleEdit(row: any) {
  dialogTitle.value = 'Edit User'
  Object.assign(form, row)
  dialogVisible.value = true
}

// Delete
function handleDelete(row: UserInfo) {
  ElMessageBox.confirm(`Are you sure you want to delete user "${row.username}"?`, 'Confirm', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteUserApi(row.user_id)
      ElMessage.success('Deleted successfully')
      getList()
      getAllUsers() // Reload statistics data
    } catch (error: any) {
      console.error('Failed to delete:', error)
      // Error is already handled by axios interceptor
    }
  })
}

// Reset password
function handleResetPassword(row: UserInfo) {
  ElMessageBox.prompt(`Enter new password for user "${row.username}"`, 'Reset Password', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    inputPattern: /.{6,}/,
    inputErrorMessage: 'Password must be at least 6 characters',
  }).then(async ({ value }) => {
    try {
      await resetUserPasswordApi(row.user_id, { new_password: value })
      ElMessage.success('Password reset successfully')
    } catch (error: any) {
      console.error('Failed to reset password:', error)
      // Error is already handled by axios interceptor
    }
  })
}

// Submit form
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (form.user_id) {
          // Update user
          await updateUserApi(form.user_id, {
            real_name: form.real_name || undefined,
            position: form.position || undefined,
            email: form.email || undefined,
            role: form.role
          })
          ElMessage.success('Updated successfully')
        } else {
          // Create user
          await createUserApi({
            username: form.username,
            password: form.password,
            real_name: form.real_name || undefined,
            position: form.position || undefined,
            email: form.email || undefined,
            role: form.role
          })
          ElMessage.success('Created successfully')
        }
        dialogVisible.value = false
        getList()
        getAllUsers() // Reload statistics data
      } catch (error: any) {
        console.error('Failed to submit:', error)
        // Error is already handled by axios interceptor
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// Close dialog
function handleDialogClose() {
  formRef.value?.resetFields()
  form.user_id = null
  form.username = ''
  form.password = ''
  form.real_name = ''
  form.position = ''
  form.email = ''
  form.role = 'user'
}

onMounted(() => {
  // Load statistics data
  getAllUsers()
})
</script>

<style scoped lang="scss">
.app-container {
  padding: 20px;
}

.statistics-cards {
  margin-bottom: 30px;
  
  .stat-card {
    height: 180px;
    transition: all 0.3s ease;
    border-radius: 12px;
    overflow: hidden;
    
    :deep(.el-card__body) {
      height: 100%;
      padding: 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    
    &.clickable {
      cursor: pointer;
      
      &:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(64, 158, 255, 0.2);
        
        .stat-content-center {
          .el-icon {
            transform: scale(1.1);
          }
          
          .stat-value {
            color: #409eff;
          }
        }
        
        .card-footer {
          color: #409eff;
        }
      }
    }
    
    .stat-content-center {
      text-align: center;
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;
      
      .el-icon {
        transition: all 0.3s ease;
      }
      
      .stat-label {
        font-size: 15px;
        color: #909399;
        font-weight: 400;
        letter-spacing: 0.5px;
      }
      
      .stat-value {
        font-size: 42px;
        font-weight: 600;
        color: #303133;
        line-height: 1;
        transition: all 0.3s ease;
      }
    }
    
    .card-footer {
      text-align: center;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;
      color: #c0c4cc;
      font-size: 13px;
      transition: all 0.3s ease;
      font-weight: 400;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 16px;
}

.el-table {
  margin-bottom: 16px;
}

.el-pagination {
  justify-content: flex-end;
}
</style>
