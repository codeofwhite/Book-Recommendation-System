<template>
  <div id="app">
    <nav class="main-nav">
      <router-link to="/" class="nav-item">The Grand Hall</router-link>
      <router-link to="/books" class="nav-item">The Catalogue</router-link>
      <router-link to="/about" class="nav-item">About Our Establishment</router-link>

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
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoggedIn = ref(false);

// Function to check login status
const checkLoginStatus = () => {
  console.log("App.vue: checkLoginStatus called.");
  const storedUserData = localStorage.getItem('user_data');
  console.log("App.vue: Raw storedUserData from localStorage:", storedUserData);

  if (storedUserData) {
    try {
      const userData = JSON.parse(storedUserData);
      isLoggedIn.value = !!userData.auth_token; // 检查 auth_token 是否存在
      console.log("App.vue: Parsed userData.auth_token:", userData.auth_token ? 'Exists' : 'Does NOT exist');
      console.log("App.vue: isLoggedIn.value set to:", isLoggedIn.value);
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
  alert('您已成功登出。');
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
});
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