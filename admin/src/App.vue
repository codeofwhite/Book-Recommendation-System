<template>
  <div id="admin-dashboard" :class="{ 'auth-mode': !isAuthenticated }">
    <template v-if="isAuthenticated">
      <aside class="sidebar">
        <div class="sidebar-brand">
          <span class="brand-icon">📚</span>
          <span class="brand-text">图书管理系统</span>
        </div>

        <div class="user-profile" v-if="currentUser">
          <div class="avatar">{{ currentUser.username.charAt(0).toUpperCase() }}</div>
          <div class="user-details">
            <p class="role">超级管理员</p>
            <p class="username">{{ currentUser.username }}</p>
          </div>
        </div>

        <nav class="sidebar-nav">
          <div class="nav-group-title">核心管理</div>
          <ul>
            <li>
              <router-link to="/dashboard" active-class="active">
                <i class="icon">📊</i> 控制面板总览
              </router-link>
            </li>
            <li>
              <router-link to="/books" active-class="active">
                <i class="icon">📖</i> 图书资源管理
              </router-link>
            </li>
            <li>
              <router-link to="/add-book" active-class="active">
                <i class="icon">✨</i> 上架新图书
              </router-link>
            </li>
          </ul>

          <div class="nav-group-title">系统维护</div>
          <ul>
            <li>
              <router-link to="/reviews" active-class="active">
                <i class="icon">💬</i> 评论审核中心
              </router-link>
            </li>
            <li>
              <router-link to="/users" active-class="active">
                <i class="icon">👤</i> 用户账号管理
              </router-link>
            </li>
          </ul>
        </nav>

        <div class="sidebar-footer">
          <button @click="handleLogout" class="logout-btn">
            <span>退出登录</span>
            <i class="icon-exit">➔</i>
          </button>
        </div>
      </aside>

      <main class="main-content">
        <header class="main-header">
          <div class="header-left">
            <span class="breadcrumb">后台首页 / {{ currentRouteName }}</span>
          </div>
          <div class="header-right">
            <span class="current-time">{{ currentTime }}</span>
          </div>
        </header>

        <div class="content-area">
          <div class="page-container">
            <router-view v-slot="{ Component }">
              <transition name="fade-transform" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </div>
        </div>
      </main>
    </template>

    <template v-else>
      <div class="auth-wrapper">
        <router-view />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const currentUser = ref(null)
const currentTime = ref('')

const isAuthenticated = computed(() => {
  const token = localStorage.getItem('adminToken')
  const user = localStorage.getItem('adminUser')
  return !!(token && user)
})

// 根据路由路径映射中文名称
const currentRouteName = computed(() => {
  const map = {
    '/dashboard': '控制面板',
    '/books': '图书管理',
    '/add-book': '新增图书',
    '/reviews': '评论审核',
    '/users': '用户列表'
  }
  return map[route.path] || '系统操作'
})

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

const handleLogout = () => {
  if (confirm('确认要退出管理系统吗？')) {
    localStorage.removeItem('adminToken')
    localStorage.removeItem('adminUser')
    currentUser.value = null
    router.push('/login')
  }
}

let timeInterval = null
onMounted(() => {
  const userData = localStorage.getItem('adminUser')
  if (userData) currentUser.value = JSON.parse(userData)

  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})
</script>

<style scoped>
/* 变量定义 */
:root {
  --sidebar-width: 260px;
  --primary-color: #4361ee;
  --bg-color: #f8f9fa;
  --sidebar-bg: #1e1e2d;
}

#admin-dashboard {
  display: flex;
  min-height: 100vh;
  background-color: #f0f2f5;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 侧边栏设计 */
.sidebar {
  width: 260px;
  background-color: #1e1e2d;
  color: #a2a3b7;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
  box-shadow: 4px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar-brand {
  height: 70px;
  display: flex;
  align-items: center;
  padding: 0 25px;
  background-color: #1b1b28;
}

.brand-icon {
  font-size: 24px;
  margin-right: 12px;
}

.brand-text {
  color: #fff;
  font-size: 1.2rem;
  font-weight: 600;
  letter-spacing: 1px;
}

.user-profile {
  padding: 25px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #2d2d3f;
  margin-bottom: 10px;
}

.avatar {
  width: 45px;
  height: 45px;
  background: linear-gradient(135deg, #4361ee, #4cc9f0);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
  margin-right: 15px;
}

.role {
  font-size: 0.75rem;
  color: #565674;
  margin: 0;
}

.username {
  color: #fff;
  font-size: 0.95rem;
  font-weight: 500;
  margin: 2px 0 0 0;
}

.nav-group-title {
  padding: 15px 25px 10px;
  font-size: 0.7rem;
  text-transform: uppercase;
  color: #49495e;
  letter-spacing: 1px;
  font-weight: bold;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav a {
  display: flex;
  align-items: center;
  padding: 12px 25px;
  color: #a2a3b7;
  text-decoration: none;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.sidebar-nav a .icon {
  margin-right: 12px;
  font-size: 1.1rem;
}

.sidebar-nav a:hover {
  background-color: #242436;
  color: #fff;
}

.sidebar-nav a.active {
  background-color: #242436;
  color: #4361ee;
  border-right: 4px solid #4361ee;
}

.sidebar-footer {
  padding: 20px;
  margin-top: auto;
}

.logout-btn {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: none;
  background-color: rgba(246, 78, 96, 0.1);
  color: #f64e60;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.3s;
}

.logout-btn:hover {
  background-color: #f64e60;
  color: #fff;
}

/* 主内容区设计 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.main-header {
  height: 70px;
  background: #fff;
  padding: 0 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  z-index: 10;
}

.breadcrumb {
  color: #7e8299;
  font-size: 0.9rem;
}

.current-time {
  background: #f3f6f9;
  padding: 6px 15px;
  border-radius: 6px;
  font-family: monospace;
  color: #3f4254;
  font-size: 0.85rem;
}

.content-area {
  padding: 25px;
  min-height: calc(100vh - 70px);
}

.page-container {
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
  min-height: 100%;
}

/* 动画效果 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 登录模式覆盖 */
.auth-mode .auth-wrapper {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>