<template>
  <div class="user-dashboard-container">
    <h1 class="dashboard-title">欢迎回来, {{ user.nickname || '用户' }}!</h1>

    <div class="user-profile-section">
      <div class="avatar-wrapper">
        <img :src="user.avatar_url || 'https://via.placeholder.com/150'" alt="用户头像" class="user-avatar" />
        <input type="file" @change="handleAvatarChange" accept="image/*" class="avatar-upload-input" />
        <button @click="uploadAvatar" :disabled="!selectedAvatarFile" class="btn-upload-avatar">上传头像</button>
      </div>
      <div class="profile-info">
        <div class="info-item">
          <label for="nickname">昵称:</label>
          <input type="text" id="nickname" v-model="editableNickname" :disabled="!isEditingNickname" />
          <button @click="toggleEditNickname" class="btn-edit">
            {{ isEditingNickname ? '保存' : '编辑' }}
          </button>
        </div>
        <p class="user-email">邮箱: {{ user.email }}</p>
      </div>
    </div>

    <hr class="section-divider" />

    <section class="favorite-books-section">
      <h2 class="section-heading">我的收藏图书 ({{ favoriteBooks.length }})</h2>
      <div v-if="favoriteBooks.length > 0" class="books-grid">
        <div v-for="book in favoriteBooks" :key="book.book_id" class="book-card">
          <img :src="book.cover_img || 'https://via.placeholder.com/100x150'" :alt="book.title" class="book-cover" />
          <div class="book-info">
            <h3>{{ book.title }}</h3>
            <p>作者: {{ book.author }}</p>
            <p>收藏时间: {{ formatDate(book.add_time) }}</p>
            <button @click="removeFavoriteBook(book.book_id)" class="btn-remove">移除</button>
          </div>
        </div>
      </div>
      <p v-else class="no-data-message">您还没有收藏任何图书。</p>
    </section>

    <hr class="section-divider" />

    <section class="favorite-reviews-section">
      <h2 class="section-heading">我的收藏书评 ({{ favoriteReviews.length }})</h2>
      <div v-if="favoriteReviews.length > 0" class="reviews-list">
        <div v-for="review in favoriteReviews" :key="review.review_id" class="review-card">
          <h3>书评标题: {{ review.book_title }}</h3> <p class="review-content">{{ truncateContent(review.content) }}</p>
          <p class="review-meta">
            评分: {{ review.rating }} | 点赞: {{ review.like_count }} | 收藏时间: {{ formatDate(review.add_time) }}
          </p>
          <button @click="removeFavoriteReview(review.review_id)" class="btn-remove">移除</button>
        </div>
      </div>
      <p v-else class="no-data-message">您还没有收藏任何书评。</p>
    </section>
  </div>
</template>

<script>
import axios from 'axios'; // 确保你已经安装了axios: npm install axios

