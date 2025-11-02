<template>
  <div id="app">
    <nav class="main-nav">
      <div class="project-title">BookHug</div>
      <router-link to="/" class="nav-item">The Grand Hall</router-link>
      <router-link to="/books" class="nav-item">The Catalogue</router-link>
      <template v-if="isLoggedIn">
        <router-link to="/userview" class="nav-item user-dashboard-button">My Scriptorium</router-link>
        <a href="#" @click.prevent="logout" class="nav-item logout-button">Depart the Archives</a>
      </template>
      <template v-else>
        <router-link to="/auth" class="nav-item login-button">Enter the Archives</router-link>
      </template>
    </nav>

    <main class="app-content">
      <router-view />
    </main>

    <footer class="main-footer">
      <p>&copy; 2025 The Scriptorium. All rights reserved.</p>
      <router-link to="/about" class="footer-nav-item">关于我们的机构</router-link>
    </footer>

    <div v-if="showGlobalPopup" class="global-popup-overlay">
      <div class="global-popup-content">
        <h3 class="popup-title">{{ popupTitle }}</h3>
        <p class="popup-message">{{ popupMessage }}</p>
        <button @click="closeGlobalPopup" class="popup-close-button">了解</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoggedIn = ref(false);

// --- 全局弹窗相关状态 ---
const showGlobalPopup = ref(false);
const popupTitle = ref('');
const popupMessage = ref('');
let popupTimeout = null; // 用于自动关闭弹窗的计时器

/**
 * 显示全局弹窗
 * @param {string} title 弹窗标题
 * @param {string} message 弹窗内容
 * @param {number} [duration=3000] 弹窗自动关闭的持续时间 (毫秒)，0 表示手动关闭
 */
const showPopup = (title, message, duration = 3000) => {
  popupTitle.value = title;
  popupMessage.value = message;
  showGlobalPopup.value = true;

  // 清除之前的计时器，防止冲突
  if (popupTimeout) {
    clearTimeout(popupTimeout);
  }

  // 设置自动关闭弹窗
  if (duration > 0) {
    popupTimeout = setTimeout(() => {
      closeGlobalPopup();
    }, duration);
  }
};

const closeGlobalPopup = () => {
  showGlobalPopup.value = false;
  if (popupTimeout) {
    clearTimeout(popupTimeout);
    popupTimeout = null;
  }
};
// --- 全局弹窗相关状态结束 ---


// Function to check login status
const checkLoginStatus = () => {
  console.log("App.vue: checkLoginStatus called.");
  const storedUserData = localStorage.getItem('user_data');
  console.log("App.vue: Raw storedUserData from localStorage:", storedUserData);

  // 记录上次登录状态
  const wasLoggedIn = isLoggedIn.value;

  if (storedUserData) {
    try {
      const userData = JSON.parse(storedUserData);
      isLoggedIn.value = !!userData.auth_token; // 检查 auth_token 是否存在
      console.log("App.vue: Parsed userData.auth_token:", userData.auth_token ? 'Exists' : 'Does NOT exist');
      console.log("App.vue: isLoggedIn.value set to:", isLoggedIn.value);

      // 如果之前未登录，现在登录了，则显示欢迎弹窗
      if (!wasLoggedIn && isLoggedIn.value) {
        showPopup('欢迎回来！', `欢迎您，${userData.user_nickname || '读者'}，回到BookHug！探索更多精彩书籍吧。`);
      }

    } catch (e) {
      console.error("App.vue: Error parsing user_data from localStorage:", e);
      isLoggedIn.value = false;
      localStorage.removeItem('user_data'); // 清除可能损坏的数据
      console.log("App.vue: Cleared corrupted user_data from localStorage.");
    }
  } else {
    isLoggedIn.value = false;
    console.log("App.vue: No user_data found in localStorage. isLoggedIn.value set to false.");
  }
};

// Function to handle logout
const logout = () => {
  console.log("App.vue: logout called.");
  // 清除 'user_data' 和 'user_last_login_time'
  localStorage.removeItem('user_data');
  localStorage.removeItem('user_last_login_time');

  // 确保清除所有旧的单独存储的键，以防万一（只在过渡期需要）
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('user_nickname');
  localStorage.removeItem('user_email');
  localStorage.removeItem('user_avatar_url');
  localStorage.removeItem('user_registration_date');


  isLoggedIn.value = false;
  console.log("App.vue: All user data removed from localStorage. isLoggedIn.value set to false.");

  router.push('/');
  // 使用我们自己的弹窗来替代原生的 alert
  showPopup('已登出', '您已成功登出。期待您的再次光临！', 3000);
};

