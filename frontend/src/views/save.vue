<template>
  <div class="scholar-sanctum-container">
    <!-- 美化后的左侧导航栏 -->
    <aside class="sanctum-navigation">
      <div class="navigation-header">
        <div class="scholar-emblem">
          <img :src="user.avatar_url || '/placeholder.svg?height=120&width=120'" :alt="user.nickname" class="emblem-portrait" />
          <div class="user-info">
            <h4 class="user-name">{{ user.nickname }}</h4>
            <p class="user-status">Online</p>
          </div>
        </div>
      </div>

      <nav class="navigation-scroll">
        <div class="nav-section-unified">
          <ul class="nav-menu-enhanced">
            <li class="nav-item-enhanced" :class="{ active: activeSection === 'overview' }">
              <a href="#" @click.prevent="setActiveSection('overview')" class="nav-link-enhanced">
                <div class="nav-icon-wrapper">
                  <i class="fas fa-home"></i>
                </div>
                <span class="nav-text">Home Page</span>
                <div class="nav-indicator"></div>
              </a>
            </li>
            
            <li class="nav-item-enhanced" :class="{ active: activeSection === 'library' }">
              <a href="#" @click.prevent="setActiveSection('library')" class="nav-link-enhanced">
                <div class="nav-icon-wrapper">
                  <i class="fas fa-books"></i>
                </div>
                <span class="nav-text">Personal Library</span>
                <div class="nav-indicator"></div>
              </a>
            </li>
            
            <li class="nav-item-enhanced" :class="{ active: activeSection === 'reviews' }">
              <a href="#" @click.prevent="setActiveSection('reviews')" class="nav-link-enhanced">
                <div class="nav-icon-wrapper">
                  <i class="fas fa-pen-fancy"></i>
                </div>
                <span class="nav-text">My Critiques</span>
                <div class="nav-indicator"></div>
              </a>
            </li>
            
            <li class="nav-item-enhanced" :class="{ active: activeSection === 'notifications' }">
              <a href="#" @click.prevent="setActiveSection('notifications')" class="nav-link-enhanced">
                <div class="nav-icon-wrapper">
                  <i class="fas fa-bell"></i>
                  <span class="notification-badge" v-if="unreadNotifications > 0">{{ unreadNotifications }}</span>
                </div>
                <span class="nav-text">Notifications</span>
                <div class="nav-indicator"></div>
              </a>
            </li>
            
            <li class="nav-item-enhanced" :class="{ active: activeSection === 'edit' }">
              <a href="#" @click.prevent="setActiveSection('edit')" class="nav-link-enhanced">
                <div class="nav-icon-wrapper">
                  <i class="fas fa-user-edit"></i>
                </div>
                <span class="nav-text">Edit Info</span>
                <div class="nav-indicator"></div>
              </a>
            </li>
          </ul>
        </div>
      </nav>

      <div class="navigation-footer">
        <button class="logout-btn-enhanced" @click="logout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Sign Out</span>
        </button>
      </div>
    </aside>

    <!-- 主要内容区域 -->
    <main class="sanctum-content">
      <!-- 页面标题区域 -->
      <header class="sanctum-header">
        <div class="header-content">
          <h1 class="sanctum-title">{{ getSectionTitle() }}</h1>
          <p class="sanctum-subtitle">{{ getSectionSubtitle() }}</p>
        </div>
      </header>

      <!-- 动态内容区域 -->
      <div class="content-sections">
        <!-- Home Page -->
        <section v-show="activeSection === 'overview'" class="content-section">
          <!-- 阅读统计 -->
          <div class="reading-chronicles">
            <div class="chronicle-header">
              <h3 class="chronicle-title">Literary Accomplishments & Endeavours</h3>
            </div>
            <div class="chronicle-grid">
              <div class="chronicle-card">
                <div class="card-illumination">
                  <i class="fas fa-book-open"></i>
                </div>
                <div class="card-inscription">
                  <h4>Current Literary Pursuit</h4>
                  <p class="current-book" v-if="currentReading">{{ currentReading.title }}</p>
                  <p class="no-current" v-else>No tome currently under scrutiny</p>
                  <div class="progress-scroll" v-if="currentReading">
                    <div class="progress-bar">
                      <div class="progress-fill" :style="{ width: currentReading.progress + '%' }"></div>
                    </div>
                    <span class="progress-text">{{ currentReading.progress }}% Complete</span>
                  </div>
                </div>
              </div>

              <div class="chronicle-card">
                <div class="card-illumination">
                  <i class="fas fa-chart-line"></i>
                </div>
                <div class="card-inscription">
                  <h4>Monthly Reading Velocity</h4>
                  <div class="progress-scroll">
                    <div class="progress-bar">
                      <div class="progress-fill" :style="{ width: (2 / 5 * 100) + '%' }"></div>
                    </div>
                    <span class="progress-text">10% of Monthly Quest</span>
                  </div>
                </div>
              </div>

              <div class="chronicle-card">
                <div class="card-illumination">
                  <i class="fas fa-star"></i>
                </div>
                <div class="card-inscription">
                  <h4>Preferred Literary Domains</h4>
                  <div class="genre-seals">
                    <!-- 模拟数据 -->
                    <span v-for="genre in ['philosophy']" :key="genre" class="genre-seal">{{ genre }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 最近活动 -->
          <div class="recent-activities">
            <div class="activity-header">
              <h3 class="activity-title">Recent Critiques</h3>
            </div>
            <div class="activity-scroll">
              <div v-for="review in recentCritiques" :key="review.id" class="activity-entry">
                <div class="activity-icon">
                  <i class="fas fa-pen-fancy"></i>
                </div>
                <div class="activity-details">
                  <p class="activity-description">
                    <strong>{{ review.book?.title || 'Book' }}</strong>:
                    {{ review.title || (review.content ? review.content.slice(0, 40) + '...' : '') }}
                  </p>
                  <span class="activity-timestamp">{{ formatDate(review.date) }}</span>
                </div>
              </div>
              <div v-if="recentCritiques.length === 0" class="empty-state">
                <span>No recent critiques found.</span>
              </div>
            </div>

            <!-- 最近添加的收藏 -->
            <div class="activity-header" style="margin-top: 2rem;">
              <h3 class="activity-title">Recent Added Collections</h3>
            </div>
            <div class="recent-collections">
              <div v-for="book in recentCollections" :key="book.id" class="collection-book">
                <div class="book-cover-container">
                  <img :src="book.cover_img" :alt="book.title" class="collection-cover" />
                  <div class="book-overlay">
                    <button class="view-book-btn" @click="viewBook(book.id)">
                      <i class="fas fa-eye"></i>
                    </button>
                  </div>
                </div>
                <div class="book-info-compact">
                  <h4 class="book-title-compact">{{ book.title }}</h4>
                  <p class="book-author-compact">{{ book.author }}</p>
                  <div class="book-rating">
                    <span class="stars">{{ '★'.repeat(Math.round(book.rating || book.myRating || 0)) }}{{ '☆'.repeat(5 - Math.round(book.rating || book.myRating || 0)) }}</span>
                    <span class="rating-text">{{ (book.rating || book.myRating || 0).toFixed(1) }}</span>
                  </div>
                  <span class="added-date">Added {{ formatDate(book.add_time) }}</span>
                </div>
              </div>
              <div v-if="recentCollections.length === 0" class="empty-state">
                <span>No recent collections found.</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Enhanced Personal Library 页面 -->
        <section v-show="activeSection === 'library'" class="content-section">
          <div class="library-content-enhanced">
            <!-- 美化的头部区域 -->
            <div class="library-header-enhanced">
              <div class="library-title-section">
                <h3 class="section-title-enhanced">
                  <i class="fas fa-book-reader"></i>
                  Personal Literary Collection
                </h3>
                <p class="section-description">Curate and explore your literary treasures</p>
              </div>
              
              <div class="library-controls-enhanced">
                <div class="search-box">
                  <i class="fas fa-search"></i>
                  <input type="text" v-model="searchQuery" placeholder="Search your collection..." class="search-input" />
                </div>
                
                <div class="filter-controls">
                  <select v-model="libraryFilter" class="filter-select-enhanced">
                    <option value="all">All Books</option>
                    <option value="reading">Currently Reading</option>
                    <option value="completed">Completed</option>
                  </select>
                  
                  <select v-model="sortBy" class="filter-select-enhanced">
                    <option value="title">Sort by Title</option>
                    <option value="author">Sort by Author</option>
                    <option value="date">Sort by Date Added</option>
                    <option value="rating">Sort by Rating</option>
                  </select>
                </div>
                
                <div class="view-toggle-enhanced">
                  <button :class="{ active: libraryView === 'grid' }" @click="libraryView = 'grid'" class="view-btn">
                    <i class="fas fa-th"></i>
                    <span>Grid</span>
                  </button>
                  <button :class="{ active: libraryView === 'list' }" @click="libraryView = 'list'" class="view-btn">
                    <i class="fas fa-list"></i>
                    <span>List</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- 美化的统计区域 -->
            <div class="library-stats-enhanced">
              <div class="stat-card-enhanced">
                <div class="stat-icon-wrapper">
                  <i class="fas fa-books"></i>
                </div>
                <div class="stat-info">
                  <span class="stat-value-enhanced">{{ libraryBooks.length }}</span>
                  <span class="stat-name-enhanced">Total Books</span>
                </div>
              </div>
              
              <div class="stat-card-enhanced">
                <div class="stat-icon-wrapper completed">
                  <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-info">
                  <span class="stat-value-enhanced">{{ libraryBooks.filter(b => b.status === 'completed').length }}</span>
                  <span class="stat-name-enhanced">Completed</span>
                </div>
              </div>
              
              <div class="stat-card-enhanced">
                <div class="stat-icon-wrapper reading">
                  <i class="fas fa-book-open"></i>
                </div>
                <div class="stat-info">
                  <span class="stat-value-enhanced">{{ libraryBooks.filter(b => b.status === 'reading').length }}</span>
                  <span class="stat-name-enhanced">Currently Reading</span>
                </div>
              </div>
              
              <div class="stat-card-enhanced">
                <div class="stat-icon-wrapper average">
                  <i class="fas fa-star"></i>
                </div>
                <div class="stat-info">
                  <span class="stat-value-enhanced">{{ averageBookRating.toFixed(1) }}</span>
                  <span class="stat-name-enhanced">Avg Rating</span>
                </div>
              </div>
            </div>

            <!-- 书籍展示区域 -->
            <div :class="['library-books-enhanced', libraryView]">
              <div v-for="book in filteredAndSortedBooks" :key="book.id" class="library-book-card">
                <div class="book-cover-area">
                  <div class="book-cover-wrapper">
                    <img :src="book.cover_img" :alt="book.title" class="book-cover-fixed" />
                    <div class="book-overlay-enhanced">
                      <button class="quick-action-btn" @click="viewBook(book.id)" title="View Details">
                        <i class="fas fa-eye"></i>
                      </button>
                      <button class="quick-action-btn" @click="editBook(book.id)" title="Edit Book">
                        <i class="fas fa-edit"></i>
                      </button>
                    </div>
                  </div>
                  <div class="book-status-indicator" :class="book.status">
                    <i :class="getStatusIcon(book.status)"></i>
                    <span>{{ getStatusText(book.status) }}</span>
                  </div>
                </div>

                <!-- 书籍信息区域 -->
                <div class="book-info-area">
                  <div class="book-header">
                    <h4 class="book-title-fixed">{{ book.title }}</h4>
                    <p class="book-author-fixed">by {{ book.author }}</p>
                  </div>
                  
                  <div class="book-metadata">
                    <div class="metadata-item">
                      <i class="fas fa-tag"></i>
                      <span>{{ book.genres?.join(', ') }}</span>
                    </div>
                    <div class="metadata-item">
                      <i class="fas fa-file-alt"></i>
                      <span>{{ book.pages }} pages</span>
                    </div>
                  </div>

                  <div class="book-rating-area">
                    <div class="rating-header">
                      <span class="rating-label">Your Rating</span>
                      <div class="rating-stars">
                        <span class="stars-display">{{ '★'.repeat(book.myRating) }}{{ '☆'.repeat(5 - book.myRating) }}</span>
                        <span class="rating-number">{{ book.myRating }}/5</span>
                      </div>
                    </div>
                    <span class="completion-date">Completed {{ formatDate(book.completedDate) }}</span>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="book-actions-enhanced">
                    <button class="action-btn-enhanced primary" @click="viewBook(book.id)">
                      <i class="fas fa-book-open"></i>
                      <span>View Details</span>
                    </button>
                    <button class="action-btn-enhanced secondary" @click="editBook(book.id)">
                      <i class="fas fa-edit"></i>
                      <span>Edit</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-if="filteredAndSortedBooks.length === 0" class="empty-state">
              <div class="empty-icon">
                <i class="fas fa-book"></i>
              </div>
              <h3 class="empty-title">No Books Found</h3>
              <p class="empty-description">
                {{ searchQuery ? 'Try adjusting your search terms or filters.' : 'Start building your literary collection by adding your first book.' }}
              </p>
              <button class="add-book-btn" @click="addNewBook">
                <i class="fas fa-plus"></i>
                Add Your First Book
              </button>
            </div>
          </div>
        </section>

        <!-- My Critiques 页面 -->
        <section v-show="activeSection === 'reviews'" class="content-section">
          <div class="reviews-content">
            <div class="reviews-header-section">
              <h3 class="section-title">My Literary Critiques</h3>
              <div class="reviews-stats">
                <div class="review-stat">
                  <span class="stat-number">{{ favoriteReviews.length }}</span>
                  <span class="stat-label">Total Reviews</span>
                </div>
                <div class="review-stat">
                  <span class="stat-number">{{ averageRating.toFixed(1) }}</span>
                  <span class="stat-label">Avg Rating</span>
                </div>
                <div class="review-stat">
                  <span class="stat-number">{{ favoriteReviews.filter(r => r.helpful > 10).length }}</span>
                  <span class="stat-label">Helpful Reviews</span>
                </div>
              </div>
            </div>

            <div class="reviews-list">
              <div v-for="review in favoriteReviews" :key="review.id" class="review-item">
                <div class="review-book-info">
                  <img :src="review.book.cover_img" :alt="review.book_title" class="review-book-cover" />
                  <div class="review-book-details">
                    <h4 class="review-book-title">{{ review.book_title }}</h4>
                    <p class="review-book-author">by {{ review.book_author }}</p>
                    <div class="review-rating">
                      <span class="stars-review">{{ '★'.repeat(review.rating) }}{{ '☆'.repeat(5 - review.rating) }}</span>
                      <span class="rating-value">{{ review.rating }}/5</span>
                    </div>
                  </div>
                </div>
                <div class="review-content">
                  <div class="review-header">
                    <h5 class="review-title">{{ review.title }}</h5>
                    <span class="review-date">{{ formatDate(review.add_time) }}</span>
                  </div>
                  <p class="review-text">{{ review.content }}</p>
                  <div class="review-footer">
                    <div class="review-engagement">
                      <span class="helpful-count">
                        <i class="fas fa-thumbs-up"></i>
                         helpful
                      </span>
                      <span class="comment-count">
                        <i class="fas fa-comment"></i>
                         comments
                      </span>
                    </div>
                    <div class="review-actions">
                      <button class="review-action-btn" @click="editReview(review.id)">
                        <i class="fas fa-edit"></i> Edit
                      </button>
                      <button class="review-action-btn" @click="deleteReview(review.id)">
                        <i class="fas fa-trash"></i> Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Notifications 页面 -->
        <section v-show="activeSection === 'notifications'" class="content-section">
          <div class="notifications-content">
            <div class="notifications-header">
              <h3 class="section-title">Scholarly Notifications</h3>
              <div class="notification-controls">
                <button class="control-btn" @click="markAllAsRead" :disabled="unreadNotifications === 0">
                  <i class="fas fa-check-double"></i>
                  Mark All Read
                </button>
                <select v-model="notificationFilter" class="filter-select">
                  <option value="all">All Notifications</option>
                  <option value="unread">Unread Only</option>
                  <option value="reviews">Reviews</option>
                  <option value="system">System</option>
                </select>
              </div>
            </div>

            <div class="notifications-stats">
              <div class="notification-stat">
                <span class="stat-number">{{ notifications.length }}</span>
                <span class="stat-label">Total</span>
              </div>
              <div class="notification-stat">
                <span class="stat-number">{{ unreadNotifications }}</span>
                <span class="stat-label">Unread</span>
              </div>
              <div class="notification-stat">
                <span class="stat-number">{{ notifications.filter(n => n.type === 'review').length }}</span>
                <span class="stat-label">Reviews</span>
              </div>
            </div>

            <div class="notifications-list">
              <div v-for="notification in filteredNotifications" :key="notification.id" 
                   class="notification-item" 
                   :class="{ unread: !notification.read, important: notification.priority === 'high' }">
                <div class="notification-icon" :class="notification.type">
                  <i :class="getNotificationIcon(notification.type)"></i>
                </div>
                <div class="notification-content">
                  <div class="notification-header">
                    <h4 class="notification-title">{{ notification.title }}</h4>
                    <span class="notification-time">{{ formatTimeAgo(notification.timestamp) }}</span>
                  </div>
                  <p class="notification-message">{{ notification.message }}</p>
                  <div class="notification-actions" v-if="!notification.read">
                    <button class="notification-action-btn primary" @click="markAsRead(notification.id)">
                      Mark as Read
                    </button>
                    <button class="notification-action-btn secondary" @click="dismissNotification(notification.id)">
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Edit Info 页面 -->
        <section v-show="activeSection === 'edit'" class="content-section">
          <div class="edit-content">
            <div class="edit-header">
              <h3 class="section-title">Edit Personal Information</h3>
              <p class="edit-subtitle">Update your profile details and literary preferences</p>
            </div>

            <div class="edit-form-container">
              <form @submit.prevent="saveProfile" class="edit-form">
                <!-- 基本信息 -->
                <div class="form-section">
                  <h4 class="form-section-title">
                    <i class="fas fa-user"></i>
                    Basic Information
                  </h4>
                  <div class="form-grid">
                    <div class="form-group">
                      <label for="username" class="form-label">Username</label>
                      <input type="text" id="username" v-model="editForm.username" class="form-input" />
                    </div>
                    <div class="form-group">
                      <label for="email" class="form-label">Email Address</label>
                      <input type="email" id="email" v-model="editForm.email" class="form-input" />
                    </div>
                    <div class="form-group">
                      <label for="title" class="form-label">Literary Title</label>
                      <input type="text" id="title" v-model="editForm.title" class="form-input" 
                             placeholder="e.g., Master of Ancient Texts" />
                    </div>
                    <div class="form-group">
                      <label for="location" class="form-label">Location</label>
                      <input type="text" id="location" v-model="editForm.location" class="form-input" 
                             placeholder="Your literary sanctuary" />
                    </div>
                    <div class="form-group">
                      <label for="avatar" class="form-label">Avatar</label>
                      <input type="file" @change="handleAvatarChange" accept="image/*" />
                      <button id="select avatar" class="form-label" @click="uploadAvatar">上传头像</button>
                    </div>
                  </div>
                </div>

                <!-- 个人简介 -->
                <div class="form-section">
                  <h4 class="form-section-title">
                    <i class="fas fa-scroll"></i>
                    Literary Biography
                  </h4>
                  <div class="form-group">
                    <label for="bio" class="form-label">About Yourself</label>
                    <textarea id="bio" v-model="editForm.bio" class="form-textarea" rows="4"
                              placeholder="Share your literary journey and interests..."></textarea>
                  </div>
                </div>

                <!-- 阅读偏好 -->
                <div class="form-section">
                  <h4 class="form-section-title">
                    <i class="fas fa-book-open"></i>
                    Reading Preferences
                  </h4>
                  <div class="form-grid">
                    <div class="form-group">
                      <label for="monthlyGoal" class="form-label">Monthly Reading Goal</label>
                      <input type="number" id="monthlyGoal" v-model="editForm.monthlyGoal" 
                             class="form-input" min="1" max="50" />
                    </div>
                    <div class="form-group">
                      <label for="favoriteGenre" class="form-label">Favorite Genre</label>
                      <select id="favoriteGenre" v-model="editForm.favoriteGenre" class="form-select">
                        <option value="">Select a genre</option>
                        <option value="Philosophy">Philosophy</option>
                        <option value="Historical Fiction">Historical Fiction</option>
                        <option value="Poetry">Poetry</option>
                        <option value="Science">Science</option>
                        <option value="Biography">Biography</option>
                        <option value="Mystery">Mystery</option>
                        <option value="Romance">Romance</option>
                        <option value="Fantasy">Fantasy</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Preferred Literary Domains</label>
                    <div class="genre-checkboxes">
                      <label v-for="genre in availableGenres" :key="genre" class="checkbox-label">
                        <input type="checkbox" :value="genre" v-model="editForm.favoriteGenres" class="checkbox-input" />
                        <span class="checkbox-custom"></span>
                        {{ genre }}
                      </label>
                    </div>
                  </div>
                </div>

                <!-- 隐私设置 -->
                <div class="form-section">
                  <h4 class="form-section-title">
                    <i class="fas fa-shield-alt"></i>
                    Privacy & Visibility
                  </h4>
                  <div class="privacy-options">
                    <label class="privacy-option">
                      <input type="checkbox" v-model="editForm.profilePublic" class="checkbox-input" />
                      <span class="checkbox-custom"></span>
                      <div class="privacy-info">
                        <span class="privacy-title">Public Profile</span>
                        <span class="privacy-desc">Allow others to view your reading activity</span>
                      </div>
                    </label>
                    <label class="privacy-option">
                      <input type="checkbox" v-model="editForm.showReadingProgress" class="checkbox-input" />
                      <span class="checkbox-custom"></span>
                      <div class="privacy-info">
                        <span class="privacy-title">Show Reading Progress</span>
                        <span class="privacy-desc">Display your current reading progress to others</span>
                      </div>
                    </label>
                    <label class="privacy-option">
                      <input type="checkbox" v-model="editForm.allowRecommendations" class="checkbox-input" />
                      <span class="checkbox-custom"></span>
                      <div class="privacy-info">
                        <span class="privacy-title">Receive Recommendations</span>
                        <span class="privacy-desc">Get personalized book recommendations</span>
                      </div>
                    </label>
                  </div>
                </div>

                <!-- 表单按钮 -->
                <div class="form-actions">
                  <button type="button" @click="resetForm" class="form-btn secondary">
                    <i class="fas fa-undo"></i>
                    Reset Changes
                  </button>
                  <button type="submit" class="form-btn primary">
                    <i class="fas fa-save"></i>
                    Save Profile
                  </button>
                </div>
              </form>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// 当前激活的页面部分
const activeSection = ref('overview')
const libraryFilter = ref('all')
const libraryView = ref('grid')
const notificationFilter = ref('all')
const searchQuery = ref('')
const sortBy = ref('title')
const libraryBooks = ref([])
const favoriteReviews = ref([])
const user = ref({
  user_id: '',
  nickname: '',
  avatar_url: '',
  email: ''
})

// 用户资料获取
const fetchUserProfile = async () => {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    console.error('User ID not found in localStorage. Redirecting to login.');
    this.$router.push('/login');
    return;
  }
  try {
    const res = await axios.get(`/service-a/api/users/${userId}`)
    user.value = res.data
  } catch (error) {
      console.error('Error fetching user data:', error);
      // 如果用户信息获取失败，可能是用户未登录或会话过期，可以提示并重定向
      alert('获取用户信息失败，请重新登录。');
      this.$router.push('/login');
  }
}

