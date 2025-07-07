<!-- 书籍细节信息页面 -->
<template>
  <div class="ancient-scroll-page" v-if="book">
    <div class="main-parchment-folio">
      <div class="tome-unveiling-header">
        <div class="tome-illumination">
          <img :src="book.coverImg" :alt="book.title" class="tome-cover-illustration" />
        </div>
        <div class="tome-essential-data">
          <h1 class="tome-grand-title">{{ book.title }}</h1>
          <h2 v-if="book.series" class="tome-series-chapter">A Volume in The {{ book.series }} Chronicle</h2>
          <p class="tome-scribe">Penned by {{ book.author }}</p>

          <div class="celestial-judgement">
            <span class="stars-bestowed">{{ '★'.repeat(Math.round(book.rating)) }}{{ '☆'.repeat(5 -
              Math.round(book.rating))
            }}</span>
            <span class="whispers-of-appraisal">({{ book.rating }} from {{ book.numRatings }} Judgements)</span>
          </div>

          <div class="tome-interactive-actions">
            <button @click="toggleLike" :class="{ 'action-button': true, 'liked': isLiked }">
              <span class="icon">{{ isLiked ? '❤️' : '🤍' }}</span> {{ isLiked ? 'Liked' : 'Like' }} ({{ likeCount }})
            </button>
            <button @click="toggleCollect" :class="{ 'action-button': true, 'collected': isCollected }">
              <span class="icon">{{ isCollected ? '✅' : '➕' }}</span> {{ isCollected ? 'Collected' : 'Collect' }}
            </button>
              <button v-if="book && book.epubUrl" @click="readOnline" class="action-button">
                <span class="icon">📖</span> Read Online
              </button>
          </div>
          <div class="tome-provenance-details-grid">
            <div class="detail-item"><strong>First Inscribed:</strong> {{ book.firstPublishDate || 'Unknown' }}</div>
            <div class="detail-item"><strong>Published:</strong> {{ book.publishDate }}</div>
            <div class="detail-item"><strong>Folios:</strong> {{ book.pages }}</div>
            <div class="detail-item"><strong>Appraisal:</strong> ${{ book.price }}</div>
            <div class="detail-item" v-if="book.language"><strong>Tongue:</strong> {{ book.language }}</div>
            <div class="detail-item" v-if="book.isbn"><strong>Cipher (ISBN):</strong> {{ book.isbn }}</div>
            <div class="detail-item" v-if="book.bookFormat"><strong>Form:</strong> {{ book.bookFormat }}</div>
            <div class="detail-item" v-if="book.edition"><strong>Edition:</strong> {{ book.edition }}</div>
            <div class="detail-item" v-if="book.publisher"><strong>Printer:</strong> {{ book.publisher }}</div>
            <div class="detail-item" v-if="book.bbeScore"><strong>BBE Oracle Score:</strong> {{ book.bbeScore }} (from
              {{
                book.bbeVotes }} Voices)</div>
          </div>

          <div class="scholarly-genres-seals">
            <span v-for="genre in book.genres" :key="genre" class="genre-crest">{{ genre }}</span>
          </div>
        </div>
      </div>

      <div class="tome-narrative-summary">
        <h3 class="section-heading">The Chronicle's Essence</h3>
        <p class="summary-parchment">
          {{ displayDescription }}
          <span v-if="shouldShowDescriptionToggle" @click="toggleDescription" class="toggle-text-button">
            {{ showFullDescription ? 'Show Less' : 'Show More' }}
          </span>
        </p>
      </div>

      <div class="tome-additional-annotations">
        <div v-if="book.characters && book.characters.length > 0">
          <h3 class="section-heading">Notable Figures Within</h3>
          <div class="characters-of-note">
            <span v-for="character in book.characters" :key="character" class="character-sigil">{{ character
              }}</span>
          </div>
        </div>

        <div v-if="book.setting && book.setting.length > 0">
          <h3 class="section-heading">Realms & Locales Described</h3>
          <div class="settings-of-the-tale">
            <span v-for="loc in book.setting" :key="loc" class="setting-marker">{{ loc }}</span>
          </div>
        </div>

        <div v-if="book.awards && book.awards.length > 0">
          <h3 class="section-heading">Laurels & Distinctions Awarded</h3>
          <ul class="laurels-list">
            <li v-for="(award, index) in displayAwards" :key="index">{{ award }}</li>
            <li v-if="shouldShowAwardsToggle" @click="toggleAwards" class="toggle-list-item">
              <a href="#" class="toggle-text-button">{{ showAllAwards ? 'Show Less' : 'Show More' }}</a>
            </li>
          </ul>
        </div>

        <div v-if="book.likedPercent || (book.ratingsByStars && Object.keys(book.ratingsByStars).length > 0)"
          class="readership-stats-group">
          <h3 class="section-heading">Affection & Distribution of Critiques</h3>
          <div class="stats-content-flex">
            <div v-if="book.likedPercent" class="affection-measure-container">
              <p class="affection-measure">{{ book.likedPercent }}% of Readers Hold This Tome Dearly.</p>
            </div>

            <div v-if="book.ratingsByStars && Object.keys(book.ratingsByStars).length > 0"
              class="critique-distribution">
              <div v-for="(count, star) in book.ratingsByStars" :key="star" class="star-critique-row">
                <span>{{ star }} Stars:</span>
                <div class="star-bar-scroll-container">
                  <div class="star-bar-illumination" :style="{ width: (count / book.numRatings * 100) + '%' }"></div>
                </div>
                <span>({{ count }})</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="tome-reviews-section">
        <h3 class="section-heading">Reader's Reflections</h3>

        <div class="review-submission-form">
          <h4>Pen Your Own Reflection</h4>
          <textarea v-model="newReviewContent" placeholder="Share your thoughts on this tome..." rows="5"
            class="review-textarea"></textarea>
          <div class="review-rating-input">
            <label for="review-rating">Your Appraisal:</label>
            <select v-model.number="newReviewRating" id="review-rating" class="review-rating-select">
              <option value="0" disabled>Select a rating</option>
              <option v-for="n in 5" :key="n" :value="n">{{ n }} Star{{ n > 1 ? 's' : '' }}</option>
            </select>
          </div>
          <button @click="submitReview" class="submit-review-button">Inscribe Your Review</button>
        </div>

        <div class="existing-reviews-list">
          <p v-if="bookReviews.length === 0" class="no-reviews-message">No reflections penned yet. Be the first!</p>
          <div v-for="review in bookReviews" :key="review.id" class="review-entry">
            <div class="review-header">
              <span class="reviewer-name">{{ review.reviewerName }}</span>
              <span class="review-date">{{ new Date(review.datePosted).toLocaleDateString() }}</span>
              <span class="review-stars">{{ '★'.repeat(review.rating) }}{{ '☆'.repeat(5 - review.rating) }}</span>
            </div>
            <p class="review-content">{{ review.content }}</p>
            <div class="review-actions">
              <button @click="toggleReviewLike(review)"
                :class="{ 'review-action-button': true, 'liked': review.isLikedByCurrentUser }">
                <span class="icon">{{ review.isLikedByCurrentUser ? '❤️' : '🤍' }}</span> Like ({{ review.likeCount }})
              </button>
              <button @click="toggleReviewCollect(review)"
                :class="{ 'review-action-button': true, 'collected': review.isCollectedByCurrentUser }">
                <span class="icon">{{ review.isCollectedByCurrentUser ? '✅' : '➕' }}</span> Collect ({{
                  review.collectCount }})
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="tome-actions">
        <button @click="goBack" class="return-to-catalogue-button">Return to the Grand Catalogue</button>
      </div>
    </div>

    <div class="scribe-notes-sidebar">
      <div class="oracle-douban-section">
        <div class="sidebar-section-header" @click="toggleDoubanResults">
          <h2 class="sidebar-section-title">Douban Oracle's Prophecies <span class="toggle-rune">{{ showDoubanResults ?
            '▼' : '▶' }}</span></h2>
        </div>
        <transition name="unfurl-scroll">
          <div v-show="showDoubanResults" class="oracle-results-container">
            <ul v-if="doubanSearchResults.length > 0" class="oracle-findings-list">
              <li v-for="(doubanBook, index) in doubanSearchResults" :key="index" class="oracle-finding-item">
                <a :href="doubanBook.link" target="_blank" rel="noopener noreferrer" class="oracle-link">
                  {{ doubanBook.title }}
                </a>
                <span class="douban-oracle-rating" v-if="doubanBook.rating">
                  {{ '★'.repeat(Math.round(doubanBook.rating)) }}{{ '☆'.repeat(5 - Math.round(doubanBook.rating)) }}
                  ({{ doubanBook.rating }})
                </span>
              </li>
            </ul>
            <p v-else-if="searched && doubanSearchResults.length === 0" class="no-oracle-findings">
              The Oracle finds no kindred spirits on Douban.
            </p>
          </div>
        </transition>
      </div>

      <div class="scribe-notes-section">
        <h3 class="sidebar-section-title">Further Recommendations</h3>
        <p class="sidebar-text">More recommended chronicles to behold...</p>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="scribe-at-work">
    The Scribe is diligently retrieving the Tome's details...
  </div>
  <div v-else class="tome-vanished">
    Alas, this Tome has vanished from our collection.
  </div>
