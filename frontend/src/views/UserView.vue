<template>
  <div class="establishment-container">
    <div class="dashboard-layout">
      <nav class="classic-nav">
        <div class="nav-header">
          <div class="nav-logo">📚</div>
          <h3 class="nav-title">The Scholar's Study</h3>
        </div>
        <ul>
          <li @click="activeSection = 'user-info'" :class="{ active: activeSection === 'user-info' }">
            <span class="nav-icon">👤</span>
            <span class="nav-text">Personal Ledger</span>
            <span class="nav-decoration">〰</span>
          </li>
          <li @click="activeSection = 'favorite-books'" :class="{ active: activeSection === 'favorite-books' }">
            <span class="nav-icon">📚</span>
            <span class="nav-text">Literary Treasury</span>
            <span class="nav-decoration">〰</span>
          </li>
          <li @click="activeSection = 'favorite-reviews'" :class="{ active: activeSection === 'favorite-reviews' }">
            <span class="nav-icon">✍️</span>
            <span class="nav-text">Critiques & Reflections</span>
            <span class="nav-decoration">〰</span>
          </li>
          <li @click="activeSection = 'my-reviews'" :class="{ active: activeSection === 'my-reviews' }">
            <span class="nav-icon">📝</span>
            <span class="nav-text">My Reviews</span>
            <span class="nav-decoration">〰</span>
          </li>
          <li @click="activeSection = 'my-comments'" :class="{ active: activeSection === 'my-comments' }">
            <span class="nav-icon">💬</span>
            <span class="nav-text">My Comments</span>
            <span class="nav-decoration">〰</span>
          </li>
        </ul>
        <div class="nav-footer">
          <p class="chinese-proverb">"The path to learning is arduous, but diligence is the way."</p>
        </div>
      </nav>

      <main class="content-area">
        <div class="parchment-header">
          <h1 class="main-heading">
            <span class="chinese-brush">The User's Athenaeum</span>
          </h1>
          <div class="header-ornament">✒︎</div>
        </div>

        <section v-show="activeSection === 'user-info'" class="chapter-section">
          <div class="section-header">
            <h2 class="chapter-title">
              <span class="title-icon">🖋</span>
              <span>Personal Particulars</span>
            </h2>
            <div class="section-divider"></div>
          </div>

          <div class="avatar-section">
            <div class="avatar-frame">
              <img :src="user.avatar_url || 'https://via.placeholder.com/150'" alt="User Effigy" class="user-avatar" />
              <div class="frame-decoration"></div>
            </div>
          </div>

          <div class="info-section">
            <div class="info-item">
              <span class="info-label">Appellation:</span>
              <span v-if="!isEditingNickname" class="info-value">{{ user.nickname }}</span>
              <input v-else type="text" v-model="editableNickname" class="elegant-input" />
              <button @click="toggleEditNickname" class="elegant-button small">
                {{ isEditingNickname ? 'Preserve' : 'Amend' }}
              </button>
            </div>

            <div class="info-item">
              <span class="info-label">Electronic Mail:</span>
              <span class="info-value">{{ user.email }}</span>
            </div>
          </div>

          <div v-if="!user.is_profile_complete" class="profile-incomplete-warning">
            <span class="warning-icon">⚠️</span>
            <span>Your Chronicle Awaits Completion. Kindly proceed to <router-link to="/user-onboarding">Fulfill Your
                Details</router-link>.</span>
          </div>
        </section>

        <section v-show="activeSection === 'favorite-books'" class="chapter-section">
          <div class="section-header">
            <h2 class="chapter-title">
              <span class="title-icon">📖</span>
              <span>Literary Treasury ({{ favoriteBooks.length }} Tomes)</span>
            </h2>
            <div class="section-divider"></div>
          </div>

          <div v-if="favoriteBooks.length === 0" class="empty-state">
            <div class="empty-icon">📚</div>
            <p class="empty-text">No Esteemed Volumes as yet Adorn Your Treasury.</p>
          </div>

          <div v-else class="book-gallery">
            <div v-for="book in favoriteBooks" :key="book.bookId" @click="goToBookDetails(book.bookId)"
              class="book-card">
              <div class="book-cover-wrapper">
                <img :src="book.coverImg || 'https://via.placeholder.com/100'" alt="Book's Visage" class="book-cover" />
                <div class="book-cover-overlay"></div>
              </div>
              <div class="book-info">
                <h4 class="book-title">{{ book.title }}</h4>
                <p class="book-author">Authored By: {{ book.author }}</p>
                <p class="book-publisher">Printed By: {{ book.publisher }}</p>
              </div>
              <div class="book-corner"></div>
            </div>
          </div>
        </section>

        <section v-show="activeSection === 'favorite-reviews'" class="chapter-section">
          <div class="section-header">
            <h2 class="chapter-title">
              <span class="title-icon">🖋</span>
              <span>Critiques & Reflections ({{ favoriteReviews.length }} Scrolls)</span>
            </h2>
            <div class="section-divider"></div>
          </div>

          <div v-if="favoriteReviews.length === 0" class="empty-state">
            <div class="empty-icon">✍️</div>
            <p class="empty-text">No Learned Discourses as yet Grace Your Collection.</p>
          </div>

          <div v-else class="review-container">
            <div v-for="review in favoriteReviews" :key="review.id" @click="goToBookDetails(review.bookId)"
              class="review-card">
              <div class="review-header">
                <div class="reviewer-avatar-wrapper">
                  <img :src="review.reviewerAvatarUrl || 'https://via.placeholder.com/50'" alt="Reviewer's Likeness"
                    class="reviewer-avatar" />
                </div>
                <div class="reviewer-info">
                  <span class="reviewer-nickname">Penned By: {{ review.reviewerNickname || 'Anonymous Scribe' }}</span>
                  <div class="review-meta">
                    <span class="review-rating">
                      <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= review.rating }">★</span>
                    </span>
                    <span class="review-time">{{ formatDate(review.postTime) }}</span>
                  </div>
                </div>
              </div>
              <div class="review-content">
                <p class="review-text">{{ truncateContent(review.content) }}</p>
              </div>
              <div class="review-footer">
                <span class="review-action">
                  <span class="action-icon">👍</span>
                  <span class="action-count">{{ review.likeCount || 0 }}</span>
                </span>
                <span class="review-action">
                  <span class="action-icon">⭐</span>
                  <span class="action-count">{{ review.collectCount || 0 }}</span>
                </span>
              </div>
              <div class="review-corner"></div>
            </div>
          </div>
        </section>

        <section v-show="activeSection === 'my-reviews'" class="chapter-section">
          <div class="section-header">
            <h2 class="chapter-title">
              <span class="title-icon">📝</span>
              <span>My Published Reviews ({{ myReviews.length }} Entries)</span>
            </h2>
            <div class="section-divider"></div>
          </div>

          <div v-if="myReviews.length === 0" class="empty-state">
            <div class="empty-icon">🤷‍♀️</div>
            <p class="empty-text">You have not yet inscribed any reviews.</p>
          </div>

          <div v-else class="review-container">
            <div v-for="review in myReviews" :key="review.id" @click="goToBookDetails(review.bookId)"
              class="review-card">
              <div class="review-header">
                <div class="reviewer-avatar-wrapper">
                  <img :src="user.avatar_url || 'https://via.placeholder.com/50'" alt="Your Likeness"
                    class="reviewer-avatar" />
                </div>
                <div class="reviewer-info">
                  <span class="reviewer-nickname">Authored by: {{ user.nickname || 'You' }}</span>
                  <div class="review-meta">
                    <span class="review-rating">
                      <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= review.rating }">★</span>
                    </span>
                    <span class="review-time">{{ formatDate(review.postTime) }}</span>
                    <span class="review-status" :class="review.status">{{ review.status }}</span>
                  </div>
                </div>
              </div>
              <div class="review-content">
                <p class="review-text">{{ truncateContent(review.content) }}</p>
              </div>
              <div class="review-footer">
                <span class="review-action">
                  <span class="action-icon">👍</span>
                  <span class="action-count">{{ review.likeCount || 0 }}</span>
                </span>
              </div>
              <div class="review-corner"></div>
            </div>
          </div>
          <div v-if="myReviewsPagination.pages > 1" class="pagination-controls">
            <button @click="fetchMyReviews(myReviewsPagination.current_page - 1)"
              :disabled="!myReviewsPagination.has_prev" class="elegant-button">Previous</button>
            <span>Page {{ myReviewsPagination.current_page }} of {{ myReviewsPagination.pages }}</span>
            <button @click="fetchMyReviews(myReviewsPagination.current_page + 1)"
              :disabled="!myReviewsPagination.has_next" class="elegant-button">Next</button>
          </div>
        </section>
        <section v-show="activeSection === 'my-comments'" class="chapter-section">
          <div class="section-header">
            <h2 class="chapter-title">
              <span class="title-icon">💬</span>
              <span>My Published Comments ({{ myComments.length }} Entries)</span>
            </h2>
            <div class="section-divider"></div>
          </div>

          <div v-if="myComments.length === 0" class="empty-state">
            <div class="empty-icon">🤷‍♂️</div>
            <p class="empty-text">You have not yet penned any comments.</p>
          </div>

          <div v-else class="comment-container">
            <div v-for="comment in myComments" :key="comment.id" class="comment-card">
              <div class="comment-header">
                <div class="commenter-avatar-wrapper">
                  <img :src="user.avatar_url || 'https://via.placeholder.com/50'" alt="Your Likeness"
                    class="commenter-avatar" />
                </div>
                <div class="commenter-info">
                  <span class="commenter-nickname">Comment by: {{ user.nickname || 'You' }}</span>
                  <div class="comment-meta">
                    <span class="comment-time">{{ formatDate(comment.commentTime) }}</span>
                  </div>
                </div>
              </div>
              <div class="comment-content">
                <p class="comment-text">{{ truncateContent(comment.content) }}</p>
              </div>
              <div class="comment-footer">
                <span class="comment-action">
                  <span class="action-icon">👍</span>
                  <span class="action-count">{{ comment.likeCount || 0 }}</span>
                </span>
                <span class="comment-link" @click="goToBookDetails(comment.bookId)">
                  <span class="action-icon">📖</span> View Related Book
                </span>
              </div>
              <div class="comment-corner"></div>
            </div>
          </div>
          <div v-if="myCommentsPagination.pages > 1" class="pagination-controls">
            <button @click="fetchMyComments(myCommentsPagination.current_page - 1)"
              :disabled="!myCommentsPagination.has_prev" class="elegant-button">Previous</button>
            <span>Page {{ myCommentsPagination.current_page }} of {{ myCommentsPagination.pages }}</span>
            <button @click="fetchMyComments(myCommentsPagination.current_page + 1)"
              :disabled="!myCommentsPagination.has_next" class="elegant-button">Next</button>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useRouter } from 'vue-router';

