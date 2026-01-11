<template>
  <div class="ancient-tome-container">
    <div class="top-folio-controls">
      <div class="search-quill-box">
        <input type="text" v-model="inputSearchKeyword" placeholder="在此镌刻您的求索..." @keyup.enter="handleSearch"
          class="quill-input" />
        <button @click="handleSearch" class="seek-button">
          探寻典籍
          <div class="info-bubble bottom-right" v-if="showSearchTip">
            按下回车键或点击"探寻典籍"，开启您的书香之旅！
          </div>
        </button>
      </div>

      <div class="astrolabe-filters-horizontal">
        <div class="filter-section-inline genre-filter-section">
          <h3 class="filter-title-inline">按類型甄选：</h3>
          <div class="genre-filter-wrapper">
            <input type="text" v-model="genreSearchTerm" placeholder="搜索類型..." class="genre-search-input" />
            <div class="genre-pill-container">
              <span v-for="genre in filteredAvailableGenres" :key="genre" class="genre-filter-pill"
                :class="{ 'is-selected': selectedGenres.includes(genre) }" @click="toggleGenre(genre)">
                {{ genre }}
                <div class="info-bubble top-center" v-if="showGenreTip && genre === 'Fiction'">
                  点击類型即可筛选结果！
                </div>
              </span>
              <span v-if="filteredAvailableGenres.length === 0 && availableGenres.length > 0"
                class="no-options-message">无匹配類型。</span>
              <span v-else-if="availableGenres.length === 0" class="no-options-message">暂无已发现類型。</span>
            </div>
            <button v-if="availableGenres.length > maxDisplayedGenres && !showAllGenres" @click="showAllGenres = true"
              class="toggle-genre-button">Show All ({{ availableGenres.length - maxDisplayedGenres }} More)</button>
            <button v-if="showAllGenres" @click="showAllGenres = false" class="toggle-genre-button">Show Less</button>
          </div>
        </div>

        <div class="filter-section-inline">
          <h3 class="filter-title-inline">按星评等级：</h3>
          <select v-model="selectedRating" @change="applyFilters" class="filter-select-inline">
            <option value="">不限星评</option>
            <option value="4">4星及以上</option>
            <option value="3">3星及以上</option>
            <option value="2">2星及以上</option>
            <option value="1">1星及以上</option>
          </select>
        </div>

        <div class="filter-section-inline">
          <h3 class="filter-title-inline">按典籍定价：</h3>
          <div class="price-input-wrapper">
            <input type="number" v-model.number="minPrice" @input="applyFiltersDebounced" placeholder="最低"
              class="filter-input-inline" />
            <span> — </span>
            <input type="number" v-model.number="maxPrice" @input="applyFiltersDebounced" placeholder="最高"
              class="filter-input-inline" />
          </div>
        </div>
        <div class="filter-section-inline">
          <h3 class="filter-title-inline">按刊印年份：</h3>
          <select v-model="selectedYear" @change="applyFilters" class="filter-select-inline">
            <option value="">所有年代</option>
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
      </div>

      <button @click="resetFilters" class="reset-filters-button-inline">重置所有筛选条件</button>
    </div>

    <div class="parchment-scroll-wrapper">
      <main class="catalogue-of-works">
        <p v-if="loading" class="scribe-message">典籍官正在勤勉检索...稍候</p>
        <p v-else-if="!paginatedBooks || paginatedBooks.length === 0" class="scribe-message">暂无符合此条件的典籍。</p>
        <transition-group name="book-fade" tag="div" class="tome-collection" v-else>
          <div v-for="book in paginatedBooks" :key="book.bookId" class="tome-folio">
            <div class="illumination-plate">
              <img :src="book.coverImg" :alt="book.title" class="tome-cover-art" />
            </div>
            <div class="tome-inscriptions">
              <router-link :to="{ name: 'BookDetails', params: { bookId: book.bookId } }" class="tome-title-link"
                @click.native="handleBookClick(book)">
                <h2 class="tome-title">{{ book.title }}</h2>
              </router-link>
              <h3 v-if="book.series" class="tome-series"> {{ book.series }} 系列篇章</h3>
              <p class="tome-author">著者： {{ book.author }}</p>
              <div class="celestial-guidance">
                <span class="stars-illuminated">{{ '★'.repeat(Math.round(book.rating)) }}{{
                  '☆'.repeat(5 - Math.round(book.rating)) }}</span>
                <span class="whispers-of-critics">({{ book.rating }} 分 {{ book.numRatings }} 条评价)</span>
              </div>
              <p class="tome-summary">{{ truncateDescription(book.description) }}</p>
              <div class="tome-provenance">
                <span><strong>刊印日期：</strong> {{ book.publishDate }}</span>
                <span><strong>页数：</strong> {{ book.pages }}</span>
                <span><strong>定价：</strong> ${{ book.price }}</span>
              </div>
              <div class="scholarly-genres">
                <span v-for="genre in book.genres.slice(0, 3)" :key="genre" class="genre-seal">{{ genre }}</span>
                <span v-if="book.genres.length > 3" class="genre-seal more-genres">...</span>
              </div>
            </div>
          </div>
        </transition-group>

        <div v-if="totalPages > 1" class="pagination-controls">
          <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="pagination-button">
            &laquo; 上一页
          </button>
          <span v-for="page in paginationPages" :key="page" class="page-number"
            :class="{ 'is-current': page === currentPage, 'is-ellipsis': page === '...' }"
            @click="page !== '...' && goToPage(page)">
            {{ page }}
          </span>
          <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages" class="pagination-button">
            下一页 &raquo;
          </button>
        </div>

      </main>

      <aside class="oracle-sidebar">
        <div class="oracle-header">
          <h3 class="oracle-title">智者私语</h3>
          <p class="oracle-subtitle">为您量身定制的卷轴 (实时推荐)</p>
        </div>
        <div class="oracle-list">
          <p v-if="loadingRecommendations" class="scribe-message">
            正在为您生成实时推荐...
          </p>
          <p v-else-if="realtimeRecommendations.length === 0" class="no-recommendations-message">
            尚无实时推荐。探索更多书籍以生成个性化推荐！
            <div class="info-bubble bottom-left" v-if="showRecommendationTip">
              点击书籍可优化您的"智者私语"推荐！
            </div>
          </p>
          <transition-group name="recommendation-slide" tag="div" v-else>
            <div v-for="(rec, index) in realtimeRecommendations" :key="rec.bookId || index" class="oracle-insight">
              <router-link :to="{ name: 'BookDetails', params: { bookId: rec.bookId } }" class="oracle-insight-link"
                @click.native="handleBookClick(rec)">
                <div class="oracle-effigy">
                  <img :src="rec.coverImg" :alt="rec.title" class="oracle-cover-mini" />
                </div>
                <div class="oracle-details">
                  <h4 class="oracle-insight-title">{{ rec.title }}</h4>
                  <p class="oracle-insight-author">{{ rec.author }}</p>
                </div>
              </router-link>
            </div>
          </transition-group>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { trackBookClick, trackPageView, trackBookDetailView } from '../services/logger';

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

