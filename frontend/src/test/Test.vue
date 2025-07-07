<template>
  <div class="main-layout">
    <div class="left-content">
      <div class="search-bar">
        <input type="text" v-model="inputSearchKeyword" placeholder="搜索图书名称..." @keyup.enter="handleSearch"
          class="search-input" />
        <button @click="handleSearch" class="search-button">
          搜索
        </button>
      </div>

      <p v-if="loading" class="loading-message">
      <div class="spinner"></div> 正在加载图书...
      </p>
      <p v-else-if="filteredBooks.length === 0" class="no-books-message">
        没有找到相关书籍或当前筛选条件下没有书籍。
      </p>

      <div v-else class="book-list-container">
        <div v-for="book in filteredBooks" :key="book.bookId" class="book-card-original">
          <div @click="trackBookClick(book)" class="book-card-clickable-original">
            <div class="book-cover-original">
              <img :src="book.coverImg" :alt="book.title" class="rounded-lg shadow-md" />
            </div>
            <div class="book-details-original">
              <router-link :to="{ name: 'BookDetails', params: { bookId: book.bookId } }"
                class="text-blue-600 hover:underline">
                <h2 class="text-2xl font-bold mb-1">{{ book.title }}</h2>
              </router-link>
              <h3 v-if="book.series" class="text-lg text-gray-600 mb-2">Part of {{ book.series }}</h3>
              <p class="author text-gray-700 mb-2">By {{ book.author }}</p>
              <div class="rating flex items-center mb-2">
                <span class="stars text-yellow-500 text-xl mr-1">{{ '★'.repeat(Math.round(book.rating)) }}{{
                  '☆'.repeat(5 -
                    Math.round(book.rating)) }}</span>
                <span class="text-sm text-gray-500">({{ book.rating }} from {{ book.numRatings }} ratings)</span>
              </div>
              <p class="description text-gray-800 leading-relaxed mb-3">{{ truncateDescription(book.description) }}</p>
              <div class="meta flex flex-wrap gap-x-4 gap-y-2 text-sm text-gray-600 mb-3">
                <span><strong>Published:</strong> {{ book.publishDate }}</span>
                <span><strong>Pages:</strong> {{ book.pages }}</span>
                <span><strong>Price:</strong> ${{ book.price }}</span>
              </div>
              <div class="genres flex flex-wrap gap-2">
                <span v-for="genre in book.genres.slice(0, 5)" :key="genre"
                  class="genre-tag bg-gray-200 text-gray-700 px-3 py-1 rounded-full text-xs font-medium">{{ genre
                  }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <aside class="right-sidebar">
      <div class="filter-section card">
        <h3 class="section-heading">📚 筛选分类</h3>
        <div class="genre-checkbox-group">
          <div v-for="genre in availableGenres" :key="genre" class="genre-checkbox-item">
            <input type="checkbox" :id="genre" :value="genre" v-model="selectedGenres" class="genre-checkbox" />
            <label :for="genre" class="genre-label">{{ genre }}</label>
          </div>
          <button v-if="selectedGenres.length > 0" @click="clearGenres" class="clear-genres-button">
            清空筛选
          </button>
        </div>
      </div>

      <div class="recommendation-section card">
        <h3 class="section-heading">💡 推荐给您</h3>
        <div v-if="recommendedBooks.length === 0" class="no-recommendations">
          暂无个性化推荐。
        </div>
        <div v-else class="recommendation-list">
          <div v-for="book in recommendedBooks" :key="book.id" class="recommended-book-item">
            <img :src="book.coverImage" :alt="book.title" class="recommended-book-cover" />
            <div class="recommended-book-info">
              <router-link :to="{ name: 'BookDetails', params: { bookId: book.id } }"
                class="recommended-book-title-link">
                <h4>{{ book.title }}</h4>
              </router-link>
              <p class="recommended-book-author">{{ book.author }}</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, onMounted, computed, watch } from 'vue';