// Helper function to get user data from localStorage
const getParsedUserData = () => {
  const storedUserData = localStorage.getItem('user_data');
  if (storedUserData) {
    try {
      return JSON.parse(storedUserData);
    } catch (e) {
      console.error("Error parsing user_data from localStorage:", e);
      return null;
    }
  }
  return null;
};

export default {
  name: 'UserDashboard',
  data() {
    return {
      activeSection: 'user-info', // Initialize active section
      user: {
        user_id: '',
        nickname: '',
        email: '',
        avatar_url: '',
        is_profile_complete: false,
      },
      favoriteBooks: [],
      favoriteReviews: [],
      // New data properties for user's own reviews and comments
      myReviews: [],
      myReviewsPagination: {
        total: 0,
        pages: 1,
        current_page: 1,
        per_page: 10,
        has_next: false,
        has_prev: false,
      },
      myComments: [],
      myCommentsPagination: {
        total: 0,
        pages: 1,
        current_page: 1,
        per_page: 10,
        has_next: false,
        has_prev: false,
      },
      isEditingNickname: false,
      editableNickname: '',
      selectedAvatarFile: null,
    };
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  watch: {
    // Watch for changes in activeSection to fetch data only when the section becomes active
    activeSection(newSection, oldSection) {
      const loggedInUser = getParsedUserData();
      const userId = loggedInUser ? loggedInUser.user_id : null;
      if (!userId) return; // Don't fetch if no user ID

      if (newSection === 'my-reviews' && this.myReviews.length === 0) {
        this.fetchMyReviews(this.myReviewsPagination.current_page);
      } else if (newSection === 'my-comments' && this.myComments.length === 0) {
        this.fetchMyComments(this.myCommentsPagination.current_page);
      }
    },
  },
  created() {
    this.fetchUserData();
    this.fetchFavoriteBooks();
    this.fetchFavoriteReviews();

    this.fetchMyReviews(1);
    this.fetchMyComments(1);
  },
  methods: {
    async fetchUserData() {
      const currentStoredUserData = getParsedUserData(); // 获取当前 localStorage 中的完整数据

      if (!currentStoredUserData || !currentStoredUserData.user_id) {
        console.error('UserView: User data not found in localStorage. Redirecting to login.');
        this.router.push({ name: 'auth' });
        return;
      }

      this.user.user_id = currentStoredUserData.user_id;
      // 优先从 localStorage 获取，减少 API 调用
      this.user.nickname = currentStoredUserData.nickname || '';
      this.user.email = currentStoredUserData.email || '';
      this.user.avatar_url = currentStoredUserData.avatar_url || '';
      this.user.is_profile_complete = currentStoredUserData.is_profile_complete || false;
      this.editableNickname = this.user.nickname;

      try {
        const response = await axios.get(`/service-a/api/users/${this.user.user_id}`);
        const userDataFromBackend = response.data; // 从后端获取的最新资料

        // **核心修改：更新 localStorage 中的 user_data，但保留 auth_token**
        // 合并后端返回的资料，并保留 auth_token
        const updatedUserData = {
          ...currentStoredUserData, // 保留所有现有字段，包括 auth_token
          ...userDataFromBackend,   // 合并后端返回的最新资料
          // 确保 is_profile_complete 字段也被正确更新
          is_profile_complete: userDataFromBackend.is_profile_complete !== undefined ? userDataFromBackend.is_profile_complete : currentStoredUserData.is_profile_complete
        };
        localStorage.setItem('user_data', JSON.stringify(updatedUserData));
        console.log('UserView: fetchUserData updated localStorage with:', updatedUserData);

        // 更新组件的 user data
        this.user = updatedUserData; // 直接使用合并后的数据更新组件状态
        this.editableNickname = this.user.nickname;

      } catch (error) {
        console.error('UserView: Error fetching user data from API:', error);
        if (error.response && error.response.status === 401) {
          alert('会话已过期，请重新登录。');
          this.router.push({ name: 'auth' });
        } else if (!currentStoredUserData) {
          this.router.push({ name: 'auth' });
        }
      }
    },

    async fetchFavoriteBooks() {
      const loggedInUser = getParsedUserData();
      const userId = loggedInUser ? loggedInUser.user_id : null;
      if (!userId) { console.warn('UserView: User ID not available for fetching favorite books.'); return; }
      try {
        const bookIdsResponse = await axios.get(`/service-c/api/books/favorite_books`, { params: { userId } });
        const bookIds = bookIdsResponse.data;
        console.log("UserView: 收藏图书 IDs:", bookIds);
        if (bookIds.length > 0) {
          const booksDetailResponse = await axios.get(`/service-b/api/books/batch`, { params: { ids: bookIds.join(',') } });
          this.favoriteBooks = booksDetailResponse.data;
        } else { this.favoriteBooks = []; }
      } catch (error) { console.error('UserView: Error fetching favorite books:', error); this.favoriteBooks = []; }
    },

    async fetchFavoriteReviews() {
      const loggedInUser = getParsedUserData();
      const userId = loggedInUser ? loggedInUser.user_id : null;
      if (!userId) { console.warn('UserView: User ID not available for fetching favorite reviews.'); return; }
      try {
        const reviewIdsResponse = await axios.get(`/service-c/api/reviews/favorite_reviews`, { params: { userId } });
        const reviewIds = reviewIdsResponse.data;
        console.log("UserView: 收藏书评 IDs:", reviewIds);
        if (reviewIds.length > 0) {
          const reviewsDetailResponse = await axios.get(`/service-c/api/reviews/batch`, { params: { ids: reviewIds.join(',') } });
          this.favoriteReviews = await Promise.all(reviewsDetailResponse.data.map(async review => {
            let reviewerNickname = '未知用户'; let reviewerAvatarUrl = 'https://via.placeholder.com/50';
            try {
              const userProfile = await axios.get(`/service-a/api/users/${review.userId}`);
              reviewerNickname = userProfile.data.nickname || '匿名用户';
              reviewerAvatarUrl = userProfile.data.avatar_url || 'https://via.placeholder.com/50';
            } catch (userError) { console.warn(`UserView: Could not fetch user info for review userId ${review.userId}:`, userError); }
            return { ...review, reviewerNickname, reviewerAvatarUrl, };
          }));
        } else { this.favoriteReviews = []; }
      } catch (error) { console.error('UserView: Error fetching favorite reviews:', error); this.favoriteReviews = []; }
    },

    // --- New Method: Fetch User's Own Reviews with Pagination ---
    async fetchMyReviews(page = 1) {
      const loggedInUser = getParsedUserData();
      const userId = loggedInUser ? loggedInUser.user_id : null;
      if (!userId) {
        console.warn('UserView: User ID not available for fetching my reviews.');
        this.myReviews = [];
        return;
      }
      try {
        // 确保请求的页码不小于1
        const targetPage = Math.max(1, page);
        const response = await axios.get(`/service-c/api/reviews/user/${userId}`, {
          params: { page: targetPage, per_page: this.myReviewsPagination.per_page }
        });
        this.myReviews = response.data.reviews;
        this.myReviewsPagination = {
          total: response.data.total,
          pages: response.data.pages,
          current_page: response.data.current_page,
          per_page: response.data.per_page,
          has_next: response.data.has_next,
          has_prev: response.data.has_prev,
        };
        console.log("UserView: My Reviews:", this.myReviews, "Pagination:", this.myReviewsPagination);
      } catch (error) {
        console.error('UserView: Error fetching my reviews:', error);
        this.myReviews = [];
        // 在错误发生时重置分页信息
        this.myReviewsPagination = { total: 0, pages: 1, current_page: 1, per_page: 10, has_next: false, has_prev: false };
      }
    },

    // --- New Method: Fetch User's Own Comments with Pagination ---
    async fetchMyComments(page = 1) {
      const loggedInUser = getParsedUserData();
      const userId = loggedInUser ? loggedInUser.user_id : null;
      if (!userId) {
        console.warn('UserView: User ID not available for fetching my comments.');
        this.myComments = [];
        return;
      }
      try {
        // 确保请求的页码不小于1
        const targetPage = Math.max(1, page);
        // Assuming your comment API endpoint for user's comments is /comments/user/<user_id>
        const response = await axios.get(`/service-c/api/comments/user/${userId}`, {
          params: { page: targetPage, per_page: this.myCommentsPagination.per_page }
        });
        this.myComments = response.data.comments;
        this.myCommentsPagination = {
          total: response.data.total,
          pages: response.data.pages,
          current_page: response.data.current_page,
          per_page: response.data.per_page,
          has_next: response.data.has_next,
          has_prev: response.data.has_prev,
        };

        // 对于评论，您可能希望获取相关的图书详细信息，如果 `comment.bookId` 没有直接返回的话。
        // 我将添加一个占位符，以使 `goToBookDetails` 能够正常工作。
        this.myComments = await Promise.all(this.myComments.map(async comment => {
          let bookId = null;
          if (comment.reviewId) { // 假设评论与书评关联，并且可以通过书评找到图书ID
            try {
              const reviewResponse = await axios.get(`/service-c/api/reviews/${comment.reviewId}`);
              bookId = reviewResponse.data.bookId; // 假设书评对象中包含 bookId
            } catch (error) {
              console.warn(`Could not fetch review for comment ${comment.id}:`, error);
            }
          }
          return { ...comment, bookId }; // 添加 bookId 以便导航
        }));

        console.log("UserView: My Comments:", this.myComments, "Pagination:", this.myCommentsPagination);
      } catch (error) {
        console.error('UserView: Error fetching my comments:', error);
        this.myComments = [];
        // 在错误发生时重置分页信息
        this.myCommentsPagination = { total: 0, pages: 1, current_page: 1, per_page: 10, has_next: false, has_prev: false };
      }
    },


    toggleEditNickname() {
      if (this.isEditingNickname) { this.updateNickname(); }
      this.isEditingNickname = !this.isEditingNickname;
    },
    async updateNickname() {
      const currentStoredUserData = getParsedUserData();
      const userId = currentStoredUserData ? currentStoredUserData.user_id : null;
      if (!userId) {
        console.error('UserView: User ID not found for updating nickname.');
        alert('用户ID缺失，无法更新昵称。');
        this.router.push({ name: 'auth' });
        return;
      }
      try {
        await axios.put(`/service-a/api/users/${userId}/nickname`, { nickname: this.editableNickname });
        this.user.nickname = this.editableNickname;

        // **核心修改：同步更新 localStorage 中的 'user_data'，保留 auth_token**
        if (currentStoredUserData) {
          const updatedUserData = {
            ...currentStoredUserData,
            nickname: this.editableNickname // 更新昵称
          };
          localStorage.setItem('user_data', JSON.stringify(updatedUserData));
          console.log('UserView: updateNickname updated localStorage with:', updatedUserData);
        }
        alert('昵称更新成功！');
      } catch (error) { console.error('UserView: Error updating nickname:', error); alert('昵称更新失败。'); }
    },
    handleAvatarChange(event) { this.selectedAvatarFile = event.target.files[0]; },
    async uploadAvatar() {
      if (!this.selectedAvatarFile) { alert('请选择一个头像文件。'); return; }
      const currentStoredUserData = getParsedUserData();
      const userId = currentStoredUserData ? currentStoredUserData.user_id : null;
      if (!userId) {
        console.error('UserView: User ID not found for uploading avatar.');
        alert('用户ID缺失，无法上传头像。');
        this.router.push({ name: 'auth' });
        return;
      }
      try {
        const formData = new FormData();
        formData.append('avatar', this.selectedAvatarFile);
        const response = await axios.post(`/service-a/api/users/${userId}/avatar`, formData, { headers: { 'Content-Type': 'multipart/form-data', }, });
        this.user.avatar_url = response.data.avatar_url;

        // **核心修改：同步更新 localStorage 中的 'user_data'，保留 auth_token**
        if (currentStoredUserData) {
          const updatedUserData = {
            ...currentStoredUserData,
            avatar_url: this.user.avatar_url // 更新头像URL
          };
          localStorage.setItem('user_data', JSON.stringify(updatedUserData));
          console.log('UserView: uploadAvatar updated localStorage with:', updatedUserData);
        }
        this.selectedAvatarFile = null;
        alert('头像上传成功！');
      } catch (error) { console.error('UserView: Error uploading avatar:', error); alert('头像上传失败。'); }
    },
    goToBookDetails(bookId) {
      if (!bookId) { console.error('UserView: Tried to navigate to BookDetails with an undefined or null bookId.'); alert('无法打开图书详情，图书ID缺失。'); return; }
      this.router.push({ name: 'BookDetails', params: { bookId: bookId } });
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) { return dateString; }
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
    },
    truncateContent(content, maxLength = 100) {
      if (!content) return '';
      if (content.length > maxLength) { return content.substring(0, maxLength) + '...'; }
      return content;
    },
  },
};
</script>

