<template>
  <div class="book-details-layout" v-if="book">
    <!-- 左侧栏 - 图书详细信息 -->
    <div class="book-details-container">
      <div class="book-header">
        <div class="book-cover">
          <img :src="book.coverImg" :alt="book.title" />
        </div>
        <div class="book-info">
          <h1>{{ book.title }}</h1>
          <h2 v-if="book.series">Part of {{ book.series }}</h2>
          <p class="author">By {{ book.author }}</p>

          <div class="rating">
            <span class="stars">{{ '★'.repeat(Math.round(book.rating)) }}{{ '☆'.repeat(5 - Math.round(book.rating))
              }}</span>
            <span>({{ book.rating }} from {{ book.numRatings }} ratings)</span>
          </div>

          <div class="meta">
            <span><strong>Published:</strong> {{ book.publishDate }}</span>
            <span><strong>Pages:</strong> {{ book.pages }}</span>
            <span><strong>Price:</strong> ${{ book.price }}</span>
          </div>

          <div class="genres">
            <span v-for="genre in book.genres" :key="genre" class="genre-tag">{{ genre }}</span>
          </div>


        </div>
        <div class="actions">
          <button @click="goBack">返回列表</button>
        </div>
      </div>

      <div class="book-content">
        <h3>Description</h3>
        <p class="description">{{ book.description }}</p>

        <div v-if="book.reviews && book.reviews.length > 0" class="reviews-section">
          <h3>Reviews</h3>
          <div v-for="review in book.reviews" :key="review.id" class="review">
            <div class="review-header">
              <span class="review-author">{{ review.author }}</span>
              <span class="review-rating">{{ '★'.repeat(review.rating) }}</span>
            </div>
            <p class="review-content">{{ review.content }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧栏 - 豆瓣搜索结果 -->
    <div class="sidebar">
      <div class="douban-results">
        <div class="sidebar-header" @click="toggleDoubanResults">
          <h2>豆瓣搜索结果 <span class="toggle-icon">{{ showDoubanResults ? '▼' : '▶' }}</span></h2>
        </div>
        <transition name="slide">
          <div v-show="showDoubanResults">
            <ul v-if="doubanSearchResults.length > 0">
              <li v-for="(doubanBook, index) in doubanSearchResults" :key="index">
                <a :href="doubanBook.link" target="_blank" rel="noopener noreferrer">
                  {{ doubanBook.title }}
                </a>
                <span class="douban-rating" v-if="doubanBook.rating">
                  {{ '★'.repeat(Math.round(doubanBook.rating)) }}{{ '☆'.repeat(5 - Math.round(doubanBook.rating)) }}
                  ({{ doubanBook.rating }})
                </span>
              </li>
            </ul>
            <p v-else-if="searched && doubanSearchResults.length === 0" class="no-results">
              没有找到相关的豆瓣书籍。
            </p>
          </div>
        </transition>
      </div>

      <!-- 可以在这里添加更多侧边栏内容 -->
      <div class="sidebar-section">
        <h3>相关推荐</h3>
        <p>更多推荐内容...</p>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="loading">
    Loading book details...
  </div>
  <div v-else class="not-found">
    Book not found
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'BookDetails',
  data() {
    return {
      book: null,
      loading: true,
      doubanSearchResults: [],
      searched: false,
      showDoubanResults: true
    };
  },
  async created() {
    await this.fetchBookDetails();
    if (this.book && this.book.title) {
      await this.performDoubanSearch(this.book.title);
    }
  },
  methods: {
    async fetchBookDetails() {
      this.loading = true;
      try {
        const bookId = this.$route.params.bookId;
        const response = await axios.get(`http://localhost:5000/api/books/${bookId}`);
        this.book = response.data;
      } catch (error) {
        console.error('Error fetching book details:', error);
        this.book = null;
      } finally {
        this.loading = false;
      }
    },
    goBack() {
      this.$router.go(-1);
    },
    async performDoubanSearch(keyword) {
      if (!keyword.trim()) {
        console.warn('豆瓣搜索关键词为空，跳过搜索。');
        return;
      }
      this.searched = true;
      this.doubanSearchResults = [];
      try {
        const response = await axios.get(
          `http://localhost:5000/api/search_douban?keyword=${encodeURIComponent(keyword)}`
        );
        this.doubanSearchResults = response.data;
      } catch (error) {
        console.error('Error fetching Douban books:', error);
      }
    },
    toggleDoubanResults() {
      this.showDoubanResults = !this.showDoubanResults;
    }
  }
};
</script>

