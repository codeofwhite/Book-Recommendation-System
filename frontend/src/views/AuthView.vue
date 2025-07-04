<template>
  <div class="container">
    <div class="left-panel">
      <div class="brand">
        <h1>BookHug</h1>
        <p>Discover your next literary adventure with personalized recommendations from classic to contemporary
          masterpieces.</p>
      </div>

      <div class="quote">
        <p>"A reader lives a thousand lives before he dies. The man who never reads lives only one."</p>
        <div class="author">- George R.R. Martin</div>
      </div>

      <div class="book-icons">
        <div class="book-icon"></div>
        <div class="book-icon"></div>
        <div class="book-icon"></div>
      </div>
    </div>

    <div class="right-panel">
      <div class="page-corner"></div>
      <div class="feather-pen">
        <i class="fas fa-feather-alt"></i>
      </div>

      <div class="ink-blot ink-blot-1"></div>
      <div class="ink-blot ink-blot-2"></div>

      <div class="form-container">
        <form @submit.prevent="handleSubmit">
          <div class="form-header">
            <h2>{{ isRegister ? '创建你的账号' : '欢迎回来' }}</h2>
            <p>{{ isRegister ? '加入我们，开始你的阅读之旅' : '登录以继续你的文学旅程' }}</p>
          </div>

          <div class="form-group">
            <i class="fas fa-user"></i>
            <input type="text" id="username" v-model="username" :placeholder="isRegister ? '用户名' : '用户名或邮箱'" required
              @focus="handleInputFocus" @blur="handleInputBlur">
          </div>

          <div class="form-group" v-if="isRegister">
            <i class="fas fa-envelope"></i>
            <input type="email" id="email" v-model="email" placeholder="邮箱" required @focus="handleInputFocus"
              @blur="handleInputBlur">
          </div>

          <div class="form-group">
            <i class="fas fa-lock"></i>
            <input type="password" id="password" v-model="password" placeholder="密码" required @focus="handleInputFocus"
              @blur="handleInputBlur">
          </div>

          <div class="options" v-if="!isRegister">
            <div class="remember">
              <input type="checkbox" id="remember">
              <label for="remember">记住我</label>
            </div>
          </div>

          <button type="submit" class="btn" :disabled="loading" @click="handleButtonClick">
            {{ isRegister ? '注册' : '登录' }}
          </button>

          <p v-if="message" :class="{ 'success-message': !isError, 'error-message': isError }" class="message-display">
            {{ message }}
          </p>

          <div class="auth-link">
            {{ isRegister ? '已有账号？' : '还没有账号？' }}
            <a href="#" @click.prevent="toggleMode">
              {{ isRegister ? '去登录' : '去注册' }}
            </a>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();

const username = ref('');
const email = ref('');
const password = ref('');
const isRegister = ref(false);
const message = ref('');
const isError = ref(false);
const loading = ref(false);

const toggleMode = () => {
  isRegister.value = !isRegister.value;
  message.value = '';
  isError.value = false;
  username.value = '';
  email.value = '';
  password.value = '';
};

const handleInputFocus = (event) => {
  event.target.parentElement.style.transform = 'translateX(5px)';
};

const handleInputBlur = (event) => {
  event.target.parentElement.style.transform = 'translateX(0)';
};

const handleButtonClick = (event) => {
  if (!loading.value) {
    const button = event.target;
    button.style.transform = 'translateY(1px)';
    button.style.boxShadow = '0 4px 12px rgba(60, 42, 33, 0.25), 0 2px 5px rgba(60, 42, 33, 0.2)';
    setTimeout(() => {
      button.style.transform = '';
      button.style.boxShadow = '';
    }, 200);
  }
};