<style scoped>
/* Container for all comment cards */
.comment-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  /* Space between each comment card */
  padding: 0 10px;
  /* Add some horizontal padding */
}

/* Individual comment card styling */
.comment-card {
  background-color: #fff;
  /* White background for the card */
  border-radius: 8px;
  /* Slightly rounded corners */
  padding: 20px;
  /* Inner spacing */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  /* Softer, more elegant shadow */
  transition: all 0.3s ease;
  /* Smooth transition for hover effects */
  position: relative;
  border: 1px solid #e0d8cc;
  /* Subtle border to define the card */
}

.comment-card:hover {
  transform: translateY(-3px);
  /* Slight lift effect on hover */
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
  /* Enhanced shadow on hover */
}

/* Header section within the comment card (avatar and info) */
.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  /* Space between header and content */
}

/* Avatar wrapper for comments */
.commenter-avatar-wrapper {
  /* Changed from .comment-avatar-wrapper for consistency with review styling */
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 15px;
  border: 2px solid #f5ebe0;
  /* Matches your existing theme */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
  /* Prevent shrinking if space is tight */
}

/* Actual avatar image */
.commenter-avatar {
  /* Changed from .comment-avatar */
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Info section (nickname, time) within the header */
.commenter-info {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  /* Allows info to take available space */
}

.commenter-nickname {
  font-weight: bold;
  color: #333;
  font-size: 1.1em;
  margin-bottom: 3px;
}

.comment-meta {
  font-size: 0.85em;
  color: #777;
}

.comment-time {
  /* No additional styling needed if it's already part of .comment-meta */
}

/* Comment content area */
.comment-content {
  margin-bottom: 15px;
  /* Space below content */
}

.comment-text {
  font-size: 0.95em;
  line-height: 1.6;
  color: #444;
  white-space: pre-wrap;
  /* Preserves whitespace and wraps text */
  word-wrap: break-word;
  /* Breaks long words if necessary */
}

/* Footer for actions like likes and links */
.comment-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  /* Align actions to the right */
  padding-top: 10px;
  /* Space from content above */
  border-top: 1px dashed #eee;
  /* Subtle separator */
}