const fetchFavoriteBooks = async () => {
  const userId = localStorage.getItem('user_id')
  if (!userId) return
  try {
    // 获取收藏的 bookId 列表
    const bookIdsRes = await axios.get(`/service-c/api/books/favorite_books`, { params: { userId } })
    const bookIds = bookIdsRes.data
    if (bookIds.length > 0) {
      // 批量获取图书详情
      const booksRes = await axios.get(`/service-b/api/books/batch`,{
        params: {
            ids: bookIds.join(',') // 拼接成逗号分隔的字符串
          }
        });
      libraryBooks.value = booksRes.data
    } else {
      libraryBooks.value = []
    }
  } catch (e) {
    libraryBooks.value = []
  }
}

const fetchFavoriteReviews = async () => {
  const userId = localStorage.getItem('user_id')
  if (!userId) return
  try {
    // 获取收藏的 reviewId 列表
    const reviewIdsRes = await axios.get(`/service-c/api/reviews/favorite_reviews`, { params: { userId } })
    const reviewIds = reviewIdsRes.data
    if (reviewIds.length > 0) {
      // 批量获取书评详情
      const reviewsDetailResponse = await axios.get(`/service-c/api/reviews/batch`, { // service-c 有批量获取接口
        params: {
          ids: reviewIds.join(',')
        }
      });
      favoriteReviews.value = await Promise.all(reviewsDetailResponse.data.map(async review => {
            let reviewerNickname = '未知用户';
            let reviewerAvatarUrl = 'https://via.placeholder.com/50';
            try {
              const userProfile = await axios.get(`/service-a/api/users/${review.userId}`);
              reviewerNickname = userProfile.data.nickname || '匿名用户';
              reviewerAvatarUrl = userProfile.data.avatar_url || 'https://via.placeholder.com/50';
            } catch (userError) {
              console.warn(`Could not fetch user info for review userId ${review.userId}:`, userError);
            }
            // 如果你的后端 Review 表里没有 likeCount 和 collectCount，这里需要从 engagement service 再次查询
            // 如果你的 review_engagement.py 后端能返回这些，则不需要额外查询


            return {
              ...review,
              reviewerNickname,
              reviewerAvatarUrl,
              // 这里假设后端返回的 review 对象包含了 likeCount 和 collectCount，否则需要额外获取
            };
          }));
    } else {
      favoriteReviews.value = []
    }
  } catch (e) {
    favoriteReviews.value = []
  }
}

