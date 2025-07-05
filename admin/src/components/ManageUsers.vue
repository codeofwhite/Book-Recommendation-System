<template>
  <div class="admin-panel-card">
    <div class="header-section">
      <h2>Manage Users</h2>
      <p>View, edit, or manage user accounts and their permissions.</p>
    </div>

    <div class="filter-bar">
      <select v-model="statusFilter" class="filter-select">
        <option value="all">All Users</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
        <option value="banned">Banned</option>
      </select>
      <select v-model="roleFilter" class="filter-select">
        <option value="all">All Roles</option>
        <option value="admin">Admin</option>
        <option value="user">User</option>
        <option value="moderator">Moderator</option>
      </select>
      <input 
        type="text" 
        v-model="searchKeyword" 
        placeholder="Search users..." 
        class="search-input"
      />
    </div>

    <div class="users-container">
      <div v-for="user in paginatedUsers" :key="user.id" class="user-card">
        <div class="user-header">
          <div class="user-info">
            <div class="user-avatar">{{ user.name.charAt(0).toUpperCase() }}</div>
            <div class="user-details">
              <h4>{{ user.name }}</h4>
              <span class="user-email">{{ user.email }}</span>
            </div>
          </div>
          <div class="user-badges">
            <span :class="['status-badge', user.status]">{{ user.status.toUpperCase() }}</span>
            <span :class="['role-badge', user.role]">{{ user.role.toUpperCase() }}</span>
          </div>
        </div>

        <div class="user-stats">
          <div class="stat-item">
            <span class="stat-label">Joined:</span>
            <span class="stat-value">{{ formatDate(user.joinedAt) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Reviews:</span>
            <span class="stat-value">{{ user.reviewCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Last Login:</span>
            <span class="stat-value">{{ formatDate(user.lastLogin) }}</span>
          </div>
        </div>

        <div class="user-actions">
          <button 
            @click="editUser(user)"
            class="action-btn edit-btn"
          >
            ✏️ Edit
          </button>
          <button 
            v-if="user.status === 'active'"
            @click="toggleUserStatus(user.id, 'inactive')"
            class="action-btn deactivate-btn"
          >
            ⏸️ Deactivate
          </button>
          <button 
            v-if="user.status === 'inactive'"
            @click="toggleUserStatus(user.id, 'active')"
            class="action-btn activate-btn"
          >
            ▶️ Activate
          </button>
          <button 
            v-if="user.status !== 'banned'"
            @click="banUser(user.id)"
            class="action-btn ban-btn"
          >
            🚫 Ban
          </button>
          <button 
            @click="viewUserDetails(user)"
            class="action-btn details-btn"
          >
            👁️ Details
          </button>
        </div>
      </div>
    </div>

    <div class="pagination">
      <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="pagination-btn">
        ← Previous
      </button>
      <span class="pagination-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages" class="pagination-btn">
        Next →
      </button>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Edit User</h3>
          <button class="close-button" @click="closeEditModal">×</button>
        </div>
        <form @submit.prevent="saveUser" class="edit-form">
          <div class="form-group">
            <label>Name:</label>
            <input type="text" v-model="editingUser.name" required>
          </div>
          <div class="form-group">
            <label>Email:</label>
            <input type="email" v-model="editingUser.email" required>
          </div>
          <div class="form-group">
            <label>Role:</label>
            <select v-model="editingUser.role">
              <option value="user">User</option>
              <option value="moderator">Moderator</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div class="form-group">
            <label>Status:</label>
            <select v-model="editingUser.status">
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="banned">Banned</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-button" @click="closeEditModal">Cancel</button>
            <button type="submit" class="save-button">Save Changes</button>
          </div>
        </form>
      </div>
    </div>

    <!-- User Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>User Details</h3>
          <button class="close-button" @click="closeDetailsModal">×</button>
        </div>
        <div class="modal-body" v-if="selectedUser">
          <div class="detail-section">
            <h4>Basic Information</h4>
            <div class="detail-row">
              <strong>Name:</strong> {{ selectedUser.name }}
            </div>
            <div class="detail-row">
              <strong>Email:</strong> {{ selectedUser.email }}
            </div>
            <div class="detail-row">
              <strong>Role:</strong> 
              <span :class="['role-badge', selectedUser.role]">{{ selectedUser.role.toUpperCase() }}</span>
            </div>
            <div class="detail-row">
              <strong>Status:</strong> 
              <span :class="['status-badge', selectedUser.status]">{{ selectedUser.status.toUpperCase() }}</span>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>Activity Information</h4>
            <div class="detail-row">
              <strong>Joined:</strong> {{ formatDate(selectedUser.joinedAt) }}
            </div>
            <div class="detail-row">
              <strong>Last Login:</strong> {{ formatDate(selectedUser.lastLogin) }}
            </div>
            <div class="detail-row">
              <strong>Total Reviews:</strong> {{ selectedUser.reviewCount }}
            </div>
            <div class="detail-row">
              <strong>Books Read:</strong> {{ selectedUser.booksRead }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const users = ref([
  {
    id: 1,
    name: 'Alice Johnson',
    email: 'alice@example.com',
    role: 'admin',
    status: 'active',
    joinedAt: new Date('2023-06-15T10:30:00'),
    lastLogin: new Date('2024-01-15T14:20:00'),
    reviewCount: 23,
    booksRead: 45
  },
  {
    id: 2,
    name: 'Bob Smith',
    email: 'bob@example.com',
    role: 'user',
    status: 'active',
    joinedAt: new Date('2023-08-22T09:15:00'),
    lastLogin: new Date('2024-01-14T16:45:00'),
    reviewCount: 12,
    booksRead: 28
  },
  {
    id: 3,
    name: 'Carol Davis',
    email: 'carol@example.com',
    role: 'moderator',
    status: 'active',
    joinedAt: new Date('2023-05-10T11:00:00'),
    lastLogin: new Date('2024-01-13T13:30:00'),
    reviewCount: 34,
    booksRead: 67
  },
  {
    id: 4,
    name: 'David Wilson',
    email: 'david@example.com',
    role: 'user',
    status: 'inactive',
    joinedAt: new Date('2023-09-05T14:20:00'),
    lastLogin: new Date('2023-12-20T10:15:00'),
    reviewCount: 8,
    booksRead: 15
  },
  {
    id: 5,
    name: 'Eva Brown',
    email: 'eva@example.com',
    role: 'user',
    status: 'banned',
    joinedAt: new Date('2023-11-12T16:45:00'),
    lastLogin: new Date('2024-01-05T09:30:00'),
    reviewCount: 3,
    booksRead: 7
  },
  {
    id: 6,
    name: 'Frank Miller',
    email: 'frank@example.com',
    role: 'user',
    status: 'active',
    joinedAt: new Date('2023-07-18T12:00:00'),
    lastLogin: new Date('2024-01-12T18:20:00'),
    reviewCount: 19,
    booksRead: 32
  },
  {
    id: 7,
    name: 'Grace Lee',
    email: 'grace@example.com',
    role: 'moderator',
    status: 'active',
    joinedAt: new Date('2023-04-03T08:30:00'),
    lastLogin: new Date('2024-01-11T15:10:00'),
    reviewCount: 41,
    booksRead: 89
  },
  {
    id: 8,
    name: 'Henry Taylor',
    email: 'henry@example.com',
    role: 'user',
    status: 'inactive',
    joinedAt: new Date('2023-10-28T13:15:00'),
    lastLogin: new Date('2023-12-15T11:45:00'),
    reviewCount: 5,
    booksRead: 12
  }
])

const statusFilter = ref('all')
const roleFilter = ref('all')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = 6
const showEditModal = ref(false)
const showDetailsModal = ref(false)
const editingUser = ref({})
const selectedUser = ref(null)

const filteredUsers = computed(() => {
  let filtered = users.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(user => user.status === statusFilter.value)
  }

  if (roleFilter.value !== 'all') {
    filtered = filtered.filter(user => user.role === roleFilter.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(user =>
      user.name.toLowerCase().includes(keyword) ||
      user.email.toLowerCase().includes(keyword)
    )
  }

  return filtered.sort((a, b) => new Date(b.lastLogin) - new Date(a.lastLogin))
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredUsers.value.length / pageSize))
)

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredUsers.value.slice(start, start + pageSize)
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const editUser = (user) => {
  editingUser.value = { ...user }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingUser.value = {}
}

const saveUser = () => {
  const index = users.value.findIndex(u => u.id === editingUser.value.id)
  if (index !== -1) {
    users.value[index] = { ...editingUser.value }
  }
  closeEditModal()
  alert('User updated successfully!')
}

const toggleUserStatus = (userId, newStatus) => {
  const user = users.value.find(u => u.id === userId)
  if (user) {
    user.status = newStatus
    alert(`User ${newStatus === 'active' ? 'activated' : 'deactivated'} successfully!`)
  }
}

const banUser = (userId) => {
  if (confirm('Are you sure you want to ban this user? This action can be reversed later.')) {
    const user = users.value.find(u => u.id === userId)
    if (user) {
      user.status = 'banned'
      alert('User banned successfully!')
    }
  }
}

const viewUserDetails = (user) => {
  selectedUser.value = user
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedUser.value = null
}

onMounted(() => {
  console.log('Users loaded:', users.value.length)
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

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  background-color: white;
  font-size: 1em;
  min-width: 120px;
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

.users-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
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
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.user-badges {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
}

.status-badge, .role-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75em;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.banned {
  background-color: #f8d7da;
  color: #721c24;
}

.role-badge.admin {
  background-color: #e7e3ff;
  color: #5a4fcf;
}

.role-badge.moderator {
  background-color: #cff4fc;
  color: #055160;
}

.role-badge.user {
  background-color: #e2e3e5;
  color: #383d41;
}

.user-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background-color: white;
  border-radius: 6px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 0.8em;
  color: #7f8c8d;
  font-weight: 500;
}

.stat-value {
  font-size: 0.9em;
  color: #2c3e50;
  font-weight: 600;
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

.activate-btn {
  background-color: #d4edda;
  color: #155724;
}

.activate-btn:hover {
  background-color: #c3e6cb;
}

.deactivate-btn {
  background-color: #fff3cd;
  color: #856404;
}

.deactivate-btn:hover {
  background-color: #ffeaa7;
}

.ban-btn {
  background-color: #f8d7da;
  color: #721c24;
}

.ban-btn:hover {
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

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 1em;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
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

.save-button:hover {
  background-color: #218838;
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
  min-width: 100px;
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
  
  .user-stats {
    grid-template-columns: 1fr 1fr;
  }
}
</style>