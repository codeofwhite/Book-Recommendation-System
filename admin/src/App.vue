<template>
  <div id="admin-dashboard" :class="{ 'auth-mode': !isAuthenticated }">
    <!-- Show sidebar and main content only when authenticated -->
    <template v-if="isAuthenticated">
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2>📚 Book Admin Portal</h2>
          <div class="user-info" v-if="currentUser">
            <div class="user-avatar">{{ currentUser.username.charAt(0).toUpperCase() }}</div>
            <span class="user-name">{{ currentUser.username }}</span>
          </div>
        </div>
        <nav class="sidebar-nav">
          <ul>
            <li>
              <router-link to="/dashboard" active-class="active">
                📊 Dashboard Overview
              </router-link>
            </li>
            <li>
              <router-link to="/books" active-class="active">
                📚 Manage Books
              </router-link>
            </li>
            <li>
              <router-link to="/add-book" active-class="active">
                ➕ Add New Book
              </router-link>
            </li>
            <li>
              <router-link to="/reviews" active-class="active">
                💬 Manage Reviews
              </router-link>
            </li>
            <li>
              <router-link to="/users" active-class="active">
                👥 Manage Users
              </router-link>
            </li>
          </ul>
        </nav>
        <div class="sidebar-footer">
          <button @click="handleLogout" class="logout-button">
            🚪 Logout
          </button>
        </div>
      </aside>

      <main class="main-content">
        <header class="main-header">
          <h1>Welcome, {{ currentUser?.username || 'Administrator' }}!</h1>
          <div class="header-actions">
            <span class="current-time">{{ currentTime }}</span>
          </div>
        </header>
        <div class="content-area">
          <router-view />
        </div>
      </main>
    </template>

    <!-- Show router-view directly for login page -->
    <template v-else>
      <div class="auth-wrapper">
        <router-view />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const currentUser = ref(null)
const currentTime = ref('')

// Computed
const isAuthenticated = computed(() => {
  const token = localStorage.getItem('adminToken')
  const user = localStorage.getItem('adminUser')
  return !!(token && user)
})

// Methods
const loadUserData = () => {
  const userData = localStorage.getItem('adminUser')
  if (userData) {
    try {
      currentUser.value = JSON.parse(userData)
    } catch (error) {
      console.error('Error parsing user data:', error)
      currentUser.value = null
    }
  }
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleLogout = () => {
  if (confirm('Are you sure you want to logout?')) {
    localStorage.removeItem('adminToken')
    localStorage.removeItem('adminUser')
    currentUser.value = null
    router.push('/login')
  }
}

// Lifecycle
let timeInterval = null

onMounted(() => {
  loadUserData()
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
#admin-dashboard {
  display: flex;
  min-height: 100vh;
  font-family: 'Arial', sans-serif;
  background-color: #f4f7f6;
  color: #333;
}

/* Sidebar Styles */
.sidebar {
  width: 280px;
  min-width: 280px;
  max-width: 280px;
  flex-shrink: 0;
  background-color: #2c3e50;
  color: white;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

.sidebar-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #34495e;
}

.sidebar-header h2 {
  margin: 0 0 16px 0;
  font-size: 1.4em;
  color: #ecf0f1;
}

.user-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #3498db;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9em;
}

.user-name {
  font-size: 0.9em;
  color: #bdc3c7;
}

.sidebar-nav {
  flex-grow: 1;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav li {
  margin-bottom: 8px;
}

.sidebar-nav a {
  display: block;
  padding: 12px 16px;
  text-decoration: none;
  color: #bdc3c7;
  border-radius: 8px;
  transition: all 0.3s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.95em;
}

.sidebar-nav a:hover,
.sidebar-nav a.active {
  background-color: #34495e;
  color: #ffffff;
  transform: translateX(4px);
}

.sidebar-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #34495e;
}

.logout-button {
  width: 100%;
  padding: 12px 16px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95em;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.logout-button:hover {
  background-color: #c0392b;
}

/* Main Content Styles */
.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.main-header {
  background-color: #ffffff;
  padding: 20px 30px;
  border-bottom: 1px solid #eee;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.main-header h1 {
  margin: 0;
  font-size: 1.6em;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.current-time {
  color: #7f8c8d;
  font-size: 0.9em;
  font-weight: 500;
}

.content-area {
  flex-grow: 1;
  padding: 30px;
  background-color: #f4f7f6;
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    width: 240px;
  }
  
  .main-header {
    padding: 16px 20px;
  }
  
  .main-header h1 {
    font-size: 1.4em;
  }
  
  .content-area {
    padding: 20px;
  }
}

/* Basic Router Link Active Class */
.router-link-exact-active {
  background-color: #34495e !important;
  color: #ffffff !important;
}

#admin-dashboard.auth-mode {
  display: block;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}

.auth-wrapper {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
}
</style>