.comment-action {
  display: inline-flex;
  align-items: center;
  margin-right: 15px;
  /* Space between actions */
  color: #666;
  font-size: 0.9em;
}

.comment-action .action-icon {
  margin-right: 5px;
  color: #888;
  /* Slightly darker icon color */
}

/* Styling for the "View Related Book" link specifically */
.comment-link {
  cursor: pointer;
  color: #007bff;
  /* Standard link blue */
  text-decoration: none;
  /* No underline by default */
  font-weight: bold;
  display: inline-flex;
  align-items: center;
  transition: color 0.2s ease, text-decoration 0.2s ease;
}

.comment-link:hover {
  color: #0056b3;
  /* Darker blue on hover */
  text-decoration: underline;
  /* Underline on hover */
}

.review-status {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  margin-left: 10px;
  font-weight: bold;
}

.review-status.approved {
  background-color: #d4edda;
  color: #155724;
}

.review-status.pending {
  background-color: #fff3cd;
  color: #856404;
}

.review-status.rejected {
  background-color: #f8d7da;
  color: #721c24;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 15px;
  /* Spacing between elements */
}

.pagination-controls .elegant-button {
  padding: 8px 15px;
  border: 1px solid #ccc;
  background-color: #f9f9e0;
  /* Match your theme */
  color: #333;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.pagination-controls .elegant-button:hover:not(:disabled) {
  background-color: #e0e0c0;
}

