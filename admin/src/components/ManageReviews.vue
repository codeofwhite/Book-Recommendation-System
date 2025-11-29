<template>
  <div class="admin-panel-card">
    <div class="header-section">
      <h2>Manage Reviews</h2>
      <p>Here you can moderate, approve, or delete user reviews.</p>
    </div>

    <div class="filter-bar">
      <select v-model="statusFilter" @change="fetchReviews" class="filter-select">
        <option value="all">All Reviews</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
      </select>
      <input type="text" v-model="searchKeyword" @input="debounceSearch" placeholder="Search reviews..."
        class="search-input" />
      <button @click="fetchReviews" class="search-btn">🔍 Search</button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading reviews...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button @click="fetchReviews" class="retry-btn">Retry</button>
    </div>

    <!-- Reviews Container -->
    <div v-if="!loading && !error" class="reviews-container">
      <div v-for="review in reviews" :key="review.id" class="review-card">
        <div class="review-header">
          <div class="user-info">
            <div class="user-avatar">{{ review.userId.charAt(0).toUpperCase() }}</div>
            <div class="user-details">
              <h4>{{ review.userId }}</h4>
              <span class="review-date">{{ formatDate(review.postTime) }}</span>
            </div>
          </div>
          <div class="review-status">
            <span :class="['status-badge', review.status]">{{ review.status.toUpperCase() }}</span>
          </div>
        </div>

        <div class="review-content">
          <div class="book-info">
            <strong>Book ID:</strong> {{ review.bookId }}
          </div>
          <div class="rating">
            <span class="stars">{{ '★'.repeat(Math.floor(review.rating)) }}{{ '☆'.repeat(5 - Math.floor(review.rating))
              }}</span>
            <span class="rating-text">({{ review.rating }}/5)</span>
          </div>
          <div class="review-text">
            {{ review.content }}
          </div>
          <div class="review-stats">
            <span class="like-count">👍 {{ review.likeCount }} likes</span>
          </div>
        </div>

        <div class="review-actions">
          <button v-if="review.status === 'pending'" @click="approveReview(review.id)" class="action-btn approve-btn"
            :disabled="updating">
            ✅ Approve
          </button>
          <button v-if="review.status === 'pending'" @click="rejectReview(review.id)" class="action-btn reject-btn"
            :disabled="updating">
            ❌ Reject
          </button>
          <button @click="deleteReview(review.id)" class="action-btn delete-btn" :disabled="deleting">
            ❌ Reject
          </button>
          <button @click="viewDetails(review)" class="action-btn details-btn">
            👁️ Details
          </button>
          <button @click="viewComments(review.id)" class="action-btn comments-btn">
            💬 Comments
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !error && reviews.length === 0" class="empty-state">
      <div class="empty-icon">📝</div>
      <p>No reviews found matching your criteria.</p>
      <button @click="clearFilters" class="clear-filters-btn">Clear Filters</button>
    </div>

    <!-- Pagination -->
    <div v-if="pagination && pagination.pages > 1" class="pagination">
      <button @click="goToPage(pagination.current_page - 1)" :disabled="!pagination.has_prev" class="pagination-btn">
        ← Previous
      </button>
      <span class="pagination-info">
        Page {{ pagination.current_page }} of {{ pagination.pages }}
        ({{ pagination.total }} total reviews)
      </span>
      <button @click="goToPage(pagination.current_page + 1)" :disabled="!pagination.has_next" class="pagination-btn">
        Next →
      </button>
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
            <strong>Review ID:</strong> {{ selectedReview.id }}
          </div>
          <div class="detail-row">
            <strong>User ID:</strong> {{ selectedReview.userId }}
          </div>
          <div class="detail-row">
            <strong>Book ID:</strong> {{ selectedReview.bookId }}
          </div>
          <div class="detail-row">
            <strong>Rating:</strong> {{ selectedReview.rating }}/5 stars
          </div>
          <div class="detail-row">
            <strong>Status:</strong>
            <span :class="['status-badge', selectedReview.status]">{{ selectedReview.status.toUpperCase() }}</span>
          </div>
          <div class="detail-row">
            <strong>Posted:</strong> {{ formatDate(selectedReview.postTime) }}
          </div>
          <div class="detail-row">
            <strong>Likes:</strong> {{ selectedReview.likeCount }}
          </div>
          <div class="detail-row">
            <strong>Review Content:</strong>
            <div class="review-content-full">{{ selectedReview.content }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Comments Modal -->
    <div v-if="showCommentsModal" class="modal-overlay" @click="closeCommentsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Comments for Review</h3>
          <button class="close-button" @click="closeCommentsModal">×</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingComments" class="loading-container">
            <div class="loading-spinner"></div>
            <p>Loading comments...</p>
          </div>

          <div v-if="comments.length === 0 && !loadingComments" class="no-comments">
            <p>No comments found for this review.</p>
          </div>

          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <strong>{{ comment.userId }}</strong>
              <span class="comment-time">{{ formatDate(comment.commentTime) }}</span>
            </div>
            <div class="comment-content">{{ comment.content }}</div>
            <div class="comment-stats">
              <span class="like-count">👍 {{ comment.likeCount }} likes</span>
              <button @click="deleteComment(comment.id)" class="delete-comment-btn">🗑️</button>
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
const reviews = ref([])
const comments = ref([])
const pagination = ref(null)
const loading = ref(false)
const loadingComments = ref(false)
const error = ref(null)

// Filter and search
const statusFilter = ref('all')
const searchKeyword = ref('')
const currentPage = ref(1)
const perPage = ref(10)

// Modal states
const showDetailsModal = ref(false)
const showCommentsModal = ref(false)
const selectedReview = ref(null)
const selectedReviewId = ref(null)

// Loading states
const updating = ref(false)
const deleting = ref(false)

// Search debounce
let searchTimeout = null

// API Base URL
const API_BASE = '/service-c/api/admin'

// Fetch reviews from API
const fetchReviews = async (page = 1) => {
  loading.value = true
  error.value = null

  try {
    const params = {
      page: page,
      per_page: perPage.value
    }

    if (statusFilter.value !== 'all') {
      params.status = statusFilter.value
    }

    if (searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim()
    }

    const response = await axios.get(`${API_BASE}/reviews`, { params })

    reviews.value = response.data.reviews || []
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
    console.error('Error fetching reviews:', err)
    error.value = err.response?.data?.error || 'Failed to fetch reviews'
  } finally {
    loading.value = false
  }
}

// Fetch comments for a review
const fetchComments = async (reviewId) => {
  loadingComments.value = true

  try {
    const response = await axios.get(`${API_BASE}/reviews/${reviewId}/comments`)
    comments.value = response.data.comments || []
  } catch (err) {
    console.error('Error fetching comments:', err)
    comments.value = []
  } finally {
    loadingComments.value = false
  }
}

// Approve review
const approveReview = async (reviewId) => {
  if (updating.value) return

  updating.value = true

  try {
    await axios.put(`${API_BASE}/reviews/${reviewId}/status`, { status: 'approved' })

    // Update local data
    const index = reviews.value.findIndex(r => r.id === reviewId)
    if (index !== -1) {
      reviews.value[index].status = 'approved'
    }

    alert('Review approved successfully!')

  } catch (err) {
    console.error('Error approving review:', err)
    alert(err.response?.data?.error || 'Failed to approve review')
  } finally {
    updating.value = false
  }
}

// Reject review
const rejectReview = async (reviewId) => {
  if (updating.value) return

  updating.value = true

  try {
    await axios.put(`${API_BASE}/reviews/${reviewId}/status`, { status: 'rejected' })

    // Update local data
    const index = reviews.value.findIndex(r => r.id === reviewId)
    if (index !== -1) {
      reviews.value[index].status = 'rejected'
    }

    alert('Review rejected successfully!')

  } catch (err) {
    console.error('Error rejecting review:', err)
    alert(err.response?.data?.error || 'Failed to reject review')
  } finally {
    updating.value = false
  }
}

// Delete review
const deleteReview = async (reviewId) => {
  if (!confirm('Are you sure you want to delete this review? This action cannot be undone.')) {
    return
  }

  if (deleting.value) return

  deleting.value = true

  try {
    await axios.delete(`${API_BASE}/reviews/${reviewId}`)

    // Remove from local data
    reviews.value = reviews.value.filter(r => r.id !== reviewId)

    alert('Review deleted successfully!')

  } catch (err) {
    console.error('Error deleting review:', err)
    alert(err.response?.data?.error || 'Failed to delete review')
  } finally {
    deleting.value = false
  }
}

// Delete comment
const deleteComment = async (commentId) => {
  if (!confirm('Are you sure you want to delete this comment?')) {
    return
  }

  try {
    await axios.delete(`${API_BASE}/comments/${commentId}`)

    // Remove from local data
    comments.value = comments.value.filter(c => c.id !== commentId)

    alert('Comment deleted successfully!')

  } catch (err) {
    console.error('Error deleting comment:', err)
    alert(err.response?.data?.error || 'Failed to delete comment')
  }
}

// View review details
const viewDetails = (review) => {
  selectedReview.value = review
  showDetailsModal.value = true
}

// View comments
const viewComments = async (reviewId) => {
  selectedReviewId.value = reviewId
  showCommentsModal.value = true
  await fetchComments(reviewId)
}

// Pagination
const goToPage = (page) => {
  if (page >= 1 && page <= pagination.value.pages) {
    fetchReviews(page)
  }
}

// Modal controls
const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedReview.value = null
}