const handleSubmit = async () => {
  message.value = '';
  isError.value = false;
  loading.value = true;

  const endpoint = isRegister.value ? '/service-a/api/auth/register' : '/service-a/api/auth/login';
  const payload = isRegister.value
    ? { username: username.value, email: email.value, password: password.value }
    : { username: username.value, password: password.value };

  try {
    const response = await axios.post(endpoint, payload);
    message.value = response.data.message;
    isError.value = false;

    if (!isRegister.value) { // 登录逻辑
      // **核心：从后端响应中解构出所有相关数据，包括 'token'**
      const {
        user_id, token, nickname, email, avatar_url, registration_date,
        is_profile_complete, age, gender, location, occupation,
        interest_tags, preferred_book_types, preferred_authors,
        preferred_genres, preferred_reading_duration, last_login_date
      } = response.data;

      // **重要检查：确保 user_id 和 token 都存在**
      if (user_id && token) {
        // **将所有用户数据（包括 auth_token）打包成一个对象**
        const userDataToStore = {
          user_id: user_id,
          auth_token: token, // <-- 确保这一行存在且 token 被正确赋值
          nickname: nickname || username.value,
          email: email || '',
          avatar_url: avatar_url || 'https://th.bing.com/th/id/OIP.cTPVthB0oT1RXrEcSHaaTwHaHa?w=191&h=191&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3',
          registration_date: registration_date || null,
          last_login_date: last_login_date || null,
          age: age || null,
          gender: gender || '',
          location: location || '',
          occupation: occupation || '',
          interest_tags: interest_tags || '',
          preferred_book_types: preferred_book_types || '',
          preferred_authors: preferred_authors || '',
          preferred_genres: preferred_genres || '',
          preferred_reading_duration: preferred_reading_duration || '',
          is_profile_complete: is_profile_complete === undefined ? false : is_profile_complete
        };

        // **只存储一个键 'user_data' 到 localStorage**
        localStorage.setItem('user_data', JSON.stringify(userDataToStore));

        // 记录最后登录时间（如果需要单独存储，也可以放在 userDataToStore 里）
        localStorage.setItem('user_last_login_time', new Date().toISOString());

        console.log('AuthView.vue: 登录成功！存储的用户数据:', userDataToStore);

        // 发送自定义事件，通知 App.vue 更新登录状态
        window.dispatchEvent(new Event('user-logged-in'));

        // 根据 is_profile_complete 状态进行路由跳转
        if (!userDataToStore.is_profile_complete) {
          console.log("AuthView.vue: 用户资料不完整，跳转到 /user-onboarding");
          router.push('/user-onboarding');
        } else {
          console.log("AuthView.vue: 用户资料完整，跳转到 /userview");
          router.push('/userview');
        }
        alert('登录成功！');

      } else {
        isError.value = true;
        message.value = '登录成功，但用户信息不完整（缺少用户ID或认证令牌），请联系管理员。';
        console.error('AuthView.vue: Login successful but missing user_id or token in response:', response.data);
      }
    } else { // 注册逻辑
      username.value = '';
      email.value = '';
      password.value = '';
      message.value = '注册成功！请登录。';
    }

  } catch (err) {
    isError.value = true;
    if (err.response && err.response.data && err.response.data.message) {
      message.value = err.response.data.message;
    } else {
      message.value = '请求失败，请稍后再试。';
      console.error('AuthView.vue: Auth request failed:', err);
    }
  } finally {
    loading.value = false;
  }
};
</script>


<style scoped>
/* Base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Body styles - these would typically be global in public/index.html or a global CSS file */
/* For a single component, we apply them to the top-level container for demonstration */
html,
body,
#app {
  height: 100%;
  margin: 0;
  overflow: hidden;
  /* Prevent body scroll if container is centered */
}

.container {
  font-family: 'Cormorant Garamond', serif;
  /* Using the new fonts */
  background: linear-gradient(135deg, #f9f5eb 0%, #f0e6d5 100%);
  color: #3c2a21;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background-image:
    radial-gradient(circle at 10% 20%, rgba(212, 163, 115, 0.05) 0%, transparent 20%),
    radial-gradient(circle at 90% 80%, rgba(212, 163, 115, 0.05) 0%, transparent 20%),
    url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100" height="100" fill="%23f9f5eb"/><path d="M0,0 L100,100 M100,0 L0,100" stroke="%23d4a373" stroke-width="0.5" opacity="0.1"/></svg>');
  position: relative;
  overflow: hidden;
  /* Changed from overflow-x: hidden to overflow: hidden for consistency */

  /* The .container is now the main wrapper for the two panels */
  width: 100%;
  background: white;
  border-radius: 16px;
  box-shadow:
    0 25px 60px rgba(60, 42, 33, 0.2),
    0 10px 20px rgba(60, 42, 33, 0.1),
    0 0 0 1px rgba(212, 163, 115, 0.1);
  transition: transform 0.4s ease, box-shadow 0.4s ease;
}

/* Add pseudo-element for background effect within .container */
.container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle, transparent 20%, rgba(249, 245, 235, 0.7) 70%),
    linear-gradient(to bottom, rgba(249, 245, 235, 0.85), rgba(249, 245, 235, 0.95));
  z-index: -1;
}