.pagination-controls .elegant-button:disabled {
  background-color: #eee;
  color: #aaa;
  cursor: not-allowed;
}

.pagination-controls span {
  font-family: 'STSong', serif;
  /* Or your preferred elegant font */
  font-size: 1em;
  color: #555;
}

/* --- 基础容器样式 --- */
.establishment-container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 20px;
  font-family: 'Noto Serif SC', 'SimSun', 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
  color: #4e342e;
}

.dashboard-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 30px;
  min-height: 80vh;
}

/* --- 导航栏样式 - 古典风格 --- */
.classic-nav {
  background: linear-gradient(135deg, #f5ebe0 0%, #e6d5c3 100%);
  border-radius: 12px;
  padding: 25px 0;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #d4b896;
  position: relative;
  overflow: hidden;
}

.classic-nav::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #8d6e63, #d7ccc8, #8d6e63);
}

.nav-header {
  text-align: center;
  padding: 0 20px 20px;
  border-bottom: 1px dashed #d7ccc8;
  margin-bottom: 20px;
}

.nav-logo {
  font-size: 3rem;
  margin-bottom: 10px;
  color: #5d4037;
}

.nav-title {
  margin: 0;
  font-size: 1.5rem;
  color: #5d4037;
  font-weight: 600;
  letter-spacing: 2px;
}