</template>

<script>
import axios from 'axios';
import { trackPageView, trackButtonClick } from '../services/logger.js';

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
  name: 'BookDetails',
  data() {
    return {
      book: null,
      loading: true,
      doubanSearchResults: [],
      searched: false,
      showDoubanResults: true,
      isLiked: false,
      likeCount: 0,
      isCollected: false,
      bookReviews: [],
      newReviewContent: '',
      newReviewRating: 0,
      showFullDescription: false,
      descriptionLimit: 300,
      showAllAwards: false,
      awardsLimit: 3,
      // currentUserNickname 和 currentUserAvatar 可以直接通过 computed 属性获取
    };
  },
  
  computed: {
    // **核心修改：从 'user_data' 获取 userId**
    currentUserId() {
      const userData = getParsedUserData();
      return userData ? userData.user_id : null;
    },
    // **核心修改：从 'user_data' 获取 nickname**
    getCurrentUserNickname() {
      const userData = getParsedUserData();
      return userData ? (userData.nickname || userData.email || '访客') : '访客'; // 提供 email 作为备用，或直接 '访客'
    },
    // **核心修改：从 'user_data' 获取 avatar_url**
    getCurrentUserAvatar() {
      const userData = getParsedUserData();
      return userData ? (userData.avatar_url || 'https://via.placeholder.com/150') : 'https://via.placeholder.com/150';
    },
    displayDescription() {
      if (!this.book || !this.book.description) return '';
      if (this.showFullDescription || this.book.description.length <= this.descriptionLimit) {
        return this.book.description;
      }
      return this.book.description.substring(0, this.descriptionLimit) + '...';
    },
    shouldShowDescriptionToggle() {
      return this.book && this.book.description && this.book.description.length > this.descriptionLimit;
    },
    displayAwards() {
      if (!this.book || !this.book.awards) return [];
      if (this.showAllAwards || this.book.awards.length <= this.awardsLimit) {
        return this.book.awards;
      }
      return this.book.awards.slice(0, this.awardsLimit);
    },
    shouldShowAwardsToggle() {
      return this.book && this.book.awards && this.book.awards.length > this.awardsLimit;
    }
  },
  //埋点
  mounted() {
    this.pageViewStartTime = Date.now();
    this.pageUrlOnMount = window.location.href; // 【新增】在挂载时捕获URL
  },
  beforeUnmount() {
    const endTime = Date.now();
    const dwellTimeInSeconds = Math.round((endTime - this.pageViewStartTime) / 1000);

    // 【修改】调用 logger.js 中的函数，显式传递页面名称和捕获的URL
    trackPageView('BookDetails', dwellTimeInSeconds, this.pageUrlOnMount);
  },
  async created() {
    await this.fetchBookDetails();
    if (this.book && this.book.bookId) {
      // 新增：在获取到书籍详情后，记录浏览事件
      console.log("在获取到书籍详情后，记录浏览事件")
      trackBookView(this.book.bookId);

      await this.fetchBookReviews();
      await this.fetchUserEngagementStatus();
      await this.performDoubanSearch(this.book.title);
    }
  },
  methods: {
    async fetchBookDetails() {
      this.loading = true;
      try {
        const bookId = this.$route.params.bookId;
        const response = await axios.get(`/service-b/api/books/${bookId}`);
        this.book = response.data;

        // ======================== 前端测试代码块 (开始) ========================
        // 为了在没有后端支持的情况下测试，为特定 ID 的书籍手动添加 epubUrl
        if (bookId === "41865.Twilight") {
          console.warn("--- 前端测试 ---: 正在为书籍 " + bookId + " 注入模拟的 EPUB 链接。");
          // this.$set 是一个 Vue 方法，确保向响应式对象添加新属性时，视图也能更新
          this.book.epubUrl = '/TestEpub/Twilight.epub'; 

        }
      } catch (error) {
        console.error('Error fetching book details:', error);
        this.book = null;
      } finally {
        this.loading = false;
      }
    },

    // 线上阅读功能
    readOnline() {
      if (!this.book || !this.book.bookId) return;
      this.$router.push({ name: 'EpubReader', params: { bookId: this.book.bookId } });
    },

    async fetchUserEngagementStatus() {
      const userId = this.currentUserId;
      const bookId = this.book.bookId;

      // 始终尝试获取书籍的总点赞数和总收藏数
      try {
        const likeCountResponse = await axios.get(`/service-c/api/books/${bookId}/total_likes`);
        this.likeCount = likeCountResponse.data.totalLikeCount;
      } catch (error) {
        console.error('Error fetching total like count:', error);
        this.likeCount = 0;
      }

      // 如果需要显示总收藏数，也同样添加一个调用
      // try {
      //   const favoriteCountResponse = await axios.get(`/service-c/api/books/${bookId}/total_favorites`);
      //   // 假设你有一个 data 属性叫做 totalCollectCount 或者直接更新 this.book.collectCount
      //   // this.totalCollectCount = favoriteCountResponse.data.totalFavoriteCount;
      // } catch (error) {
      //   console.error('Error fetching total favorite count:', error);
      // }

      // 如果用户未登录，仅显示总数，个人状态保持默认值并提前返回
      if (!userId) {
        console.log("User not logged in. Displaying total counts only.");
        this.isLiked = false;
        this.isCollected = false;
        return;
      }

      // 如果用户已登录，则获取用户的点赞和收藏状态
      try {
        const likeStatusResponse = await axios.get(`/service-c/api/books/${bookId}/like_status`, {
          params: { userId }
        });
        this.isLiked = likeStatusResponse.data.isLiked;
        // this.likeCount = likeStatusResponse.data.likeCount; // 可选：如果后端在个人状态接口也返回了总数，可以再次更新
      } catch (error) {
        console.error('Error fetching user like status:', error);
        this.isLiked = false;
      }

      try {
        const collectStatusResponse = await axios.get(`/service-c/api/books/${bookId}/favorite_status`, {
          params: { userId }
        });
        this.isCollected = collectStatusResponse.data.isFavorited;
      } catch (error) {
        console.error('Error fetching user collect status:', error);
        this.isCollected = false;
      }
    },
    async toggleLike() {
      //喜欢按钮埋点
       trackButtonClick('LikeButton', 'BookDetails', { bookId: this.book?.bookId });
      
       if (!this.book || !this.book.bookId) return;

      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能点赞！');
        return;
      }
      const endpoint = `/service-c/api/books/${this.book.bookId}/like`;

      try {
        const response = await axios.post(endpoint, { userId });
        this.isLiked = response.data.isLiked;
        this.likeCount = response.data.likeCount;
        console.log(`Book ${this.isLiked ? 'liked' : 'unliked'}! Current likes: ${this.likeCount}`);
      } catch (error) {
        console.error('Error toggling book like status:', error);
        alert('Failed to update book like status. Please try again.');
      }
    },
    async toggleCollect() {
      //收藏按钮埋点
      trackButtonClick('CollectButton', 'BookDetails', { bookId: this.book?.bookId });
      if (!this.book || !this.book.bookId) return;

      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能收藏！');
        return;
      }
      const endpoint = `/service-c/api/books/${this.book.bookId}/favorite`;

      try {
        const response = await axios.post(endpoint, { userId });
        this.isCollected = response.data.isFavorited;
        console.log(`Book ${this.isCollected ? 'collected' : 'uncollected'}!`);
      } catch (error) {
        console.error('Error toggling book collect status:', error);
        alert('Failed to update book collection status. Please try again.');
      }
    },
    async fetchBookReviews() {
      if (!this.book || !this.book.bookId) return;
      const bookId = this.book.bookId;
      const userId = this.currentUserId; // 获取当前用户ID，用于判断点赞/收藏状态

      try {
        const reviewsResponse = await axios.get(`/service-c/api/books/${bookId}/reviews`);

        this.bookReviews = await Promise.all(reviewsResponse.data.map(async review => {
          let isLikedByCurrentUser = false;
          let likeCount = review.likeCount || 0; // 优先使用后端返回的likeCount
          let isCollectedByCurrentUser = false;
          let collectCount = review.collectCount || 0; // 优先使用后端返回的collectCount

          let reviewerNickname = '匿名用户';
          let reviewerAvatarUrl = 'https://via.placeholder.com/50';

          // 获取评论者的昵称和头像
          try {
            const userProfile = await axios.get(`/service-a/api/users/${review.userId}`);
            reviewerNickname = userProfile.data.nickname || '匿名用户';
            reviewerAvatarUrl = userProfile.data.avatar_url || 'https://via.placeholder.com/50';
          } catch (userError) {
            console.warn(`Could not fetch user info for review userId ${review.userId}:`, userError);
          }

          // 只有当用户登录时才查询其个人对书评的点赞/收藏状态
          if (userId) {
            try {
              const reviewLikeStatus = await axios.get(`/service-c/api/reviews/${review.id}/like_status`, {
                params: { userId }
              });
              isLikedByCurrentUser = reviewLikeStatus.data.isLiked;
              likeCount = reviewLikeStatus.data.likeCount; // 更新为用户个人状态返回的最新总数
            } catch (likeError) {
              console.warn(`Could not fetch like status for review ${review.id}:`, likeError);
            }

            try {
              const reviewFavoriteStatus = await axios.get(`/service-c/api/reviews/${review.id}/favorite_status`, {
                params: { userId }
              });
              isCollectedByCurrentUser = reviewFavoriteStatus.data.isFavorited;
              collectCount = reviewFavoriteStatus.data.favoriteCount; // 更新为用户个人状态返回的最新总数
            } catch (favError) {
              console.warn(`Could not fetch favorite status for review ${review.id}:`, favError);
            }
          }

          return {
            ...review,
            reviewerNickname,
            reviewerAvatarUrl,
            likeCount, // 使用更新后的 likeCount
            isLikedByCurrentUser,
            collectCount, // 使用更新后的 collectCount
            isCollectedByCurrentUser,
          };
        }));
        console.log('Fetched reviews:', this.bookReviews);
      } catch (error) {
        console.error('Error fetching book reviews:', error);
        this.bookReviews = [];
      }
    },
    async submitReview() {
      //提交书评埋点
      trackButtonClick('SubmitReview', 'BookDetails', { bookId: this.book?.bookId });
      if (!this.book || !this.book.bookId) return;
      const bookId = this.book.bookId;

      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能提交评论！');
        return;
      }

      if (!this.newReviewContent.trim() || this.newReviewRating === 0) {
        alert('请输入评论内容并选择评分。');
        return;
      }

      try {
        const response = await axios.post(`/service-c/api/books/${bookId}/reviews`, {
          userId: userId,
          content: this.newReviewContent,
          rating: this.newReviewRating,
        });
        console.log('Review submitted:', response.data);
        alert('评论提交成功！');
        this.newReviewContent = '';
        this.newReviewRating = 0;
        this.fetchBookReviews();
      } catch (error) {
        console.error('Error submitting review:', error);
        alert('提交评论失败，请重试。');
      }
    },
    async deleteReview(reviewId) {
      const userId = this.currentUserId;

      if (!userId) {
        alert('请先登录才能删除评论！');
        return;
      }

      // ⚠️ 实际应用中，你还需要一个机制来验证当前用户是否是这条评论的作者
      // 或者是一个拥有删除权限的管理员。这里为了演示简化，直接发送删除请求。
      if (!confirm('确定要删除这条评论吗？')) {
        return;
      }

      try {
        const response = await axios.delete(`/service-c/api/reviews/${reviewId}`, {
          params: { userId: userId }
        });
        console.log('Review deleted:', response.data);
        alert('评论删除成功！');
        this.fetchBookReviews();
      } catch (error) {
        console.error('Error deleting review:', error);
        alert('删除评论失败，请重试。');
      }
    },
    async toggleReviewLike(review) {
      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能点赞评论！');
        return;
      }
      const endpoint = `/service-c/api/reviews/${review.id}/like`;

      try {
        const response = await axios.post(endpoint, { userId });
        review.isLikedByCurrentUser = response.data.isLiked;
        review.likeCount = response.data.likeCount;
      } catch (error) {
        console.error('Error toggling review like status:', error);
        alert('更新评论点赞状态失败，请重试。');
      }
    },
    async toggleReviewCollect(review) {
      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能收藏评论！');
        return;
      }
      const endpoint = `/service-c/api/reviews/${review.id}/favorite`;

      try {
        const response = await axios.post(endpoint, { userId });
        review.isCollectedByCurrentUser = response.data.isFavorited;
        review.collectCount = response.data.favoriteCount;
      } catch (error) {
        console.error('Error toggling review collect status:', error);
        alert('更新评论收藏状态失败，请重试。');
      }
    },
    goBack() {
      this.$router.go(-1);
    },
    async performDoubanSearch(keyword) {
      if (!keyword.trim()) {
        console.warn('Douban search keyword is empty, skipping search.');
        return;
      }
      this.searched = true;
      this.doubanSearchResults = [];
      try {
        const response = await axios.get(
          `/service-b/api/search_douban?keyword=${encodeURIComponent(keyword)}`
        );
        this.doubanSearchResults = response.data;
      } catch (error) {
        console.error('Error fetching Douban books:', error);
      }
    },
    toggleDoubanResults() {
      this.showDoubanResults = !this.showDoubanResults;
    },
    toggleDescription() {
      this.showFullDescription = !this.showFullDescription;
    },
    toggleAwards() {
      this.showAllAwards = !this.showAllAwards;
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return dateString;
      }
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
    },
  }
};
</script>

