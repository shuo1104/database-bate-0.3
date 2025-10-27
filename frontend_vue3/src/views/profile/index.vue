<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 左侧基本信息卡片 -->
      <el-col :span="8">
        <el-card shadow="hover" :loading="loading">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
            </div>
          </template>
          
          <div class="user-info-header">
            <div class="avatar-wrapper">
              <el-avatar 
                v-if="userInfo.avatar"
                :src="userInfo.avatar" 
                :size="120"
              />
              <el-avatar 
                v-else
                :icon="UserFilled" 
                :size="120"
              />
            </div>
            <div class="user-name">{{ userInfo.real_name || userInfo.username }}</div>
            <el-tag :type="userInfo.role === 'admin' ? 'success' : 'info'">
              {{ roleText }}
            </el-tag>
          </div>

          <el-divider />

          <el-descriptions :column="1" size="default" class="user-details">
            <el-descriptions-item label="用户名">
              {{ userInfo.username }}
            </el-descriptions-item>
            <el-descriptions-item label="真实姓名">
              {{ userInfo.real_name || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="职位">
              {{ userInfo.position || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ userInfo.email || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="角色">
              {{ roleText }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(userInfo.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 右侧编辑卡片 -->
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>编辑信息</span>
            </div>
          </template>

          <el-tabs v-model="activeTab">
            <el-tab-pane label="个人信息" name="profile">
              <el-form
                ref="profileFormRef"
                :model="profileForm"
                :rules="profileRules"
                label-width="100px"
                style="max-width: 600px"
              >
                <el-form-item label="真实姓名" prop="real_name">
                  <el-input v-model="profileForm.real_name" placeholder="请输入真实姓名" />
                </el-form-item>
                <el-form-item label="职位" prop="position">
                  <el-input v-model="profileForm.position" placeholder="请输入职位" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profileForm.email" type="email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleUpdateProfile" :loading="submitLoading">
                    保存修改
                  </el-button>
                  <el-button @click="resetProfileForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="修改密码" name="password">
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="100px"
                style="max-width: 600px"
              >
                <el-form-item label="当前密码" prop="old_password">
                  <el-input
                    v-model="passwordForm.old_password"
                    type="password"
                    placeholder="请输入当前密码"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="新密码" prop="new_password">
                  <el-input
                    v-model="passwordForm.new_password"
                    type="password"
                    placeholder="请输入新密码"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="确认密码" prop="confirm_password">
                  <el-input
                    v-model="passwordForm.confirm_password"
                    type="password"
                    placeholder="请再次输入新密码"
                    show-password
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleChangePassword" :loading="submitLoading">
                    修改密码
                  </el-button>
                  <el-button @click="resetPasswordForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { getCurrentUserInfoApi, updateProfileApi, changePasswordApi } from '@/api/auth'
import { formatDateTime } from '@/utils/common'
import { useUserStore } from '@/store'

const userStore = useUserStore()

const loading = ref(false)
const submitLoading = ref(false)
const activeTab = ref('profile')

const userInfo = ref<any>({
  username: '',
  real_name: '',
  position: '',
  email: '',
  role: '',
  created_at: '',
  avatar: ''
})

const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const profileForm = reactive({
  real_name: '',
  position: '',
  email: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const roleText = computed(() => {
  const roleMap: Record<string, string> = {
    'admin': '管理员',
    'user': '普通用户'
  }
  return roleMap[userInfo.value.role] || '未知'
})

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const profileRules: FormRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const passwordRules: FormRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 加载用户信息
async function loadUserInfo() {
  loading.value = true
  try {
    const res = await getCurrentUserInfoApi()
    userInfo.value = res
    
    // 填充表单
    profileForm.real_name = res.real_name || ''
    profileForm.position = res.position || ''
    profileForm.email = res.email || ''
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败')
  } finally {
    loading.value = false
  }
}

// 更新个人信息
async function handleUpdateProfile() {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await updateProfileApi(profileForm)
        ElMessage.success('更新成功')
        // 重新加载用户信息
        await loadUserInfo()
        // 更新store中的用户信息
        userStore.setUserInfo(userInfo.value)
      } catch (error) {
        console.error('更新失败:', error)
        ElMessage.error('更新失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 修改密码
async function handleChangePassword() {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await changePasswordApi(passwordForm)
        ElMessage.success('密码修改成功，请重新登录')
        // 清空表单
        resetPasswordForm()
        // 退出登录
        setTimeout(() => {
          userStore.logout()
          window.location.href = '/login'
        }, 1500)
      } catch (error) {
        console.error('修改密码失败:', error)
        ElMessage.error('修改密码失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 重置个人信息表单
function resetProfileForm() {
  profileForm.real_name = userInfo.value.real_name || ''
  profileForm.position = userInfo.value.position || ''
  profileForm.email = userInfo.value.email || ''
}

// 重置密码表单
function resetPasswordForm() {
  passwordFormRef.value?.resetFields()
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped lang="scss">
.profile-container {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
  }
  
  .user-info-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0;
    
    .avatar-wrapper {
      margin-bottom: 20px;
      cursor: pointer;
      transition: transform 0.3s;
      
      &:hover {
        transform: scale(1.05);
      }
    }
    
    .user-name {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 10px;
      color: #303133;
    }
  }
  
  .user-details {
    margin-top: 20px;
  }
}
</style>

