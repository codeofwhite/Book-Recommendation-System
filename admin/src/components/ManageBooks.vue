<template>
  <div class="admin-panel-card">
    <div class="header-section">
      <h2>Manage Books</h2>
      <p>View, edit, or delete existing book entries.</p>
    </div>

    <div class="search-filter-bar">
      <input 
        type="text" 
        v-model="inputSearchKeyword" 
        placeholder="Search by title, author, ISBN..." 
        class="search-input"
      />
      <button class="search-button" @click="searchBooks">
        <span class="search-icon">🔍</span>
        Search
      </button>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Author</th>
            <th>ISBN</th>
            <th>Rating</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="book in paginatedBooks" :key="book.bookId" class="table-row">
            <td>{{ book.bookId }}</td>
            <td class="title-cell">{{ book.title }}</td>
            <td>{{ book.author }}</td>
            <td>{{ book.isbn || 'N/A' }}</td>
            <td>
              <span class="rating-badge">{{ book.rating || 'N/A' }}</span>
            </td>
            <td>
              <div class="action-buttons">
                <button class="action-button edit-button" @click="openEditModal(book)">
                  ✏️ Edit
                </button>
                <button class="action-button delete-button" @click="deleteBook(book.bookId)">
                  🗑️ Delete
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
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

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Edit Book</h3>
          <button class="close-button" @click="closeEditModal">×</button>
        </div>
        <form @submit.prevent="saveBook" class="edit-form">
          <div class="form-group">
            <label>Title:</label>
            <input type="text" v-model="editingBook.title" required>
          </div>
          <div class="form-group">
            <label>Author:</label>
            <input type="text" v-model="editingBook.author" required>
          </div>
          <div class="form-group">
            <label>ISBN:</label>
            <input type="text" v-model="editingBook.isbn">
          </div>
          <div class="form-group">
            <label>Description:</label>
            <textarea v-model="editingBook.description" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label>Publisher:</label>
            <input type="text" v-model="editingBook.publisher">
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-button" @click="closeEditModal">Cancel</button>
            <button type="submit" class="save-button">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const allBooks = ref([])
const inputSearchKeyword = ref('')
const currentPage = ref(1)
const pageSize = 10
const showEditModal = ref(false)
const editingBook = ref({})

// !!!获取书籍信息采用BookList相同接口
const fetchBooks = async () => {
  try {
    const response = await axios.get('/service-b/api/books')
    allBooks.value = response.data
  } catch (error) {
    console.error('Error fetching books:', error)
  }
}

const filteredBooks = computed(() => {
  let filtered = [...allBooks.value]
  if (inputSearchKeyword.value) {
    const keyword = inputSearchKeyword.value.toLowerCase()
    filtered = filtered.filter(book =>
      book.title.toLowerCase().includes(keyword) ||
      book.author.toLowerCase().includes(keyword) ||
      (book.isbn && book.isbn.toLowerCase().includes(keyword))
    )
  }
  return filtered
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredBooks.value.length / pageSize))
)

const paginatedBooks = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredBooks.value.slice(start, start + pageSize)
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const searchBooks = () => {
  currentPage.value = 1
}

const openEditModal = (book) => {
  editingBook.value = { ...book }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingBook.value = {}
}

const saveBook = async () => {
  try {
    await axios.put(`/service-b/api/books/${editingBook.value.bookId}`, editingBook.value)
    const index = allBooks.value.findIndex(b => b.bookId === editingBook.value.bookId)
    if (index !== -1) {
      allBooks.value[index] = { ...editingBook.value }
    }
    closeEditModal()
    alert('Book updated successfully!')
  } catch (error) {
    console.error('Error updating book:', error)
    alert('Failed to update book.')
  }
}

const deleteBook = async (bookId) => {
  if (!confirm('Are you sure you want to delete this book? This action cannot be undone.')) return
  
  try {
    await axios.delete(`/service-b/api/books/${bookId}`)
    allBooks.value = allBooks.value.filter(b => b.bookId !== bookId)
    alert('Book deleted successfully!')
  } catch (error) {
    console.error('Error deleting book:', error)
    alert('Failed to delete book.')
  }
}

watch(inputSearchKeyword, () => {
  currentPage.value = 1
})

onMounted(fetchBooks)
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

.search-filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  align-items: center;
}

.search-input {
  flex-grow: 1;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1em;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.search-button {
  padding: 12px 20px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-button:hover {
  background-color: #2980b9;
}

.table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background-color: #f8f9fa;
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #e9ecef;
}

.data-table td {
  padding: 16px;
  border-bottom: 1px solid #e9ecef;
}

.table-row:hover {
  background-color: #f8f9fa;
}

.title-cell {
  font-weight: 500;
  color: #2c3e50;
}

.rating-badge {
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.9em;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-button {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.edit-button {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.edit-button:hover {
  background-color: #ffeaa7;
}

.delete-button {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.delete-button:hover {
  background-color: #f5c6cb;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 24px;
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
  max-width: 600px;
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
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 1em;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
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
</style>