<style scoped>
/* A Font of Ages: Evoking the Scribe's Hand */
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Playfair+Display:wght@400;700&display=swap');

/* Add some basic styling for the new buttons */
.tome-interactive-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: flex-start;
  align-items: center;
}

.action-button {
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.2s, border-color 0.2s;
}

.action-button:hover {
  background-color: #e0e0e0;
}

.action-button.liked {
  background-color: #ffebee;
  /* Light red for liked */
  border-color: #ef9a9a;
  color: #d32f2f;
  /* Darker red */
}

.action-button.collected {
  background-color: #e8f5e9;
  /* Light green for collected */
  border-color: #a5d6a7;
  color: #388e3c;
  /* Darker green */
}

.action-button .icon {
  font-size: 1.2em;
  line-height: 1;
}


/* The Ancient Scroll Layout */
.ancient-scroll-page {
  display: flex;
  max-width: 1300px;
  margin: 3rem auto;
  gap: 2.5rem;
  align-items: flex-start;
  padding: 0 1.5rem;
  font-family: 'Merriweather', serif;
  color: #3b2f2f;
  /* Deep Ink */
  position: relative;
}

/* Base Parchment Style */
.main-parchment-folio,
.scribe-notes-sidebar {
  background: #fdfaf3;
  /* Old Paper */
  border: 1px solid #d4c7b2;
  border-radius: 8px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  position: relative;
}