.classic-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.classic-nav li {
  padding: 16px 30px;
  margin: 5px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #5d4037;
  position: relative;
  border-left: 4px solid transparent;
}

.classic-nav li:hover {
  background-color: rgba(141, 110, 99, 0.1);
}

.classic-nav li.active {
  background-color: rgba(141, 110, 99, 0.15);
  border-left: 4px solid #8d6e63;
  color: #3e2723;
  font-weight: 600;
}

.classic-nav li.active::after {
  content: "";
  position: absolute;
  right: 20px;
  width: 8px;
  height: 8px;
  background-color: #8d6e63;
  border-radius: 50%;
}

.nav-icon {
  font-size: 1.3rem;
  margin-right: 15px;
}

.nav-text {
  font-size: 1.1rem;
  flex-grow: 1;
}

.nav-decoration {
  color: #bcaaa4;
  font-size: 1.2rem;
}

.nav-footer {
  text-align: center;
  padding: 20px;
  margin-top: 20px;
  border-top: 1px dashed #d7ccc8;
}

.chinese-proverb {
  font-style: italic;
  color: #8d6e63;
  font-size: 0.95rem;
  letter-spacing: 1px;
}

/* --- 内容区域样式 --- */
.content-area {
  background-color: #fffaf0;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #d4b896;
}