// 定义定时器变量（放在方法外，全局作用域，避免重复创建）
let recommendationRefreshTimer = null;
// 防抖标记（避免短时间内重复请求）
let isRefreshing = false;

export default {
  name: 'BookListWithRecommendation',
  props: {
    searchKeyword: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      user: {
        user_id: '',
        nickname: '',
        email: '',
        avatar_url: '',
        is_profile_complete: false,
      },

      inputSearchKeyword: '',
      initialSearchKeyword: '',
      allBooks: [], // This will hold ALL fetched books
      realtimeRecommendations: [],
      loadingRecommendations: false, // 实时推荐的加载状态
      loading: true, // 这是主列表的加载状态

      // Filter states
      availableGenres: [], // All unique genres found in books
      genreSearchTerm: '', // For searching within genres
      showAllGenres: false, // Control for showing all or limited genres
      maxDisplayedGenres: 10, // Max number of genres to show initially

      availableYears: [],
      selectedGenres: [],
      selectedRating: '',
      minPrice: null,
      maxPrice: null,
      selectedYear: '',
      priceDebounceTimer: null, // For debouncing price inputs

      // Pagination states
      currentPage: 1,
      itemsPerPage: 5, // Number of books per page
      pageRange: 2, // Number of pages to show around the current page

      pageViewStartTime: 0,
      pageUrlOnMount: '', // 记录页面加载时的URL

      // --- 气泡提示状态 ---
      showSearchTip: false,
      showGenreTip: false,
      showRecommendationTip: false,

      editableNickname: ''
    };
  },
  computed: {
    filteredAvailableGenres() {
      const filtered = this.availableGenres.filter(genre =>
        genre.toLowerCase().includes(this.genreSearchTerm.toLowerCase())
      );
      return this.showAllGenres ? filtered : filtered.slice(0, this.maxDisplayedGenres);
    },
    // This computed property now returns ALL filtered books, BEFORE pagination
    filteredBooks() {
      let filtered = [...this.allBooks];

      // Apply keyword search
      if (this.inputSearchKeyword) {
        const lowerCaseKeyword = this.inputSearchKeyword.toLowerCase();
        filtered = filtered.filter(book =>
          book.title.toLowerCase().includes(lowerCaseKeyword) ||
          book.author.toLowerCase().includes(lowerCaseKeyword) ||
          (book.description && book.description.toLowerCase().includes(lowerCaseKeyword))
        );
      }

      // Filter by Genre
      if (this.selectedGenres.length > 0) {
        filtered = filtered.filter(book =>
          this.selectedGenres.some(genre => book.genres.includes(genre))
        );
      }

      // Filter by Rating
      if (this.selectedRating) {
        const minRating = parseFloat(this.selectedRating);
        filtered = filtered.filter(book => book.rating >= minRating);
      }

      // Filter by Price
      if (this.minPrice !== null && this.minPrice !== '') {
        filtered = filtered.filter(book => book.price >= this.minPrice);
      }
      if (this.maxPrice !== null && this.maxPrice !== '') {
        filtered = filtered.filter(book => book.price <= this.maxPrice);
      }

      // Filter by Year
      if (this.selectedYear) {
        filtered = filtered.filter(book => {
          const publishYear = new Date(book.publishDate).getFullYear();
          return publishYear == this.selectedYear;
        });
      }

      return filtered;
    },
    totalPages() {
      return Math.ceil(this.filteredBooks.length / this.itemsPerPage);
    },
    paginatedBooks() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredBooks.slice(start, end);
    },
    paginationPages() {
      const pages = [];
      const total = this.totalPages;
      const current = this.currentPage;
      const range = this.pageRange;

      if (total <= 1) return [];

      // Always include first page
      pages.push(1);

      // Add pages around current page
      for (let i = current - range; i <= current + range; i++) {
        if (i > 1 && i < total) {
          pages.push(i);
        }
      }

      // Always include last page
      if (total > 1) {
        pages.push(total);
      }

      // Remove duplicates and sort
      const uniquePages = [...new Set(pages)].sort((a, b) => a - b);

      const finalPages = [];
      let lastPage = 0;
      for (let i = 0; i < uniquePages.length; i++) {
        const page = uniquePages[i];
        if (page - lastPage > 1) {
          finalPages.push('...');
        }
        finalPages.push(page);
        lastPage = page;
      }
      return finalPages;
    }
  },
  created() {
    this.initialSearchKeyword = this.searchKeyword;
    this.inputSearchKeyword = this.initialSearchKeyword;
    this.fetchBooks(); // Fetch all books initially
    this.fetchUserData();
    this.fetchRealtimeRecommendationsForList(); // <--- 调用新的实时推荐方法

    // 初始化时显示提示气泡
    this.showTipsInitially();
  },
  //埋点
  mounted() {
    this.pageViewStartTime = Date.now();
    this.pageUrlOnMount = window.location.href;
    // 页面加载时先手动获取一次，再启动定时
    this.fetchRealtimeRecommendationsForList();
    this.startRecommendationRefresh();
  },

  beforeUnmount() {
    const endTime = Date.now();
    const dwellTimeInSeconds = Math.round((endTime - this.pageViewStartTime) / 1000);
    // 页面销毁时停止定时
    this.stopRecommendationRefresh();
    // 调用 logger.js 中的函数，显式传递页面名称和捕获的URL
    trackPageView('BookList', dwellTimeInSeconds, this.pageUrlOnMount);
  },

  watch: {
    // Watch filteredBooks to reset currentPage when filters change
    filteredBooks() {
      this.currentPage = 1; // Reset to first page whenever filters change
    },
    inputSearchKeyword() {
      this.applyFilters();
    },
    // 监听user.user_id变化，用户信息加载完成后自动加载推荐
    'user.user_id'(newVal) {
      if (newVal) {
        this.fetchRealtimeRecommendationsForList();
        this.startRecommendationRefresh();
      }
    }
  },
  methods: {
    // --- 气泡提示相关方法 ---
    showTipsInitially() {
      // 搜索框提示在页面加载后几秒显示，然后自动隐藏
      setTimeout(() => {
        this.showSearchTip = true;
      }, 1500); // 1.5秒后显示
      setTimeout(() => {
        this.showSearchTip = false;
      }, 6500); // 6.5秒后隐藏（显示5秒）

      // 流派筛选提示在页面加载后稍晚显示，然后自动隐藏
      setTimeout(() => {
        this.showGenreTip = true;
      }, 3000); // 3秒后显示
      setTimeout(() => {
        this.showGenreTip = false;
      }, 8000); // 8秒后隐藏（显示5秒）

      // 实时推荐提示在没有推荐时显示，然后自动隐藏
      // 这将在 fetchRealtimeRecommendationsForList 结束后根据 realtimeRecommendations.length 判断
      // 如果没有实时推荐，且用户在侧边栏，则显示
      setTimeout(() => {
        if (this.realtimeRecommendations.length === 0) {
          this.showRecommendationTip = true;
        }
      }, 5000); // 5秒后检查并显示
      setTimeout(() => {
        this.showRecommendationTip = false;
      }, 10000); // 10秒后隐藏（显示5秒）
    },

    async handleBookClick(book) {
      await trackBookDetailView(book.bookId, window.location.href);
      console.log(`用户 ${this.user.user_id} 点击了书籍: ${book.title} (${book.bookId}) → 已上报有效事件，pure_realtime立即处理`);

      // 3. 主动刷新推荐列表，拿到过滤后的数据
      await this.fetchRealtimeRecommendationsForList();

      // 隐藏气泡提示
      this.showRecommendationTip = false;
    },

    async fetchUserData() {
      const currentStoredUserData = getParsedUserData(); // 获取当前 localStorage 中的完整数据

      if (!currentStoredUserData || !currentStoredUserData.user_id) {
        console.error('UserView: User data not found in localStorage. Redirecting to login.');
        this.$router.push({ name: 'auth' }); // 注意这里使用了 $router 而不是 this.router
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

        // 更新 localStorage 中的 user_data，但保留 auth_token
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
          this.$router.push({ name: 'auth' }); // 注意这里使用了 $router
        } else if (!currentStoredUserData) {
          this.$router.push({ name: 'auth' }); // 注意这里使用了 $router
        }
      }
    },
    handleSearch() {
      this.applyFilters();
      // 用户搜索后，可以隐藏搜索提示气泡
      this.showSearchTip = false;
    },
    async fetchBooks() {
      this.loading = true;
      try {
        // Always fetch all books from the API
        const response = await axios.get('/service-b/api/books');
        this.allBooks = response.data;
        this.extractFilterOptions();
        this.applyFilters(); // Apply filters initially
      } catch (error) {
        console.error('Error fetching books:', error);
        this.allBooks = [];
      } finally {
        this.loading = false;
      }
    },
    // 获取实时更新的推荐数据的方法，用于书籍列表页
    async fetchRealtimeRecommendationsForList() {
      // 防抖判断，如果正在请求，直接返回
      if (isRefreshing) return;

      const loggedInUser = getParsedUserData();
      const userId = loggedInUser ? loggedInUser.user_id : null;

      if (!userId) {
        console.log("用户未登录，无法获取实时推荐。");
        this.realtimeRecommendations = []; // 清空推荐
        this.showRecommendationTip = true; // 用户未登录时显示推荐气泡
        // 用户未登录时，清空定时器
        this.stopRecommendationRefresh();
        return;
      }

      this.loadingRecommendations = true; // 显示加载状态
      // 标记正在请求
      isRefreshing = true;

      try {
        // 调用实时推荐的接口
        const response = await axios.get(`/service-f/realtime_updated_recommendations/${userId}`);
        this.realtimeRecommendations = response.data.recommendations || [];
        console.log("实时推荐数据 (BookList):", this.realtimeRecommendations);

        // 如果没有实时推荐，显示提示气泡
        if (this.realtimeRecommendations.length === 0) {
          this.showRecommendationTip = true;
        } else {
          this.showRecommendationTip = false; // 有推荐时隐藏
        }

      } catch (error) {
        console.error('Error fetching realtime recommendations for book list:', error);
        this.realtimeRecommendations = []; // 出错时清空推荐
        this.showRecommendationTip = true; // 出错时也显示提示气泡

        if (error.response && error.response.data && error.response.data.message === "Redis 中没有实时更新的推荐数据。") {
          console.log("Redis 中当前没有该用户的实时推荐数据。");
        }
      } finally {
        this.loadingRecommendations = false; // 隐藏加载状态
        // 取消请求标记
        isRefreshing = false;
      }
    },

    // 启动推荐定时刷新的方法
    startRecommendationRefresh() {
      // 先停止原有定时器，避免重复
      this.stopRecommendationRefresh();
      // 每5秒刷新一次（可根据需求调整，比如3秒）
      recommendationRefreshTimer = setInterval(() => {
        this.fetchRealtimeRecommendationsForList();
      }, 5000); // 5000毫秒 = 5秒
      console.log("推荐数据定时刷新已启动（每5秒）");
    },

    // 停止推荐定时刷新的方法
    stopRecommendationRefresh() {
      if (recommendationRefreshTimer) {
        clearInterval(recommendationRefreshTimer);
        recommendationRefreshTimer = null;
        console.log("推荐数据定时刷新已停止");
      }
    },
    extractFilterOptions() {
      const genres = new Set();
      const years = new Set();
      this.allBooks.forEach(book => {
        book.genres.forEach(genre => genres.add(genre));
        if (book.publishDate) {
          const year = new Date(book.publishDate).getFullYear();
          if (!isNaN(year)) {
            years.add(year);
          }
        }
      });
      this.availableGenres = Array.from(genres).sort();
      this.availableYears = Array.from(years).sort((a, b) => b - a);
    },
    toggleGenre(genre) {
      const index = this.selectedGenres.indexOf(genre);
      if (index > -1) {
        this.selectedGenres.splice(index, 1);
      } else {
        this.selectedGenres.push(genre);
      }
      this.applyFilters();
      // 用户点击流派后，可以隐藏流派提示气泡
      this.showGenreTip = false;
    },
    applyFilters() {
      // Re-evaluates computed properties `filteredBooks` and `paginatedBooks`
      // `currentPage` is reset by the `filteredBooks` watcher
    },
    applyFiltersDebounced() {
      clearTimeout(this.priceDebounceTimer);
      this.priceDebounceTimer = setTimeout(() => {
        this.applyFilters();
      }, 500); // Debounce by 500ms
    },
    resetFilters() {
      this.selectedGenres = [];
      this.selectedRating = '';
      this.minPrice = null;
      this.maxPrice = null;
      this.selectedYear = '';
      this.inputSearchKeyword = ''; // Reset search keyword
      this.genreSearchTerm = ''; // Reset genre search term
      this.showAllGenres = false; // Reset genre display
      this.applyFilters();
    },
    truncateDescription(desc) {
      if (!desc) return '';
      return desc.length > 200 ? desc.substring(0, 200) + '...' : desc;
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        // Optionally scroll to top of book list when page changes
        const catalogue = this.$el.querySelector('.catalogue-of-works');
        if (catalogue) {
          catalogue.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    }
  },
};
</script>

