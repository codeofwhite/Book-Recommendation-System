<template>
  <div class="auth-container">
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
    </div>

    <div class="auth-card">
      <div class="auth-header">
        <div class="admin-logo">
          <span class="logo-icon">🔒</span>
        </div>
        <h2>图书后台管理系统</h2>
        <p>Book Administration Portal</p>
      </div>

      <div class="auth-body">
        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label for="username">管理员账号</label>
            <div class="input-wrapper">
              <span class="input-icon">👤</span>
              <input type="text" id="username" v-model="loginForm.email" required placeholder="请输入管理员用户名"
                :disabled="loading">
            </div>
          </div>

          <div class="form-group">
            <label for="password">安全密码</label>
            <div class="input-wrapper">
              <span class="input-icon">🔑</span>
              <input type="password" id="password" v-model="loginForm.password" required placeholder="请输入登录密码"
                :disabled="loading">
            </div>
          </div>

          <div class="form-options">
            <label class="remember-me">
              <input type="checkbox"> 记住登录状态
            </label>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>

          <button type="submit" class="auth-button" :disabled="loading">
            <span v-if="loading" class="loader"></span>
            <span>{{ loading ? '正在验证身份...' : '立即登录' }}</span>
          </button>
        </form>

        <transition name="fade">
          <div v-if="error" class="message-banner error">
            <span class="msg-icon">⚠️</span> {{ error }}
          </div>
        </transition>
        <transition name="fade">
          <div v-if="success" class="message-banner success">
            <span class="msg-icon">✅</span> {{ success }}
          </div>
        </transition>
      </div>

      <div class="auth-footer">
        <p>&copy; 2026 图书管理系统 - 安全加固环境</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')

const loginForm = ref({
  email: '',
  password: ''
})

const handleLogin = async () => {
  if (loading.value) return
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    // 模拟或真实请求
    const response = await axios.post('/api/admin/login', loginForm.value)

    localStorage.setItem('adminToken', response.data.token)
    localStorage.setItem('adminUser', JSON.stringify(response.data.user))
    success.value = '身份验证成功，正在进入系统...'

    setTimeout(() => {
      router.push('/dashboard').then(() => {
        window.location.reload()
      })
    }, 1200)

  } catch (err) {
    // 演示账号 root/root123 的逻辑处理保持一致
    if (loginForm.value.email === 'root' && loginForm.value.password === 'root123') {
      const mockUser = { id: 1, username: '超级管理员', role: 'admin' }
      localStorage.setItem('adminToken', 'demo-token-123')
      localStorage.setItem('adminUser', JSON.stringify(mockUser))
      success.value = '演示账号登录成功...'
      setTimeout(() => {
        router.push('/dashboard').then(() => window.location.reload())
      }, 1000)
    } else {
      error.value = '登录失败：账号或密码校验未通过'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 容器设计：深色专业背景 */
.auth-container {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0f172a;
  /* 深色科技蓝 */
  background-image:
    radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.5) 0, transparent 50%),
    radial-gradient(at 100% 100%, rgba(126, 34, 206, 0.3) 0, transparent 50%);
  overflow: hidden;
  font-family: 'Inter', -apple-system, sans-serif;
}

/* 背景装饰 */
.bg-decoration .circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
}

.circle-1 {
  width: 400px;
  height: 400px;
  background: rgba(59, 130, 246, 0.15);
  top: -100px;
  left: -100px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  background: rgba(147, 51, 234, 0.1);
  bottom: -50px;
  right: -50px;
}

/* 登录卡片 */
.auth-card {
  position: relative;
  z-index: 10;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 50px 40px;
  width: 100%;
  max-width: 440px;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.auth-header {
  text-align: center;
  margin-bottom: 35px;
}

.admin-logo {
  width: 64px;
  height: 64px;
  background: #3b82f6;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  font-size: 32px;
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
}

.auth-header h2 {
  color: #1e293b;
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0;
}

.auth-header p {
  color: #64748b;
  font-size: 0.9rem;
  margin-top: 5px;
  letter-spacing: 1px;
}

/* 表单设计 */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  font-size: 18px;
  color: #94a3b8;
}

.form-group input {
  width: 100%;
  padding: 14px 14px 14px 44px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.95rem;
  transition: all 0.2s;
  background: #f8fafc;
}

.form-group input:focus {
  outline: none;
  background: #fff;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.remember-me {
  color: #64748b;
  cursor: pointer;
}

.forgot-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

/* 按钮设计 */
.auth-button {
  position: relative;
  width: 100%;
  padding: 14px;
  background: #1e293b;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.auth-button:hover:not(:disabled) {
  background: #0f172a;
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
}

.auth-button:disabled {
  opacity: 0.8;
  cursor: not-allowed;
}

/* 消息横幅 */
.message-banner {
  margin-top: 20px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.message-banner.error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fee2e2;
}

.message-banner.success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #dcfce7;
}

.auth-footer {
  margin-top: 30px;
  text-align: center;
  font-size: 0.75rem;
  color: #94a3b8;
}

/* 加载动画 */
.loader {
  width: 18px;
  height: 18px;
  border: 2px solid #ffffff;
  border-bottom-color: transparent;
  border-radius: 50%;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 渐变过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>