.parchment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #d7ccc8;
}

.main-heading {
  margin: 0;
  font-size: 2.5rem;
  color: #5d4037;
  font-weight: 600;
  letter-spacing: 2px;
}

.chinese-brush {
  background: linear-gradient(90deg, #5d4037, #8d6e63);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.header-ornament {
  font-size: 2rem;
  color: #bcaaa4;
}

/* --- 章节样式 --- */
.chapter-section {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
  border-left: 5px solid #8d6e63;
  position: relative;
  overflow: hidden;
}

.chapter-section::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(90deg, #8d6e63, #d7ccc8);
}

.section-header {
  margin-bottom: 25px;
}

.chapter-title {
  font-size: 1.8rem;
  color: #5d4037;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  position: relative;
  padding-bottom: 10px;
}

.chapter-title::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #8d6e63, transparent);
}

.title-icon {
  margin-right: 15px;
  font-size: 1.5rem;
}

.section-divider {
  height: 1px;
  background: linear-gradient(90deg, #d7ccc8, transparent);
  margin-top: 15px;
}

/* --- 头像区域 --- */
.avatar-section {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  gap: 30px;
}

.avatar-frame {
  position: relative;
  width: 150px;
  height: 150px;
}

.user-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 5px solid #f5ebe0;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.frame-decoration {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8d6e63, #d7ccc8);
  z-index: 0;
  opacity: 0.3;
}

