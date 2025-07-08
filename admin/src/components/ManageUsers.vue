<template>
  <div class="admin-panel-card">
    <div class="header-section">
      <h2>Manage Users</h2>
      <p>View, edit, or manage user accounts.</p>
    </div>

    <div class="action-bar">
      <button @click="showCreateModal = true" class="create-btn">
        ➕ Add New User
      </button>
    </div>

    <div class="filter-bar">
      <input type="text" v-model="searchKeyword" @input="debounceSearch" placeholder="Search users..."
        class="search-input" />
      <button @click="fetchUsers" class="search-btn">🔍 Search</button>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading users...</p>
    </div>

    <div v-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button @click="fetchUsers" class="retry-btn">Retry</button>
    </div>

    <div v-if="!loading && !error" class="users-container">
      <div v-for="user in users" :key="user.id" class="user-card">
        <div class="user-header">
          <div class="user-info">
            <div class="user-avatar">
              <img v-if="user.avatar_url" :src="user.avatar_url" :alt="user.username" />
              <span v-else>{{ user.username.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="user-details">
              <h4>{{ user.username }}</h4>
              <span class="user-email">{{ user.email }}</span>
            </div>
          </div>
        </div>

        <div class="user-actions">
          <button @click="editUser(user)" class="action-btn edit-btn">
            ✏️ Edit
          </button>
          <button @click="viewUserDetails(user)" class="action-btn details-btn">
            👁️ Details
          </button>
          <button @click="banUser(user.id)" class="action-btn ban-btn">
            🚫 Ban User
          </button>
        </div>
      </div>
    </div>

    <div v-if="!loading && !error && users.length === 0" class="empty-state">
      <div class="empty-icon">👥</div>
      <p>No users found matching your criteria.</p>
      <button @click="clearFilters" class="clear-filters-btn">Clear Search</button>
    </div>

    <div v-if="pagination && pagination.pages > 1" class="pagination">
      <button @click="goToPage(pagination.current_page - 1)" :disabled="!pagination.has_prev" class="pagination-btn">
        ← Previous
      </button>
      <span class="pagination-info">
        Page {{ pagination.current_page }} of {{ pagination.pages }}
        ({{ pagination.total }} total users)
      </span>
      <button @click="goToPage(pagination.current_page + 1)" :disabled="!pagination.has_next" class="pagination-btn">
        Next →
      </button>
    </div>

    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create New User</h3>
          <button class="close-button" @click="closeCreateModal">×</button>
        </div>
        <form @submit.prevent="createUser" class="edit-form">
          <div class="form-group">
            <label>Username:</label>
            <input type="text" v-model="newUser.username" required>
          </div>
          <div class="form-group">
            <label>Email:</label>
            <input type="email" v-model="newUser.email" required>
          </div>
          <div class="form-group">
            <label>Password:</label>
            <input type="password" v-model="newUser.password" required minlength="6">
          </div>
          <div class="form-group">
            <label>Avatar URL (optional):</label>
            <input type="url" v-model="newUser.avatar_url">
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-button" @click="closeCreateModal">Cancel</button>
            <button type="submit" class="save-button" :disabled="creating">
              {{ creating ? 'Creating...' : 'Create User' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Edit User</h3>
          <button class="close-button" @click="closeEditModal">×</button>
        </div>
        <form @submit.prevent="saveUser" class="edit-form">
          <div class="form-group">
            <label>Username:</label>
            <input type="text" v-model="editingUser.username" required>
          </div>
          <div class="form-group">
            <label>Email:</label>
            <input type="email" v-model="editingUser.email" required>
          </div>
          <div class="form-group">
            <label>Avatar URL:</label>
            <input type="url" v-model="editingUser.avatar_url">
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-button" @click="closeEditModal">Cancel</button>
            <button type="submit" class="save-button" :disabled="updating">
              {{ updating ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>User Details</h3>
          <button class="close-button" @click="closeDetailsModal">×</button>
        </div>
        <div class="modal-body" v-if="selectedUser">
          <div class="detail-section">
            <h4>User Information</h4>
            <div class="detail-row">
              <strong>ID:</strong> {{ selectedUser.id }}
            </div>
            <div class="detail-row">
              <strong>Username:</strong> {{ selectedUser.username }}
            </div>
            <div class="detail-row">
              <strong>Email:</strong> {{ selectedUser.email }}
            </div>
            <div class="detail-row" v-if="selectedUser.avatar_url">
              <strong>Avatar:</strong>
              <img :src="selectedUser.avatar_url" alt="Avatar" class="detail-avatar">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// Reactive data
const users = ref([])
const pagination = ref(null)
const loading = ref(false)
const error = ref(null)

// Search
const searchKeyword = ref('')
const currentPage = ref(1)
const perPage = ref(12)

// Modal states
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDetailsModal = ref(false)
const editingUser = ref({})
const selectedUser = ref(null)
const newUser = ref({
  username: '',
  email: '',
  password: '',
  avatar_url: ''
})

// Loading states
const creating = ref(false)
const updating = ref(false)

// Search debounce
let searchTimeout = null


// Fetch users from API
const fetchUsers = async (page = 1) => {
  loading.value = true
  error.value = null

  try {
    const params = {
      page: page,
      per_page: perPage.value
    }

    if (searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim()
    }

    const response = await axios.get(`/service-a/api/users`, { params })

    users.value = response.data.users || []
    pagination.value = {
      total: response.data.total,
      pages: response.data.pages,
      current_page: response.data.current_page,
      per_page: response.data.per_page,
      has_next: response.data.has_next,
      has_prev: response.data.has_prev
    }

    currentPage.value = page

  } catch (err) {
    console.error('Error fetching users:', err)
    error.value = err.response?.data?.error || 'Failed to fetch users'
  } finally {
    loading.value = false
  }
}

// Create new user
const createUser = async () => {
  if (creating.value) return

  creating.value = true

  try {
    await axios.post(`/service-a/api/users`, newUser.value)

    // Reset form
    newUser.value = {
      username: '',
      email: '',
      password: '',
      avatar_url: ''
    }

    closeCreateModal()
    await fetchUsers(currentPage.value)

    alert('User created successfully!')

  } catch (err) {
    console.error('Error creating user:', err)
    alert(err.response?.data?.error || 'Failed to create user')
  } finally {
    creating.value = false
  }
}

// Edit user
const editUser = (user) => {
  editingUser.value = { ...user }
  showEditModal.value = true
}

// Save user changes
const saveUser = async () => {
  if (updating.value) return

  updating.value = true

  try {
    const response = await axios.put(`/service-a/api/users/${editingUser.value.id}`, editingUser.value)

    // Update local user data
    const index = users.value.findIndex(u => u.id === editingUser.value.id)
    if (index !== -1) {
      users.value[index] = response.data
    }

    closeEditModal()
    alert('User updated successfully!')

  } catch (err) {
    console.error('Error updating user:', err)
    alert(err.response?.data?.error || 'Failed to update user')
  } finally {
    updating.value = false
  }
}

// Delete user
const deleteUser = async (userId) => {
  if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
    return
  }

  try {
    await axios.delete(`/service-a/api/users/${userId}`)

    // Remove from local data
    users.value = users.value.filter(u => u.id !== userId)

    alert('User deleted successfully!')

  } catch (err) {
    console.error('Error deleting user:', err)
    alert(err.response?.data?.error || 'Failed to delete user')
  }
}

// View user details
const viewUserDetails = (user) => {
  selectedUser.value = user
  showDetailsModal.value = true
}

// Pagination
const goToPage = (page) => {
  if (page >= 1 && page <= pagination.value.pages) {
    fetchUsers(page)
  }
}

// Modal controls
const closeCreateModal = () => {
  showCreateModal.value = false
  newUser.value = {
    username: '',
    email: '',
    password: '',
    avatar_url: ''
  }
}

const closeEditModal = () => {
  showEditModal.value = false
  editingUser.value = {}
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedUser.value = null
}

// Utility functions
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchUsers(1)
  }, 500)
}

const clearFilters = () => {
  searchKeyword.value = ''
  currentPage.value = 1
  fetchUsers(1)
}

// Initialize
onMounted(() => {
  fetchUsers()
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

.header-section h2 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1.8em;
  font-weight: 600;
}

.header-section p {
  color: #7f8c8d;
  margin-bottom: 30px;
  font-size: 1.1em;
}

.action-bar {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 24px;
}

.create-btn {
  padding: 12px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.create-btn:hover {
  background-color: #218838;
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
  padding: 10px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1em;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.search-btn {
  padding: 10px 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.search-btn:hover {
  background-color: #2980b9;
}

.loading-container {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.error-container {
  text-align: center;
  padding: 40px;
  color: #e74c3c;
}

.error-message {
  margin-bottom: 16px;
  font-weight: 500;
}

.retry-btn {
  padding: 10px 20px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.retry-btn:hover {
  background-color: #c0392b;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 4em;
  margin-bottom: 16px;
}

.clear-filters-btn {
  padding: 10px 20px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 16px;
}

.clear-filters-btn:hover {
  background-color: #5a6268;
}

.users-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.user-card {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  padding: 20px;
  transition: box-shadow 0.3s ease;
}

.user-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-header {
  margin-bottom: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.4em;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details h4 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 1.2em;
}

.user-email {
  color: #7f8c8d;
  font-size: 0.9em;
}

.user-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.edit-btn {
  background-color: #fff3cd;
  color: #856404;
}

.edit-btn:hover {
  background-color: #ffeaa7;
}

.delete-btn {
  background-color: #f8d7da;
  color: #721c24;
}

.delete-btn:hover {
  background-color: #f5c6cb;
}

.details-btn {
  background-color: #e2e3e5;
  color: #383d41;
}

.details-btn:hover {
  background-color: #d6d8db;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.pagination-btn {
  padding: 10px 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #2980b9;
}

.pagination-btn:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.pagination-info {
  font-weight: 500;
  color: #495057;
  text-align: center;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.4em;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
  color: #7f8c8d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #495057;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 1em;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-button {
  padding: 10px 20px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.save-button {
  padding: 10px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-button:hover {
  background-color: #5a6268;
}

.save-button:hover:not(:disabled) {
  background-color: #218838;
}

.save-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.modal-body {
  padding: 24px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  color: #2c3e50;
  margin-bottom: 12px;
  font-size: 1.1em;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 6px;
}

.detail-row {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-row strong {
  color: #495057;
  min-width: 80px;
}

.detail-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

@media (max-width: 768px) {
  .users-container {
    grid-template-columns: 1fr;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    min-width: auto;
  }
}
</style>
