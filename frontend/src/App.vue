<template>
  <div id="app">
    <nav class="main-nav">
      <div class="project-title">书语相拥</div>
      <router-link to="/" class="nav-item">主页</router-link>
      <router-link to="/books" class="nav-item">书库</router-link>
      <template v-if="isLoggedIn">
        <router-link to="/userview" class="nav-item user-dashboard-button">个人中心</router-link>
        <a href="#" @click.prevent="logout" class="nav-item logout-button">退出登录</a>
      </template>
      <template v-else>
        <router-link to="/auth" class="nav-item login-button">登录</router-link>
      </template>
    </nav>

    <main class="app-content">
      <router-view />
    </main>

    <footer class="main-footer">
      <p>&copy; 2025 The Scriptorium. All rights reserved.</p>
      <router-link to="/about" class="footer-nav-item">关于我们</router-link>
    </footer>

    <div v-if="showGlobalPopup" class="global-popup-overlay">
      <div class="global-popup-content">
        <h3 class="popup-title">{{ popupTitle }}</h3>
        <p class="popup-message">{{ popupMessage }}</p>
        <button @click="closeGlobalPopup" class="popup-close-button">确认</button>
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
  color: #4a5043;
  /* 低饱和深绿灰，替代原深棕 */
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
  /* 极浅米白，更清爽 */
}

.main-nav {
  padding: 20px 30px;
  background-color: #7c9473;
  /* 莫兰迪蓝绿，替代原深棕 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  /* 阴影减淡，更柔和 */
  display: flex;
  justify-content: center;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

/* --- Project Title Styles --- */
.project-title {
  font-family: 'Playfair Display', serif;
  font-size: 2.2em;
  font-weight: bold;
  color: #f0e6d2;
  /* 米白色，替代原金色 */
  margin-right: auto;
  padding-right: 40px;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
  letter-spacing: 1.5px;

  /* Animation for BookHug */
  animation: pulseBeige 2s infinite alternate ease-in-out;
}

@keyframes pulseBeige {
  from {
    color: #f0e6d2;
    transform: scale(1);
    opacity: 1;
  }

  to {
    color: #fff8e7;
    /* 更浅的米白，替代原亮金 */
    transform: scale(1.02);
    opacity: 0.95;
  }
}

.nav-item {
  font-weight: bold;
  color: #faf6ed;
  /* 极浅米白，替代原浅棕 */
  text-decoration: none;
  margin: 0 25px;
  padding: 8px 0;
  transition: color 0.3s ease, transform 0.2s ease;
  letter-spacing: 0.5px;
}

.nav-item:hover {
  color: #d4c7b8;
  /* 暖灰棕，替代原灰棕 */
  transform: translateY(-2px);
}

.nav-item.router-link-exact-active {
  color: #d4c7b8;
  border-bottom: 2px solid #d4c7b8;
}

/* Login Button Styles */
.login-button {
  background-color: #9da8a3;
  /* 莫兰迪灰绿，替代原棕 */
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  margin-left: 40px;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
  letter-spacing: 0.5px;
}

.login-button:hover {
  background-color: #8a9690;
  /* 深一点的灰绿，替代原深棕 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.app-content {
  flex-grow: 1;
  padding: 40px;
  background-color: #faf6ed;
  /* 浅米白，比原背景更柔和 */
}

.main-footer {
  padding: 20px;
  background-color: #7c9473;
  /* 与导航一致的蓝绿 */
  color: #faf6ed;
  /* 极浅米白，替代原浅棕 */
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
  color: #faf6ed;
  text-decoration: none;
  margin-left: 20px;
  transition: color 0.3s ease;
}

.footer-nav-item:hover {
  color: #d4c7b8;
  /* 与导航hover一致 */
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
  background-color: rgba(0, 0, 0, 0.4);
  /* 稍浅的遮罩 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.global-popup-content {
  background-color: #faf6ed;
  /* 与内容区一致 */
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  text-align: center;
  max-width: 400px;
  width: 90%;
  position: relative;
  animation: slideIn 0.4s ease-out;
}

.popup-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.8em;
  color: #7c9473;
  /* 与导航一致的蓝绿，替代原深棕 */
  margin-bottom: 15px;
}

.popup-message {
  font-size: 1.1em;
  color: #4a5043;
  /* 与正文一致的深绿灰 */
  margin-bottom: 25px;
  line-height: 1.6;
}

.popup-close-button {
  background-color: #9da8a3;
  /* 与登录按钮一致的灰绿 */
  color: white;
  padding: 10px 25px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.popup-close-button:hover {
  background-color: #8a9690;
  /* 深一点的灰绿 */
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

/* --- 新增：书籍列表相关配色（保持风格统一）--- */
/* 筛选器样式（如果需要） */
.filter-container {
  background-color: #f5f1e9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-label {
  color: #4a5043;
  font-weight: bold;
  margin-right: 10px;
}

.genre-tag {
  background-color: #e8e3d7;
  color: #4a5043;
  padding: 5px 12px;
  border-radius: 20px;
  margin: 0 8px 8px 0;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.genre-tag:hover,
.genre-tag.active {
  background-color: #7c9473;
  color: white;
}

/* 书籍卡片样式（如果需要） */
.book-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.book-title {
  color: #7c9473;
  font-family: 'Playfair Display', serif;
  margin-bottom: 10px;
}

.book-author {
  color: #6b7268;
  font-style: italic;
  margin-bottom: 15px;
}
</style>