.avatar-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* --- 按钮和输入框 --- */
.elegant-input {
  padding: 10px 15px;
  border: 1px solid #d7ccc8;
  border-radius: 6px;
  background-color: #fffaf0;
  color: #4e342e;
  font-family: 'Noto Serif SC', 'SimSun', 'Palatino Linotype', serif;
  transition: all 0.3s ease;
  font-size: 1rem;
  width: 200px;
}

.elegant-input:focus {
  outline: none;
  border-color: #8d6e63;
  box-shadow: 0 0 0 3px rgba(141, 110, 99, 0.2);
}

.elegant-button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #8d6e63, #a1887f);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Noto Serif SC', 'SimSun', 'Palatino Linotype', serif;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 3px 10px rgba(141, 110, 99, 0.3);
}

.elegant-button:hover {
  background: linear-gradient(135deg, #6d4c41, #8d6e63);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(141, 110, 99, 0.4);
}

.elegant-button:active {
  transform: translateY(0);
}

.elegant-button.small {
  padding: 8px 15px;
  font-size: 0.9rem;
}

.button-icon {
  font-size: 0.9em;
}

.elegant-file-input {
  padding: 10px 20px;
  background: linear-gradient(135deg, #a1887f, #bcaaa4);
  color: #fff;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 3px 10px rgba(161, 136, 127, 0.3);
}

.elegant-file-input:hover {
  background: linear-gradient(135deg, #8d6e63, #a1887f);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(161, 136, 127, 0.4);
}

.file-input-icon {
  font-size: 0.9em;
}

/* --- 信息展示 --- */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.info-label {
  font-weight: 600;
  color: #5d4037;
  min-width: 60px;
}

.info-value {
  color: #4e342e;
  flex-grow: 1;
}

/* --- 警告信息 --- */
.profile-incomplete-warning {
  padding: 15px;
  background-color: #fff3e0;
  border-left: 4px solid #ffa000;
  color: #e65100;
  border-radius: 6px;
  margin-top: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.warning-icon {
  font-size: 1.2rem;
}

/* --- 图书展示 --- */
.book-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 25px;
}

.book-card {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.book-cover-wrapper {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.book-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.book-cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.3));
}

.book-card:hover .book-cover {
  transform: scale(1.05);
}

.book-info {
  padding: 15px;
}

.book-title {
  margin: 0 0 8px 0;
  color: #4e342e;
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.3;
}

.book-author,
.book-publisher {
  margin: 5px 0;
  color: #8d6e63;
  font-size: 0.9rem;
}

.book-corner {
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 40px 40px 0;
  border-color: transparent #8d6e63 transparent transparent;
}

/* --- 书评卡片 --- */
.review-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
}

.review-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.review-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.reviewer-avatar-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 15px;
  border: 2px solid #f5ebe0;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.reviewer-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.reviewer-info {
  flex: 0;
}

.reviewer-nickname {
  font-weight: 600;
  color: #5d4037;
  margin-bottom: 5px;
  display: block;
}

.review-meta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.review-rating {
  color: #d4a017;
}

.star {
  color: #d7ccc8;
  font-size: 0.9rem;
}

.star.filled {
  color: #d4a017;
}

.review-time {
  font-size: 0.85rem;
  color: #a1887f;
}

.review-content {
  margin-bottom: 15px;
}

.review-text {
  color: #4e342e;
  line-height: 1.7;
  margin: 0;
}

.review-footer {
  display: flex;
  gap: 20px;
}

.review-action {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #8d6e63;
  font-size: 0.9rem;
}

.action-icon {
  font-size: 1rem;
}

.review-corner {
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 30px 30px 0;
  border-color: transparent #8d6e63 transparent transparent;
}

/* --- 空状态 --- */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin: 20px 0;
}

.empty-icon {
  font-size: 3rem;
  color: #bcaaa4;
  margin-bottom: 15px;
}

.empty-text {
  color: #8d6e63;
  font-size: 1.1rem;
  margin: 0;
}

/* --- 响应式设计 --- */
@media (max-width: 992px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
  }

  .classic-nav {
    margin-bottom: 30px;
  }
}

@media (max-width: 768px) {
  .establishment-container {
    padding: 15px;
  }

  .content-area {
    padding: 20px;
  }

  .avatar-section {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .book-gallery {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }

  .review-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .reviewer-avatar-wrapper {
    margin-bottom: 15px;
  }
}

@media (max-width: 480px) {
  .main-heading {
    font-size: 2rem;
  }

  .chapter-title {
    font-size: 1.5rem;
  }

  .book-gallery {
    grid-template-columns: 1fr;
  }
}
</style>