<style scoped>
/* A Font of Ages: Evoking the Scribe's Hand */
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Playfair+Display:wght@400;700;900&display=swap');

/* --- 气泡提示样式【优化核心：柔化+精准定位+防遮挡】 --- */
.info-bubble {
  position: absolute;
  background-color: #795548;
  color: #fff;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 0.85em;
  white-space: nowrap;
  z-index: 9999;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(253,250,243,0.5);
  pointer-events: none;
  opacity: 0;
  animation: fadeInOut 6s forwards cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(2px);
}
/* 气泡箭头【优化：圆润+精准对齐】 */
.info-bubble::after {
  content: '';
  position: absolute;
  border-width: 7px;
  border-style: solid;
}
.seek-button { position: relative; }
.info-bubble.bottom-right {
  top: calc(100% + 5px);
  left: 50%;
  transform: translate(-10%, 0);
}
.info-bubble.bottom-right::after {
  top: -7px;
  left: 20%;
  border-color: transparent transparent #795548 transparent;
}
.genre-filter-pill { position: relative; }
.info-bubble.top-center {
  bottom: calc(100% + 5px);
  left: 50%;
  transform: translate(-50%, 0);
}
.info-bubble.top-center::after {
  bottom: -7px;
  left: 50%;
  transform: translateX(-50%);
  border-color: #795548 transparent transparent transparent;
}
.no-recommendations-message {
  position: relative;
  display: inline-block;
}
.info-bubble.bottom-left {
  top: calc(100% + 5px);
  right: 0;
  transform: translate(0, 0);
}
.info-bubble.bottom-left::after {
  top: -7px;
  right: 15px;
  border-color: transparent transparent #795548 transparent;
}

