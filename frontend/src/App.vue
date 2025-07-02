<template>
  <div id="app">
    <nav class="main-nav">
      <router-link to="/" class="nav-item">The Grand Hall</router-link>
      <router-link to="/books" class="nav-item">The Catalogue</router-link>
      <router-link to="/about" class="nav-item">About Our Establishment</router-link>

      <template v-if="userStore.isLoggedIn">
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
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
// 1. 导入 useUserStore
import { useUserStore } from './stores/userStore';

// 2. 获取 store 和 router 实例
const userStore = useUserStore();
const router = useRouter();

// 3. (删除) 不再需要本地 isLoggedIn ref 和任何事件监听器 (onMounted, onUnmounted)。
//    Pinia 的 state 本身就是响应式的，store.isLoggedIn 会自动更新 UI。

// 4. 重构 logout 函数
const logout = () => {
  // 调用 store 中的 logout action，它会处理所有状态和 localStorage 的清理工作
  userStore.logout();

  // 登出后跳转到首页
  router.push('/');
  alert('您已成功登出。');
};
</script>

<style>
/* Global Styles for the Grand Scriptorium */
#app {
  /* Choosing a classic serif font for an authentic feel */
  font-family: 'Georgia', 'Times New Roman', Times, serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #3e2723;
  /* Deep, rich brown reminiscent of aged wood or leather */
  min-height: 100vh;
  /* Ensures content fills the viewport height */
  display: flex;
  flex-direction: column;
  /* Vertical layout to pin the footer to the bottom */
  background-color: #fcf8f0;
  /* Soft parchment white for the overall background */
}

.main-nav {
  padding: 20px 30px;
  /* More generous padding for a stately feel */
  background-color: #5d4037;
  /* A deep, warm brown for the navigation bar */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  /* A subtle, elegant shadow */
  display: flex;
  justify-content: center;
  /* Centering navigation items */
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  /* A delicate bottom border */
}

.nav-item {
  font-weight: bold;
  color: #ede0d4;
  /* A creamy, light beige for navigation text */
  text-decoration: none;
  margin: 0 25px;
  /* Increased spacing between navigation items */
  padding: 8px 0;
  /* Slightly more vertical padding */
  transition: color 0.3s ease, transform 0.2s ease;
  /* Smooth transitions */
  letter-spacing: 0.5px;
  /* Subtle letter spacing for readability */
}

.nav-item:hover {
  color: #bcaaa4;
  /* A muted, antique silver on hover */
  transform: translateY(-2px);
  /* A slight lift effect */
}

.nav-item.router-link-exact-active {
  color: #bcaaa4;
  /* Muted silver for the active link */
  border-bottom: 2px solid #bcaaa4;
  /* A distinguished underline for the active link */
}

/* Login Button Styles */
.login-button {
  background-color: #8d6e63;
  /* A refined medium brown for the button */
  color: white;
  padding: 10px 20px;
  /* Ample padding for the button */
  border-radius: 5px;
  /* Subtle rounded corners */
  margin-left: 40px;
  /* More distance from other navigation items */
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  /* Smooth transitions */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  /* A gentle shadow */
  letter-spacing: 0.5px;
}

.login-button:hover {
  background-color: #795548;
  /* Darker brown on hover */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
  /* Enhanced shadow on hover */
}

.app-content {
  flex-grow: 1;
  /* Ensures the main content area occupies all available space, pushing the footer to the bottom */
  padding: 40px;
  /* More generous padding for content areas */
  background-color: #fffaf0;
  /* A soft, warm off-white for the content background */
}

.main-footer {
  padding: 20px;
  background-color: #5d4037;
  /* Matching the navigation bar's deep brown */
  color: #ede0d4;
  /* Matching the navigation text color */
  font-size: 0.95em;
  /* Slightly larger font size for readability */
  margin-top: auto;
  /* Pushes the footer to the bottom */
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
  /* A subtle top shadow */
  letter-spacing: 0.5px;
}
</style>