.container:hover {
  transform: translateY(-5px);
  box-shadow:
    0 30px 70px rgba(60, 42, 33, 0.25),
    0 15px 25px rgba(60, 42, 33, 0.15),
    0 0 0 1px rgba(212, 163, 115, 0.15);
}

.left-panel {
  flex: 1;
  background: linear-gradient(135deg, #3c2a21 0%, #2a1d16 100%);
  color: #f9f5eb;
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.left-panel::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><path d="M20,50 Q40,30 60,50 T100,50 T140,50 T180,50" stroke="%23d4a373" stroke-width="0.5" fill="none" opacity="0.1"/></svg>'),
    linear-gradient(135deg, transparent 60%, rgba(212, 163, 115, 0.05) 100%);
  opacity: 0.15;
}

.brand {
  margin-bottom: 50px;
  text-align: center;
  position: relative;
  z-index: 2;
}

.brand h1 {
  font-size: 3.4rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  margin-bottom: 10px;
  color: #d4a373;
  position: relative;
  display: inline-block;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.brand h1::after {
  content: "";
  position: absolute;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 90px;
  height: 4px;
  background: linear-gradient(90deg, transparent, #d4a373, transparent);
  border-radius: 2px;
}

.brand p {
  font-family: 'Montserrat', sans-serif;
  font-size: 1.15rem;
  margin-top: 30px;
  opacity: 0.9;
  line-height: 1.7;
  max-width: 90%;
  margin-left: auto;
  margin-right: auto;
  font-weight: 300;
}

.quote {
  position: relative;
  padding: 35px 30px 35px 40px;
  border-left: 4px solid #d4a373;
  margin-top: 35px;
  background: rgba(26, 18, 11, 0.4);
  border-radius: 0 8px 8px 0;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.15);
  transition: all 0.4s ease;
}

.quote:hover {
  background: rgba(26, 18, 11, 0.5);
  transform: translateX(5px);
}

.quote p {
  font-style: italic;
  font-size: 1.45rem;
  line-height: 1.7;
  margin-bottom: 15px;
  position: relative;
  padding-left: 25px;
}

.quote p::before {
  content: "“";
  /* Use actual quotation mark */
  position: absolute;
  left: 0px;
  /* Adjusted position to be inside padding */
  top: -10px;
  /* Adjusted position */
  font-family: Georgia, serif;
  font-size: 5rem;
  color: rgba(212, 163, 115, 0.2);
}

.quote .author {
  font-family: 'Montserrat', sans-serif;
  font-size: 1.1rem;
  text-align: right;
  opacity: 0.85;
  font-weight: 400;
  letter-spacing: 0.5px;
}

.book-icons {
  position: absolute;
  bottom: 40px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 30px;
  z-index: 2;
}

.book-icon {
  width: 45px;
  height: 55px;
  background: linear-gradient(135deg, #d4a373 0%, #b8855a 100%);
  border-radius: 4px;
  position: relative;
  transform: rotate(-5deg);
  box-shadow:
    0 8px 20px rgba(0, 0, 0, 0.25),
    inset 0 -3px 5px rgba(0, 0, 0, 0.1),
    inset 0 3px 5px rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
  transition: all 0.3s ease;
}

.book-icon:hover {
  transform: rotate(-5deg) scale(1.1);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.book-icon:nth-child(2) {
  background: linear-gradient(135deg, #a47148 0%, #8b5e3c 100%);
  transform: rotate(3deg);
  animation-delay: 1s;
}

.book-icon:nth-child(3) {
  background: linear-gradient(135deg, #7c5336 0%, #634025 100%);
  transform: rotate(-2deg);
  animation-delay: 2s;
}

.book-icon::before {
  content: "";
  position: absolute;
  top: 6px;
  left: 6px;
  right: 6px;
  bottom: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 3px;
}

.book-icon::after {
  content: "";
  position: absolute;
  top: 10px;
  left: 8px;
  width: 4px;
  height: 35px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.right-panel {
  flex: 1;
  padding: 80px 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  background:
    radial-gradient(circle at top right, rgba(249, 245, 235, 0.5) 0%, transparent 30%),
    radial-gradient(circle at bottom left, rgba(249, 245, 235, 0.5) 0%, transparent 30%),
    #ffffff;
}

.feather-pen {
  position: absolute;
  top: 45px;
  right: 45px;
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d4a373;
  font-size: 2.3rem;
  transform: rotate(25deg);
  opacity: 0.85;
  animation: featherFloat 4s ease-in-out infinite;
  filter: drop-shadow(0 5px 5px rgba(0, 0, 0, 0.1));
}

.form-container {
  max-width: 400px;
  width: 100%;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.form-header {
  text-align: center;
  margin-bottom: 45px;
}

.form-header h2 {
  font-size: 2.6rem;
  font-weight: 600;
  color: #3c2a21;
  margin-bottom: 10px;
  position: relative;
  letter-spacing: 0.5px;
}

.form-header h2::after {
  content: "";
  position: absolute;
  bottom: -18px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #d4a373, #b8855a);
  border-radius: 2px;
}

.form-header p {
  font-family: 'Montserrat', sans-serif;
  margin-top: 30px;
  color: #7c5336;
  font-size: 1.15rem;
  font-weight: 400;
}

.form-group {
  margin-bottom: 30px;
  position: relative;
  transition: transform 0.3s ease;
}

/* No direct hover transform on form-group as it's now handled by JS on input focus/blur */
/* .form-group:hover {
  transform: translateX(5px);
} */

.form-group i {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: #d4a373;
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

.form-group input {
  width: 100%;
  padding: 18px 18px 18px 50px;
  /* Increased left padding for icon */
  border: 1px solid #e8dccf;
  border-radius: 10px;
  font-family: 'Montserrat', sans-serif;
  font-size: 1.05rem;
  color: #3c2a21;
  background: #fdfaf5;
  transition: all 0.3s ease;
  box-shadow:
    0 4px 12px rgba(60, 42, 33, 0.06) inset,
    0 1px 2px rgba(0, 0, 0, 0.05);
  letter-spacing: 0.3px;
}

.form-group input:focus {
  outline: none;
  border-color: #d4a373;
  box-shadow:
    0 0 0 3px rgba(212, 163, 115, 0.2),
    0 4px 15px rgba(60, 42, 33, 0.08) inset;
}

.form-group input:focus+i {
  color: #b8855a;
  transform: translateY(-50%) scale(1.1);
}

.form-group input::placeholder {
  color: #a89b8c;
  letter-spacing: 0.3px;
}

.options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 35px;
  font-family: 'Montserrat', sans-serif;
}

.remember {
  display: flex;
  align-items: center;
}

.remember input {
  margin-right: 10px;
  accent-color: #d4a373;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.remember label {
  color: #7c5336;
  font-size: 0.95rem;
  cursor: pointer;
  transition: color 0.3s ease;
}

.remember label:hover {
  color: #3c2a21;
}

.btn {
  display: block;
  width: 100%;
  padding: 18px;
  background: linear-gradient(135deg, #3c2a21 0%, #2a1d16 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-family: 'Montserrat', sans-serif;
  font-size: 1.15rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  letter-spacing: 0.5px;
  box-shadow:
    0 8px 20px rgba(60, 42, 33, 0.25),
    0 4px 10px rgba(60, 42, 33, 0.15);
}

.btn:disabled {
  background: linear-gradient(135deg, #7c5336 0%, #634025 100%);
  /* Lighter disabled state */
  cursor: not-allowed;
  box-shadow: none;
}


/* Use btn directly for consistency */
/* .btn-secondary {
  background: linear-gradient(135deg, #d4a373 0%, #b8855a 100%);
  margin-top: 15px;
} */

.btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
  transition: all 0.8s ease;
}

.btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #2a1d16 0%, #1a120b 100%);
  transform: translateY(-3px);
  box-shadow:
    0 12px 25px rgba(60, 42, 33, 0.3),
    0 6px 15px rgba(60, 42, 33, 0.2);
}

/* For the secondary button (register/login toggle) if you want it to have its own hover */
/* .btn-secondary:hover {
  background: linear-gradient(135deg, #b8855a 0%, #a47148 100%);
} */

.btn:hover::before {
  left: 100%;
}

.btn:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow:
    0 4px 12px rgba(60, 42, 33, 0.25),
    0 2px 5px rgba(60, 42, 33, 0.2);
}

.message-display {
  margin-top: 15px;
  padding: 12px;
  border-radius: 8px;
  font-weight: 500;
  font-family: 'Montserrat', sans-serif;
  font-size: 0.95rem;
  text-align: center;
  animation: fadeIn 0.5s ease-out;
}

.success-message {
  background-color: #e6ffe6;
  color: #28a745;
  border: 1px solid #28a745;
}

.error-message {
  background-color: #ffe6e6;
  color: #dc3545;
  border: 1px solid #dc3545;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}


.auth-link {
  text-align: center;
  margin-top: 35px;
  font-family: 'Montserrat', sans-serif;
  color: #7c5336;
  font-size: 1.05rem;
}

.auth-link a {
  color: #d4a373;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  letter-spacing: 0.3px;
}

.auth-link a::after {
  content: "";
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: #d4a373;
  transition: width 0.3s ease;
}

.auth-link a:hover {
  color: #b8855a;
}

.auth-link a:hover::after {
  width: 100%;
}

.ink-blot {
  position: absolute;
  width: 140px;
  height: 140px;
  background: radial-gradient(circle, #3c2a21 0%, transparent 70%);
  opacity: 0.04;
  border-radius: 50%;
  z-index: 1;
  filter: blur(2px);
}

.ink-blot-1 {
  top: -60px;
  left: -60px;
}

.ink-blot-2 {
  bottom: -70px;
  right: -50px;
}

.page-corner {
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 60px 60px 0;
  border-color: transparent #f9f5eb transparent transparent;
  box-shadow: -2px 2px 5px rgba(0, 0, 0, 0.1);
  z-index: 2;
}

.page-corner::after {
  content: "";
  position: absolute;
  top: 6px;
  right: -58px;
  width: 15px;
  height: 15px;
  background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23d4a373" opacity="0.7"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>') no-repeat center;
  background-size: contain;
}

@keyframes float {
  0% {
    transform: translateY(0) rotate(-5deg);
  }

  50% {
    transform: translateY(-15px) rotate(-5deg);
  }

  100% {
    transform: translateY(0) rotate(-5deg);
  }
}

@keyframes featherFloat {
  0% {
    transform: rotate(25deg) translateY(0);
  }

  50% {
    transform: rotate(25deg) translateY(-8px);
  }

  100% {
    transform: rotate(25deg) translateY(0);
  }
}

/* Media Queries */
@media (max-width: 900px) {
  .container {
    flex-direction: column;
    min-height: auto;
  }

  .left-panel,
  .right-panel {
    padding: 45px 35px;
  }

  .book-icons {
    position: relative;
    margin-top: 45px;
    bottom: auto;
  }

  .feather-pen {
    top: 25px;
    right: 25px;
  }
}

@media (max-width: 480px) {
  .container {
    border-radius: 12px;
    min-height: auto;
  }

  .left-panel,
  .right-panel {
    padding: 35px 25px;
  }

  .brand h1 {
    font-size: 2.7rem;
  }

  .form-header h2 {
    font-size: 2.2rem;
  }

  .quote p {
    font-size: 1.3rem;
  }
}
</style>