export default {
  name: 'BookList',
  props: {
    searchKeyword: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const inputSearchKeyword = ref(props.searchKeyword);
    const currentSearchKeyword = ref(props.searchKeyword);
    const books = ref([]);
    const loading = ref(true);
    const selectedGenres = ref([]);
    const availableGenres = ref([]); // 存储所有可用分类

    // 模拟推荐数据 (占位用)
    const recommendedBooks = ref([
      { id: 'rec1', title: '深度学习入门', author: 'AI小李', coverImage: 'https://via.placeholder.com/80x120?text=DeepLearning' },
      { id: 'rec2', title: '番茄工作法图解', author: '效率达人', coverImage: 'https://via.placeholder.com/80x120?text=Pomodoro' },
      { id: 'rec3', title: '软技能：代码之外的生存指南', author: '码农小哥', coverImage: 'https://via.placeholder.com/80x120?text=SoftSkills' },
    ]);

    // 根据搜索关键词和选定分类过滤图书
    const filteredBooks = computed(() => {
      let filtered = books.value;

      // 1. 关键词过滤
      if (currentSearchKeyword.value) {
        const keywordLower = currentSearchKeyword.value.toLowerCase();
        filtered = filtered.filter(book =>
          book.title.toLowerCase().includes(keywordLower) ||
          book.author.toLowerCase().includes(keywordLower) ||
          (book.description && book.description.toLowerCase().includes(keywordLower))
        );
      }

      // 2. 分类过滤
      if (selectedGenres.value.length > 0) {
        filtered = filtered.filter(book =>
          book.genres && selectedGenres.value.some(selectedGenre => book.genres.includes(selectedGenre))
        );
      }
      return filtered;
    });

    const fetchBooks = async (keyword) => {
      loading.value = true;
      try {
        const url = keyword
          ? `http://localhost:5000/api/search_local_books?keyword=${encodeURIComponent(keyword)}`
          : 'http://localhost:5000/api/books';

        const response = await axios.get(url);
        books.value = response.data;

        // 提取所有不重复的分类
        const genresSet = new Set();
        books.value.forEach(book => {
          if (book.genres) {
            book.genres.forEach(genre => genresSet.add(genre));
          }
        });
        availableGenres.value = Array.from(genresSet).sort(); // 排序分类

      } catch (error) {
        console.error('Error fetching books:', error);
        books.value = [];
        availableGenres.value = [];
      } finally {
        loading.value = false;
      }
    };

    const handleSearch = () => {
      currentSearchKeyword.value = inputSearchKeyword.value;
      // 搜索时清空分类筛选，避免冲突
      selectedGenres.value = [];
    };

    const truncateDescription = (desc) => {
      if (!desc) return '';
      // Original description length was 200, but 80 was used in the first prompt's original display
      return desc.length > 200 ? desc.substring(0, 200) + '...' : desc;
    };

    const clearGenres = () => {
      selectedGenres.value = [];
    };

    // --- 新增的 GA4 追踪方法 ---
    const trackBookClick = (book) => {
      console.log('Book click detected, preparing GA4 event for:', book.title);

      // 确保 dataLayer 可用
      if (window.dataLayer) {
        window.dataLayer.push({
          event: 'book_clicked_custom', // GTM 监听的自定义事件名称
          book_id: book.bookId,
          book_title: book.title,
          book_author: book.author,
          book_genres: book.genres ? book.genres.join(',') : '', // 将数组转换为逗号分隔的字符串
          book_price: book.price,
        });
        console.log('DataLayer pushed for book_clicked_custom:', {
          book_id: book.bookId,
          book_title: book.title
        });
      } else {
        console.warn('dataLayer not found. GTM might not be loaded correctly.');
      }
    };

    // 监听外部传入的 searchKeyword 变化
    watch(() => props.searchKeyword, (newKeyword) => {
      inputSearchKeyword.value = newKeyword;
      currentSearchKeyword.value = newKeyword;
      selectedGenres.value = []; // 外部搜索时清空分类
    }, { immediate: true }); // 立即执行一次，用于初始加载

    onMounted(() => {
      // initial fetch is handled by the immediate watcher on props.searchKeyword
    });

    return {
      inputSearchKeyword,
      books,
      loading,
      selectedGenres,
      availableGenres,
      recommendedBooks,
      filteredBooks,
      handleSearch,
      truncateDescription,
      clearGenres,
      trackBookClick,
    };
  }
};
</script>

