<template>
  <div class="user-dashboard">
    <h2>用户仪表盘</h2>

    <section class="user-info">
      <h3>个人信息</h3>
      <div class="avatar-section">
        <img :src="user.avatar_url || 'https://via.placeholder.com/150'" alt="用户头像" class="user-avatar" />
        <input type="file" @change="handleAvatarChange" accept="image/*" />
        <button @click="uploadAvatar">上传头像</button>
      </div>
      <p>
        昵称:
        <span v-if="!isEditingNickname">{{ user.nickname }}</span>
        <input v-else type="text" v-model="editableNickname" />
        <button @click="toggleEditNickname">{{ isEditingNickname ? '保存' : '编辑' }}</button>
      </p>
      <p>邮箱: {{ user.email }}</p>
      <p v-if="!user.is_profile_complete" class="profile-incomplete-warning">
        您的资料未完善，请前往 <router-link to="/user-onboarding">完善资料</router-link>
      </p>
    </section>

    <hr>

    <section class="favorite-books">
      <h3>我收藏的图书 ({{ favoriteBooks.length }})</h3>
      <div v-if="favoriteBooks.length === 0">
        <p>您还没有收藏任何图书。</p>
      </div>
      <ul v-else class="book-list">
        <li v-for="book in favoriteBooks" :key="book.bookId" @click="goToBookDetails(book.bookId)" class="book-item">
          <img :src="book.coverUrl || 'https://via.placeholder.com/100'" alt="图书封面" class="book-cover" />
          <div class="book-details">
            <h4>{{ book.title }}</h4>
            <p>作者: {{ book.author }}</p>
            <p>出版社: {{ book.publisher }}</p>
          </div>
        </li>
      </ul>
    </section>

    <hr>

    <section class="favorite-reviews">
      <h3>我收藏的书评 ({{ favoriteReviews.length }})</h3>
      <div v-if="favoriteReviews.length === 0">
        <p>您还没有收藏任何书评。</p>
      </div>
      <ul v-else class="review-list">
        <li v-for="review in favoriteReviews" :key="review.id" @click="goToBookDetails(review.bookId)"
          class="review-item">
          <div class="review-header">
            <img :src="review.reviewerAvatarUrl || 'https://via.placeholder.com/50'" alt="评论者头像"
              class="reviewer-avatar" />
            <span class="reviewer-nickname">{{ review.reviewerNickname || '匿名用户' }}</span>
            <span class="review-rating">评分: {{ review.rating }} / 5</span>
            <span class="review-time">{{ formatDate(review.postTime) }}</span>
          </div>
          <p class="review-content">{{ truncateContent(review.content) }}</p>
          <div class="review-actions">
            <span>👍 {{ review.likeCount || 0 }}</span>
            <span>⭐ {{ review.collectCount || 0 }}</span>
          </div>
        </li>
      </ul>
    </section>
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
      user: {
        user_id: '',
        nickname: '',
        email: '',
        avatar_url: '',
        is_profile_complete: false,
      },
      favoriteBooks: [],
      favoriteReviews: [],
      isEditingNickname: false,
      editableNickname: '',
      selectedAvatarFile: null,
    };
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  created() {
    this.fetchUserData();
    this.fetchFavoriteBooks();
    this.fetchFavoriteReviews();
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
/* 你的样式保持不变 */
.user-dashboard {
  max-width: 900px;
  margin: 40px auto;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.user-dashboard h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 2.2em;
}

section {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  margin-bottom: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

section h3 {
  color: #007bff;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
  font-size: 1.6em;
}

/* User Info Section */
.user-info p {
  margin-bottom: 10px;
  font-size: 1.1em;
  color: #555;
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info input[type="text"] {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.user-info button {
  padding: 8px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-info button:hover {
  background-color: #0056b3;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.user-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #eee;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
}

.avatar-section input[type="file"] {
  flex-grow: 1;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 5px;
  background-color: #f0f0f0;
}

/* Book and Review Lists */
.book-list,
.review-list {
  list-style: none;
  padding: 0;
}

.book-item,
.review-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.book-item:last-child,
.review-item:last-child {
  border-bottom: none;
}

.book-item:hover,
.review-item:hover {
  background-color: #f6f6f6;
}

.book-cover {
  width: 80px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  margin-right: 15px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.book-details h4 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 1.2em;
}

.book-details p {
  margin: 0;
  color: #777;
  font-size: 0.95em;
}

.reviewer-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 10px;
}

.review-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.reviewer-nickname {
  font-weight: bold;
  color: #333;
  margin-right: 10px;
}

.review-rating {
  font-size: 0.9em;
  color: #f39c12;
  margin-right: 10px;
}

.review-time {
  font-size: 0.85em;
  color: #999;
}

.review-content {
  font-size: 1em;
  color: #444;
  line-height: 1.5;
  margin-top: 5px;
}

.review-actions span {
  margin-right: 15px;
  font-size: 0.9em;
  color: #666;
}

.profile-incomplete-warning {
  color: orange;
  font-weight: bold;
  margin-top: 15px;
}

.profile-incomplete-warning a {
  color: #007bff;
  text-decoration: underline;
}
</style>
