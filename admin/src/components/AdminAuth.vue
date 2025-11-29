<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h2>📚 Book Admin Portal</h2>
        <p>{{ isLogin ? 'Sign in to your admin account' : 'Create a new admin account' }}</p>
      </div>

      <!-- Login Form -->
      <form v-if="isLogin" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="email">📧 Name</label>
          <input type="text" id="email" v-model="loginForm.email" required placeholder="Enter your name">
        </div>
        <div class="form-group">
          <label for="password">🔒 Password</label>
          <input type="password" id="password" v-model="loginForm.password" required placeholder="Enter your password">
        </div>
        <button type="submit" class="auth-button" :disabled="loading">
          {{ loading ? 'Signing in...' : '🚀 Sign In' }}
        </button>
      </form>

      <!-- Error message -->
      <div v-if="error" class="error-message">
        ⚠️ {{ error }}
      </div>

      <!-- Success message -->
      <div v-if="success" class="success-message">
        ✅ {{ success }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// Reactive data
const isLogin = ref(true)
const loading = ref(false)
const error = ref('')
const success = ref('')

const loginForm = ref({
  email: '',
  password: ''
})

// Handle login
const handleLogin = async () => {
  if (loading.value) return

  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const response = await axios.post('/api/admin/login', {
      email: loginForm.value.email,
      password: loginForm.value.password
    })

    // Store auth token
    localStorage.setItem('adminToken', response.data.token)
    localStorage.setItem('adminUser', JSON.stringify(response.data.user))

    success.value = 'Login successful! Redirecting...'

    // Redirect to dashboard
    setTimeout(() => {
      router.push('/dashboard');
      // 强制刷新页面
      window.location.reload();
    }, 1000);


  } catch (err) {
    console.error('Login error:', err)

    // For demo purposes, allow login with demo credentials
    if (loginForm.value.email === 'root' && loginForm.value.password === 'root123') {
      const mockUser = {
        id: 1,
        email: 'root',
        username: 'root',
        role: 'admin'
      }

      localStorage.setItem('adminToken', 'demo-token-123')
      localStorage.setItem('adminUser', JSON.stringify(mockUser))

      success.value = 'Login successful! Redirecting...'

      setTimeout(() => {
        router.push('/dashboard');
        // 强制刷新页面
        window.location.reload();
      }, 1000);

    } else {
      error.value = err.response?.data?.message || 'Login failed. Please check your credentials.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Reset and ensure full screen coverage */
* {
  box-sizing: border-box;
}

.auth-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  margin: 0;
  z-index: 1000;
  overflow: auto;
}

.auth-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 480px;
  animation: slideUp 0.5s ease-out;
  margin: auto;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1.8em;
  font-weight: 600;
}

.auth-header p {
  color: #7f8c8d;
  font-size: 1em;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #495057;
  font-size: 1em;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1em;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  width: 100%;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.help-text {
  margin-top: 4px;
  color: #6c757d;
  font-size: 0.85em;
}

.auth-button {
  padding: 14px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  margin-top: 10px;
  width: 100%;
}

.auth-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.auth-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.auth-toggle {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.auth-toggle p {
  color: #6c757d;
  margin: 0;
}

.toggle-button {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-weight: 500;
  text-decoration: underline;
}

.toggle-button:hover {
  color: #764ba2;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 16px;
  border: 1px solid #f5c6cb;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 16px;
  border: 1px solid #c3e6cb;
}

/* Responsive design */
@media (max-width: 768px) {
  .auth-container {
    padding: 16px;
  }

  .auth-card {
    padding: 30px 20px;
    max-width: 100%;
  }

  .auth-header h2 {
    font-size: 1.5em;
  }
}

@media (max-width: 480px) {
  .auth-container {
    padding: 12px;
  }

  .auth-card {
    padding: 24px 16px;
  }

  .form-group input {
    padding: 10px 12px;
  }

  .auth-button {
    padding: 12px 16px;
  }
}
</style>