.main-parchment-folio {
  flex: 3;
  min-width: 65%;
}

.scribe-notes-sidebar {
  flex: 1;
  min-width: 320px;
  position: sticky;
  top: 3rem;
  height: fit-content;
}

/* Tome Unveiling Header */
.tome-unveiling-header {
  display: flex;
  gap: 2.5rem;
  margin-bottom: 2.5rem;
  align-items: flex-start;
}

.tome-illumination {
  flex-shrink: 0;
  width: 220px;
  height: 320px;
  overflow: hidden;
  background-color: #e8e0d4;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #d4c7b2;
  position: relative;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.tome-illumination::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to right, rgba(253, 250, 243, 0) 0%, rgba(253, 250, 243, 0.3) 100%);
  pointer-events: none;
}

.tome-cover-illustration {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
  transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.tome-cover-illustration:hover {
  transform: scale(1.05) rotateZ(1deg);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.tome-essential-data {
  flex-grow: 1;
}

.tome-grand-title {
  font-family: 'Playfair Display', serif;
  font-size: 2.8em;
  color: #5a4b41;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.tome-series-chapter {
  font-family: 'Merriweather', serif;
  font-size: 1.2em;
  color: #7b6a5e;
  margin-top: 0;
  margin-bottom: 1rem;
  font-style: italic;
}

.tome-scribe {
  font-size: 1.1em;
  color: #5a4b41;
  margin-bottom: 1.5rem;
}

.celestial-judgement {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.stars-bestowed {
  color: #e6b800;
  /* Gold */
  font-size: 1.8em;
  margin-right: 0.6rem;
  letter-spacing: 0.05em;
}

.whispers-of-appraisal {
  font-size: 0.95em;
  color: #8c7f73;
}

/* Optimized Provenance Details Grid */
.tome-provenance-details-grid {
  margin-top: 1.5rem;
  font-size: 0.95em;
  color: #7b6a5e;
  display: grid;
  /* Use CSS Grid for flexible columns */
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  /* Adjust minmax as needed */
  gap: 0.8rem 1.5rem;
  /* Row and column gap */
  padding-top: 1.5rem;
  border-top: 1px dashed #e0d4c0;
}

.detail-item {
  display: flex;
  /* Ensures strong and text stay on one line if possible */
  flex-wrap: wrap;
  /* Allows wrapping if content is too long */
  align-items: baseline;
  /* Aligns first line of text */
}

.detail-item strong {
  font-weight: 700;
  margin-right: 0.3em;
  /* Small space after label */
  flex-shrink: 0;
  /* Prevents label from shrinking */
}


.scholarly-genres-seals {
  margin-top: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.genre-crest,
.character-sigil,
.setting-marker {
  display: inline-block;
  background-color: #e0d4c0;
  color: #5a4b41;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  /* margin-right removed as gap handles spacing */
  /* margin-bottom removed as gap handles spacing */
  font-size: 0.85em;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 1px solid #d4c7b2;
}

.genre-crest:hover,
.character-sigil:hover,
.setting-marker:hover {
  background-color: #d4c7b2;
  transform: translateY(-2px) rotateZ(-1deg);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.tome-narrative-summary {
  margin-top: 2.5rem;
}

.section-heading {
  font-family: 'Playfair Display', serif;
  font-size: 1.8em;
  color: #5a4b41;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e0d4c0;
}

.summary-parchment {
  line-height: 1.8;
  color: #4b3e3e;
  text-align: justify;
}

.tome-additional-annotations {
  margin-top: 2.5rem;
  padding-top: 2rem;
  border-top: 1px dashed #d4c7b2;
}

.characters-of-note,
.settings-of-the-tale {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 1.5rem;
}

.laurels-list {
  list-style-type: disc;
  margin-left: 1.5rem;
  padding: 0;
  color: #5a4b41;
}

.laurels-list li {
  margin-bottom: 0.5rem;
}

/* Grouping Affection & Distribution for better layout */
.readership-stats-group {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px dashed #d4c7b2;
}

.stats-content-flex {
  display: flex;
  flex-wrap: wrap;
  /* Allow wrapping on smaller screens */
  gap: 2rem;
  /* Space between the two sections */
  align-items: flex-start;
}

.affection-measure-container {
  flex: 1;
  min-width: 250px;
  /* Ensure it doesn't get too narrow */
}

.affection-measure {
  font-size: 1em;
  color: #5a4b41;
  font-style: italic;
  margin-bottom: 1.5rem;
  /* Space before next section if stacked */
}

.critique-distribution {
  flex: 1.5;
  /* Give more space to bars */
  min-width: 300px;
  /* Ensure it doesn't get too narrow */
  margin-top: 0;
  /* Reset margin if inherited */
}

.star-critique-row {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.95em;
  color: #7b6a5e;
}

.star-critique-row span:first-child {
  width: 70px;
  flex-shrink: 0;
  font-weight: 600;
}

.star-bar-scroll-container {
  flex-grow: 1;
  background-color: #eee;
  height: 10px;
  border-radius: 5px;
  margin: 0 0.8rem;
  overflow: hidden;
  border: 1px solid #d4c7b2;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.star-bar-illumination {
  height: 100%;
  background-color: #e6b800;
  /* Gold */
  border-radius: 5px;
  transition: width 0.5s ease-out;
}

/* Actions Section */
.tome-actions {
  margin-top: 2.5rem;
  text-align: center;
  border-top: 1px dashed #e0d4c0;
  padding-top: 2rem;
}

.return-to-catalogue-button {
  padding: 0.8rem 1.8rem;
  background-color: #8d6e63;
  /* Deep Sepia */
  color: #fdfaf3;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1em;
  transition: all 0.3s ease-in-out;
  font-family: 'Playfair Display', serif;
  letter-spacing: 0.05em;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.return-to-catalogue-button:hover {
  background-color: #6d5448;
  transform: translateY(-3px) scale(1.01);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25);
}

.return-to-catalogue-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* Scribe Notes Sidebar */
.sidebar-section-header {
  cursor: pointer;
  padding: 1rem;
  background-color: #f0ebe0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  transition: background-color 0.2s ease, transform 0.2s ease;
  border: 1px solid #d4c7b2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.sidebar-section-header:hover {
  background-color: #e5e0d4;
  transform: translateY(-2px);
}

.sidebar-section-title {
  margin: 0;
  font-family: 'Playfair Display', serif;
  font-size: 1.5em;
  color: #5a4b41;
  display: flex;
  align-items: center;
  flex-grow: 1;
}

.toggle-rune {
  margin-left: 1rem;
  font-size: 0.7em;
  color: #8c7f73;
  transition: transform 0.3s ease;
}

.sidebar-section-header:hover .toggle-rune {
  transform: rotate(5deg);
}

.oracle-douban-section {
  margin-bottom: 2rem;
}

.oracle-results-container {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e0d4c0;
  box-shadow: inset 0 1px 5px rgba(0, 0, 0, 0.05);
  padding: 1.2rem 1.5rem;
}

.oracle-findings-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.oracle-finding-item {
  padding: 0.8rem 0;
  border-bottom: 1px dashed #e0d4c0;
  transition: background-color 0.2s ease;
}

.oracle-finding-item:last-child {
  border-bottom: none;
}

.oracle-finding-item:hover {
  background-color: #f9f7f0;
}

.oracle-link {
  color: #8d6e63;
  /* Deep Sepia */
  text-decoration: none;
  display: block;
  margin-bottom: 0.3rem;
  font-weight: 600;
  transition: color 0.2s ease;
}

.oracle-link:hover {
  text-decoration: underline;
  color: #6d5448;
}

.douban-oracle-rating {
  color: #e6b800;
  font-size: 0.9em;
  display: block;
}

.no-oracle-findings {
  color: #7b6a5e;
  font-style: italic;
  padding: 1rem 0;
  text-align: center;
}

.scribe-notes-section {
  padding: 1.5rem;
}

.scribe-notes-section .sidebar-section-title {
  border-bottom: 1px dashed #e0d4c0;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.sidebar-text {
  color: #5a4b41;
  font-size: 0.95em;
  line-height: 1.6;
}

/* Transition for Douban Results (Unfurl Scroll Effect) */
.unfurl-scroll-enter-active,
.unfurl-scroll-leave-active {
  transition: all 0.4s ease-out;
  max-height: 500px;
  overflow: hidden;
}

.unfurl-scroll-enter-from,
.unfurl-scroll-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-20px);
}


/* Loading and Not Found States */
.scribe-at-work,
.tome-vanished {
  text-align: center;
  padding: 5rem;
  font-size: 1.5em;
  color: #7b6a5e;
  width: 100%;
  font-family: 'Playfair Display', serif;
  font-style: italic;
}

/* Responsive Adaptations for Smaller Screens (Papyrus Roll Adjustment) */
@media (max-width: 992px) {
  .ancient-scroll-page {
    flex-direction: column;
    align-items: center;
  }

  .main-parchment-folio,
  .scribe-notes-sidebar {
    min-width: auto;
    width: 100%;
    padding: 2rem;
  }

  .scribe-notes-sidebar {
    position: static;
    margin-top: 2.5rem;
  }

  .tome-unveiling-header {
    flex-direction: column;
    align-items: center;
  }

  .tome-illumination {
    width: 250px;
    height: 350px;
    border-right: none;
    border-bottom: 1px solid #d4c7b2;
    border-radius: 8px 8px 0 0;
  }

  .tome-illumination::before {
    background: linear-gradient(to bottom, rgba(253, 250, 243, 0) 0%, rgba(253, 250, 243, 0.3) 100%);
  }

  .tome-essential-data {
    text-align: center;
  }

  .tome-grand-title {
    font-size: 2.5em;
  }

  /* Adjust provenance details for smaller screens */
  .tome-provenance-details-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    justify-items: center;
    /* Center items in the grid */
    text-align: center;
  }

  .celestial-judgement,
  .scholarly-genres-seals,
  .characters-of-note,
  .settings-of-the-tale,
  .stats-content-flex {
    justify-content: center;
  }

  .stats-content-flex {
    flex-direction: column;
    /* Stack on smaller screens */
    align-items: center;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .ancient-scroll-page {
    padding: 0 1rem;
  }

  .main-parchment-folio,
  .scribe-notes-sidebar {
    padding: 1.5rem;
  }

  .tome-grand-title {
    font-size: 2.2em;
  }

  .section-heading {
    font-size: 1.6em;
  }

  .tome-scribe,
  .tome-series-chapter,
  .summary-parchment,
  .tome-provenance-details-grid .detail-item {
    font-size: 0.95em;
  }

  .return-to-catalogue-button {
    font-size: 1em;
    padding: 0.7rem 1.5rem;
  }

  .sidebar-section-title {
    font-size: 1.3em;
  }

  .tome-provenance-details-grid {
    grid-template-columns: 1fr;
    /* Stack on very small screens */
    gap: 0.5rem;
    text-align: left;
    /* Align text left when stacked */
  }

  .detail-item {
    justify-content: center;
    /* Center content when stacked on small screens */
  }
}

@media (max-width: 480px) {
  .tome-illumination {
    width: 180px;
    height: 260px;
  }

  .tome-grand-title {
    font-size: 1.8em;
  }

  .section-heading {
    font-size: 1.4em;
  }

  .genre-crest,
  .character-sigil,
  .setting-marker {
    font-size: 0.8em;
    padding: 0.4rem 0.8rem;
  }
}

/* New styles for the Book Reviews Section */
/* New styles for "Show More" buttons */
.toggle-text-button {
  color: #7a5f4c;
  /* A darker earthy tone for the link */
  cursor: pointer;
  margin-left: 5px;
  font-weight: bold;
  text-decoration: underline;
  transition: color 0.3s ease;
}

.toggle-text-button:hover {
  color: #5a3c2f;
  /* Darker on hover */
}

.toggle-list-item {
  list-style: none;
  /* Remove bullet point for this specific list item */
  text-align: right;
  /* Align the "Show More" link to the right */
  margin-top: 10px;
}

/* Existing styles for the Book Reviews Section */
.tome-reviews-section {
  background-color: #fdfaf2;
  border: 1px solid #d4c29a;
  border-radius: 8px;
  padding: 20px;
  margin-top: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.tome-reviews-section .section-heading {
  color: #5a3c2f;
  font-family: 'Georgia', serif;
  font-size: 1.8em;
  margin-bottom: 20px;
  text-align: center;
  position: relative;
}

.tome-reviews-section .section-heading::after {
  content: '';
  display: block;
  width: 50px;
  height: 2px;
  background: #d4c29a;
  margin: 10px auto 0;
}

.review-submission-form {
  background-color: #fffbf5;
  border: 1px dashed #d4c29a;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 25px;
}

.review-submission-form h4 {
  color: #5a3c2f;
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.2em;
}

.review-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #d4c29a;
  border-radius: 4px;
  font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
  font-size: 1em;
  color: #333;
  resize: vertical;
  margin-bottom: 10px;
  background-color: #fefdfb;
}

.review-rating-input {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.review-rating-input label {
  color: #5a3c2f;
  font-weight: bold;
}

.review-rating-select {
  padding: 8px;
  border: 1px solid #d4c29a;
  border-radius: 4px;
  background-color: #fefdfb;
  font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
}

.submit-review-button {
  background-color: #a08462;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  font-family: 'Georgia', serif;
  transition: background-color 0.3s ease;
}

.submit-review-button:hover {
  background-color: #8c735a;
}

.existing-reviews-list {
  margin-top: 20px;
}

.no-reviews-message {
  text-align: center;
  color: #777;
  font-style: italic;
  padding: 20px;
  border: 1px dashed #e0d0b0;
  border-radius: 5px;
  background-color: #fffaf0;
}

.review-entry {
  background-color: #fffef9;
  border: 1px solid #e0d0b0;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.reviewer-name {
  font-weight: bold;
  color: #5a3c2f;
  font-size: 1.1em;
}

.review-date {
  font-size: 0.9em;
  color: #777;
  margin-left: auto;
  padding-left: 10px;
}

.review-stars {
  color: #f39c12;
  font-size: 1.2em;
  margin-left: 10px;
}

.review-content {
  color: #333;
  line-height: 1.6;
  margin-bottom: 15px;
}

.review-actions {
  display: flex;
  gap: 15px;
}

.review-action-button {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  border: 1px solid #d4c29a;
  border-radius: 4px;
  background-color: #fcf8f0;
  color: #5a3c2f;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.review-action-button:hover {
  background-color: #f0e6da;
  border-color: #a08462;
}

.review-action-button .icon {
  font-size: 1.1em;
}

.review-action-button.liked {
  background-color: #ffebee;
  border-color: #e74c3c;
  color: #e74c3c;
}

.review-action-button.collected {
  background-color: #e8f5e9;
  border-color: #27ae60;
  color: #27ae60;
}
</style>