<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- Login Card -->
    <div class="login-card">
      <!-- Logo and Title -->
      <div class="login-header">
        <div class="logo-wrapper">
          <img src="@/assets/images/logo.png" alt="Logo" class="logo-image" />
        </div>
        <h1 class="system-title">
          <span class="company-name">Advanced</span>
          <span class="product-name">PhotoPolymer</span>
        </h1>
        <p class="system-subtitle">Formulation Management DB</p>
      </div>

      <!-- Login Form -->
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="Enter username"
            size="large"
            clearable
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon class="input-icon"><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Enter password"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon class="input-icon"><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item class="login-button-item">
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            <span v-if="!loading">Login</span>
            <span v-else>Logging in...</span>
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Footer Info -->
      <div class="login-footer">
        <p class="copyright">© 2025 Advanced - PhotoPolymer Formulation Management DB</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { User, Lock, Grid } from '@element-plus/icons-vue'
import { useUserStore } from '@/store'
import { usernameRules, passwordRules } from '@/utils/validators'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const loginRules = {
  username: usernameRules,
  password: passwordRules,
}

async function handleLogin() {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(loginForm)
        ElMessage.success('Login successful')
        
        // Redirect to previous page or home
        const redirect = route.query.redirect as string
        router.push(redirect || '/')
      } catch (error: any) {
        // Error is already handled by axios interceptor, no need to show again
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: radial-gradient(1200px circle at 88% -12%, #e3f1fa 0%, #f4f8fb 42%, #eef4f8 100%);
  transition: background 0.3s ease;
}

// 背景装饰圆圈
.bg-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;

  .circle {
    position: absolute;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(15, 130, 197, 0.11) 0%, rgba(23, 168, 144, 0.11) 100%);
    backdrop-filter: blur(2px);
    animation: float 20s infinite ease-in-out;
  }

  .circle-1 {
    width: 300px;
    height: 300px;
    top: -100px;
    right: -100px;
    animation-delay: 0s;
  }

  .circle-2 {
    width: 200px;
    height: 200px;
    bottom: -50px;
    left: 10%;
    animation-delay: 5s;
  }

  .circle-3 {
    width: 400px;
    height: 400px;
    top: 50%;
    left: -200px;
    animation-delay: 10s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.3;
  }
  50% {
    transform: translateY(-30px) rotate(180deg);
    opacity: 0.6;
  }
}

// 登录卡片
.login-card {
  position: relative;
  z-index: 1;
  width: 450px;
  padding: 50px 45px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid #dce8f1;
  box-shadow: 0 22px 60px rgba(14, 36, 58, 0.22);
  animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 登录头部
.login-header {
  text-align: center;
  margin-bottom: 40px;

  .logo-wrapper {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;

    .logo-image {
      width: 180px;
      height: 180px;
      object-fit: contain;
      transition: all 0.3s ease;
      filter: drop-shadow(0 10px 26px rgba(15, 130, 197, 0.26));

      &:hover {
        transform: translateY(-5px) scale(1.05);
        filter: drop-shadow(0 15px 34px rgba(15, 130, 197, 0.34));
      }
    }
  }

  .system-title {
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 8px 0;
    line-height: 1.3;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    
    .company-name {
      font-size: 38px;
      font-weight: 800;
      background: linear-gradient(135deg, #0f82c5 0%, #17a890 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      letter-spacing: 4px;
      text-transform: uppercase;
    }
    
    .product-name {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      letter-spacing: 1px;
    }
  }

  .system-subtitle {
    font-size: 16px;
    color: #606266;
    margin: 0;
    font-weight: 500;
    line-height: 1.6;
    letter-spacing: 1px;
  }
}

// 登录表单
.login-form {
  margin-bottom: 20px;

  :deep(.el-input__wrapper) {
    width: 100%;
    border-radius: 12px;
    padding: 12px 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    &.is-focus {
      box-shadow: 0 4px 16px rgba(15, 130, 197, 0.26);
    }
  }

  .input-icon {
    color: #909399;
    font-size: 18px;
  }

  .el-form-item {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .login-button-item {
    margin-top: 32px;
    margin-bottom: 0;
  }

  .login-button {
    width: 100%;
    height: 48px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 500;
    letter-spacing: 2px;
    background: linear-gradient(135deg, #0f82c5 0%, #17a890 100%);
    border: none;
    box-shadow: 0 8px 22px rgba(15, 130, 197, 0.28);
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 30px rgba(15, 130, 197, 0.34);
    }

    &:active {
      transform: translateY(0);
    }
  }
}

// 登录底部
.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;

  .copyright {
    margin: 0;
    font-size: 12px;
    color: #909399;
    line-height: 1.5;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .login-card {
    width: 90%;
    padding: 40px 30px;
  }

  .login-header {
    .logo-wrapper .logo-icon {
      width: 70px;
      height: 70px;
    }

    .system-title {
      font-size: 24px;
    }
  }
}
</style>

