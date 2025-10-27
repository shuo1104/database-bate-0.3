<template>
  <div class="app-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="statistics-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card clickable" @click="handleCardClick('all')">
          <el-statistic :value="total" title="总用户数">
            <template #prefix>
              <el-icon color="#409eff" :size="32"><User /></el-icon>
            </template>
          </el-statistic>
          <div class="card-footer">
            <span>点击查看用户列表</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card clickable" @click="handleCardClick('admin')">
          <div class="stat-content-center">
            <el-icon color="#67c23a" :size="40"><Avatar /></el-icon>
            <div class="stat-label">管理员</div>
            <div class="stat-value">{{ adminCount }}</div>
          </div>
          <div class="card-footer">
            <span>点击查看用户列表</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card clickable" @click="handleCardClick('user')">
          <div class="stat-content-center">
            <el-icon color="#409eff" :size="40"><User /></el-icon>
            <div class="stat-label">普通用户</div>
            <div class="stat-value">{{ normalUserCount }}</div>
          </div>
          <div class="card-footer">
            <span>点击查看用户列表</span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card clickable" @click="handleAdd">
          <div class="stat-content-center">
            <el-icon color="#409eff" :size="40"><Plus /></el-icon>
            <div class="stat-label">新增用户</div>
          </div>
          <div class="card-footer">
            <span>点击新增用户</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 用户列表对话框 -->
    <el-dialog
      v-model="listDialogVisible"
      :title="listDialogTitle"
      width="80%"
      top="5vh"
    >
      <template #header>
        <div class="card-header">
          <span>{{ listDialogTitle }}</span>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增用户</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="用户名">
          <el-input
            v-model="queryParams.username"
            placeholder="请输入用户名"
            clearable
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table
        v-loading="loading"
        :data="userList"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="user_id" label="用户ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="real_name" label="真实姓名" width="120" />
        <el-table-column prop="position" label="职位" width="120" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'success' : 'info'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 新增/编辑对话框 -->
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
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="!!form.user_id" />
        </el-form-item>
        <el-form-item v-if="!form.user_id" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="职位" prop="position">
          <el-input v-model="form.position" placeholder="请输入职位" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
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

// 统计数据（从后端获取全部用户来计算）
const allUsers = ref<any[]>([])
const adminCount = computed(() => {
  return allUsers.value.filter(u => u.role === 'admin').length
})

const normalUserCount = computed(() => {
  return allUsers.value.filter(u => u.role === 'user').length
})

// 列表对话框
const listDialogVisible = ref(false)
const listDialogTitle = ref('用户列表')

const dialogVisible = ref(false)
const dialogTitle = ref('新增用户')
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
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 获取所有用户（用于统计）
async function getAllUsers() {
  try {
    const res = await getUserListApi({ page: 1, page_size: 1000 })
    allUsers.value = res.items
    total.value = res.total
  } catch (error: any) {
    console.error('获取用户统计失败:', error)
  }
}

// 获取用户列表
async function getList() {
  loading.value = true
  try {
    const res = await getUserListApi(queryParams)
    userList.value = res.items
    total.value = res.total
  } catch (error: any) {
    console.error('获取用户列表失败:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.msg || '获取用户列表失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 查询
function handleQuery() {
  queryParams.page = 1
  getList()
}

// 重置
function handleReset() {
  queryParams.username = ''
  queryParams.role = ''
  handleQuery()
}

// 处理卡片点击
function handleCardClick(type: string) {
  queryParams.page = 1
  queryParams.username = ''
  
  if (type === 'all') {
    queryParams.role = ''
    listDialogTitle.value = '全部用户'
  } else if (type === 'admin') {
    queryParams.role = 'admin'
    listDialogTitle.value = '管理员列表'
  } else if (type === 'user') {
    queryParams.role = 'user'
    listDialogTitle.value = '普通用户列表'
  }
  
  listDialogVisible.value = true
  getList()
}

// 新增
function handleAdd() {
  dialogTitle.value = '新增用户'
  dialogVisible.value = true
}

// 编辑
function handleEdit(row: any) {
  dialogTitle.value = '编辑用户'
  Object.assign(form, row)
  dialogVisible.value = true
}

// 删除
function handleDelete(row: UserInfo) {
  ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteUserApi(row.user_id)
      ElMessage.success('删除成功')
      getList()
      getAllUsers() // 重新加载统计数据
    } catch (error: any) {
      console.error('删除失败:', error)
      const errorMsg = error.response?.data?.detail || error.response?.data?.msg || '删除失败'
      ElMessage.error(errorMsg)
    }
  })
}

// 重置密码
function handleResetPassword(row: UserInfo) {
  ElMessageBox.prompt(`请输入用户 "${row.username}" 的新密码`, '重置密码', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /.{6,}/,
    inputErrorMessage: '密码长度不能少于6个字符',
  }).then(async ({ value }) => {
    try {
      await resetUserPasswordApi(row.user_id, { new_password: value })
      ElMessage.success('密码重置成功')
    } catch (error: any) {
      console.error('重置密码失败:', error)
      const errorMsg = error.response?.data?.detail || error.response?.data?.msg || '重置密码失败'
      ElMessage.error(errorMsg)
    }
  })
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (form.user_id) {
          // 更新用户
          await updateUserApi(form.user_id, {
            real_name: form.real_name || undefined,
            position: form.position || undefined,
            email: form.email || undefined,
            role: form.role
          })
          ElMessage.success('更新成功')
        } else {
          // 创建用户
          await createUserApi({
            username: form.username,
            password: form.password,
            real_name: form.real_name || undefined,
            position: form.position || undefined,
            email: form.email || undefined,
            role: form.role
          })
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        getList()
        getAllUsers() // 重新加载统计数据
      } catch (error: any) {
        console.error('提交失败:', error)
        const errorMsg = error.response?.data?.detail || error.response?.data?.msg || '提交失败'
        ElMessage.error(errorMsg)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 关闭对话框
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
  // 加载统计数据
  getAllUsers()
})
</script>

<style scoped lang="scss">
.app-container {
  padding: 20px;
}

.statistics-cards {
  margin-bottom: 20px;
  
  .stat-card {
    height: 200px;
    transition: all 0.3s;
    display: flex;
    flex-direction: column;
    
    :deep(.el-card__body) {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    
    &.clickable {
      cursor: pointer;
      
      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        border-color: #409eff;
      }
    }
    
    .stat-content-center {
      text-align: center;
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12px;
      
      .stat-label {
        font-size: 16px;
        color: #606266;
        font-weight: 500;
      }
      
      .stat-value {
        font-size: 36px;
        font-weight: bold;
        color: #303133;
      }
    }
    
    .card-footer {
      text-align: center;
      padding-top: 12px;
      border-top: 1px solid #ebeef5;
      color: #909399;
      font-size: 13px;
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