/* 气泡动画【优化：更顺滑的淡入淡出+停留时长】 */
@keyframes fadeInOut {
  0% { opacity: 0; transform: translateY(5px); }
  12% { opacity: 1; transform: translateY(0); }
  88% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(5px); }
}

/* 父级定位兼容 */
.top-folio-controls, .genre-filter-section, .oracle-sidebar { position: relative; }

/* The Grand Container of Lore 【核心优化：纸张纹理+做旧质感+双层阴影】 */
.ancient-tome-container {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fdfaf3;
  border: 1px solid #d4c7b2;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18), 10px 10px 0 rgba(212,199,178,0.2);
  font-family: 'Merriweather', serif;
  color: #3b2f2f;
  position: relative;
  overflow: hidden;
}
/* 羊皮纸纹理【新增：叠加肌理，告别纯色】 */
.ancient-tome-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle, rgba(253, 250, 243, 0.92) 0%, rgba(240, 235, 220, 0.92) 100%);
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0.5 0"/></filter><rect width="200" height="200" filter="url(%23noise)" opacity="0.1"/></svg>');
  opacity: 0.9;
  pointer-events: none;
  z-index: -1;
}

/* --- Top Folio Controls (Search & Horizontal Filters) 【优化：内阴影+浮雕边框+质感升级】--- */
.top-folio-controls {
  background: #f0ebe0;
  border-radius: 16px;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.08), 0 2px 0 rgba(255,255,255,0.6) inset;
  border: 1px solid #d4c7b2;
  border-top-color: #e0d4c0;
  border-bottom-color: #c0b29b;
  padding: 1.5rem 2rem;
  margin-bottom: 2.5rem;
}

