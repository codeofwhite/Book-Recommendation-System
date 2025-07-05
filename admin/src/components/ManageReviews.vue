<template>
  <div class="admin-panel-card">
    <div class="header-section">
      <h2>Manage Reviews</h2>
      <p>Here you can moderate, approve, or delete user reviews.</p>
    </div>

    <div class="filter-bar">
      <select v-model="statusFilter" class="filter-select">
        <option value="all">All Reviews</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
      </select>
      <input 
        type="text" 
        v-model="searchKeyword" 
        placeholder="Search reviews..." 
        class="search-input"
      />
    </div>

    <div class="reviews-container">
      <div v-for="review in filteredReviews" :key="review.id" class="review-card">
        <div class="review-header">
          <div class="user-info">
            <div class="user-avatar">{{ review.userName.charAt(0).toUpperCase() }}</div>
            <div class="user-details">
              <h4>{{ review.userName }}</h4>
              <span class="review-date">{{ formatDate(review.createdAt) }}</span>
            </div>
          </div>
          <div class="review-status">
            <span :class="['status-badge', review.status]">{{ review.status.toUpperCase() }}</span>
          </div>
        </div>

        <div class="review-content">
          <div class="book-info">
            <strong>Book:</strong> {{ review.bookTitle }}
          </div>
          <div class="rating">
            <span class="stars">{{ '★'.repeat(review.rating) }}{{ '☆'.repeat(5 - review.rating) }}</span>
            <span class="rating-text">({{ review.rating }}/5)</span>
          </div>
          <div class="review-text">
            {{ review.content }}
          </div>
        </div>

        <div class="review-actions">
          <button 
            v-if="review.status === 'pending'" 
            @click="approveReview(review.id)"
            class="action-btn approve-btn"
          >
            ✅ Approve
          </button>
          <button 
            v-if="review.status === 'pending'" 
            @click="rejectReview(review.id)"
            class="action-btn reject-btn"
          >
            ❌ Reject
          </button>
          <button 
            @click="deleteReview(review.id)"
            class="action-btn delete-btn"
          >
            🗑️ Delete
          </button>
          <button 
            @click="viewDetails(review)"
            class="action-btn details-btn"
          >
            👁️ Details
          </button>
        </div>
      </div>
    </div>

    <div v-if="filteredReviews.length === 0" class="no-reviews">
      <div class="no-reviews-icon">📝</div>
      <p>No reviews found matching your criteria.</p>
    </div>

    <!-- Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Review Details</h3>
          <button class="close-button" @click="closeDetailsModal">×</button>
        </div>
        <div class="modal-body" v-if="selectedReview">
          <div class="detail-row">
            <strong>User:</strong> {{ selectedReview.userName }} ({{ selectedReview.userEmail }})
          </div>
          <div class="detail-row">
            <strong>Book:</strong> {{ selectedReview.bookTitle }}
          </div>
          <div class="detail-row">
            <strong>Rating:</strong> {{ selectedReview.rating }}/5 stars
          </div>
          <div class="detail-row">
            <strong>Status:</strong> 
            <span :class="['status-badge', selectedReview.status]">{{ selectedReview.status.toUpperCase() }}</span>
          </div>
          <div class="detail-row">
            <strong>Created:</strong> {{ formatDate(selectedReview.createdAt) }}
          </div>
          <div class="detail-row">
            <strong>Review Content:</strong>
            <div class="review-content-full">{{ selectedReview.content }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const reviews = ref([
  {
    id: 1,
    userName: 'Alice Johnson',
    userEmail: 'alice@example.com',
    bookTitle: 'The Great Gatsby',
    rating: 5,
    content: 'An absolutely magnificent piece of literature! Fitzgerald\'s prose is beautiful and the story is timeless. The characters are complex and the themes are still relevant today.',
    status: 'pending',
    createdAt: new Date('2024-01-15T10:30:00')
  },
  {
    id: 2,
    userName: 'Bob Smith',
    userEmail: 'bob@example.com',
    bookTitle: 'To Kill a Mockingbird',
    rating: 4,
    content: 'A powerful story about justice and morality. Harper Lee created unforgettable characters and addressed important social issues with grace and wisdom.',
    status: 'approved',
    createdAt: new Date('2024-01-14T15:45:00')
  },
  {
    id: 3,
    userName: 'Carol Davis',
    userEmail: 'carol@example.com',
    bookTitle: '1984',
    rating: 5,
    content: 'Orwell\'s dystopian masterpiece is more relevant than ever. The concepts of surveillance, thought control, and propaganda are chillingly prescient.',
    status: 'approved',
    createdAt: new Date('2024-01-13T09:20:00')
  },
  {
    id: 4,
    userName: 'David Wilson',
    userEmail: 'david@example.com',
    bookTitle: 'Pride and Prejudice',
    rating: 3,
    content: 'While I appreciate Austen\'s wit and social commentary, the pacing felt slow at times. Still a classic worth reading for its historical significance.',
    status: 'pending',
    createdAt: new Date('2024-01-12T14:10:00')
  },
  {
    id: 5,
    userName: 'Eva Brown',
    userEmail: 'eva@example.com',
    bookTitle: 'The Catcher in the Rye',
    rating: 2,
    content: 'I found Holden to be insufferable and whiny. The book didn\'t resonate with me at all. Maybe I\'m missing something, but it felt overrated.',
    status: 'rejected',
    createdAt: new Date('2024-01-11T11:55:00')
  }
])

const statusFilter = ref('all')
const searchKeyword = ref('')
const showDetailsModal = ref(false)
const selectedReview = ref(null)

const filteredReviews = computed(() => {
  let filtered = reviews.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(review => review.status === statusFilter.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(review =>
      review.userName.toLowerCase().includes(keyword) ||
      review.bookTitle.toLowerCase().includes(keyword) ||
      review.content.toLowerCase().includes(keyword)
    )
  }

  return filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const approveReview = (reviewId) => {
  const review = reviews.value.find(r => r.id === reviewId)
  if (review) {
    review.status = 'approved'
    alert('Review approved successfully!')
  }
}

const rejectReview = (reviewId) => {
  const review = reviews.value.find(r => r.id === reviewId)
  if (review) {
    review.status = 'rejected'
    alert('Review rejected successfully!')
  }
}

const deleteReview = (reviewId) => {
  if (confirm('Are you sure you want to delete this review? This action cannot be undone.')) {
    reviews.value = reviews.value.filter(r => r.id !== reviewId)
    alert('Review deleted successfully!')
  }
}

const viewDetails = (review) => {
  selectedReview.value = review
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedReview.value = null
}

onMounted(() => {
  console.log('Reviews loaded:', reviews.value.length)
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
}

.filter-select {
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  background-color: white;
  font-size: 1em;
  min-width: 150px;
}

.search-input {
  flex: 1;
  padding: 10px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1em;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.reviews-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-card {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  padding: 20px;
  transition: box-shadow 0.3s ease;
}

.review-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.2em;
}

.user-details h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1em;
}

.review-date {
  color: #7f8c8d;
  font-size: 0.9em;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.approved {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.rejected {
  background-color: #f8d7da;
  color: #721c24;
}

.review-content {
  margin-bottom: 16px;
}

.book-info {
  color: #495057;
  margin-bottom: 8px;
  font-size: 1em;
}

.rating {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.stars {
  color: #ffc107;
  font-size: 1.2em;
}

.rating-text {
  color: #6c757d;
  font-size: 0.9em;
}

.review-text {
  color: #2c3e50;
  line-height: 1.6;
  padding: 12px;
  background-color: white;
  border-radius: 6px;
  border-left: 4px solid #3498db;
}

.review-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 8px 16px;
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

.approve-btn {
  background-color: #d4edda;
  color: #155724;
}

.approve-btn:hover {
  background-color: #c3e6cb;
}

.reject-btn {
  background-color: #f8d7da;
  color: #721c24;
}

.reject-btn:hover {
  background-color: #f5c6cb;
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

.no-reviews {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.no-reviews-icon {
  font-size: 3em;
  margin-bottom: 16px;
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

.modal-body {
  padding: 24px;
}

.detail-row {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-row strong {
  color: #495057;
}

.review-content-full {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid #3498db;
  margin-top: 8px;
  line-height: 1.6;
}
</style>