<style scoped>
/* Main Layout */
.main-layout {
  display: flex;
  justify-content: center;
  gap: 30px;
  padding: 30px;
  max-width: 1500px;
  margin: 0 auto;
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  background-color: #f8fbfd;
  color: #333;
}

/* Left Content - Book List */
.left-content {
  flex: 3;
  min-width: 600px;
}

.search-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 40px;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
}

.search-input {
  flex-grow: 1;
  padding: 12px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1.1em;
  outline: none;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.search-input:focus {
  border-color: #8ac0e2;
  box-shadow: 0 0 0 3px rgba(138, 192, 226, 0.3);
}

.search-button {
  padding: 12px 25px;
  background-color: #5cb85c;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1.1em;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.search-button:hover {
  background-color: #4cae4c;
  transform: translateY(-2px);
}

.search-button:active {
  transform: translateY(0);
}

.loading-message,
.no-books-message {
  text-align: center;
  padding: 50px;
  font-size: 1.3em;
  color: #777;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background-color: #ffffff;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  min-height: 200px;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid #5cb85c;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.book-list-container {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Original Book Card Styles (re-applied and isolated with -original suffix) */
.book-card-original {
  display: flex;
  background-color: #fff;
  border-radius: 12px;
  /* More rounded */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  /* More prominent shadow */
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  /* Add pointer for clickability */
}

.book-card-original:hover {
  transform: translateY(-5px);
  /* Lift effect on hover */
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  /* Deeper shadow on hover */
}

.book-card-clickable-original {
  display: flex;
  width: 100%;
}

.book-cover-original {
  flex-shrink: 0;
  width: 150px;
  height: 220px;
  overflow: hidden;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-cover-original img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.book-details-original {
  padding: 20px;
  text-align: left;
  flex-grow: 1;
}

.book-details-original h2 {
  font-size: 1.8em;
  color: #333;
  margin-bottom: 5px;
}

.book-details-original h3 {
  font-size: 1.1em;
  color: #666;
  margin-top: 0;
  margin-bottom: 10px;
}

.book-details-original .author {
  font-size: 1em;
  color: #555;
  margin-bottom: 10px;
}

.rating .stars {
  color: #f39c12;
  font-size: 1.2em;
}

.rating span {
  font-size: 0.85em;
  color: #777;
  margin-left: 5px;
}

.description {
  line-height: 1.6;
  color: #444;
  margin-bottom: 15px;
  font-size: 0.95em;
}

.meta {
  margin-top: 10px;
  font-size: 0.9em;
  color: #666;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.genres {
  margin-top: 15px;
}

/* Specificity for Tailwind-like classes from original code */
.text-blue-600 {
  color: #2563eb;
}

.hover\:underline:hover {
  text-decoration: underline;
}

.text-2xl {
  font-size: 1.5rem;
}

.font-bold {
  font-weight: 700;
}

.mb-1 {
  margin-bottom: 0.25rem;
}

.text-lg {
  font-size: 1.125rem;
}

.text-gray-600 {
  color: #4b5563;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.text-gray-700 {
  color: #374151;
}

.rating {
  display: flex;
  align-items: center;
}

.text-yellow-500 {
  color: #f59e0b;
}

.text-xl {
  font-size: 1.25rem;
}

.mr-1 {
  margin-right: 0.25rem;
}

.text-sm {
  font-size: 0.875rem;
}

.text-gray-500 {
  color: #6b7280;
}

.leading-relaxed {
  line-height: 1.625;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.flex {
  display: flex;
}

.flex-wrap {
  flex-wrap: wrap;
}

.gap-x-4 {
  -moz-column-gap: 1rem;
  column-gap: 1rem;
}

.gap-y-2 {
  row-gap: 0.5rem;
}

.text-xs {
  font-size: 0.75rem;
}

.font-medium {
  font-weight: 500;
}

.bg-gray-200 {
  background-color: #e5e7eb;
}

.px-3 {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.py-1 {
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}

.rounded-full {
  border-radius: 9999px;
}


/* Right Sidebar */
.right-sidebar {
  flex: 1.2;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.card {
  background-color: #ffffff;
  border-radius: 15px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
  padding: 25px;
}

.section-heading {
  font-size: 1.8em;
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 25px;
  font-weight: 700;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 15px;
  text-align: center;
}

/* Genre Filter Section */
.genre-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 15px;
}

.genre-checkbox-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.genre-checkbox {
  margin-right: 10px;
  width: 18px;
  height: 18px;
  accent-color: #5cb85c;
}

.genre-label {
  font-size: 1.05em;
  color: #444;
  cursor: pointer;
  transition: color 0.2s ease;
}

.genre-checkbox-item:hover .genre-label {
  color: #5cb85c;
}

.clear-genres-button {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 15px;
  font-size: 0.9em;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 15px;
  align-self: flex-start;
}

.clear-genres-button:hover {
  background-color: #c82333;
}

/* Recommendation Section */
.no-recommendations {
  text-align: center;
  color: #777;
  font-style: italic;
  padding: 20px 0;
}

.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.recommended-book-item {
  display: flex;
  align-items: center;
  gap: 15px;
  background-color: #f7fbfd;
  padding: 12px;
  border-radius: 10px;
  transition: background-color 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.recommended-book-item:hover {
  background-color: #edf5f8;
}

.recommended-book-cover {
  width: 60px;
  height: 90px;
  object-fit: cover;
  border-radius: 5px;
  flex-shrink: 0;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.recommended-book-info {
  flex-grow: 1;
}

.recommended-book-title-link {
  text-decoration: none;
  color: #34495e;
  font-weight: 600;
  font-size: 1.1em;
  line-height: 1.4;
  transition: color 0.3s ease;
}

.recommended-book-title-link:hover {
  color: #2980b9;
  text-decoration: underline;
}

.recommended-book-author {
  font-size: 0.9em;
  color: #7f8c8d;
  margin-top: 5px;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .main-layout {
    flex-direction: column;
    gap: 40px;
    padding: 20px;
  }

  .left-content,
  .right-sidebar {
    min-width: unset;
    width: 100%;
  }

  /* Original book card needs adjustment for smaller screens */
  .book-card-original {
    flex-direction: row;
    /* Keeps it horizontal on tablets */
    justify-content: center;
  }

  .book-cover-original {
    width: 150px;
    height: 220px;
    border-right: 1px solid #eee;
    border-bottom: none;
    margin-bottom: 0;
  }

  .book-details-original {
    text-align: left;
  }

  .section-heading {
    text-align: left;
  }
}

@media (max-width: 768px) {
  .main-layout {
    padding: 15px;
  }

  .search-bar {
    flex-direction: column;
    gap: 10px;
    padding: 15px;
  }

  .search-input,
  .search-button {
    width: 100%;
    text-align: center;
  }

  .book-card-original {
    flex-direction: column;
    /* Stacks vertically on smaller phones */
    align-items: center;
    text-align: center;
  }

  .book-cover-original {
    width: 100%;
    max-width: 200px;
    height: 280px;
    border-right: none;
    border-bottom: 1px solid #eee;
    margin-bottom: 15px;
  }

  .book-cover-original img {
    border-radius: 8px 8px 0 0;
  }

  .book-details-original {
    padding: 15px;
  }

  .book-details-original h2 {
    font-size: 1.5em;
  }

  .book-details-original h3 {
    font-size: 1em;
  }

  .meta,
  .genres {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .book-details-original h2 {
    font-size: 1.5em;
  }

  .description {
    font-size: 0.9em;
  }

  .book-cover-original {
    height: 250px;
  }
}
</style>