onMounted(() => {
  fetchFavoriteBooks()
  fetchFavoriteReviews()
  fetchUserProfile()
})

// mock模拟数据：未读通知数量
const unreadNotifications = ref(5)

// 编辑表单数据
const editForm = ref({
  username: 'user_name',
  email: 'user@example.com',
  title: 'Master of Ancient Texts',
  location: 'Literary Sanctuary',
  bio: 'A passionate reader exploring the depths of human knowledge through literature.',
  monthlyGoal: 4,
  favoriteGenre: 'Philosophy',
  favoriteGenres: ['Philosophy', 'Historical Fiction', 'Poetry', 'Science'],
  profilePublic: true,
  showReadingProgress: true,
  allowRecommendations: true
})

// mock 模拟数据：可选择的文学类型
const availableGenres = ref([
  'Philosophy', 'Historical Fiction', 'Poetry', 'Science', 'Biography', 
  'Mystery', 'Romance', 'Fantasy', 'Thriller', 'Non-fiction'
])

// 当前阅读
const currentReading = ref({
  title: 'The Meditations of Marcus Aurelius',
  progress: 67
})


// mock 模拟数据：通知数据
const notifications = ref([
  {
    id: 1,
    type: 'review',
    title: 'New Review Response',
    message: 'Scholar_Jane responded to your review of "The Art of War"',
    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
    read: false,
    priority: 'normal'
  },
  {
    id: 2,
    type: 'system',
    title: 'Reading Goal Achievement',
    message: 'Congratulations! You\'ve reached 75% of your monthly reading goal.',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
    read: false,
    priority: 'high'
  },
  {
    id: 3,
    type: 'recommendation',
    title: 'New Book Recommendation',
    message: 'Based on your reading history, we recommend "Meditations" by Marcus Aurelius',
    timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000),
    read: false,
    priority: 'normal'
  },
  {
    id: 4,
    type: 'social',
    title: 'New Follower',
    message: 'BookLover_Alex started following your literary journey',
    timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    read: true,
    priority: 'normal'
  },
  {
    id: 5,
    type: 'review',
    title: 'Review Liked',
    message: 'Your review of "Sapiens" received 5 new likes',
    timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    read: false,
    priority: 'normal'
  },
])