/* The Seeker's Scrutiny 搜索区 */
.search-quill-box {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
  gap: 1rem;
  align-items: center;
}
.quill-input {
  flex-grow: 1;
  max-width: 30rem;
  padding: 1rem 1.5rem;
  border: 2px solid #b3a08d;
  border-radius: 8px;
  background: #ffffff;
  font-family: 'Merriweather', serif;
  font-size: 1.1rem;
  color: #3b2f2f;
  transition: all 0.3s ease-in-out;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05) inset;
}
.quill-input::placeholder {
  color: #8c7f73;
  opacity: 0.8;
}
.quill-input:focus {
  outline: none;
  border-color: #8d6e63;
  box-shadow: 0 0 0 3px rgba(141, 110, 99, 0.25), 0 1px 3px rgba(0,0,0,0.05) inset;
}
/* 搜索按钮【核心优化：渐变背景+按压反馈+hover抬升+字体加粗】 */
.seek-button {
  padding: 1rem 2rem;
  background: linear-gradient(180deg, #8d6e63 0%, #6d5448 100%);
  color: #fdfaf3;
  font-weight: 700;
  font-family: 'Playfair Display', serif;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15), 0 1px 0 rgba(255,255,255,0.2) inset;
  transition: all 0.3s ease-in-out;
  border: none;
  cursor: pointer;
  letter-spacing: 0.05em;
  position: relative;
}
.seek-button:hover {
  background: linear-gradient(180deg, #7d5e53 0%, #5d4438 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2);
}
.seek-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0,0,0,0.2), 0 1px 0 rgba(0,0,0,0.1) inset;
}
.seek-button:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(141, 110, 99, 0.4), 0 4px 10px rgba(0,0,0,0.15);
}

