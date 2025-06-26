<!-- 登录页面 -->
<template>
  <div class="auth-container">
    <h1>{{ isRegister ? '注册新用户' : '用户登录' }}</h1>

    <form @submit.prevent="handleSubmit" class="auth-form">
      <div class="form-group">
        <label for="username">用户名:</label>
        <input type="text" id="username" v-model="username" required>
      </div>

      <div class="form-group" v-if="isRegister">
        <label for="email">邮箱:</label>
        <input type="email" id="email" v-model="email" required>
      </div>

      <div class="form-group">
        <label for="password">密码:</label>
        <input type="password" id="password" v-model="password" required>
      </div>

      <button type="submit" :disabled="loading">{{ isRegister ? '注册' : '登录' }}</button>

      <p v-if="message" :class="{'success': !isError, 'error': isError}">{{ message }}</p>
    </form>

    <p class="toggle-mode">
      {{ isRegister ? '已有账号？' : '还没有账号？' }}
      <span @click="toggleMode">{{ isRegister ? '去登录' : '去注册' }}</span>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; // For redirection after login

const router = useRouter();

const username = ref('');
const email = ref('');
const password = ref('');
const isRegister = ref(true); // true for register, false for login
const message = ref('');
const isError = ref(false);
const loading = ref(false);

const toggleMode = () => {
  isRegister.value = !isRegister.value;
  message.value = ''; // Clear message when toggling mode
  isError.value = false;
};

const handleSubmit = async () => {
  message.value = '';
  isError.value = false;
  loading.value = true;

  const endpoint = isRegister.value ? '/api/auth/register' : '/api/auth/login';
  const payload = isRegister.value
    ? { username: username.value, email: email.value, password: password.value }
    : { username: username.value, password: password.value };

  try {
    const response = await axios.post(endpoint, payload);
    message.value = response.data.message;
    isError.value = false;

    // If login successful, store token (e.g., in localStorage) and redirect
    if (!isRegister.value && response.data.token) {
      localStorage.setItem('auth_token', response.data.token);
      // console.log('Login successful, token stored:', response.data.token);
      router.push('/'); // Redirect to home page
    }

    // After successful registration, you might want to switch to login mode
    if (isRegister.value) {
        username.value = '';
        email.value = '';
        password.value = '';
        // Optionally, uncomment to auto-switch to login after successful registration
        // toggleMode();
    }

  } catch (err) {
    isError.value = true;
    if (err.response && err.response.data && err.response.data.message) {
      message.value = err.response.data.message;
    } else {
      message.value = 'An unexpected error occurred.';
      console.error('Auth request failed:', err);
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h1 {
  color: #34495e;
  margin-bottom: 25px;
  font-size: 2em;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  text-align: left;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

input[type="text"],
input[type="email"],
input[type="password"] {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1em;
  transition: border-color 0.3s ease;
}

input[type="text"]:focus,
input[type="email"]:focus,
input[type="password"]:focus {
  border-color: #42b983;
  outline: none;
}

button {
  background-color: #42b983;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 5px;
  font-size: 1.1em;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 10px;
}

button:hover:not(:disabled) {
  background-color: #369c73;
}

button:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 5px;
  font-weight: bold;
}

.success {
  background-color: #e6ffe6;
  color: #28a745;
  border: 1px solid #28a745;
}

.error {
  background-color: #ffe6e6;
  color: #dc3545;
  border: 1px solid #dc3545;
}

.toggle-mode {
  margin-top: 20px;
  color: #666;
}

.toggle-mode span {
  color: #42b983;
  cursor: pointer;
  font-weight: bold;
  text-decoration: underline;
}

.toggle-mode span:hover {
  color: #369c73;
}
</style>