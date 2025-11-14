<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- Left side: Basic information card -->
      <el-col :span="8">
        <el-card shadow="hover" :loading="loading">
          <template #header>
            <div class="card-header">
              <span>Basic Information</span>
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
            <el-descriptions-item label="Username">
              {{ userInfo.username }}
            </el-descriptions-item>
            <el-descriptions-item label="Real Name">
              {{ userInfo.real_name || 'Not Set' }}
            </el-descriptions-item>
            <el-descriptions-item label="Position">
              {{ userInfo.position || 'Not Set' }}
            </el-descriptions-item>
            <el-descriptions-item label="Email">
              {{ userInfo.email || 'Not Set' }}
            </el-descriptions-item>
            <el-descriptions-item label="Role">
              {{ roleText }}
            </el-descriptions-item>
            <el-descriptions-item label="Created At">
              {{ formatDateTime(userInfo.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- Right side: Edit card -->
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Edit Information</span>
            </div>
          </template>

          <el-tabs v-model="activeTab">
            <el-tab-pane label="Profile" name="profile">
              <el-form
                ref="profileFormRef"
                :model="profileForm"
                :rules="profileRules"
                label-width="150px"
                style="max-width: 600px"
              >
                <el-form-item label="Real Name" prop="real_name">
                  <el-input v-model="profileForm.real_name" placeholder="Enter real name" />
                </el-form-item>
                <el-form-item label="Position" prop="position">
                  <el-input v-model="profileForm.position" placeholder="Enter position" />
                </el-form-item>
                <el-form-item label="Email" prop="email">
                  <el-input v-model="profileForm.email" type="email" placeholder="Enter email" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleUpdateProfile" :loading="submitLoading">
                    Save Changes
                  </el-button>
                  <el-button @click="resetProfileForm">Reset</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="Change Password" name="password">
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="160px"
                style="max-width: 600px"
              >
                <el-form-item label="Current Password" prop="old_password">
                  <el-input
                    v-model="passwordForm.old_password"
                    type="password"
                    placeholder="Enter current password"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="New Password" prop="new_password">
                  <el-input
                    v-model="passwordForm.new_password"
                    type="password"
                    placeholder="Enter new password"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="Confirm Password" prop="confirm_password">
                  <el-input
                    v-model="passwordForm.confirm_password"
                    type="password"
                    placeholder="Enter new password again"
                    show-password
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleChangePassword" :loading="submitLoading">
                    Change Password
                  </el-button>
                  <el-button @click="resetPasswordForm">Reset</el-button>
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
import {
  realNameRules,
  positionRules,
  emailRules,
  passwordRules as passwordValidationRules,
  createRequiredValidator,
} from '@/utils/validators'

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
    'admin': 'Administrator',
    'user': 'Regular User'
  }
  return roleMap[userInfo.value.role] || 'Unknown'
})

const profileRules: FormRules = {
  real_name: realNameRules,
  position: positionRules,
  email: emailRules,
}

const passwordRules: FormRules = {
  old_password: [createRequiredValidator('current password')],
  new_password: passwordValidationRules,
  confirm_password: [
    createRequiredValidator('password confirmation'),
    {
      validator: (_rule: any, value: string, callback: any) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('The two passwords do not match'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// Load user information
async function loadUserInfo() {
  loading.value = true
  try {
    const res = await getCurrentUserInfoApi()
    userInfo.value = res
    
    // Fill form
    profileForm.real_name = res.real_name || ''
    profileForm.position = res.position || ''
    profileForm.email = res.email || ''
  } catch (error) {
    console.error('Failed to load user information:', error)
    ElMessage.error('Failed to load user information')
  } finally {
    loading.value = false
  }
}

// Update profile
async function handleUpdateProfile() {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await updateProfileApi(profileForm)
        ElMessage.success('Update successful')
        // Reload user information
        await loadUserInfo()
        // Update user info in store
        userStore.setUserInfo(userInfo.value)
      } catch (error) {
        console.error('Update failed:', error)
        ElMessage.error('Update failed')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// Change password
async function handleChangePassword() {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await changePasswordApi(passwordForm)
        ElMessage.success('Password changed successfully, please login again')
        // Clear form
        resetPasswordForm()
        // Logout
        setTimeout(() => {
          userStore.logout()
          window.location.href = '/login'
        }, 1500)
      } catch (error) {
        console.error('Failed to change password:', error)
        ElMessage.error('Failed to change password')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// Reset profile form
function resetProfileForm() {
  profileForm.real_name = userInfo.value.real_name || ''
  profileForm.position = userInfo.value.position || ''
  profileForm.email = userInfo.value.email || ''
}

// Reset password form
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

