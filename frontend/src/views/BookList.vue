<!-- 书籍展示页面 -->
<template>
  <div class="ancient-tome-container">
    <div class="top-folio-controls">
      <div class="search-quill-box">
        <input type="text" v-model="inputSearchKeyword" placeholder="Inscribe thy quest here..."
          @keyup.enter="handleSearch" class="quill-input" />
        <button @click="handleSearch" class="seek-button">
          Seek & Discover
        </button>
      </div>

      <div class="astrolabe-filters-horizontal">
        <div class="filter-section-inline">
          <h3 class="filter-title-inline">By Genre's Lore:</h3>
          <div class="genre-filter-wrapper">
            <input type="text" v-model="genreSearchTerm" placeholder="Search genres..." class="genre-search-input" />
            <div class="genre-pill-container">
              <span v-for="genre in filteredAvailableGenres" :key="genre" class="genre-filter-pill"
                :class="{ 'is-selected': selectedGenres.includes(genre) }" @click="toggleGenre(genre)">
                {{ genre }}
              </span>
              <span v-if="filteredAvailableGenres.length === 0 && availableGenres.length > 0"
                class="no-options-message">No matching genres.</span>
              <span v-else-if="availableGenres.length === 0" class="no-options-message">No genres discovered.</span>
            </div>
            <button v-if="availableGenres.length > maxDisplayedGenres && !showAllGenres" @click="showAllGenres = true"
              class="toggle-genre-button">Show All ({{ availableGenres.length - maxDisplayedGenres }} More)</button>
            <button v-if="showAllGenres" @click="showAllGenres = false" class="toggle-genre-button">Show Less</button>
          </div>
        </div>

        <div class="filter-section-inline">
          <h3 class="filter-title-inline">By Celestial Judgement (Rating):</h3>
          <select v-model="selectedRating" @change="applyFilters" class="filter-select-inline">
            <option value="">Any Appraisal</option>
            <option value="4">4 Stars & Above</option>
            <option value="3">3 Stars & Above</option>
            <option value="2">2 Stars & Above</option>
            <option value="1">1 Star & Above</option>
          </select>
        </div>

        <div class="filter-section-inline price-filter-group">
          <h3 class="filter-title-inline">By Scrivener's Price:</h3>
          <input type="number" v-model.number="minPrice" @input="applyFiltersDebounced" placeholder="Min."
            class="filter-input-inline" />
          <span> — </span>
          <input type="number" v-model.number="maxPrice" @input="applyFiltersDebounced" placeholder="Max."
            class="filter-input-inline" />
        </div>

        <div class="filter-section-inline">
          <h3 class="filter-title-inline">By Inscription Year:</h3>
          <select v-model="selectedYear" @change="applyFilters" class="filter-select-inline">
            <option value="">All Epochs</option>
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>

        <button @click="resetFilters" class="reset-filters-button-inline">Clear All Astrolabe Settings</button>
      </div>
    </div>

    <div class="parchment-scroll-wrapper">
      <main class="catalogue-of-works">
        <p v-if="loading" class="scribe-message">The Scribe is diligently turning pages...</p>
        <p v-else-if="!paginatedBooks || paginatedBooks.length === 0" class="scribe-message">Alas, no such tome matches
          these refined criteria.</p>
        <transition-group name="book-fade" tag="div" class="tome-collection" v-else>
          <div v-for="book in paginatedBooks" :key="book.bookId" class="tome-folio">
            <div class="illumination-plate">
              <img :src="book.coverImg" :alt="book.title" class="tome-cover-art" />
            </div>
            <div class="tome-inscriptions">
              <router-link :to="{ name: 'BookDetails', params: { bookId: book.bookId } }" class="tome-title-link">
                <h2 class="tome-title">{{ book.title }}</h2>
              </router-link>
              <h3 v-if="book.series" class="tome-series">A Chapter in the Chronicle of {{ book.series }}</h3>
              <p class="tome-author">Penned by {{ book.author }}</p>
              <div class="celestial-guidance">
                <span class="stars-illuminated">{{ '★'.repeat(Math.round(book.rating)) }}{{
                  '☆'.repeat(5 - Math.round(book.rating)) }}</span>
                <span class="whispers-of-critics">({{ book.rating }} from {{ book.numRatings }} Judgements)</span>
              </div>
              <p class="tome-summary">{{ truncateDescription(book.description) }}</p>
              <div class="tome-provenance">
                <span><strong>Incepted:</strong> {{ book.publishDate }}</span>
                <span><strong>Folios:</strong> {{ book.pages }}</span>
                <span><strong>Appraisal:</strong> ${{ book.price }}</span>
              </div>
              <div class="scholarly-genres">
                <span v-for="genre in book.genres.slice(0, 3)" :key="genre" class="genre-seal">{{ genre
                }}</span>
                <span v-if="book.genres.length > 3" class="genre-seal more-genres">...</span>
              </div>
            </div>
          </div>
        </transition-group>

        <div v-if="totalPages > 1" class="pagination-controls">
          <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="pagination-button">
            &laquo; Prior Folio
          </button>
          <span v-for="page in paginationPages" :key="page" class="page-number"
            :class="{ 'is-current': page === currentPage, 'is-ellipsis': page === '...' }"
            @click="page !== '...' && goToPage(page)">
            {{ page }}
          </span>
          <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages" class="pagination-button">
            Next Folio &raquo;
          </button>
        </div>

      </main>

      <aside class="oracle-sidebar">
        <div class="oracle-header">
          <h3 class="oracle-title">Whispers from the Oracle</h3>
          <p class="oracle-subtitle">Guided by the Constellations of Thy Past Readings</p>
        </div>
        <div class="oracle-list">
          <transition-group name="recommendation-slide" tag="div">
            <div v-for="(rec, index) in recommendations" :key="index" class="oracle-insight">
              <router-link :to="{ name: 'BookDetails', params: { bookId: rec.bookId } }" class="oracle-insight-link">
                <div class="oracle-effigy">
                  <img :src="rec.coverImg" :alt="rec.title" class="oracle-cover-mini" />
                </div>
                <div class="oracle-details">
                  <h4 class="oracle-insight-title">{{ rec.title }}</h4>
                  <p class="oracle-insight-author">{{ rec.author }}</p>
                  <div class="oracle-celestial-guidance">
                    <span class="stars-illuminated-small">{{ '★'.repeat(Math.round(rec.rating)) }}</span>
                    <span class="whispers-of-critics-small">({{ rec.rating }})</span>
                  </div>
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
      recommendations: [],
      loading: true,

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
    this.fetchRecommendations();
  },
  watch: {
    // Watch filteredBooks to reset currentPage when filters change
    filteredBooks() {
      this.currentPage = 1; // Reset to first page whenever filters change
    },
    inputSearchKeyword() {
      this.applyFilters();
    },
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
    handleSearch() {
      this.applyFilters();
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
    async fetchRecommendations() {
      const loggedInUser = getParsedUserData();
      const userId = loggedInUser ? loggedInUser.user_id : null;
      try {
        const recommendationApiUrl = `/service-d/recommendations/offline/${userId}`; // 根据实际API网关或Nginx配置调整
        const response = await axios.get(recommendationApiUrl);

        // 后端返回的 recommendations 列表，只包含 book_id, title, category
        const recommendedBookIds = response.data.recommendations;

        // 根据后端推荐的 book_id，从 allBooks 中查找完整的书籍信息
        // 这里的查找逻辑可以优化，例如使用 Map 结构来提高查找效率
        const fullRecommendations = recommendedBookIds.map(recBook => {
          // 在 allBooks 中找到匹配的完整书籍信息
          const fullBookInfo = this.allBooks.find(book => book.bookId === recBook.book_id);
          // 合并后端返回的简化信息和 allBooks 中的完整信息
          // 确保显示在侧边栏的推荐书籍有 coverImg, author, rating 等字段
          return {
            bookId: recBook.book_id,
            title: recBook.title,
            category: recBook.category,
            reason: recBook.reason, // 模拟推荐理由
            coverImg: fullBookInfo ? fullBookInfo.coverImg : 'path/to/default/cover.jpg', // 默认图片
            author: fullBookInfo ? fullBookInfo.author : 'Unknown Author',
            rating: fullBookInfo ? fullBookInfo.rating : 0 // 默认评分
          };
        });

        this.recommendations = fullRecommendations;

      } catch (error) {
        console.error('Error fetching recommendations:', error);
        this.recommendations = [];
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
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Playfair+Display:wght@400;700&display=swap');

/* The Grand Container of Lore */
.ancient-tome-container {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fdfaf3;
  /* Old Paper */
  border: 1px solid #d4c7b2;
  border-radius: 8px;
  box-shadow: 10px 10px 30px rgba(0, 0, 0, 0.15);
  font-family: 'Merriweather', serif;
  color: #3b2f2f;
  /* Deep Ink */
  position: relative;
  overflow: hidden;
}

/* The Subtle Grain of Parchment */
.ancient-tome-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle, rgba(253, 250, 243, 0.9) 0%, rgba(240, 235, 220, 0.9) 100%);
  opacity: 0.8;
  pointer-events: none;
  z-index: -1;
}

/* --- Top Folio Controls (Search & Horizontal Filters) --- */
.top-folio-controls {
  background: #f0ebe0;
  border-radius: 12px;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #d4c7b2;
  padding: 1.5rem 2rem;
  margin-bottom: 2.5rem;
}

/* The Seeker's Scrutiny */
.search-quill-box {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
  gap: 1rem;
}

.quill-input {
  flex-grow: 1;
  max-width: 30rem;
  padding: 0.85rem 1.25rem;
  border: 2px solid #b3a08d;
  border-radius: 6px;
  background: #ffffff;
  font-family: 'Merriweather', serif;
  font-size: 1.1rem;
  color: #3b2f2f;
  transition: all 0.3s ease-in-out;
}

.quill-input::placeholder {
  color: #8c7f73;
}

.quill-input:focus {
  outline: none;
  border-color: #8d6e63;
  box-shadow: 0 0 0 3px rgba(141, 110, 99, 0.3);
}

.seek-button {
  padding: 0.85rem 1.8rem;
  background: #8d6e63;
  color: #fdfaf3;
  font-weight: 700;
  font-family: 'Playfair Display', serif;
  border-radius: 6px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease-in-out;
  border: none;
  cursor: pointer;
  letter-spacing: 0.05em;
}

.seek-button:hover {
  background: #6d5448;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25);
}

.seek-button:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(141, 110, 99, 0.4);
}

/* Astrolabe Filters - Horizontal Layout */
.astrolabe-filters-horizontal {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: flex-start;
  justify-content: center;
  padding-top: 1.5rem;
  border-top: 1px dashed #d4c7b2;
}

.filter-section-inline {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  flex-basis: auto;
  /* Allow items to size naturally */
  flex-grow: 1;
  /* Allow growth */
  min-width: 180px;
  /* Minimum width for filter sections */
}

.filter-title-inline {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: #5a4b41;
  margin-bottom: 0.8rem;
  white-space: nowrap;
}

.filter-select-inline,
.filter-input-inline {
  width: 100%;
  padding: 0.6rem 1rem;
  border: 1px solid #b3a08d;
  border-radius: 6px;
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
}

.filter-select-inline:focus,
.filter-input-inline:focus {
  outline: none;
  border-color: #8d6e63;
  box-shadow: 0 0 0 2px rgba(141, 110, 99, 0.3);
}

.price-filter-group {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
  min-width: 200px;
}

.price-filter-group .filter-input-inline {
  flex-grow: 1;
}

/* Genre Specific Styles */
.genre-filter-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.genre-search-input {
  width: 100%;
  padding: 0.6rem 1rem;
  margin-bottom: 0.8rem;
  border: 1px solid #b3a08d;
  border-radius: 6px;
  background-color: #ffffff;
  font-family: 'Merriweather', serif;
  font-size: 0.95rem;
  color: #3b2f2f;
  transition: all 0.2s ease;
}

.genre-search-input:focus {
  outline: none;
  border-color: #8d6e63;
  box-shadow: 0 0 0 2px rgba(141, 110, 99, 0.3);
}

.genre-pill-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  max-height: 120px;
  /* Limit height for overflow */
  overflow-y: auto;
  padding-right: 5px;
  /* For scrollbar */
  scrollbar-width: thin;
  /* Firefox */
  scrollbar-color: #8d6e63 #f0ebe0;
  /* Firefox */
}