export default {
  name: 'UserDashboard',
  data() {
    return {
      user: {
        user_id: '',
        nickname: '',
        email: '',
        avatar_url: '',
      },
      favoriteBooks: [],
      favoriteReviews: [],
      isEditingNickname: false,
      editableNickname: '',
      selectedAvatarFile: null,
    };
  },
  created() {
    // 组件创建时加载用户数据
    this.fetchUserData();
    this.fetchFavoriteBooks();
    this.fetchFavoriteReviews();
  },
  methods: {
    async fetchUserData() {
      const userId = localStorage.getItem('user_id'); // 从本地存储获取用户ID
      if (!userId) {
        console.error('User ID not found in localStorage. Redirecting to login.');
        this.$router.push('/login'); // 如果没有用户ID，重定向到登录页
        return;
      }
      try {
        // 假设你的后端有一个获取用户信息的API
        const response = await axios.get(`/service-a/api/users/${userId}`);
        this.user = response.data;
        this.editableNickname = this.user.nickname;
      } catch (error) {
        console.error('Error fetching user data:', error);
        // 处理错误，例如显示消息或重定向
      }
    },
    async fetchFavoriteBooks() {
      const userId = localStorage.getItem('user_id');
      if (!userId) return;
      try {
        // 假设你的后端有一个获取用户收藏图书的API
        const response = await axios.get(`/service-a/api/users/${userId}/favorite_books`);
        this.favoriteBooks = response.data;
      } catch (error) {
        console.error('Error fetching favorite books:', error);
      }
    },
    async fetchFavoriteReviews() {
      const userId = localStorage.getItem('user_id');
      if (!userId) return;
      try {
        // 假设你的后端有一个获取用户收藏书评的API
        const response = await axios.get(`/service-a/api/users/${userId}/favorite_reviews`);
        this.favoriteReviews = response.data;
      } catch (error) {
        console.error('Error fetching favorite reviews:', error);
      }
    },
    toggleEditNickname() {
      if (this.isEditingNickname) {
        // 保存昵称
        this.updateNickname();
      }
      this.isEditingNickname = !this.isEditingNickname;
    },
    async updateNickname() {
      try {
        const userId = localStorage.getItem('user_id');
        if (!userId) return;
        // 假设你的后端有一个更新用户昵称的API
        await axios.put(`/service-a/api/users/${userId}/nickname`, { nickname: this.editableNickname });
        this.user.nickname = this.editableNickname; // 更新本地数据
        alert('昵称更新成功！');
      } catch (error) {
        console.error('Error updating nickname:', error);
        alert('昵称更新失败。');
      }
    },
    handleAvatarChange(event) {
      this.selectedAvatarFile = event.target.files[0];
    },
    async uploadAvatar() {
      if (!this.selectedAvatarFile) {
        alert('请选择一个头像文件。');
        return;
      }
      try {
        const userId = localStorage.getItem('user_id');
        if (!userId) return;
        const formData = new FormData();
        formData.append('avatar', this.selectedAvatarFile);
        // 假设你的后端有一个上传头像的API
        const response = await axios.post(`/service-a/api/users/${userId}/avatar`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.user.avatar_url = response.data.avatar_url; // 更新本地头像URL
        this.selectedAvatarFile = null; // 清除已选择的文件
        alert('头像上传成功！');
      } catch (error) {
        console.error('Error uploading avatar:', error);
        alert('头像上传失败。');
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString(); // 或者根据需要格式化
    },
    truncateContent(content, maxLength = 100) {
      if (!content) return '';
      if (content.length > maxLength) {
        return content.substring(0, maxLength) + '...';
      }
      return content;
    },
  },
};
</script>

<style scoped>
.user-dashboard-container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  font-family: 'Arial', sans-serif;
  color: #333;
}

.dashboard-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 40px;
  font-size: 2.5em;
  font-weight: 700;
  letter-spacing: 1px;
}

.user-profile-section {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 30px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.avatar-wrapper {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #42b983;
  flex-shrink: 0;
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-upload-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.btn-upload-avatar {
  margin-top: 10px;
  padding: 8px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-upload-avatar:hover {
  background-color: #0056b3;
}

.btn-upload-avatar:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.profile-info {
  flex-grow: 1;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.info-item label {
  font-weight: bold;
  margin-right: 10px;
  color: #555;
  min-width: 60px;
}

.info-item input[type="text"] {
  flex-grow: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1.1em;
  color: #333;
  transition: border-color 0.3s ease;
}

.info-item input[type="text"]:focus {
  border-color: #42b983;
  outline: none;
}

.info-item input[type="text"]:disabled {
  background-color: #f0f0f0;
  cursor: default;
}

.btn-edit {
  margin-left: 15px;
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease;
}

.btn-edit:hover {
  background-color: #369c72;
}

.user-email {
  color: #777;
  font-size: 0.95em;
  margin-left: 70px; /* Aligns with nickname input */
}

.section-divider {
  border: 0;
  height: 1px;
  background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0));
  margin: 40px 0;
}

.section-heading {
  color: #2c3e50;
  margin-bottom: 25px;
  font-size: 2em;
  border-bottom: 2px solid #42b983;
  padding-bottom: 10px;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.book-card {
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  padding: 15px;
  transition: transform 0.2s ease-in-out;
}

.book-card:hover {
  transform: translateY(-5px);
}

.book-cover {
  width: 90px;
  height: 130px;
  object-fit: cover;
  border-radius: 5px;
  margin-right: 15px;
  flex-shrink: 0;
}

.book-info {
  flex-grow: 1;
}

.book-info h3 {
  margin-top: 0;
  margin-bottom: 8px;
  color: #333;
  font-size: 1.2em;
}

.book-info p {
  margin: 4px 0;
  color: #666;
  font-size: 0.9em;
}

.reviews-list {
  display: grid;
  gap: 20px;
}

.review-card {
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 20px;
  transition: transform 0.2s ease-in-out;
}

.review-card:hover {
  transform: translateY(-5px);
}

.review-card h3 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  font-size: 1.3em;
}

.review-content {
  font-size: 1em;
  line-height: 1.6;
  color: #555;
  margin-bottom: 15px;
}

.review-meta {
  font-size: 0.85em;
  color: #888;
  margin-bottom: 15px;
}

.btn-remove {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-remove:hover {
  background-color: #c82333;
}

.no-data-message {
  text-align: center;
  color: #777;
  font-style: italic;
  padding: 20px;
  background-color: #eef;
  border-radius: 8px;
  margin-top: 20px;
}
</style>