const closeCommentsModal = () => {
  showCommentsModal.value = false
  selectedReviewId.value = null
  comments.value = []
}

// Utility functions
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchReviews(1)
  }, 500)
}

const clearFilters = () => {
  statusFilter.value = 'all'
  searchKeyword.value = ''
  currentPage.value = 1
  fetchReviews(1)
}

// Initialize
onMounted(() => {
  fetchReviews()
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
  min-width: 150px;
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

.reviews-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
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
  margin-bottom: 8px;
}

.review-stats {
  color: #6c757d;
  font-size: 0.9em;
}

.like-count {
  display: inline-flex;
  align-items: center;
  gap: 4px;
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

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.approve-btn {
  background-color: #d4edda;
  color: #155724;
}

.approve-btn:hover:not(:disabled) {
  background-color: #c3e6cb;
}

.reject-btn {
  background-color: #f8d7da;
  color: #721c24;
}

.reject-btn:hover:not(:disabled) {
  background-color: #f5c6cb;
}

.delete-btn {
  background-color: #f8d7da;
  color: #721c24;
}

.delete-btn:hover:not(:disabled) {
  background-color: #f5c6cb;
}

.details-btn {
  background-color: #e2e3e5;
  color: #383d41;
}

.details-btn:hover {
  background-color: #d6d8db;
}

.comments-btn {
  background-color: #cff4fc;
  color: #055160;
}

.comments-btn:hover {
  background-color: #b6effb;
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

.comment-item {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  background-color: #f8f9fa;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-time {
  color: #7f8c8d;
  font-size: 0.9em;
}

.comment-content {
  color: #2c3e50;
  line-height: 1.5;
  margin-bottom: 8px;
}

.comment-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.delete-comment-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.delete-comment-btn:hover {
  background-color: #f8d7da;
}

.no-comments {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    min-width: auto;
  }

  .review-actions {
    justify-content: center;
  }
}
</style>