/* Astrolabe Filters - Horizontal Layout 筛选区布局优化 */
.astrolabe-filters-horizontal {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: flex-start;
  justify-content: center;
  padding-top: 1.5rem;
  border-top: 1px dashed #c0b29b;
}
.filter-section-inline {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  flex-basis: auto;
  flex-grow: 1;
  min-width: 180px;
}
.filter-title-inline {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: #5a4b41;
  margin-bottom: 0.8rem;
  white-space: nowrap;
  letter-spacing: 0.03em;
}
/* 下拉框/输入框【优化：自定义下拉箭头+内阴影+选中高亮】 */
.filter-select-inline, .filter-input-inline {
  width: 100%;
  padding: 0.7rem 1.2rem;
  border: 1px solid #b3a08d;
  border-radius: 8px;
  background-color: #ffffff;
  font-family: 'Merriweather', serif;
  font-size: 0.95rem;
  color: #3b2f2f;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%235a4b41%22%20d%3D%22M287%2C197.3L159.2%2C69.5c-7.8-7.8-20.5-7.8-28.3%2C0L5.4%2C197.3c-7.8%2C7.8-7.8%2C20.5%2C0%2C28.3l14.2%2C14.2c7.8%2C7.8%2C20.5%2C7.8%2C28.3%2C0l102.2-102.2l102.2%2C102.2c7.8%2C7.8%2C20.5%2C7.8%2C28.3%2C0l14.2-14.2C294.8%2C217.8%2C294.8%2C205.1%2C287%2C197.3z%22%2F%3E%3C%2Fsvg%3E');
  background-repeat: no-repeat;
  background-position: right 0.8em top 50%;
  background-size: 0.65em auto;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05) inset;
}
.filter-select-inline:focus, .filter-input-inline:focus {
  outline: none;
  border-color: #8d6e63;
  box-shadow: 0 0 0 2px rgba(141, 110, 99, 0.3), 0 1px 2px rgba(0,0,0,0.05) inset;
}
.price-filter-group {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
  min-width: 200px;
}
.price-filter-group .filter-input-inline { flex-grow: 1; }