/* Scrollbar styles for Webkit (Chrome, Safari) */
.genre-pill-container::-webkit-scrollbar {
  width: 8px;
}

.genre-pill-container::-webkit-scrollbar-track {
  background: #f0ebe0;
  border-radius: 4px;
}

.genre-pill-container::-webkit-scrollbar-thumb {
  background-color: #8d6e63;
  border-radius: 4px;
  border: 2px solid #f0ebe0;
}


.genre-filter-pill {
  background-color: #e0d4c0;
  color: #5a4b41;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #d4c7b2;
  flex-shrink: 0;
  /* Prevent shrinking */
}

.genre-filter-pill:hover {
  background-color: #d4c7b2;
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.genre-filter-pill.is-selected {
  background-color: #8d6e63;
  color: #fdfaf3;
  border-color: #6d5448;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.toggle-genre-button {
  background: #b3a08d;
  color: #fdfaf3;
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  margin-top: 0.8rem;
  transition: background-color 0.2s ease;
  align-self: flex-end;
}

.toggle-genre-button:hover {
  background: #8c7f73;
}

.reset-filters-button-inline {
  padding: 0.8rem 1.5rem;
  background: #6d5448;
  color: #fdfaf3;
  font-weight: 600;
  font-family: 'Playfair Display', serif;
  border-radius: 6px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease-in-out;
  border: none;
  cursor: pointer;
  letter-spacing: 0.03em;
  align-self: center;
  /* Center horizontally */
  margin-top: 1.5rem;
  /* Space from filters above */
  white-space: nowrap;
}

.reset-filters-button-inline:hover {
  background: #5a4b41;
  transform: translateY(-1px);
  box-shadow: 0 5px 12px rgba(0, 0, 0, 0.2);
}


/* --- Main Content Area (Book Catalogue & Recommendations) --- */
.parchment-scroll-wrapper {
  display: flex;
  gap: 2.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

/* The Grand Library's Catalogue (Main Content Area) */
.catalogue-of-works {
  flex: 3;
  min-width: 600px;
}

.scribe-message {
  text-align: center;
  font-style: italic;
  font-size: 1.2rem;
  color: #5a4b41;
  padding: 3rem 0;
}

.tome-collection {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.tome-folio {
  display: flex;
  background-color: #fdfaf3;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.4s ease, box-shadow 0.4s ease;
  border: 1px solid #e0d4c0;
  position: relative;
}

.tome-folio:hover {
  transform: translateY(-8px) rotate(-1deg);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
}

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
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to right, rgba(253, 250, 243, 0) 0%, rgba(253, 250, 243, 0.3) 100%);
  pointer-events: none;
}

.tome-cover-art {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

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

.tome-title-link:hover {
  color: #8d6e63;
  text-decoration: underline;
}

.tome-title {
  font-family: 'Playfair Display', serif;
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  line-height: 1.2;
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

.celestial-guidance {
  display: flex;
  align-items: center;
  margin-bottom: 0.8rem;
}

.stars-illuminated {
  color: #e6b800;
  font-size: 1.5rem;
  margin-right: 0.5rem;
  letter-spacing: 0.05em;
}

.whispers-of-critics {
  font-size: 0.9rem;
  color: #8c7f73;
}

.tome-summary {
  font-family: 'Merriweather', serif;
  font-size: 1rem;
  color: #3b2f2f;
  line-height: 1.6;
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

.tome-provenance strong {
  font-weight: 700;
}

.scholarly-genres {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

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

.genre-seal:hover {
  background: #d4c7b2;
  color: #3b2f2f;
}

.genre-seal.more-genres {
  cursor: default;
  background-color: transparent;
  border: none;
  font-weight: 700;
  color: #8c7f73;
}

/* --- Pagination Controls --- */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 3rem;
  gap: 0.5rem;
  padding: 1.5rem;
  background: #f0ebe0;
  border-radius: 12px;
  border: 1px solid #d4c7b2;
  box-shadow: inset 0 1px 5px rgba(0, 0, 0, 0.05);
}

.pagination-button {
  padding: 0.8rem 1.2rem;
  background: #b3a08d;
  color: #fdfaf3;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Merriweather', serif;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.pagination-button:hover:not(:disabled) {
  background: #8c7f73;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.pagination-button:disabled {
  background: #d4c7b2;
  cursor: not-allowed;
  opacity: 0.7;
}

.page-number {
  padding: 0.8rem 1rem;
  min-width: 40px;
  text-align: center;
  background: #ffffff;
  color: #5a4b41;
  border: 1px solid #d4c7b2;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Merriweather', serif;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.page-number:hover:not(.is-current):not(.is-ellipsis) {
  background-color: #e8e0d4;
  border-color: #b3a08d;
}

.page-number.is-current {
  background: #6d5448;
  color: #fdfaf3;
  border-color: #5a4b41;
  font-weight: 700;
  cursor: default;
}

.page-number.is-ellipsis {
  background: transparent;
  border: none;
  cursor: default;
  color: #8c7f73;
  font-weight: 700;
  letter-spacing: 2px;
}


/* The Oracle's Prognostications (Right Sidebar) */
.oracle-sidebar {
  flex: 0 0 280px;
  background: #f0ebe0;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  height: fit-content;
  position: sticky;
  top: 2rem;
  border: 1px solid #d4c7b2;
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
  font-weight: 700;
  color: #5a4b41;
  margin-bottom: 0.4rem;
}

.oracle-subtitle {
  font-size: 0.9rem;
  color: #8c7f73;
  font-style: italic;
}

.oracle-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.oracle-insight {
  display: flex;
  gap: 1rem;
  padding: 0.8rem;
  border-radius: 8px;
  transition: background-color 0.3s ease, transform 0.2s ease;
  border: 1px solid transparent;
  cursor: pointer;
}

.oracle-insight:hover {
  background-color: #e5e0d4;
  transform: translateX(5px);
  border-color: #c0b29b;
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
}

.oracle-details {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.oracle-insight-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: #3b2f2f;
  margin-bottom: 0.2rem;
}

.oracle-insight-author {
  font-size: 0.85rem;
  color: #7b6a5e;
  margin-bottom: 0.4rem;
}

.oracle-celestial-guidance {
  display: flex;
  align-items: center;
}

.stars-illuminated-small {
  color: #e6b800;
  font-size: 1.1rem;
  margin-right: 0.3rem;
}

.whispers-of-critics-small {
  font-size: 0.75rem;
  color: #8c7f73;
}

/* Scroll Effects - Page Turning & Whispers */
/* For the main book list */
.book-fade-enter-active,
.book-fade-leave-active {
  transition: all 0.6s ease-in-out;
}

.book-fade-enter-from,
.book-fade-leave-to {
  opacity: 0;
  transform: translateX(-50px);
}

.book-fade-leave-active {
  position: absolute;
}

/* For recommendations */
.recommendation-slide-enter-active,
.recommendation-slide-leave-active {
  transition: all 0.5s ease;
}

.recommendation-slide-enter-from,
.recommendation-slide-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.recommendation-slide-move {
  transition: transform 0.5s ease;
}


/* Responsive Adaptations for Smaller Tomes */
@media (max-width: 1200px) {
  .parchment-scroll-wrapper {
    flex-direction: column;
    align-items: center;
  }

  .catalogue-of-works,
  .oracle-sidebar {
    min-width: auto;
    width: 100%;
  }

  .oracle-sidebar {
    position: static;
    margin-top: 2rem;
  }

  .astrolabe-filters-horizontal {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
  }

  .filter-section-inline {
    width: 100%;
    min-width: auto;
  }

  .price-filter-group {
    width: 100%;
    justify-content: space-between;
  }

  /* Pagination on smaller screens */
  .pagination-controls {
    flex-wrap: wrap;
    padding: 1rem;
  }

  .pagination-button,
  .page-number {
    flex-basis: 45%;
    /* Allow buttons to wrap */
    margin: 0.25rem;
  }
}

@media (max-width: 768px) {
  .ancient-tome-container {
    padding: 1.5rem;
  }

  .search-quill-box {
    flex-direction: column;
    gap: 0.8rem;
    padding: 1rem;
  }

  .quill-input,
  .seek-button {
    width: 100%;
    text-align: center;
  }

  .tome-folio {
    flex-direction: column;
    text-align: center;
  }

  .illumination-plate {
    width: 100%;
    height: 250px;
  }

  .tome-inscriptions {
    padding: 1.5rem;
  }

  .tome-title {
    font-size: 1.8rem;
  }

  .celestial-guidance {
    justify-content: center;
  }

  .tome-provenance,
  .scholarly-genres {
    justify-content: center;
  }

  .astrolabe-filters-horizontal {
    align-items: center;
  }

  .filter-section-inline {
    text-align: center;
    align-items: center;
  }

  .filter-title-inline {
    width: 100%;
    margin-bottom: 0.5rem;
  }

  .genre-pill-container {
    max-height: 100px;
    /* Adjust max height for smaller screens */
  }

  .reset-filters-button-inline {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .ancient-tome-container {
    padding: 1rem;
  }

  .tome-title {
    font-size: 1.6rem;
  }

  .tome-series,
  .tome-author,
  .tome-summary {
    font-size: 0.9rem;
  }

  .oracle-title {
    font-size: 1.5rem;
  }

  .pagination-button,
  .page-number {
    padding: 0.6rem 0.8rem;
    font-size: 0.85rem;
    flex-basis: auto;
    /* Allow items to size content */
  }
}
</style>