const recentCritiques = computed(() => {
  return [...favoriteReviews.value]
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5)
})

// 只显示最近收藏的5本书籍（按添加时间倒序）
const recentCollections = computed(() => {
  return [...libraryBooks.value]
    .sort((a, b) => new Date(b.addedDate) - new Date(a.addedDate))
    .slice(0, 5)
})

// 计算属性
const filteredLibraryBooks = computed(() => {
  let filtered = libraryBooks.value
  
  // 按状态筛选
  if (libraryFilter.value !== 'all') {
    filtered = filtered.filter(book => book.status === libraryFilter.value)
  }
  
  // 按搜索查询筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(book => 
      book.title.toLowerCase().includes(query) ||
      book.author.toLowerCase().includes(query) ||
      book.genre.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

const filteredAndSortedBooks = computed(() => {
  let books = [...libraryBooks.value]
  
  // 排序
  switch (sortBy.value) {
    case 'title':
      books.sort((a, b) => a.title.localeCompare(b.title))
      break
    case 'author':
      books.sort((a, b) => a.author.localeCompare(b.author))
      break
    case 'date':
      books.sort((a, b) => new Date(b.adde_time) - new Date(a.add_time))
      break
    case 'rating':
      books.sort((a, b) => (b.myRating || 0) - (a.myRating || 0))
      break
  }
  
  return books
})

const averageRating = computed(() => {
  const total = favoriteReviews.value.reduce((sum, review) => sum + review.rating, 0)
  return total / favoriteReviews.value.length || 0
})

const averageBookRating = computed(() => {
  const ratedBooks = libraryBooks.value.filter(book => book.myRating)
  const total = ratedBooks.reduce((sum, book) => sum + book.myRating, 0)
  return total / ratedBooks.length || 0
})

const filteredNotifications = computed(() => {
  let filtered = notifications.value
  
  if (notificationFilter.value === 'unread') {
    filtered = filtered.filter(n => !n.read)
  } else if (notificationFilter.value !== 'all') {
    filtered = filtered.filter(n => n.type === notificationFilter.value)
  }
  
  return filtered.sort((a, b) => b.timestamp - a.timestamp)
})

// 页面标题映射
const sectionTitles = {
  overview: 'The Scholar\'s Personal Sanctum',
  library: 'Personal Literary Collection',
  reviews: 'Scholarly Critiques & Commentary',
  notifications: 'Scholarly Notifications & Updates',
  edit: 'Edit Personal Chronicle'
}

const sectionSubtitles = {
  overview: 'Your Literary Journey & Scholarly Pursuits',
  library: 'Curate & Organize Your Personal Collection',
  reviews: 'Your Contributions to Literary Discourse',
  notifications: 'Stay Updated with Your Literary Community',
  edit: 'Manage Your Profile & Preferences'
}

// 方法
const setActiveSection = (section) => {
  activeSection.value = section
}

const getSectionTitle = () => {
  return sectionTitles[activeSection.value] || 'The Scholar\'s Personal Sanctum'
}

const getSectionSubtitle = () => {
  return sectionSubtitles[activeSection.value] || 'Your Literary Journey & Scholarly Pursuits'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const formatTimeAgo = (timestamp) => {
  const now = new Date()
  const diff = now - timestamp
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days > 0) {
    return `${days} day${days > 1 ? 's' : ''} ago`
  } else if (hours > 0) {
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  } else {
    return 'Just now'
  }
}

const getActivityIcon = (type) => {
  const icons = {
    review: 'fas fa-pen-fancy',
    finish: 'fas fa-check-circle',
    start: 'fas fa-book-open'
  }
  return icons[type] || 'fas fa-bookmark'
}

const getNotificationIcon = (type) => {
  const icons = {
    review: 'fas fa-comment',
    system: 'fas fa-cog',
    recommendation: 'fas fa-lightbulb',
    social: 'fas fa-users'
  }
  return icons[type] || 'fas fa-bell'
}

const getStatusIcon = (status) => {
  const icons = {
    reading: 'fas fa-book-open',
    completed: 'fas fa-check-circle'
  }
  return icons[status] || 'fas fa-book'
}

const getStatusText = (status) => {
  const texts = {
    reading: 'Reading',
    completed: 'Completed'
  }
  return texts[status] || status
}

// 通知相关方法
const markAsRead = (notificationId) => {
  const notification = notifications.value.find(n => n.id === notificationId)
  if (notification) {
    notification.read = true
    unreadNotifications.value = Math.max(0, unreadNotifications.value - 1)
  }
}

const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
  unreadNotifications.value = 0
}

const dismissNotification = (notificationId) => {
  const index = notifications.value.findIndex(n => n.id === notificationId)
  if (index > -1) {
    const notification = notifications.value[index]
    if (!notification.read) {
      unreadNotifications.value = Math.max(0, unreadNotifications.value - 1)
    }
    notifications.value.splice(index, 1)
  }
}

// 编辑表单相关方法
const saveProfile = async () => {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    alert('用户未登录，请重新登录')
    return
  }
  try {
    await axios.put(`/service-a/api/users/${userId}/nickname`, {
      nickname: editForm.value.username
    })
    user.value.nickname = editForm.value.username
    alert('个人信息修改成功！')
  } catch (e) {
    alert('修改失败，请稍后重试')
  }
}