// Listen for custom events to update login status
const handleLoginEvent = () => {
  console.log("App.vue: 'user-logged-in' event received. Calling checkLoginStatus().");
  checkLoginStatus();
};

onMounted(() => {
  console.log("App.vue: Component mounted. Performing initial login status check.");
  checkLoginStatus();
  window.addEventListener('user-logged-in', handleLoginEvent);
  // storage 事件在不同标签页/窗口之间共享存储时触发
  window.addEventListener('storage', checkLoginStatus);
});

onUnmounted(() => {
  console.log("App.vue: Component unmounted. Removing event listeners.");
  window.removeEventListener('user-logged-in', handleLoginEvent);
  window.removeEventListener('storage', checkLoginStatus);
  // 清除可能存在的弹窗计时器
  if (popupTimeout) {
    clearTimeout(popupTimeout);
  }
});
</script>

<style>
#app {
  font-family: 'Georgia', 'Times New Roman', Times, serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #3e2723;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fcf8f0;
}

.main-nav {
  padding: 20px 30px;
  background-color: #5d4037;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  justify-content: center;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* --- Project Title Styles --- */
.project-title {
  font-family: 'Playfair Display', serif;
  font-size: 2.2em;
  font-weight: bold;
  color: #ffcc80;
  margin-right: auto;
  padding-right: 40px;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
  letter-spacing: 1.5px;

  /* Animation for BookHug */
  animation: pulseGold 2s infinite alternate ease-in-out;
}

@keyframes pulseGold {
  from {
    color: #ffcc80;
    transform: scale(1);
    opacity: 1;
  }

  to {
    color: #ffd54f;
    transform: scale(1.02);
    opacity: 0.95;
  }
}

.nav-item {
  font-weight: bold;
  color: #ede0d4;
  text-decoration: none;
  margin: 0 25px;
  padding: 8px 0;
  transition: color 0.3s ease, transform 0.2s ease;
  letter-spacing: 0.5px;
}

.nav-item:hover {
  color: #bcaaa4;
  transform: translateY(-2px);
}

.nav-item.router-link-exact-active {
  color: #bcaaa4;
  border-bottom: 2px solid #bcaaa4;
}

/* Login Button Styles */
.login-button {
  background-color: #8d6e63;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  margin-left: 40px;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.5px;
}

.login-button:hover {
  background-color: #795548;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
}

.app-content {
  flex-grow: 1;
  padding: 40px;
  background-color: #fffaf0;
}

.main-footer {
  padding: 20px;
  background-color: #5d4037;
  color: #ede0d4;
  font-size: 0.95em;
  margin-top: auto;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
  letter-spacing: 0.5px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

.footer-nav-item {
  color: #ede0d4;
  /* 链接颜色与页脚文本一致 */
  text-decoration: none;
  margin-left: 20px;
  /* 与版权信息或其他页脚项的间距 */
  transition: color 0.3s ease;
}

.footer-nav-item:hover {
  color: #bcaaa4;
  /* 悬停效果与主导航链接一致 */
}

body {
  margin: 0;
}

/* --- 全局弹窗样式 --- */
.global-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  /* 半透明背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  /* 确保弹窗在最上层 */
  animation: fadeIn 0.3s ease-out;
  /* 弹窗出现动画 */
}

.global-popup-content {
  background-color: #fffaf0;
  /* 与内容区背景色一致 */
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  text-align: center;
  max-width: 400px;
  width: 90%;
  position: relative;
  animation: slideIn 0.4s ease-out;
  /* 弹窗内容滑入动画 */
}

.popup-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.8em;
  color: #5d4037;
  /* 深棕色标题 */
  margin-bottom: 15px;
}

.popup-message {
  font-size: 1.1em;
  color: #3e2723;
  /* 深棕色文字 */
  margin-bottom: 25px;
  line-height: 1.6;
}

.popup-close-button {
  background-color: #8d6e63;
  /* 与登录按钮颜色相似 */
  color: white;
  padding: 10px 25px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.popup-close-button:hover {
  background-color: #795548;
  transform: translateY(-2px);
}

/* 弹窗动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>