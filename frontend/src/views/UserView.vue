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
    </section>

    ---

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

    ---

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
      favoriteBooks: [], // 存储用户收藏的图书详情
      favoriteReviews: [], // 存储用户收藏的书评详情
      isEditingNickname: false,
      editableNickname: '',
      selectedAvatarFile: null,
    };
  },
  created() {
    this.fetchUserData();
    this.fetchFavoriteBooks();
    this.fetchFavoriteReviews();
  },
  methods: {
    // 获取用户基本信息
    async fetchUserData() {
      const userId = localStorage.getItem('user_id');
      if (!userId) {
        console.error('User ID not found in localStorage. Redirecting to login.');
        this.$router.push('/login');
        return;
      }
      try {
        // 假设 service-a 是用户管理服务
        const response = await axios.get(`/service-a/api/users/${userId}`);
        this.user = response.data;
        this.editableNickname = this.user.nickname;
        localStorage.setItem('user_nickname', this.user.nickname); // 确保本地存储也更新
        localStorage.setItem('user_avatar_url', this.user.avatar_url); // 确保本地存储也更新
      } catch (error) {
        console.error('Error fetching user data:', error);
        // 如果用户信息获取失败，可能是用户未登录或会话过期，可以提示并重定向
        alert('获取用户信息失败，请重新登录。');
        this.$router.push('/login');
      }
    },

    // 获取用户收藏的图书列表并获取详细信息
    async fetchFavoriteBooks() {
      const userId = localStorage.getItem('user_id');
      if (!userId) return;
      try {
        // 首先从 service-c (user_engagement_service) 获取收藏的 book_id 列表
        // 注意：这里 /api/books/favorite_books 是我上面建议你新增的后端路由
        const bookIdsResponse = await axios.get(`/service-c/api/books/favorite_books`, {
          params: { userId }
        });
        const bookIds = bookIdsResponse.data;
        console.log(bookIds)
        if (bookIds.length > 0) {
          // 然后，根据这些 book_id 去 service-b (Book Management Service) 获取图书的详细信息
          // 假设 service-b 有一个批量获取图书信息的API，或者你可以循环调用
          // 这里我们假设 service-b 有一个 /api/books/batch?ids=id1,id2 的接口
          // 如果没有，你需要逐个ID请求或者让后端 service-c 聚合数据
          const booksDetailResponse = await axios.get(`/service-b/api/books/batch`, {
            params: {
              ids: bookIds.join(',') // 拼接成逗号分隔的字符串
            }
          });
          this.favoriteBooks = booksDetailResponse.data; // 假设返回的是图书对象数组
        } else {
          this.favoriteBooks = [];
        }
      } catch (error) {
        console.error('Error fetching favorite books:', error);
        this.favoriteBooks = []; // 出现错误时清空列表
      }
    },

    // 获取用户收藏的书评列表并获取详细信息
    async fetchFavoriteReviews() {
      const userId = localStorage.getItem('user_id');
      console.log(userId)
      if (!userId) return;
      try {
        // 首先从 service-c (user_engagement_service) 获取收藏的 review_id 列表
        // 注意：这里 /api/reviews/favorite_reviews 是我上面建议你新增的后端路由
        const reviewIdsResponse = await axios.get(`/service-c/api/reviews/favorite_reviews`, {
          params: { userId }
        });
        const reviewIds = reviewIdsResponse.data;
        console.log(reviewIds)
        if (reviewIds.length > 0) {
          // 然后，根据这些 review_id 去 service-c (User Engagement Service，因为它现在也处理书评内容)
          // 或者如果你的书评内容是在 service-b，则需要调用 service-b 的接口
          // 这里我们假设 service-c 有一个 /api/reviews/batch?ids=id1,id2 的接口
          const reviewsDetailResponse = await axios.get(`/service-c/api/reviews/batch`, { // 假设 service-c 也有批量获取接口
            params: {
              ids: reviewIds.join(',')
            }
          });
          // 你还需要进一步处理这些书评，获取评论者的昵称和头像
          this.favoriteReviews = await Promise.all(reviewsDetailResponse.data.map(async review => {
            // 假设你有一个获取用户信息的服务（service-a），可以根据 userId 获取昵称和头像
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
          this.favoriteReviews = [];
        }
      } catch (error) {
        console.error('Error fetching favorite reviews:', error);
        this.favoriteReviews = [];
      }
    },

    toggleEditNickname() {
      if (this.isEditingNickname) {
        this.updateNickname();
      }
      this.isEditingNickname = !this.isEditingNickname;
    },
    async updateNickname() {
      try {
        const userId = localStorage.getItem('user_id');
        if (!userId) return;
        // 假设 service-a 是用户管理服务
        await axios.put(`/service-a/api/users/${userId}/nickname`, { nickname: this.editableNickname });
        this.user.nickname = this.editableNickname; // 更新本地数据
        localStorage.setItem('user_nickname', this.editableNickname); // 同步更新 localStorage
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
        // 假设 service-a 是用户管理服务
        const response = await axios.post(`/service-a/api/users/${userId}/avatar`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.user.avatar_url = response.data.avatar_url; // 更新本地头像URL
        localStorage.setItem('user_avatar_url', this.user.avatar_url); // 同步更新 localStorage
        this.selectedAvatarFile = null; // 清除已选择的文件
        alert('头像上传成功！');
      } catch (error) {
        console.error('Error uploading avatar:', error);
        alert('头像上传失败。');
      }
    },

    // 跳转到图书详情页
    goToBookDetails(bookId) {
      // 确保 bookId 有效
      if (!bookId) {
        console.error('Tried to navigate to BookDetails with an undefined or null bookId.');
        alert('无法打开图书详情，图书ID缺失。');
        return;
      }
      this.$router.push({ name: 'BookDetails', params: { bookId: bookId } }); // <-- 将 'id' 改为 'bookId'
    },

    formatDate(dateString) {
      if (!dateString) return '';
      // 尝试解析 ISO 8601 格式，例如 "2025-07-01T12:09:08.000Z"
      const date = new Date(dateString);
      if (isNaN(date.getTime())) { // 检查是否是有效日期
        // 如果解析失败，尝试作为普通字符串返回
        return dateString;
      }
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
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
.user-dashboard {
  max-width: 900px;
  margin: 20px auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

section {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

h3 {
  color: #555;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

/* 用户信息 */
.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.user-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 10px;
  border: 2px solid #ddd;
}

.user-info p {
  margin: 10px 0;
  font-size: 1.1em;
}

.user-info input[type="text"] {
  padding: 5px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-right: 10px;
}

.user-info button {
  padding: 8px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.user-info button:hover {
  background-color: #0056b3;
}

/* 收藏列表 */
.book-list,
.review-list {
  list-style: none;
  padding: 0;
}

.book-item,
.review-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.book-item:hover,
.review-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.book-cover {
  width: 80px;
  height: 120px;
  object-fit: cover;
  margin-right: 20px;
  border-radius: 4px;
  flex-shrink: 0;
}

.book-details h4 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 1.2em;
}

.book-details p {
  margin: 0 0 3px 0;
  color: #666;
  font-size: 0.95em;
}

/* 书评特定样式 */
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
}

.reviewer-nickname {
  font-weight: bold;
  margin-right: 15px;
  color: #333;
}

.review-rating {
  background-color: #f0ad4e;
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  margin-right: 15px;
}

.review-time {
  color: #999;
  font-size: 0.85em;
}

.review-content {
  margin-bottom: 10px;
  line-height: 1.6;
  color: #444;
}

.review-actions span {
  margin-right: 15px;
  color: #777;
  font-size: 0.9em;
}
</style>