const uploadAvatar = async () => {
  if (!selectedAvatarFile.value) {
    alert('请选择一个头像文件。')
    return
  }
  try {
    const userId = localStorage.getItem('user_id')
    if (!userId) return
    const formData = new FormData()
    formData.append('avatar', selectedAvatarFile.value)
    const response = await axios.post(`/service-a/api/users/${userId}/avatar`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    user.value.avatar_url = response.data.avatar_url
    localStorage.setItem('user_avatar_url', user.value.avatar_url)
    selectedAvatarFile.value = null
    alert('头像上传成功！')
  } catch (error) {
    console.error('Error uploading avatar:', error)
    alert('头像上传失败。')
  }
}

const resetForm = () => {
  editForm.value = {
    username: user.value.nickname,
    email: 'user@example.com',
    title: user.value.title,
    location: 'Literary Sanctuary',
    bio: 'A passionate reader exploring the depths of human knowledge through literature.',
    monthlyGoal: userProfile.value.monthlyGoal,
    favoriteGenre: 'Philosophy',
    favoriteGenres: [...user.value.favoriteGenres],
    profilePublic: true,
    showReadingProgress: true,
    allowRecommendations: true
  }
}

// 事件处理
const openAvatarModal = () => {
  console.log('Open avatar modal')
}

const viewBook = (bookId) => {
  console.log('View book:', bookId)
}

const editBook = (bookId) => {
  console.log('Edit book:', bookId)
}

const editReview = (reviewId) => {
  console.log('Edit review:', reviewId)
}

const deleteReview = (reviewId) => {
  console.log('Delete review:', reviewId)
}

const addNewBook = () => {
  console.log('Add new book')
}

const logout = () => {
  console.log('Logout user')
}

console.log('Enhanced user center mounted')
</script>

<style scoped>
/* 基础样式保持不变 */
.scholar-sanctum-container {
  display: flex;
  min-height: 100vh;
  background-color: #fcf8f0;
  font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
  color: #3e2723;
}

/* 导航栏样式保持不变 */
.sanctum-navigation {
  width: 18%;
  background: linear-gradient(180deg, #fffaf0 0%, #f9f5eb 100%);
  border-right: 1px solid #e0d4c0;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  position: absolute;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
  margin-top: 30px;
}

.navigation-header {
  padding: 2.5rem 1.5rem;
  text-align: center;
  background: linear-gradient(135deg, #f0ebe0 0%, #e8dccf 100%);
  border-bottom: 2px solid #d4c7b2;
  position: relative;
}

.navigation-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="%23d4b896" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="%23d4b896" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="%23d4b896" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  opacity: 0.3;
}

.scholar-emblem {
  position: relative;
  z-index: 1;
}

.emblem-portrait {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #d4b896;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  margin-bottom: 1rem;
  transition: transform 0.3s ease;
}

.emblem-portrait:hover {
  transform: scale(1.05);
}

.user-info {
  text-align: center;
}

.user-name {
  font-size: 1.3em;
  color: #4e342e;
  margin: 0 0 0.3rem 0;
  font-weight: 700;
}

.user-status {
  font-size: 0.9em;
  color: #8d6e63;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.user-status::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #4caf50;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.navigation-scroll {
  flex-grow: 1;
  padding: 2rem 0;
}

.nav-section-unified {
  padding: 0 1rem;
}

.nav-menu-enhanced {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item-enhanced {
  position: relative;
}

.nav-link-enhanced {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  color: #5d4037;
  text-decoration: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.nav-link-enhanced::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(212, 184, 150, 0.2), transparent);
  transition: left 0.5s ease;
}

.nav-link-enhanced:hover::before {
  left: 100%;
}

.nav-link-enhanced:hover {
  background: linear-gradient(135deg, #f0ebe0 0%, #e8dccf 100%);
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.nav-item-enhanced.active .nav-link-enhanced {
  background: linear-gradient(135deg, #d4b896 0%, #c4a882 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(212, 184, 150, 0.4);
}

.nav-icon-wrapper {
  position: relative;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon-wrapper i {
  font-size: 1.2em;
  transition: transform 0.3s ease;
}

.nav-item-enhanced.active .nav-icon-wrapper i {
  transform: scale(1.1);
}

.notification-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: linear-gradient(135deg, #ff4757 0%, #ff3742 100%);
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 0.7em;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-3px); }
  60% { transform: translateY(-2px); }
}

.nav-text {
  font-size: 1em;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.nav-indicator {
  position: absolute;
  right: 1rem;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: #d4b896;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.nav-item-enhanced.active .nav-indicator {
  opacity: 1;
}

.navigation-footer {
  padding: 1.5rem;
  border-top: 2px solid #d4c7b2;
  background: linear-gradient(135deg, #f0ebe0 0%, #e8dccf 100%);
}

.logout-btn-enhanced {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #8d6e63 0%, #795548 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  font-family: inherit;
  font-size: 1em;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.logout-btn-enhanced:hover {
  background: linear-gradient(135deg, #5d4037 0%, #4e342e 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(93, 64, 55, 0.4);
}

/* 主要内容区域样式 */
.sanctum-content {
  flex-grow: 1;
  margin-left: 18%;
  padding: 2rem;
  max-width: calc(82% - 4rem);
}

.sanctum-header {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem 0;
  background: linear-gradient(135deg, #d4b896 0%, #ecd9c7 100%);
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.sanctum-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM2MDU0NDgiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0bC02LTMuMjctNiA2LjI3di0xMmMwLS41NS40NS0xIDEtMSAxIDAgLjgyLjM3IDEuMTguODhsMi43NiAyLjc2LTMuNjQtMy42NGEuOTk5Ljk5OSAwIDAgMCAwLTEuNDFMMzYgMzR6TTI4IDExbDE3LTE3YzEuMTgtMS4xOCAzLjI3LTEuMTggNC40NSAwIDEuMTguNDUuNzUgMS44MSAwIDIuNTlsLTYuMTIgNi4xMmEyNS40IDI1LjQgMCAwIDAgLjY3IDcuNjNsLTIuNjYtMi42NmMtLjE4LS4xOC0uNDItLjI4LS42Ny0uMjhINzguNWEyMCAyMCAwIDAgMCAyMCAyMHYyMGMwIDEuMTguODIgMiAxLjggMiAwIDAgLjgyLjM3IDEuMTguODhsMi43NiAyLjc2LTMuNjQtMy42NGEuOTk5Ljk5OSAwIDAgMCAwLTEuNDFMMzYgMzR6Ii8+PC9nPjwvZz48L3N2Z3U+');
  opacity: 0.1;
  background-repeat: repeat;
}

.header-content {
  position: relative;
  z-index: 1;
}

.sanctum-title {
  font-size: 2.8em;
  color: #5d4037;
  margin-bottom: 0.5rem;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.sanctum-subtitle {
  font-size: 1.2em;
  color: #6d4c41;
  opacity: 0.9;
  font-style: italic;
}

.content-sections {
  display: flex;
  flex-direction: column;
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #d4c7b2;
  border-radius: 6px;
  background-color: #ffffff;
  color: #4e342e;
  font-family: inherit;
}

/* 保持原有的其他样式 */
.profile-manuscript {
  background-color: #fffaf0;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0d4c0;
}

.manuscript-header {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.scholar-portrait {
  position: relative;
  flex-shrink: 0;
}

.portrait-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #d4b896;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.portrait-edit-quill {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background-color: #8d6e63;
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.portrait-edit-quill:hover {
  background-color: #5d4037;
  transform: scale(1.1);
}

.scholar-details {
  flex-grow: 1;
}

.scholar-name {
  font-size: 2.2em;
  color: #4e342e;
  margin-bottom: 0.3rem;
  font-weight: 600;
}

.scholar-title {
  font-size: 1.2em;
  color: #8d6e63;
  font-style: italic;
  margin-bottom: 0.5rem;
}

.scholar-joined {
  color: #795548;
  margin-bottom: 1.5rem;
}

.scholar-stats {
  display: flex;
  gap: 2rem;
}

.stat-scroll {
  text-align: center;
  padding: 1rem;
  background-color: #f0ebe0;
  border-radius: 8px;
  border: 1px solid #d4c7b2;
  min-width: 100px;
}

.stat-number {
  display: block;
  font-size: 2em;
  font-weight: 700;
  color: #5d4037;
}

.stat-label {
  font-size: 0.9em;
  color: #795548;
  font-style: italic;
}

/* Enhanced Personal Library 样式 */
.library-content-enhanced {
  background: linear-gradient(135deg, #fffaf0 0%, #f9f5eb 100%);
  border-radius: 16px;
  padding: 3rem;
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c0;
  position: relative;
  overflow: hidden;
}

.library-content-enhanced::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(212, 184, 150, 0.05) 0%, transparent 70%);
  transform: rotate(45deg);
}

.library-header-enhanced {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px dashed #d4c7b2;
  position: relative;
  z-index: 1;
  flex-wrap: wrap;
  gap: 2rem;
}

.library-title-section {
  flex: 1;
  min-width: 300px;
}

.section-title-enhanced {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 2.5em;
  color: #4e342e;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title-enhanced i {
  color: #8d6e63;
  font-size: 0.9em;
}

.section-description {
  color: #795548;
  font-size: 1.1em;
  font-style: italic;
  opacity: 0.9;
}

.library-controls-enhanced {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-width: 400px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box i {
  position: absolute;
  left: 1rem;
  color: #a1887f;
  font-size: 1.1em;
  z-index: 2;
}

.search-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid #e8dccf;
  border-radius: 25px;
  background-color: #ffffff;
  color: #4e342e;
  font-family: inherit;
  font-size: 1em;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-input:focus {
  outline: none;
  border-color: #8d6e63;
  box-shadow: 0 4px 15px rgba(141, 110, 99, 0.2);
  transform: translateY(-1px);
}

.filter-controls {
  display: flex;
  gap: 1rem;
}

.filter-select-enhanced {
  flex: 1;
  padding: 0.8rem 1.2rem;
  border: 2px solid #e8dccf;
  border-radius: 10px;
  background-color: #ffffff;
  color: #4e342e;
  font-family: inherit;
  font-size: 0.95em;
  transition: all 0.3s ease;
  cursor: pointer;
}

.filter-select-enhanced:focus {
  outline: none;
  border-color: #8d6e63;
  box-shadow: 0 0 0 3px rgba(141, 110, 99, 0.1);
}

.view-toggle-enhanced {
  width: 140px;
  display: flex;
  border: 2px solid #e8dccf;
  border-radius: 10px;
  overflow: hidden;
  background-color: #ffffff;
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1.2rem;
  border: none;
  background-color: transparent;
  color: #795548;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  font-size: 0.9em;
  font-weight: 500;
}

.view-btn:hover {
  background-color: #f9f5eb;
}

.view-btn.active {
  background: linear-gradient(135deg, #8d6e63 0%, #795548 100%);
  color: white;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.library-stats-enhanced {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}

.stat-card-enhanced {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.8rem;
  background: linear-gradient(135deg, #ffffff 0%, #fefdfb 100%);
  border-radius: 12px;
  border: 1px solid #efebe9;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card-enhanced::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #d4b896 0%, #8d6e63 100%);
}

.stat-card-enhanced:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
}

.stat-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d4b896 0%, #ecd9c7 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(212, 184, 150, 0.3);
}

.stat-icon-wrapper.completed {
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.stat-icon-wrapper.reading {
  background: linear-gradient(135deg, #ff9800 0%, #ffb74d 100%);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.stat-icon-wrapper.average {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.stat-icon-wrapper i {
  font-size: 1.5em;
  color: white;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value-enhanced {
  font-size: 2.2em;
  font-weight: 700;
  color: #4e342e;
  line-height: 1;
  margin-bottom: 0.2rem;
}

.stat-name-enhanced {
  font-size: 1em;
  color: #795548;
  font-weight: 500;
  opacity: 0.9;
}

/* 固定尺寸的书籍网格 */
.library-books-enhanced {
  position: relative;
  z-index: 1;
}

.library-books-enhanced.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
}

.library-books-enhanced.list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.library-book-card {
  background: linear-gradient(135deg, #ffffff 0%, #fefdfb 100%);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #efebe9;
  transition: all 0.4s ease;
  position: relative;
  height: 480px; /* 固定高度 */
  display: flex;
  flex-direction: column;
}

.library-books-enhanced.list .library-book-card {
  height: 200px; /* 列表视图固定高度 */
  flex-direction: row;
}

.library-book-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.library-book-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #d4b896 0%, #8d6e63 100%);
}

.book-cover-area {
  position: relative;
  height: 200px; /* 固定封面区域高度 */
  flex-shrink: 0;
}

.library-books-enhanced.list .book-cover-area {
  width: 140px; /* 列表视图固定宽度 */
  height: 100%;
}

.book-cover-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.book-cover-fixed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.library-book-card:hover .book-cover-fixed {
  transform: scale(1.05);
}

.book-overlay-enhanced {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.5) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.library-book-card:hover .book-overlay-enhanced {
  opacity: 1;
}

.quick-action-btn {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8d6e63 0%, #5d4037 100%);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.quick-action-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
}

.book-status-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.book-status-indicator.reading {
  background: rgba(255, 152, 0, 0.9);
  color: white;
}

.book-status-indicator.completed {
  background: rgba(76, 175, 80, 0.9);
  color: white;
}

.book-info-area {
  padding: 1.5rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.book-header {
  margin-bottom: 1rem;
}

.book-title-fixed {
  font-size: 1.3em;
  color: #4e342e;
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 2.6em; /* 固定两行高度 */
}

.book-author-fixed {
  color: #795548;
  font-size: 1em;
  font-style: italic;
  margin-bottom: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-metadata {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #8c7f73;
  font-size: 0.9em;
}

.metadata-item i {
  color: #a1887f;
  width: 14px;
}

.book-progress-area, .book-rating-area {
  margin-bottom: 1rem;
}

.progress-header, .rating-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.progress-label, .rating-label {
  font-size: 0.9em;
  color: #795548;
  font-weight: 500;
}

.progress-percentage {
  font-size: 0.9em;
  color: #8d6e63;
  font-weight: 600;
}

.progress-bar-enhanced {
  width: 100%;
  height: 6px;
  background-color: #e8dccf;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill-enhanced {
  height: 100%;
  background: linear-gradient(90deg, #ff9800 0%, #ffb74d 100%);
  border-radius: 3px;
  transition: width 0.4s ease;
}

.rating-stars {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stars-display {
  color: #ffd700;
  font-size: 1.1em;
}

.rating-number {
  color: #795548;
  font-weight: 600;
  font-size: 0.9em;
}

.completion-date {
  font-size: 0.8em;
  color: #8c7f73;
  font-style: italic;
}

.book-actions-enhanced {
  display: flex;
  gap: 0.8rem;
  margin-top: auto;
}

.action-btn-enhanced {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.8rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.9em;
  font-weight: 500;
  transition: all 0.3s ease;
}

.action-btn-enhanced.primary {
  background: linear-gradient(135deg, #8d6e63 0%, #795548 100%);
  color: white;
  box-shadow: 0 3px 10px rgba(141, 110, 99, 0.3);
}

.action-btn-enhanced.primary:hover {
  background: linear-gradient(135deg, #5d4037 0%, #4e342e 100%);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(141, 110, 99, 0.4);
}

.action-btn-enhanced.secondary {
  background-color: #f9f5eb;
  color: #5d4037;
  border: 1px solid #e8dccf;
}

.action-btn-enhanced.secondary:hover {
  background-color: #f0ebe0;
  transform: translateY(-2px);
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, #ffffff 0%, #fefdfb 100%);
  border-radius: 16px;
  border: 2px dashed #d4c7b2;
  position: relative;
  z-index: 1;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 2rem;
  background: linear-gradient(135deg, #f0ebe0 0%, #e8dccf 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon i {
  font-size: 2.5em;
  color: #8d6e63;
}

.empty-title {
  font-size: 2em;
  color: #4e342e;
  font-weight: 600;
  margin-bottom: 1rem;
}

.empty-description {
  font-size: 1.1em;
  color: #795548;
  line-height: 1.6;
  margin-bottom: 2rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.add-book-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #8d6e63 0%, #795548 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-family: inherit;
  font-size: 1em;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(141, 110, 99, 0.3);
}

.add-book-btn:hover {
  background: linear-gradient(135deg, #5d4037 0%, #4e342e 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(141, 110, 99, 0.4);
}

/* 其他页面样式保持不变 */
.reading-chronicles {
  background-color: #fffaf0;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0d4c0;
}

.chronicle-header {
  margin-bottom: 2rem;
  text-align: center;
}

.chronicle-title {
  font-size: 2.2em;
  color: #4e342e;
  font-weight: 600;
  position: relative;
  padding-bottom: 1rem;
  border-bottom: 1px dashed #c0b2a3;
}

.chronicle-title::before {
  content: '§';
  position: absolute;
  left: -30px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8em;
  color: #a1887f;
}

.chronicle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.chronicle-card {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
  border: 1px solid #efebe9;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.chronicle-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.card-illumination {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #d4b896 0%, #ecd9c7 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-illumination i {
  font-size: 1.5em;
  color: #5d4037;
}

.card-inscription h4 {
  font-size: 1.3em;
  color: #4e342e;
  margin-bottom: 0.8rem;
  font-weight: 600;
}

.current-book {
  font-size: 1.1em;
  color: #5d4037;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.no-current {
  color: #8c7f73;
  font-style: italic;
}

.reading-goal, .reading-current {
  margin-bottom: 0.3rem;
  color: #795548;
}

.progress-scroll {
  margin-top: 1rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #e0d4c0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8d6e63, #a1887f);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.9em;
  color: #795548;
  font-style: italic;
}

.genre-seals {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.genre-seal {
  background-color: #e0d4c0;
  color: #5a4b41;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid #d4c7b2;
}

/* 最近活动样式 */
.recent-activities {
  background-color: #fffaf0;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0d4c0;
}

.activity-header {
  margin-bottom: 2rem;
  text-align: center;
}

.activity-title {
  font-size: 2.2em;
  color: #4e342e;
  font-weight: 600;
  position: relative;
  padding-bottom: 1rem;
  border-bottom: 1px dashed #c0b2a3;
}

.activity-title::before {
  content: '§';
  position: absolute;
  left: -30px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8em;
  color: #a1887f;
}

.activity-scroll {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.activity-entry {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #efebe9;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.activity-entry:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.activity-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #d4b896 0%, #ecd9c7 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon i {
  color: #5d4037;
  font-size: 1.1em;
}

.activity-details {
  flex-grow: 1;
}

.activity-description {
  color: #4e342e;
  margin-bottom: 0.3rem;
  font-size: 1.05em;
}

.activity-timestamp {
  color: #8c7f73;
  font-size: 0.9em;
  font-style: italic;
}

/* 最近收藏的图书样式 */
.recent-collections {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.collection-book {
  background-color: #ffffff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
  border: 1px solid #efebe9;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.collection-book:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.book-cover-container {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.collection-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.book-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.collection-book:hover .book-overlay {
  opacity: 1;
}

.collection-book:hover .collection-cover {
  transform: scale(1.1);
}

.view-book-btn {
  background-color: #8d6e63;
  color: white;
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-book-btn:hover {
  background-color: #5d4037;
  transform: scale(1.1);
}

.book-info-compact {
  padding: 1rem;
}

.book-title-compact {
  font-size: 1.1em;
  color: #4e342e;
  margin-bottom: 0.3rem;
  font-weight: 600;
  line-height: 1.3;
}

.book-author-compact {
  color: #795548;
  font-size: 0.9em;
  margin-bottom: 0.5rem;
  font-style: italic;
}

.book-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.stars {
  color: #ffd700;
  font-size: 0.9em;
}

.rating-text {
  color: #795548;
  font-size: 0.85em;
}

.added-date {
  color: #8c7f73;
  font-size: 0.8em;
  font-style: italic;
}

/* Reviews, Notifications, Edit Info 样式保持不变 */
.reviews-content {
  background-color: #fffaf0;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0d4c0;
}

.reviews-header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px dashed #c0b2a3;
}

.reviews-stats {
  display: flex;
  gap: 2rem;
}

.review-stat {
  text-align: center;
  padding: 1rem;
  background-color: #f9f5eb;
  border-radius: 8px;
  border: 1px solid #e8dccf;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.review-item {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
  border: 1px solid #efebe9;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.review-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.review-book-info {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0ebe0;
}

.review-book-cover {
  width: 80px;
  height: 120px;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.review-book-details {
  flex-grow: 1;
}

.review-book-title {
  font-size: 1.3em;
  color: #4e342e;
  margin-bottom: 0.3rem;
  font-weight: 600;
}

.review-book-author {
  color: #795548;
  margin-bottom: 0.5rem;
  font-style: italic;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stars-review {
  color: #ffd700;
  font-size: 1.1em;
}

.rating-value {
  color: #795548;
  font-weight: 600;
}

.review-content {
  flex-grow: 1;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.review-title {
  font-size: 1.4em;
  color: #4e342e;
  font-weight: 600;
  margin: 0;
}

.review-date {
  color: #8c7f73;
  font-size: 0.9em;
  font-style: italic;
}

.review-text {
  color: #4e342e;
  line-height: 1.7;
  margin-bottom: 1.5rem;
  font-size: 1.05em;
}

.review-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #f0ebe0;
}

.review-engagement {
  display: flex;
  gap: 1.5rem;
}

.helpful-count, .comment-count {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #795548;
  font-size: 0.9em;
}

.helpful-count i, .comment-count i {
  color: #a1887f;
}

.review-actions {
  display: flex;
  gap: 0.8rem;
}

.review-action-btn {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.4rem 0.8rem;
  background-color: #f0ebe0;
  color: #5d4037;
  border: 1px solid #d4c7b2;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85em;
  transition: all 0.3s ease;
}

.review-action-btn:hover {
  background-color: #e0d4c0;
  transform: translateY(-1px);
}

/* Notifications 页面样式 */
.notifications-content {
  background-color: #fffaf0;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0d4c0;
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px dashed #c0b2a3;
}

.notification-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.control-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background-color: #8d6e63;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.3s ease;
}

.control-btn:hover:not(:disabled) {
  background-color: #5d4037;
  transform: translateY(-1px);
}

.control-btn:disabled {
  background-color: #a1887f;
  cursor: not-allowed;
  opacity: 0.6;
}

.notifications-stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  justify-content: center;
}

.notification-stat {
  text-align: center;
  padding: 1rem;
  background-color: #f9f5eb;
  border-radius: 8px;
  border: 1px solid #e8dccf;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notification-item {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background-color: #ffffff;
  border-radius: 10px;
  border: 1px solid #efebe9;
  transition: all 0.3s ease;
}

.notification-item.unread {
  border-left: 4px solid #8d6e63;
  background-color: #fefdfb;
}

.notification-item.important {
  border-left: 4px solid #ff6b6b;
  background: linear-gradient(135deg, #fff5f5 0%, #fefdfb 100%);
}

.notification-item:hover {
  transform: translateX(3px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.notification-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-icon.review {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1976d2;
}

.notification-icon.system {
  background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
  color: #7b1fa2;
}

.notification-icon.recommendation {
  background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%);
  color: #f57c00;
}

.notification-icon.social {
  background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
  color: #388e3c;
}

.notification-content {
  flex-grow: 1;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.notification-title {
  font-size: 1.2em;
  color: #4e342e;
  font-weight: 600;
  margin: 0;
}

.notification-time {
  color: #8c7f73;
  font-size: 0.85em;
  font-style: italic;
}

.notification-message {
  color: #5d4037;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.notification-actions {
  display: flex;
  gap: 0.8rem;
}

.notification-action-btn {
  padding: 0.4rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85em;
  transition: all 0.3s ease;
}

.notification-action-btn.primary {
  background-color: #8d6e63;
  color: white;
}

.notification-action-btn.primary:hover {
  background-color: #5d4037;
}

.notification-action-btn.secondary {
  background-color: #f0ebe0;
  color: #5d4037;
  border: 1px solid #d4c7b2;
}

.notification-action-btn.secondary:hover {
  background-color: #e0d4c0;
}

/* Edit Info 页面样式 */
.edit-content {
  background-color: #fffaf0;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0d4c0;
}

.edit-header {
  text-align: center;
  margin-bottom: 3rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px dashed #c0b2a3;
}

.section-title {
  font-size: 2.2em;
  color: #4e342e;
  font-weight: 600;
  margin: 0;
}

.edit-subtitle {
  color: #795548;
  font-style: italic;
  margin-top: 0.5rem;
}

.edit-form-container {
  max-width: 800px;
  margin: 0 auto;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.form-section {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 2rem;
  border: 1px solid #efebe9;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.form-section-title {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-size: 1.4em;
  color: #4e342e;
  font-weight: 600;
  margin-bottom: 1.5rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #f0ebe0;
}

.form-section-title i {
  color: #8d6e63;
  font-size: 1.1em;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 600;
  color: #5d4037;
  font-size: 0.95em;
  letter-spacing: 0.3px;
}

.form-input, .form-select, .form-textarea {
  padding: 0.8rem 1rem;
  border: 2px solid #e8dccf;
  border-radius: 8px;
  background-color: #fefdfb;
  color: #4e342e;
  font-family: inherit;
  font-size: 1em;
  transition: all 0.3s ease;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #8d6e63;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(141, 110, 99, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.genre-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 0.8rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.checkbox-label:hover {
  background-color: #f9f5eb;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid #d4c7b2;
  border-radius: 4px;
  position: relative;
  transition: all 0.3s ease;
}

.checkbox-input:checked + .checkbox-custom {
  background-color: #8d6e63;
  border-color: #8d6e63;
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 0.8em;
  font-weight: bold;
}

.privacy-options {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.privacy-option {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  cursor: pointer;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #f0ebe0;
  transition: all 0.3s ease;
}

.privacy-option:hover {
  background-color: #f9f5eb;
  border-color: #e8dccf;
}

.privacy-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.privacy-title {
  font-weight: 600;
  color: #4e342e;
}

.privacy-desc {
  font-size: 0.9em;
  color: #795548;
  line-height: 1.4;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  padding-top: 2rem;
  border-top: 1px dashed #c0b2a3;
}

.form-btn {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
  font-size: 1em;
  font-weight: 600;
  letter-spacing: 0.3px;
  transition: all 0.3s ease;
}

.form-btn.primary {
  background: linear-gradient(135deg, #8d6e63 0%, #795548 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(141, 110, 99, 0.3);
}

.form-btn.primary:hover {
  background: linear-gradient(135deg, #5d4037 0%, #4e342e 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(141, 110, 99, 0.4);
}

.form-btn.secondary {
  background-color: #f0ebe0;
  color: #5d4037;
  border: 2px solid #d4c7b2;
}

.form-btn.secondary:hover {
  background-color: #e0d4c0;
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sanctum-navigation {
    width: 22%;
  }
  
  .sanctum-content {
    margin-left: 22%;
    max-width: calc(78% - 4rem);
  }

  .library-books-enhanced.grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 992px) {
  .sanctum-navigation {
    width: 25%;
  }
  
  .sanctum-content {
    margin-left: 25%;
    max-width: calc(75% - 4rem);
  }

  .library-header-enhanced {
    flex-direction: column;
    align-items: stretch;
  }

  .library-controls-enhanced {
    min-width: auto;
  }

  .filter-controls {
    flex-direction: column;
  }

  .library-stats-enhanced {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .library-books-enhanced.grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .genre-checkboxes {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 768px) {
  .sanctum-navigation {
    width: 100%;
    position: relative;
    height: auto;
    margin-top: 0;
  }
  
  .sanctum-content {
    margin-left: 0;
    max-width: 100%;
    padding: 1rem;
  }

  .library-content-enhanced {
    padding: 2rem;
  }

  .library-stats-enhanced {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .library-books-enhanced.grid {
    grid-template-columns: 1fr;
  }

  .library-book-card {
    height: auto;
    min-height: 400px;
  }

  .library-books-enhanced.list .library-book-card {
    flex-direction: column;
    height: auto;
  }

  .library-books-enhanced.list .book-cover-area {
    width: 100%;
    height: 200px;
  }

  .book-actions-enhanced {
    flex-direction: row;
  }

  .notifications-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .notification-controls {
    flex-direction: column;
    width: 100%;
  }

  .notifications-stats {
    flex-direction: column;
    gap: 1rem;
  }

  .notification-item {
    flex-direction: column;
    text-align: center;
  }

  .notification-header {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }

  .notification-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .sanctum-title {
    font-size: 1.8em;
  }

  .sanctum-subtitle {
    font-size: 1em;
  }

  .library-content-enhanced {
    padding: 1.5rem;
  }

  .section-title-enhanced {
    font-size: 2em;
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }

  .library-stats-enhanced {
    grid-template-columns: 1fr;
  }

  .stat-card-enhanced {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }

  .library-book-card {
    min-height: 350px;
  }

  .book-title-fixed {
    font-size: 1.1em;
  }

  .nav-link-enhanced {
    padding: 0.8rem 1rem;
  }

  .nav-text {
    font-size: 0.9em;
  }

  .user-name {
    font-size: 1.1em;
  }

  .emblem-portrait {
    width: 70px;
    height: 70px;
  }
}
</style>