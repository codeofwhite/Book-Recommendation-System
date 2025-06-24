<template>
  <div class="book-details-layout" v-if="book">
    <div class="book-details-container">
      <div class="book-header">
        <div class="book-cover">
          <img :src="book.coverImg" :alt="book.title" />
        </div>
        <div class="book-info">
          <h1>{{ book.title }}</h1>
          <h2 v-if="book.series">系列：{{ book.series }}</h2>
          <p class="author">作者：{{ book.author }}</p>

          <div class="rating">
            <span class="stars">{{ '★'.repeat(Math.round(book.rating)) }}{{ '☆'.repeat(5 - Math.round(book.rating))
              }}</span>
            <span>({{ book.rating }} 来自 {{ book.numRatings }} 评分)</span>
          </div>

          <div class="meta">
            <span><strong>出版日期:</strong> {{ book.publishDate }}</span>
            <span v-if="book.firstPublishDate"><strong>首次出版日期:</strong> {{ book.firstPublishDate }}</span>
            <span><strong>页数:</strong> {{ book.pages }}</span>
            <span><strong>价格:</strong> ${{ book.price }}</span>
            <span v-if="book.language"><strong>语言:</strong> {{ book.language }}</span>
            <span v-if="book.isbn"><strong>ISBN:</strong> {{ book.isbn }}</span>
            <span v-if="book.bookFormat"><strong>格式:</strong> {{ book.bookFormat }}</span>
            <span v-if="book.edition"><strong>版本:</strong> {{ book.edition }}</span>
            <span v-if="book.publisher"><strong>出版社:</strong> {{ book.publisher }}</span>
            <span v-if="book.bbeScore"><strong>BBE 评分:</strong> {{ book.bbeScore }} (来自 {{ book.bbeVotes }} 投票)</span>
          </div>

          <div class="genres">
            <span v-for="genre in book.genres" :key="genre" class="genre-tag">{{ genre }}</span>
          </div>

          <div class="book-content">
            <h3>内容简介</h3>
            <p class="description">{{ book.description }}</p>
          </div>

          <div class="additional-info">
            <div v-if="book.characters && book.characters.length > 0">
              <h3>主要角色</h3>
              <div class="characters-list">
                <span v-for="character in book.characters" :key="character" class="character-tag">{{ character }}</span>
              </div>
            </div>

            <div v-if="book.setting && book.setting.length > 0">
              <h3>故事背景</h3>
              <div class="setting-list">
                <span v-for="loc in book.setting" :key="loc" class="setting-tag">{{ loc }}</span>
              </div>
            </div>

            <div v-if="book.awards && book.awards.length > 0">
              <h3>所获奖项</h3>
              <ul class="awards-list">
                <li v-for="(award, index) in book.awards" :key="index">{{ award }}</li>
              </ul>
            </div>

            <div v-if="book.likedPercent">
              <h3>喜欢度</h3>
              <p>{{ book.likedPercent }}% 的用户喜欢这本书。</p>
            </div>

            <div v-if="book.ratingsByStars && Object.keys(book.ratingsByStars).length > 0">
              <h3>评分分布</h3>
              <div class="ratings-by-stars">
                <div v-for="(count, star) in book.ratingsByStars" :key="star" class="star-row">
                  <span>{{ star }} 星:</span>
                  <div class="star-bar-container">
                    <div class="star-bar" :style="{ width: (count / book.numRatings * 100) + '%' }"></div>
                  </div>
                  <span>({{ count }})</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="actions">
          <button @click="goBack">返回列表</button>
        </div>
      </div>
    </div>

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

      <div class="sidebar-section">
        <h3>相关推荐</h3>
        <p>更多推荐内容...</p>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="loading">
    正在加载图书详情...
  </div>
  <div v-else class="not-found">
    未找到该图书
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
  padding: 0 15px;
  /* 增加左右内边距，避免边缘过于贴近 */
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
  border-top: 1px solid #eee;
  /* 添加分隔线 */
  padding-top: 15px;
}

.genres {
  margin-top: 15px;
}

.genre-tag,
.character-tag,
.setting-tag {
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

.genre-tag:hover,
.character-tag:hover,
.setting-tag:hover {
  background-color: #d0d0d0;
  transform: translateY(-1px);
}

.additional-info {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px dashed #ddd;
  /* 新增更多信息的分隔线 */
}

.additional-info h3 {
  font-size: 1.3em;
  color: #333;
  margin-top: 20px;
  margin-bottom: 15px;
}

.characters-list,
.setting-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.awards-list {
  list-style-type: disc;
  margin-left: 20px;
  padding: 0;
  color: #555;
}

.awards-list li {
  margin-bottom: 5px;
}

.ratings-by-stars {
  margin-top: 15px;
}

.star-row {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
  font-size: 0.9em;
  color: #666;
}

.star-row span:first-child {
  width: 60px;
  /* 统一星级标签宽度 */
  flex-shrink: 0;
}

.star-bar-container {
  flex-grow: 1;
  background-color: #eee;
  height: 8px;
  border-radius: 4px;
  margin: 0 10px;
  overflow: hidden;
}

.star-bar {
  height: 100%;
  background-color: #f39c12;
  border-radius: 4px;
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