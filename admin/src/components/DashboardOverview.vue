<template>
  <div class="admin-panel-card">
    <h2>Dashboard Overview</h2>
    <p>Welcome to your Book Management Dashboard. Here you can see a quick summary of your data.</p>
    
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-icon">📚</div>
        <h3>Total Books</h3>
        <p class="stat-number">{{ totalBooks }}</p>
      </div>
      <div class="stat-item">
        <div class="stat-icon">⭐</div>
        <h3>Avg. Rating</h3>
        <p class="stat-number">{{ averageRating }}</p>
      </div>
      <div class="stat-item">
        <div class="stat-icon">👥</div>
        <h3>Total Users</h3>
        <p class="stat-number">{{ totalUsers }}</p>
      </div>
      <div class="stat-item">
        <div class="stat-icon">💬</div>
        <h3>Total Reviews</h3>
        <p class="stat-number">{{ totalReviews }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const allBooks = ref([])
const totalUsers = ref(0)
const loading = ref(false)
const error = ref(null)
const totalReviews = ref(423)
const totalBooks = computed(() => allBooks.value.length)

const averageRating = computed(() => {
  if (allBooks.value.length === 0) return '0.0'
  const sum = allBooks.value.reduce((acc, book) => acc + (book.rating || 0), 0)
  return (sum / allBooks.value.length).toFixed(1)
})

// Fetch users from API
// 获取用户总数
const fetchTotalUsers = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await axios.get('/service-a/api/users') // 请确认你的 API 路径
    totalUsers.value = response.data.total || 0
  } catch (err) {
    console.error('Error fetching total users:', err)
    error.value = err.response?.data?.error || 'Failed to fetch user statistics'
  } finally {
    loading.value = false
  }
}

const fetchBooks = async () => {
  try {
    const response = await axios.get('/service-b/api/books')
    allBooks.value = response.data
  } catch (error) {
    console.error('Error fetching books:', error)
  }
}

onMounted(() => {
  fetchBooks()
  fetchTotalUsers()
})
</script>

<style scoped>
.admin-panel-card {
  background-color: #ffffff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1.8em;
  font-weight: 600;
}

h2 + p {
  color: #7f8c8d;
  margin-bottom: 30px;
  font-size: 1.1em;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-item {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 24px;
  border-radius: 10px;
  text-align: center;
  border: 1px solid #e9ecef;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 2.5em;
  margin-bottom: 12px;
}

.stat-item h3 {
  margin: 0 0 12px 0;
  color: #495057;
  font-size: 1.1em;
  font-weight: 500;
}

.stat-number {
  font-size: 2.4em;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.recent-activity {
  border-top: 2px solid #e9ecef;
  padding-top: 30px;
}

.recent-activity h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.4em;
  font-weight: 600;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.activity-icon {
  font-size: 1.5em;
  margin-right: 16px;
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-weight: 500;
}

.activity-time {
  color: #7f8c8d;
  font-size: 0.9em;
}
</style>