/* Genre Specific Styles 分类筛选【核心优化：选中动效+hover质感+滚动条美化升级】 */
.genre-filter-wrapper { display: flex; flex-direction: column; width: 100%; }
.genre-search-input {
  width: 100%;
  padding: 0.7rem 1.2rem;
  margin-bottom: 0.8rem;
  border: 1px solid #b3a08d;
  border-radius: 8px;
  background-color: #ffffff;
  font-family: 'Merriweather', serif;
  font-size: 0.95rem;
  color: #3b2f2f;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05) inset;
}
.genre-search-input:focus {
  outline: none;
  border-color: #8d6e63;
  box-shadow: 0 0 0 2px rgba(141, 110, 99, 0.3);
}
.genre-pill-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  max-height: 120px;
  overflow-y: auto;
  padding-right: 5px;
  scrollbar-width: thin;
  scrollbar-color: #8d6e63 #f0ebe0;
}
.genre-pill-container::-webkit-scrollbar { width: 8px; }
.genre-pill-container::-webkit-scrollbar-track { background: #f0ebe0; border-radius: 4px; }
.genre-pill-container::-webkit-scrollbar-thumb {
  background-color: #8d6e63;
  border-radius: 4px;
  border: 2px solid #f0ebe0;
  transition: background 0.2s ease;
}
.genre-pill-container::-webkit-scrollbar-thumb:hover { background-color: #6d5448; }
/* 分类标签【核心优化：选中渐变+缩放+阴影+边框层次感】 */
.genre-filter-pill {
  background-color: #e0d4c0;
  color: #5a4b41;
  padding: 0.5rem 0.9rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #d4c7b2;
  border-bottom-color: #c0b29b;
  flex-shrink: 0;
  box-shadow: 0 1px 0 rgba(255,255,255,0.6) inset;
}
.genre-filter-pill:hover {
  background-color: #d4c7b2;
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
  border-color: #b3a08d;
}
.genre-filter-pill.is-selected {
  background: linear-gradient(180deg, #8d6e63 0%, #6d5448 100%);
  color: #fdfaf3;
  border-color: #6d5448;
  transform: translateY(-1px) scale(1.03);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
}
.toggle-genre-button {
  background: linear-gradient(180deg, #b3a08d 0%, #8c7f73 100%);
  color: #fdfaf3;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  margin-top: 0.8rem;
  transition: all 0.2s ease;
  align-self: flex-end;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.toggle-genre-button:hover { background: linear-gradient(180deg, #a3907d 0%, #7c6f63 100%); }
/* 重置按钮优化 */
.reset-filters-button-inline {
  padding: 0.9rem 1.8rem;
  background: linear-gradient(180deg, #6d5448 0%, #5a4b41 100%);
  color: #fdfaf3;
  font-weight: 600;
	font-family: 'Playfair Display', serif;
  border-radius: 8px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15), 0 1px 0 rgba(255,255,255,0.2) inset;
  transition: all 0.3s ease-in-out;
  border: none;
  cursor: pointer;
  letter-spacing: 0.03em;
  align-self: center;
  margin-top: 1.5rem;
  white-space: nowrap;
}
.reset-filters-button-inline:hover {
  background: linear-gradient(180deg, #5d4438 0%, #4a3b31 100%);
  transform: translateY(-1px);
  box-shadow: 0 5px 12px rgba(0, 0, 0, 0.2);
}
.reset-filters-button-inline:active { transform: translateY(0); }

/* --- Main Content Area (Book Catalogue & Recommendations) 布局优化 --- */
.parchment-scroll-wrapper {
  display: flex;
  gap: 2.5rem;
  flex-wrap: wrap;
  justify-content: center;
}
.catalogue-of-works { flex: 3; min-width: 600px; }
/* 提示文案优化 */
.scribe-message {
  text-align: center;
  font-style: italic;
  font-size: 1.2rem;
  color: #5a4b41;
  padding: 3rem 0;
  line-height: 1.6;
}

/* 书籍列表【核心优化：卡片立体阴影+hover翻页动效+封面悬浮放大】 */
.tome-collection { display: flex; flex-direction: column; gap: 2rem; }
.tome-folio {
  display: flex;
  background-color: #fdfaf3;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08), 0 2px 0 rgba(255,255,255,0.8) inset;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #e0d4c0;
  border-bottom-color: #d4c7b2;
  position: relative;
}
/* 书籍卡片hover：模拟翻书的倾斜+抬升+加深阴影，核心质感升级 */
.tome-folio:hover {
  transform: translateY(-8px) rotate(-0.8deg);
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.15);
}
/* 书籍封面容器 */
.illumination-plate {
  flex-shrink: 0;
  width: 150px;
  height: 220px;
  overflow: hidden;
  background-color: #e8e0d4;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #d4c7b2;
  position: relative;
  z-index: 1;
}
.illumination-plate::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(to right, rgba(253, 250, 243, 0) 0%, rgba(253, 250, 243, 0.4) 100%);
  pointer-events: none;
}
/* 书籍封面【核心优化：hover放大+圆角+阴影，模拟实体书封面】 */
.tome-cover-art {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.4s ease;
}
.tome-folio:hover .tome-cover-art { transform: scale(1.03); }

/* 书籍信息区 */
.tome-inscriptions {
  padding: 1.8rem 2.2rem;
  text-align: left;
  flex-grow: 1;
}
.tome-title-link {
  text-decoration: none;
  color: #5a4b41;
  transition: color 0.3s ease;
}
.tome-title-link:hover { color: #8d6e63; text-decoration: underline; text-decoration-style: dotted; }
.tome-title {
  font-family: 'Playfair Display', serif;
  font-size: 2.2rem;
  font-weight: 900;
  margin-bottom: 0.5rem;
  line-height: 1.2;
  letter-spacing: -0.02em;
}
.tome-series {
  font-family: 'Merriweather', serif;
	font-size: 1.1rem;
	color: #7b6a5e;
	margin-bottom: 0.8rem;
	font-style: italic;
}
.tome-author {
  font-family: 'Merriweather', serif;
	font-size: 1rem;
	color: #5a4b41;
	margin-bottom: 0.8rem;
}
/* 星级评分【核心优化：金色渐变+呼吸动画，视觉重点突出】 */
.celestial-guidance { display: flex; align-items: center; margin-bottom: 0.8rem; }
.stars-illuminated {
  color: #e6b800;
  font-size: 1.5rem;
  margin-right: 0.5rem;
  letter-spacing: 0.05em;
  text-shadow: 0 1px 2px rgba(230,184,0,0.3);
  transition: all 0.3s ease;
}
.tome-folio:hover .stars-illuminated { color: #f0c808; transform: scale(1.05); }
.whispers-of-critics { font-size: 0.9rem; color: #8c7f73; }
.tome-summary {
  font-family: 'Merriweather', serif;
	font-size: 1rem;
	color: #3b2f2f;
	line-height: 1.7;
	margin-bottom: 1.2rem;
}
.tome-provenance {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem 1.5rem;
  font-size: 0.9rem;
  color: #7b6a5e;
  margin-bottom: 1.2rem;
}
.tome-provenance strong { font-weight: 700; color: #5a4b41; }
/* 分类标签 */
.scholarly-genres { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.genre-seal {
  background: #e0d4c0;
  color: #5a4b41;
	padding: 0.4rem 0.9rem;
	border-radius: 20px;
	font-size: 0.75rem;
	font-weight: 600;
	letter-spacing: 0.03em;
	transition: all 0.2s ease;
	border: 1px solid #d4c7b2;
}
.genre-seal:hover { background: #d4c7b2; color: #3b2f2f; }
.genre-seal.more-genres {
  cursor: default;
  background-color: transparent;
  border: none;
  font-weight: 700;
  color: #8c7f73;
}

/* --- Pagination Controls 分页【核心优化：按钮质感+选中高亮+hover反馈】--- */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 3rem;
  gap: 0.6rem;
  padding: 1.5rem;
  background: #f0ebe0;
  border-radius: 16px;
  border: 1px solid #d4c7b2;
  box-shadow: inset 0 1px 5px rgba(0, 0, 0, 0.05);
}
.pagination-button {
  padding: 0.9rem 1.3rem;
  background: linear-gradient(180deg, #b3a08d 0%, #8c7f73 100%);
  color: #fdfaf3;
  border: none;
  border-radius: 8px;
  cursor: pointer;
	font-family: 'Merriweather', serif;
	font-size: 0.95rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.pagination-button:hover:not(:disabled) {
  background: linear-gradient(180deg, #a3907d 0%, #7c6f63 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}
.pagination-button:disabled {
  background: #d4c7b2;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
}
.page-number {
  padding: 0.9rem 1.1rem;
  min-width: 42px;
  text-align: center;
  background: #ffffff;
  color: #5a4b41;
  border: 1px solid #d4c7b2;
  border-radius: 8px;
  cursor: pointer;
	font-family: 'Merriweather', serif;
	font-size: 0.95rem;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.page-number:hover:not(.is-current):not(.is-ellipsis) {
  background-color: #e8e0d4;
  border-color: #b3a08d;
  transform: translateY(-1px);
}
.page-number.is-current {
  background: linear-gradient(180deg, #6d5448 0%, #5a4b41 100%);
  color: #fdfaf3;
  border-color: #5a4b41;
  font-weight: 700;
  cursor: default;
  transform: none;
}
.page-number.is-ellipsis {
  background: transparent;
  border: none;
  cursor: default;
  color: #8c7f73;
  font-weight: 700;
  letter-spacing: 2px;
}

/* The Oracle's Prognostications (Right Sidebar) 推荐侧边栏【核心优化：粘性定位优化+质感升级+卡片hover】 */
.oracle-sidebar {
  flex: 0 0 280px;
  background: linear-gradient(180deg, #f0ebe0 0%, #e8e0d4 100%);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08), 0 2px 0 rgba(255,255,255,0.6) inset;
  height: fit-content;
  position: sticky;
  top: 2rem;
  border: 1px solid #d4c7b2;
  border-bottom-color: #c0b29b;
}
.oracle-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px dashed #c0b29b;
  text-align: center;
}
.oracle-title {
  font-family: 'Playfair Display', serif;
	font-size: 1.8rem;
	font-weight: 900;
	color: #5a4b41;
	margin-bottom: 0.4rem;
  letter-spacing: -0.02em;
}
.oracle-subtitle { font-size: 0.9rem; color: #8c7f73; font-style: italic; }
.oracle-list { display: flex; flex-direction: column; gap: 1.2rem; }
/* 推荐书籍卡片【核心优化：hover右移+背景高亮+边框】 */
.oracle-insight {
  display: flex;
  gap: 1rem;
  padding: 0.8rem;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  border: 1px solid transparent;
  cursor: pointer;
}
.oracle-insight:hover {
  background-color: #e5e0d4;
  transform: translateX(6px);
  border-color: #c0b29b;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.oracle-effigy {
  width: 70px;
  height: 100px;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #d4c7b2;
}
.oracle-cover-mini {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.oracle-insight:hover .oracle-cover-mini { transform: scale(1.02); }
.oracle-details { flex-grow: 1; display: flex; flex-direction: column; justify-content: center; }
.oracle-insight-title {
  font-family: 'Playfair Display', serif;
	font-size: 1.05rem;
	font-weight: 600;
	color: #3b2f2f;
	margin-bottom: 0.2rem;
}
.oracle-insight-author { font-size: 0.85rem; color: #7b6a5e; margin-bottom: 0.4rem; }
.oracle-celestial-guidance { display: flex; align-items: center; }
.stars-illuminated-small {
  color: #e6b800;
	font-size: 1.1rem;
	margin-right: 0.3rem;
}
.whispers-of-critics-small { font-size: 0.75rem; color: #8c7f73; }

/* Scroll Effects - 过渡动画【优化：缓动函数+位移距离，更顺滑】 */
.book-fade-enter-active, .book-fade-leave-active { transition: all 0.7s cubic-bezier(0.4, 0, 0.2, 1); }
.book-fade-enter-from, .book-fade-leave-to { opacity: 0; transform: translateX(-30px); }
.book-fade-leave-active { position: absolute; }

.recommendation-slide-enter-active, .recommendation-slide-leave-active { transition: all 0.6s ease; }
.recommendation-slide-enter-from, .recommendation-slide-leave-to { opacity: 0; transform: translateY(15px); }
.recommendation-slide-move { transition: transform 0.6s ease; }

/* --- Responsive Adaptations 响应式【完善：修复小屏错位+间距优化+适配更友好】--- */
@media (max-width: 1200px) {
  .parchment-scroll-wrapper { flex-direction: column; align-items: center; }
  .catalogue-of-works, .oracle-sidebar { min-width: auto; width: 100%; }
  .oracle-sidebar { position: static; margin-top: 2rem; }
  .astrolabe-filters-horizontal { flex-direction: column; align-items: flex-start; gap: 1.5rem; }
  .filter-section-inline { width: 100%; min-width: auto; }
  .price-filter-group { width: 100%; justify-content: space-between; }
  .pagination-controls { flex-wrap: wrap; padding: 1rem; gap: 0.5rem; }
  .pagination-button, .page-number { flex-basis: 45%; margin: 0.25rem; }
}
@media (max-width: 768px) {
  .ancient-tome-container { padding: 1.5rem; }
  .search-quill-box { flex-direction: column; gap: 0.8rem; padding: 1rem; width: 100%; }
  .quill-input, .seek-button { width: 100%; text-align: center; }
  .tome-folio { flex-direction: column; text-align: center; }
  .illumination-plate { width: 100%; height: 280px; border-right: none; border-bottom:1px solid #d4c7b2; }
  .tome-inscriptions { padding: 1.5rem; }
  .tome-title { font-size: 1.8rem; }
  .celestial-guidance, .tome-provenance, .scholarly-genres { justify-content: center; }
  .astrolabe-filters-horizontal { align-items: center; }
  .filter-section-inline { text-align: center; align-items: center; }
  .filter-title-inline { width: 100%; margin-bottom: 0.5rem; }
  .genre-pill-container { max-height: 100px; }
  .reset-filters-button-inline { width: 100%; }
}
@media (max-width: 480px) {
  .ancient-tome-container { padding: 1rem; }
  .tome-title { font-size: 1.6rem; }
  .tome-series, .tome-author, .tome-summary { font-size: 0.9rem; }
  .oracle-title { font-size: 1.5rem; }
  .pagination-button, .page-number { padding: 0.6rem 0.8rem; font-size: 0.85rem; flex-basis: auto; }
  .illumination-plate { height: 240px; }
}
</style>