<style scoped>
/* 整体布局 */
.book-details-layout {
  display: flex;
  max-width: 1200px;
  margin: 20px auto;
  gap: 30px;
  align-items: flex-start;
}

.book-details-container {
  flex: 3;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.sidebar {
  flex: 1;
  min-width: 300px;
  position: sticky;
  top: 20px;
}

/* 图书详情样式 */
.book-header {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  align-items: flex-start;
}

.book-cover img {
  width: 180px;
  height: auto;
  border-radius: 5px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.book-cover img:hover {
  transform: scale(1.03);
}

.book-info {
  flex-grow: 1;
}

.book-info h1 {
  font-size: 2.2em;
  color: #333;
  margin-bottom: 5px;
}

.book-info h2 {
  font-size: 1.1em;
  color: #666;
  margin-top: 0;
  margin-bottom: 10px;
}

.book-info .author {
  font-size: 1.1em;
  color: #555;
  margin-bottom: 15px;
}

.rating .stars {
  color: #f39c12;
  font-size: 1.3em;
}

.rating span {
  font-size: 0.9em;
  color: #777;
  margin-left: 5px;
}

.meta {
  margin-top: 15px;
  font-size: 0.95em;
  color: #666;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.genres {
  margin-top: 15px;
}

.genre-tag {
  display: inline-block;
  background-color: #e0e0e0;
  color: #555;
  padding: 5px 10px;
  border-radius: 3px;
  margin-right: 8px;
  margin-bottom: 8px;
  font-size: 0.85em;
  transition: all 0.2s;
}

.genre-tag:hover {
  background-color: #d0d0d0;
  transform: translateY(-1px);
}

.actions {
  margin-top: 25px;
}

.actions button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.2s;
}

.actions button:hover {
  background-color: #0056b3;
}

.book-content {
  margin-top: 30px;
}

.book-content h3 {
  font-size: 1.5em;
  color: #333;
  margin-bottom: 15px;
  border-bottom: 2px solid #eee;
  padding-bottom: 5px;
}

.description {
  line-height: 1.8;
  color: #444;
  text-align: justify;
}

.reviews-section {
  margin-top: 30px;
}

.review {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 15px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.review:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.review-author {
  font-weight: bold;
  color: #333;
}

.review-rating {
  color: #f39c12;
  font-size: 1.1em;
}

.review-content {
  color: #555;
  line-height: 1.6;
}

/* 侧边栏样式 */
.sidebar-header {
  cursor: pointer;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 5px;
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  transition: background-color 0.2s;
}

.sidebar-header:hover {
  background-color: #e9e9e9;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 1.2em;
  color: #333;
  display: flex;
  align-items: center;
}

.toggle-icon {
  margin-left: 10px;
  font-size: 0.8em;
}

.douban-results {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px;
  margin-bottom: 20px;
}

.douban-results ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.douban-results li {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
}

.douban-results li:last-child {
  border-bottom: none;
}

.douban-results li:hover {
  background-color: #f9f9f9;
}

.douban-results a {
  color: #007bff;
  text-decoration: none;
  display: block;
  margin-bottom: 5px;
}

.douban-results a:hover {
  text-decoration: underline;
}

.douban-rating {
  color: #f39c12;
  font-size: 0.9em;
  display: block;
}

.no-results {
  color: #777;
  font-style: italic;
  padding: 10px 0;
}

.sidebar-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px;
  margin-bottom: 20px;
}

.sidebar-section h3 {
  font-size: 1.2em;
  color: #333;
  margin-top: 0;
  margin-bottom: 15px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

/* 过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.slide-enter,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
}

/* 加载和未找到状态 */
.loading,
.not-found {
  text-align: center;
  padding: 50px;
  font-size: 1.2em;
  color: #777;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .book-details-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    min-width: auto;
    position: static;
  }

  .book-header {
    flex-direction: column;
    align-items: center;
  }

  .book-info {
    text-align: center;
  }

  .meta {
    justify-content: center;
  }
}
</style>