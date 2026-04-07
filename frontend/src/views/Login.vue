<template>
  <div class="login-page">
    <div class="login-background">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>

    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <el-icon class="logo-icon"><Platform /></el-icon>
          <h1 class="login-title">K8s 集群监控管理平台</h1>
          <p class="login-subtitle">欢迎登录</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名/邮箱"
              size="large"
              clearable
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-link type="primary" :underline="false" @click="showForgotPassword">
              忘记密码？
            </el-link>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </el-form-item>

          <div class="login-footer">
            <span>还没有账号？</span>
            <el-link type="primary" :underline="false" @click="showRegister">
              立即注册
            </el-link>
          </div>
        </el-form>
      </div>

      <!-- 第三方登录 -->
      <div class="third-party-login">
        <span>其他登录方式</span>
        <div class="third-party-icons">
          <el-button class="icon-btn" circle>
            <el-icon><Cherry /></el-icon>
          </el-button>
          <el-button class="icon-btn" circle>
            <el-icon><ChatDotRound /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 注册对话框 -->
    <el-dialog v-model="registerVisible" title="用户注册" width="400px" :close-on-click-modal="false">
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRegister">注册</el-button>
      </template>
    </el-dialog>

    <!-- 忘记密码对话框 -->
    <el-dialog v-model="forgotVisible" title="找回密码" width="400px" :close-on-click-modal="false">
      <el-form ref="forgotFormRef" :model="forgotForm" :rules="forgotRules" label-width="80px">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="forgotForm.email" placeholder="请输入注册邮箱" />
        </el-form-item>
        <el-form-item label="验证码" prop="code">
          <el-input v-model="forgotForm.code" placeholder="请输入验证码">
            <template #append>
              <el-button :disabled="countdown > 0" @click="sendCode">
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="forgotForm.newPassword" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="forgotVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResetPassword">重置密码</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import {
  Platform,
  User,
  Lock,
  Cherry,
  ChatDotRound,
} from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)

// 登录表单
const loginFormRef = ref()
const loginForm = reactive({
  username: '',
  password: '',
  remember: false,
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

// 注册表单
const registerFormRef = ref()
const registerVisible = ref(false)
const registerForm = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validatePassword = (_rule: any, value: string, callback: any) => {
  if (value.length < 8) {
    callback(new Error('密码长度不能少于 8 位'))
    return
  }
  if (!/[A-Z]/.test(value)) {
    callback(new Error('密码必须包含至少一个大写字母'))
    return
  }
  if (!/[a-z]/.test(value)) {
    callback(new Error('密码必须包含至少一个小写字母'))
    return
  }
  if (!/\d/.test(value)) {
    callback(new Error('密码必须包含至少一个数字'))
    return
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(value)) {
    callback(new Error('密码必须包含至少一个特殊字符'))
    return
  }
  callback()
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { validator: validatePassword, trigger: 'blur' },
  ],
  confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }],
}

// 忘记密码表单
const forgotFormRef = ref()
const forgotVisible = ref(false)
const forgotForm = reactive({
  email: '',
  code: '',
  newPassword: '',
})
const countdown = ref(0)

const forgotRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  code: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' },
  ],
}

// 处理方法
async function handleLogin() {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    loading.value = true
    try {
      const response = await authApi.login({
        username: loginForm.username,
        password: loginForm.password,
      })

      localStorage.setItem('token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))

      ElMessage.success('登录成功')
      router.push('/')
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '登录失败')
    } finally {
      loading.value = false
    }
  })
}

function handleRegister() {
  if (!registerFormRef.value) return

  registerFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        await authApi.register({
          username: registerForm.username,
          email: registerForm.email,
          phone: registerForm.phone,
          password: registerForm.password,
          role: 'viewer',
        })
        ElMessage.success('注册成功，请登录')
        registerVisible.value = false
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '注册失败')
      }
    }
  })
}

function sendCode() {
  if (!forgotForm.email) {
    ElMessage.warning('请先输入邮箱')
    return
  }

  // TODO: 调用发送验证码 API
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

function handleResetPassword() {
  if (!forgotFormRef.value) return

  forgotFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      // TODO: 调用重置密码 API
      ElMessage.success('密码重置成功')
      forgotVisible.value = false
    }
  })
}

function showRegister() {
  registerVisible.value = true
}

function showForgotPassword() {
  forgotVisible.value = true
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1f3a 0%, #0d1121 100%);
  position: relative;
  overflow: hidden;
}

// 背景动画
.login-background {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;

  .bg-shape {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
    animation: float 20s infinite ease-in-out;
  }

  .shape-1 {
    width: 400px;
    height: 400px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    top: -100px;
    left: -100px;
  }

  .shape-2 {
    width: 300px;
    height: 300px;
    background: linear-gradient(135deg, #f093fb, #f5576c);
    bottom: -50px;
    right: -50px;
    animation-delay: -5s;
  }

  .shape-3 {
    width: 200px;
    height: 200px;
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    top: 50%;
    left: 50%;
    animation-delay: -10s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(50px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-50px, 50px) scale(0.9);
  }
}

.login-container {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 420px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;

  .logo-icon {
    font-size: 48px;
    color: #409EFF;
    margin-bottom: 16px;
  }

  .login-title {
    font-size: 24px;
    font-weight: 600;
    color: #1a1f3a;
    margin-bottom: 8px;
  }

  .login-subtitle {
    font-size: 14px;
    color: #888;
  }
}

.login-form {
  .form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .login-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;

    &:hover {
      opacity: 0.9;
    }
  }
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  color: #666;

  .el-link {
    margin-left: 4px;
    font-weight: 600;
  }
}

// 第三方登录
.third-party-login {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px 40px;
  display: flex;
  align-items: center;
  gap: 16px;

  span {
    color: #666;
    font-size: 14px;
  }

  .icon-btn {
    width: 40px;
    height: 40px;
    border: 1px solid #e0e0e0;
    background: #fff;

    &:hover {
      background: #f5f5f5;
    }
  }
}
</style>
