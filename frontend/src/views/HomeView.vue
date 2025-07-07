<template>
  <div class="home-view">
    <header class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">The Grand Tapestry of Knowledge: Charting Paths to Enlightenment</h1>
        <p class="hero-subtitle">A Conclave for Artisans, a Repository for Luminary Works. Discover, Delve, and
          Disentangle.</p>
        <button class="explore-button" @click="scrollToSection('popular-books')">Embark on the Quest</button>
      </div>
    </header>

    <main class="main-content">
      <p v-if="loading" class="loading-message">
      <div class="spinner"></div> The Quills are Busy, Kindly Stand By...
      </p>

      <div v-else class="content-wrapper">
        <div class="main-sections">
          <section class="section-container" id="popular-books">
            <div class="section-header">
              <h2 class="section-title">Volumes of Esteem: Acclaimed by the Cognoscenti</h2>
              <router-link to="/books" class="more-link">Peruse the Archives &gt;</router-link>
            </div>
            <div class="book-grid">
              <div v-for="book in popularBooks" :key="book.id" class="book-card">
                <img :src="book.coverImg" :alt="book.title" class="book-cover" />
                <div class="book-info">
                  <h3 class="book-title">{{ book.title }}</h3>
                  <p class="book-author">Authored by: {{ book.author }}</p>
                  <p class="book-genre" v-if="book.genres && book.genres.length > 0">Genre: {{ book.genres[0] }}</p>
                  <button @click="viewBookDetails(book.id)" class="details-button">Unfold the Narrative</button>
                </div>
              </div>
            </div>
          </section>

          <hr class="section-divider" />

          <section class="section-container" id="personalized-books">
            <div class="section-header">
              <h2 class="section-title">Curated for Your Discerning Eye</h2>
              <router-link to="/books" class="more-link">More Selections Befitting Your Taste &gt;</router-link>
            </div>
            <div class="book-grid">
              <div v-for="book in personalizedBooks" :key="book.id" class="book-card">
                <img :src="book.coverImg" :alt="book.title" class="book-cover" />
                <div class="book-info">
                  <h3 class="book-title">{{ book.title }}</h3>
                  <p class="book-author">Authored by: {{ book.author }}</p>
                  <p class="book-genre" v-if="book.genres && book.genres.length > 0">Genre: {{ book.genres[0] }}</p>
                  <button @click="viewBookDetails(book.id)" class="details-button">Unfold the Narrative</button>
                </div>
              </div>
            </div>
          </section>

          <hr class="section-divider" />

          <section class="section-container section-two-columns">
            <div class="ranking-section-wrapper" id="rankings">
              <div class="section-header-compact">
                <h2 class="section-title-small">The Pantheon of Literary Distinction</h2>
                <router-link to="/rankings" class="more-link-small">Behold the Full Register &gt;</router-link>
              </div>
              <div class="ranking-grid-compact">
                <div v-for="(rankList, index) in bookRankings" :key="index" class="ranking-card-compact">
                  <h3>{{ rankList.title }}</h3>
                  <ul>
                    <li v-for="(book, i) in rankList.books.slice(0, 5)" :key="book.id">
                      <span class="rank-number">{{ i + 1 }}.</span>
                      <router-link :to="`/books/${book.id}`" class="ranking-book-link">{{ book.title }}</router-link>
                      <span class="rank-author-small"> - {{ book.author }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="activity-section-wrapper" id="activities">
              <div class="section-header-compact">
                <h2 class="section-title-small">Forthcoming Convocations & Salons</h2>
                <router-link to="/activities" class="more-link-small">Discover More Gatherings &gt;</router-link>
              </div>
              <div class="activity-list-compact">
                <div v-for="activity in activities.slice(0, 3)" :key="activity.id" class="activity-item-compact">
                  <img :src="activity.image" :alt="activity.title" class="activity-image-small" />
                  <div class="activity-info-compact">
                    <h4>{{ activity.title }}</h4>
                    <p>{{ activity.date }}</p>
                    <button class="join-button-small">Graciously Attend</button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>

    <div>
      <transition name="pop-in">
        <div v-if="showTooltip" class="daily-book-tooltip" @click="hideTooltip">
          <p>✨ 发现今日好书！点击这里</p>
          <span class="tooltip-arrow"></span>
        </div>
      </transition>

      <button :class="['sidebar-toggle-button', { 'is-open': isSidebarOpen }]" @click="toggleSidebar">
        <span v-if="!isSidebarOpen">每日一书</span>
        <span v-else>&#x2715;</span>
      </button>

      <div class="sidebar-overlay" :class="{ 'is-visible': isSidebarOpen }" @click="toggleSidebar"></div>

      <aside :class="['daily-book-sidebar', { 'is-open': isSidebarOpen }]">
        <div class="daily-book-card">
          <h2 class="sidebar-title">The Day's Chosen Volume</h2>
          <BookOfTheDay v-if="isSidebarOpen" :initial-book="dailyBook" />
          <p v-else-if="!isSidebarOpen" class="no-daily-book">
            No book recommendation for today. Check back later!
          </p>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios'; // 引入axios
import BookOfTheDay from '../views/BookOfTheDay.vue'; // 导入 BookOfTheDay 组件

const router = useRouter();
const loading = ref(true);
const isSidebarOpen = ref(false);
const showTooltip = ref(false); // 新增：控制气泡显示状态

const popularBooks = ref([]);
const personalizedBooks = ref([]);
const bookRankings = ref([]); // 修改为响应式对象，等待从后端获取榜单数据
const activities = ref([
  // 活动数据暂时保持模拟，因为后端没有提供活动接口
  { id: 'a1', title: '夏日读书挑战赛：奇幻文学专题', date: '2025.07.01 - 2025.08.31', image: 'https://th.bing.com/th/id/OIP.WMA1iLv8OEsKbQNzopefQQHaGq?w=209&h=189&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3' },
  { id: 'a2', title: '线上读书分享会：哲学思辨之夜', date: '2025.07.15 19:00', image: 'https://th.bing.com/th/id/OIP.WMA1iLv8OEsKbQNzopefQQHaGq?w=209&h=189&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3' },
  { id: 'a3', title: '线下作家见面会：历史长河探秘', date: '2025.07.20 14:00', image: 'https://th.bing.com/th/id/OIP.CyDI-M6iaUlGY7yOyQeM8wHaGq?w=209&h=189&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3' },
  { id: 'a4', title: '编程技术沙龙：Vue3新特性', date: '2025.07.25 10:00', image: 'https://th.bing.com/th/id/OIP.21XL-cVbf89_FE_pAvvX4gHaGq?w=209&h=189&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3' },
]);

const dailyBook = ref(null);

// 提取API基路径
const API_BASE_URL = '/service-b/api'; // 根据您的后端服务地址调整，如果前端和后端不是在同一个域和端口，需要完整的URL，例如 'http://localhost:5000/api'

const fetchData = async () => {
  loading.value = true;
  try {
    // 获取热门书籍
    const popularRes = await axios.get(`${API_BASE_URL}/books/popular?limit=4`);
    popularBooks.value = popularRes.data.map(book => ({
      id: book.id || book.bookId, // 确保ID可用
      title: book.title,
      author: book.author,
      genres: book.genres, // genres 已经是数组
      coverImg: book.coverImg // 确保字段名正确
    }));

    // 获取个性化推荐书籍
    const personalizedRes = await axios.get(`${API_BASE_URL}/books/personalized?limit=4`);
    personalizedBooks.value = personalizedRes.data.map(book => ({
      id: book.id || book.bookId,
      title: book.title,
      author: book.author,
      genres: book.genres,
      coverImg: book.coverImg
    }));

    // 获取榜单数据
    const bestsellingRes = await axios.get(`${API_BASE_URL}/books/rankings/bestselling?limit=7`);
    const newReleasesRes = await axios.get(`${API_BASE_URL}/books/rankings/new_releases?limit=7`);

    bookRankings.value = [
      {
        title: '高分榜',
        books: bestsellingRes.data.map(book => ({
          id: book.id || book.bookId,
          title: book.title,
          author: book.author,
        }))
      },
      {
        title: '新书榜',
        books: newReleasesRes.data.map(book => ({
          id: book.id || book.bookId,
          title: book.title,
          author: book.author,
        }))
      }
    ];

    // 获取每日一书
    const dailyBookRes = await axios.get(`${API_BASE_URL}/books/daily`);
    if (dailyBookRes.data) {
      dailyBook.value = {
        id: dailyBookRes.data.id || dailyBookRes.data.bookId,
        title: dailyBookRes.data.title,
        author: dailyBookRes.data.author,
        genres: dailyBookRes.data.genres,
        coverImg: dailyBookRes.data.coverImg
      };
    }

  } catch (error) {
    console.error('Error fetching data:', error);
    // 可以在这里设置一个错误状态或显示错误消息给用户
  } finally {
    loading.value = false;
  }
};

let tooltipTimer = null; // 新增：用于清除气泡定时器

onMounted(() => {
  fetchData();
  // 在组件挂载后 3 秒显示气泡
  tooltipTimer = setTimeout(() => {
    // 只有当侧边栏未打开时才显示气泡
    if (!isSidebarOpen.value) {
      showTooltip.value = true;
    }
  }, 3000); // 3 秒后显示
});

onUnmounted(() => {
  // 在组件卸载时清除定时器，避免内存泄漏
  if (tooltipTimer) {
    clearTimeout(tooltipTimer);
  }
});

const viewBookDetails = (bookId) => {
  router.push(`/books/${bookId}`);
  isSidebarOpen.value = false;
  hideTooltip(); // 点击后隐藏气泡
};

const scrollToSection = (id) => {
  const element = document.getElementById(id);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' });
  }
};

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
  hideTooltip(); // 点击按钮后隐藏气泡
};

// 新增：隐藏气泡的函数
const hideTooltip = () => {
  showTooltip.value = false;
  // 一旦隐藏，可选地设置一个标记，确保不再自动显示（例如，存入 localStorage）
  // localStorage.setItem('hasSeenDailyBookTooltip', 'true');
};
</script>

<style scoped>
/* Global Styles and Typography */
.home-view {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
  font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
  color: #3e2723;
  background-color: #fcf8f0;
  /* Ensure the body has no horizontal overflow due to sidebar */
  overflow-x: hidden;
}

/* Hero Section Styles */
.hero-section {
  background: linear-gradient(135deg, #d4b896 0%, #ecd9c7 100%);
  color: #5d4037;
  text-align: center;
  padding: 100px 30px;
  border-bottom-left-radius: 60px;
  border-bottom-right-radius: 60px;
  margin-bottom: 50px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM2MDU0NDgiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0bC02LTMuMjctNiA2LjI3di0xMmMwLS41NS40NS0xIDEtMSAxIDAgLjgyLjM3IDEuMTguODhsMi43NiAyLjc2LTMuNjQtMy42NGEuOTk5Ljk5OSAwIDAg0C0xLjQxIDAgMSAxIDAgMCAwIDAgMS40MWwxNC4xMyAxNC4xM2ExLjAxIDEuMDEgMCAwIDAgMS40MiAwIDEgMSAwIDAgMCAwLTEuNDFMMzYgMzR6TTI4IDExbDE3LTE3YzEuMTgtMS4xOCAzLjI3LTEuMTggNC40NSAwIDEuMTguNDUuNzUgMS44MSAwIDIuNTlsLTYuMTIgNi4xMmEyNS40IDI1LjQgMCAwIDAgLjY3IDcuNjNsLTIuNjYtMi42NmMtLjE4LS4xOC0uNDItLjI4LS42Ny0uMjhINzguNWEyMCAyMCAwIDAg0S0yMCAyMHYyMGMwIDEuMTguODIgMiAxLjggMiAwIDAgLjgyLjM3IDEuMTguODhsMi43NiAyLjc2LTMuNjQtMy42NGEuOTk5Ljk5OSAwIDAg0C0xLjQxIDAgMSAxIDAgMCAwIDAgMS40MWwxNC4xMyAxNC4xM2ExLjAxIDEuMDEgMCAwIDAgMS40MiAwIDExIDExIDAgMCAwIDAgLTEuNDFMMzYgMzR6Ii8+PC9nPjwvZz48L3N2Z3U+');
  opacity: 0.1;
  background-repeat: repeat;
}

.hero-content {
  max-width: 900px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 3.8em;
  margin-bottom: 20px;
  font-weight: 700;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.1);
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.6em;
  opacity: 0.85;
  margin-bottom: 40px;
  font-style: italic;
}

.explore-button {
  background-color: #8d6e63;
  color: white;
  border: 2px solid #5d4037;
  border-radius: 5px;
  padding: 18px 45px;
  font-size: 1.3em;
  cursor: pointer;
  transition: all 0.4s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  letter-spacing: 1px;
}

.explore-button:hover {
  background-color: #5d4037;
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

/* Loading Animation */
.loading-message {
  text-align: center;
  font-size: 1.4em;
  color: #795548;
  margin-top: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  font-style: italic;
}

.spinner {
  border: 4px solid rgba(121, 85, 72, 0.2);
  border-top: 4px solid #8d6e63;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1.2s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* Main Content and Section Containers */
/* Removed .content-with-sidebar as it's no longer needed for flex layout with fixed sidebar */
.main-content {
  padding: 0 60px;
}

.content-wrapper {
  /* This div now wraps all your main sections */
  padding-bottom: 50px;
  /* Add some space at the bottom */
}

.section-container {
  margin-bottom: 80px;
  background-color: #fffaf0;
  border-radius: 10px;
  padding: 40px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #e0e0e0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  border-bottom: 1px dashed #c0b2a3;
  padding-bottom: 20px;
}

.section-title {
  font-size: 2.8em;
  color: #4e342e;
  font-weight: 600;
  position: relative;
  padding-left: 20px;
  letter-spacing: 0.5px;
}

.section-title::before {
  content: '§';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8em;
  color: #a1887f;
}

.more-link {
  color: #8d6e63;
  text-decoration: none;
  font-size: 1.2em;
  font-weight: 500;
  transition: color 0.3s ease, text-decoration 0.3s ease;
}

.more-link:hover {
  color: #5d4037;
  text-decoration: underline;
}

/* Book Card Grid Layout */
.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 30px;
  justify-content: center;
}

.book-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  min-height: 420px;
  text-align: center;
  border: 1px solid #efebe9;
}

.book-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.12);
}

.book-cover {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
  border-bottom: 1px solid #f5f5f5;
}

.book-info {
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.book-title {
  font-size: 1.45em;
  color: #4e342e;
  margin-top: 10px;
  margin-bottom: 10px;
  font-weight: 600;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.book-author,
.book-genre {
  font-size: 1em;
  color: #795548;
  margin-bottom: 8px;
  font-style: italic;
}

.details-button {
  background-color: #a1887f;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 12px 20px;
  font-size: 1.05em;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  margin-top: 20px;
  letter-spacing: 0.5px;
}

.details-button:hover {
  background-color: #8d6e63;
  transform: translateY(-3px);
}

/* Section Divider */
.section-divider {
  border: 0;
  height: 2px;
  background-image: linear-gradient(to right, rgba(161, 136, 127, 0), rgba(161, 136, 127, 0.4), rgba(161, 136, 127, 0));
  margin: 70px 0;
}

/* New Combined Section for Rankings and Activities */
.section-two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: start;
}

/* Compact Headers for sub-sections */
.section-header-compact {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #d4c7b2;
}

.section-title-small {
  font-size: 2em;
  color: #4e342e;
  font-weight: 600;
  position: relative;
  padding-left: 20px;
  letter-spacing: 0.5px;
  margin-top: 0;
  margin-bottom: 0;
}

.section-title-small::before {
  content: '§';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8em;
  color: #a1887f;
}


.more-link-small {
  color: #8d6e63;
  text-decoration: none;
  font-size: 1.05em;
  font-weight: 500;
  white-space: nowrap;
  transition: color 0.3s ease, text-decoration 0.3s ease;
}

.more-link-small:hover {
  color: #5d4037;
  text-decoration: underline;
}


/* Ranking Section Styles (Compact) */
.ranking-section-wrapper {
  background-color: #fffaf0;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  padding: 30px;
  border: 1px dashed #d7ccc8;
  /* 确保容器有明确的最大宽度，或内容不会撑破 */
  overflow: hidden;
  /* 防止内容溢出到容器外部 */
}

.ranking-grid-compact {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ranking-card-compact {
  padding: 0;
  transition: transform 0.2s ease;
}

.ranking-card-compact:hover {
  transform: translateX(5px);
}

.ranking-card-compact h3 {
  font-size: 1.5em;
  color: #6d4c41;
  margin-top: 0;
  margin-bottom: 15px;
  text-align: left;
  padding-bottom: 10px;
  border-bottom: 1px solid #e7e0da;
  letter-spacing: 0.5px;
  /* 添加文本溢出处理 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ranking-card-compact ul {
  list-style: none;
  padding: 0;
}

.ranking-card-compact li {
  display: flex;
  align-items: baseline;
  margin-bottom: 10px;
  font-size: 1em;
  color: #5d4037;
  min-width: 0;
  /* 移除这里的 gap，改为手动控制间距 */
}

.ranking-book-link {
  color: #4e342e;
  text-decoration: none;
  transition: color 0.2s ease;
  /* 关键：确保文本溢出时截断并显示省略号 */
  white-space: nowrap;
  /* 文本不换行 */
  overflow: hidden;
  /* 溢出部分隐藏 */
  text-overflow: ellipsis;
  /* 显示省略号 */
  min-width: 0;
  /* 允许flex项缩小 */
}

.ranking-book-link:hover {
  color: #8d6e63;
  text-decoration: underline;
}

.rank-number {
  font-weight: bold;
  color: #bcaaa4;
  /* 调整这里：使用 min-width 和 max-content 来确保足够的空间，并用 padding 调整间距 */
  min-width: 30px;
  /* 确保足以容纳 "10." 并留出一些空隙 */
  text-align: right;
  padding-right: 8px;
  /* 在数字和书名之间添加右侧内边距 */
  flex-shrink: 0;
}

.rank-author-small {
  font-size: 0.85em;
  color: #a1887f;
  margin-left: 10px;
  font-style: italic;
  /* 关键：确保文本溢出时截断并显示省略号 */
  white-space: nowrap;
  /* 文本不换行 */
  overflow: hidden;
  /* 溢出部分隐藏 */
  text-overflow: ellipsis;
  /* 显示省略号 */
  flex-shrink: 1;
  /* 允许缩小，但会优先 book-link */
  min-width: 0;
  /* 允许flex项缩小 */
}


/* Activities Section Styles (Compact) */
.activity-section-wrapper {
  background-color: #fffaf0;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  padding: 30px;
  border: 1px dashed #d7ccc8;
}

.activity-list-compact {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.activity-item-compact {
  display: flex;
  align-items: center;
  gap: 15px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  padding: 15px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.activity-item-compact:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 12px rgba(0, 0, 0, 0.08);
}

.activity-image-small {
  width: 90px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}

.activity-info-compact {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  /* 确保 flex item 内部内容不会溢出 */
}

.activity-info-compact h4 {
  font-size: 1.2em;
  color: #4e342e;
  margin-top: 0;
  margin-bottom: 5px;
  line-height: 1.3;
  white-space: nowrap;
  /* 不换行 */
  overflow: hidden;
  /* 隐藏溢出 */
  text-overflow: ellipsis;
  /* 显示省略号 */
}

.activity-info-compact p {
  font-size: 0.9em;
  color: #795548;
  margin-bottom: 10px;
  font-style: italic;
  white-space: nowrap;
  /* 不换行 */
  overflow: hidden;
  /* 隐藏溢出 */
  text-overflow: ellipsis;
  /* 显示省略号 */
}

.join-button-small {
  background-color: #a1887f;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 15px;
  font-size: 0.9em;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  align-self: flex-start;
  letter-spacing: 0.5px;
}

.join-button-small:hover {
  background-color: #8d6e63;
  transform: translateY(-2px);
}

/* Responsive Design */
@media (max-width: 992px) {
  .section-two-columns {
    grid-template-columns: 1fr;
    gap: 60px;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 3em;
  }

  .hero-subtitle {
    font-size: 1.4em;
  }

  .main-content {
    padding: 0 30px;
  }

  .section-container {
    padding: 30px;
  }

  .section-title {
    font-size: 2.2em;
  }

  .book-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }

  .book-card {
    min-height: 380px;
  }

  .book-cover {
    height: 180px;
  }

  .section-title-small {
    font-size: 1.8em;
  }

  .ranking-card-compact h3 {
    font-size: 1.4em;
  }

  .ranking-card-compact li {
    font-size: 0.95em;
  }

  .rank-author-small {
    margin-left: 8px;
  }

  .activity-item-compact {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .activity-image-small {
    width: 100%;
    height: 120px;
    margin-bottom: 10px;
  }

  .join-button-small {
    align-self: center;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 70px 20px;
  }

  .hero-title {
    font-size: 2.5em;
  }

  .hero-subtitle {
    font-size: 1.2em;
  }

  .explore-button {
    padding: 15px 30px;
    font-size: 1.1em;
  }

  .main-content {
    padding: 0 20px;
  }

  .section-container {
    padding: 20px;
  }

  .section-title {
    font-size: 1.8em;
  }

  .book-grid {
    grid-template-columns: 1fr;
  }

  .book-card {
    min-height: auto;
  }

  .book-cover {
    height: 180px;
  }

  .section-title-small {
    font-size: 1.5em;
  }

  .ranking-card-compact h3 {
    font-size: 1.2em;
    white-space: normal;
    /* 在小屏幕下允许换行 */
    overflow: visible;
    text-overflow: unset;
  }

  .ranking-card-compact li {
    flex-wrap: wrap;
    justify-content: center;
    text-align: center;
    /* 在小屏幕下，如果需要，可以取消 min-width: 0; */
  }

  .rank-number {
    width: auto;
    margin-right: 5px;
  }

  .ranking-book-link,
  .rank-author-small {
    white-space: normal;
    /* 允许换行 */
    text-overflow: unset;
    /* 取消省略号 */
    overflow: visible;
    /* 允许内容可见 */
    /* 在小屏幕下，如果需要，可以取消 min-width: 0; */
  }
}

/* --- Collapsible Sidebar Specific Styles --- */

/* Sidebar itself */
.daily-book-sidebar {
  position: fixed;
  /* Fixed to the viewport */
  top: 0;
  /* right: 0; */
  /* 移除或改为 left: 0 */
  left: 0;
  /* 新增：从左侧开始 */
  width: 100%;
  /* 将宽度改为 100% */
  height: 100%;
  /* Full height of the viewport */
  background-color: #fffaf0;
  /* Match your parchment theme */
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
  /* Shadow indicating it slides in */
  /* transform: translateX(100%); */
  /* 移除或改为 translateX(-100%) */
  transform: translateX(-100%);
  /* 新增：从左侧完全移出屏幕 */
  transition: transform 0.4s ease-in-out;
  /* Smooth slide animation */
  z-index: 1000;
  /* Ensure it's above other content */
  padding: 20px;
  overflow-y: auto;
  /* Allow scrolling if content is too long */
}

.daily-book-sidebar.is-open {
  transform: translateX(0);
  /* Slide into view */
}

/* --- 引导性气泡样式 --- */
.daily-book-tooltip {
  position: fixed;
  right: 50px;
  /* 调整位置，让它在按钮旁边 */
  top: calc(50% - 60px);
  /* 向上一些，避免遮挡按钮文字 */
  transform: translateY(-50%) rotate(0deg);
  /* 气泡不旋转 */
  z-index: 1002;
  /* 确保在按钮之上 */
  background-color: #fff8e1;
  /* 浅羊皮纸色 */
  color: #4e342e;
  /* 深棕色文字 */
  padding: 12px 18px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  font-size: 0.95em;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  /* 提示用户可以点击关闭 */
  border: 1px solid #dcd3c5;
  /* 细边框 */
  animation: bounce-scale 1s infinite alternate ease-in-out;
  /* 添加跳动和缩放动画 */
}

/* 气泡小箭头 */
.tooltip-arrow {
  position: absolute;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid #fff8e1;
  /* 箭头颜色与气泡背景一致 */
  bottom: -10px;
  /* 定位在气泡下方 */
  right: 20px;
  /* 与按钮对齐 */
  filter: drop-shadow(0 2px 1px rgba(0, 0, 0, 0.1));
  /* 给箭头添加柔和阴影 */
}

/* 气泡的 Vue Transition 动画 */
.pop-in-enter-active,
.pop-in-leave-active {
  transition: all 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55);
  /* 弹跳效果 */
}

.pop-in-enter-from,
.pop-in-leave-to {
  opacity: 0;
  transform: translateY(-50%) rotate(0deg) scale(0.5);
}

/* Sidebar Toggle Button - Revised Style (添加动画) */
.sidebar-toggle-button {
  position: fixed;
  right: 1%;
  /* 紧贴右侧边缘，或留一点间隙 */
  top: 50%;
  transform: translateY(-50%) rotate(-90deg);
  /* 保持旋转，使其垂直 */
  transform-origin: 100% 50%;
  /* 旋转中心改为右边缘 */
  z-index: 1001;

  background-color: #dcd3c5;
  /* 柔和的米灰色，接近羊皮纸 */
  color: #5d4037;
  /* 深棕色文字 */
  border: 1px solid rgba(0, 0, 0, 0.1);
  /* 细微的边框线 */
  border-right: none;
  /* 右侧无边框，与侧边栏融合 */
  padding: 12px 20px 12px 25px;
  /* 调整内边距，左侧多一点给弧度 */
  border-radius: 8px 0 0 8px;
  /* 左侧圆角，右侧直角，像书签 */
  cursor: pointer;
  font-size: 1.05em;
  /* 稍微大一点的字体 */
  font-weight: 500;
  letter-spacing: 0.5px;
  /* 增加字母间距，提升精致感 */
  box-shadow: -2px 2px 8px rgba(0, 0, 0, 0.1);
  /* 柔和的阴影 */
  transition: all 0.3s ease-in-out;
  /* 更平滑的过渡效果 */
  white-space: nowrap;

  /* === 新增：应用动画 === */
  animation: pulse 2s infinite ease-in-out;
  /* 动画名称、持续时间、无限循环、缓动函数 */
}

.sidebar-toggle-button:hover {
  background-color: #c0b2a3;
  /* 悬停时颜色略深 */
  box-shadow: -4px 4px 12px rgba(0, 0, 0, 0.15);
  /* 阴影更明显 */
  transform: translateY(-50%) rotate(-90deg) translateX(-5px);
  /* 悬停时向左轻微偏移 */
  animation: none;
  /* 悬停时停止动画 */
}

/* 按钮打开时的样式 */
.sidebar-toggle-button.is-open {
  transform: translateY(-50%) rotate(0deg);
  /* 恢复正常角度 */
  right: 20px;
  /* 调整到侧边栏内部，或保持在原位但隐藏 */
  background-color: #8d6e63;
  /* 打开时深色，对比更明显 */
  color: #fff;
  border-radius: 5px;
  /* 打开时恢复正常按钮形状 */
  border: none;
  /* 移除边框 */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  animation: none;
  /* 打开时也停止动画 */
}

/* Overlay that appears when sidebar is open */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  /* Semi-transparent black */
  z-index: 999;
  /* Below sidebar, above content */
  opacity: 0;
  /* Start invisible */
  visibility: hidden;
  /* Hide from screen readers when not visible */
  transition: opacity 0.4s ease-in-out, visibility 0s linear 0.4s;
  /* Fade and hide after transition */
}

.sidebar-overlay.is-visible {
  opacity: 1;
  /* Fade in */
  visibility: visible;
  /* Make visible */
  transition-delay: 0s;
  /* No delay when appearing */
}

/* Adjust main content when sidebar is open (optional, but good UX) */
.home-view.sidebar-open .main-content {
  /* You might want to push the main content slightly, or dim it */
  filter: blur(2px);
  /* Example: blur the background */
  pointer-events: none;
  /* Disable interaction with main content */
}

/* Style for the daily book card inside the sidebar */
.daily-book-card {
  text-align: center;
  padding: 20px;
  /* Add some padding inside the card */
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.sidebar-title {
  font-size: 1.8em;
  /* Slightly larger for prominence */
  color: #4e342e;
  margin-bottom: 1.5rem;
  border-bottom: 2px dashed #c0b2a3;
  padding-bottom: 10px;
}

.book-of-the-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
}

.daily-book-cover {
  max-width: 180px;
  /* A bit larger cover */
  height: auto;
  border-radius: 4px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.daily-book-title {
  font-size: 1.5em;
  /* More prominent title */
  color: #4e342e;
  margin-top: 1rem;
  font-weight: 600;
}

.daily-book-author,
.daily-book-genre {
  font-size: 1em;
  color: #795548;
  font-style: italic;
}

.no-daily-book {
  color: #777;
  font-style: italic;
  padding: 20px;
}

/* Ensure body doesn't scroll when sidebar is open */
body.no-scroll {
  overflow: hidden;
}

/* 针对全屏侧边栏的按钮定位微调 */
@media (min-width: 769px) {

  /* 在大屏幕上，侧边栏全屏时 */
  .sidebar-toggle-button.is-open {
    top: 20px;
    /* 移动到右上角 */
    right: 20px;
    transform: none;
    /* 取消所有 transform */
    padding: 10px 15px;
    /* 调整内边距 */
  }
}

/* Responsive adjustments for the sidebar toggle button */
@media (max-width: 768px) {
  .sidebar-toggle-button {
    top: 20px;
    /* 保持在顶部 */
    right: 20px;
    transform: rotate(0deg);
    /* 小屏幕不旋转 */
    transform-origin: center;
    /* 旋转中心重置 */
    border-radius: 5px;
    /* 小屏幕也正常圆角 */
    border-right: 1px solid rgba(0, 0, 0, 0.1);
    /* 小屏幕边框正常 */
  }

  .sidebar-toggle-button.is-open {
    right: 20px;
    transform: rotate(0deg);
  }

  .daily-book-sidebar {
    width: 80%;
    /* Wider sidebar on small screens */
    max-width: 350px;
    /* Cap max width */
    padding: 15px;
  }
}

/* 定义呼吸动画 */
@keyframes pulse {
  0% {
    transform: translateY(-50%) rotate(-90deg) scale(1);
    box-shadow: -2px 2px 8px rgba(0, 0, 0, 0.1);
  }

  50% {
    transform: translateY(-50%) rotate(-90deg) scale(1.03);
    /* 轻微放大 */
    box-shadow: -4px 4px 12px rgba(0, 0, 0, 0.2);
    /* 阴影更明显 */
  }

  100% {
    transform: translateY(-50%) rotate(-90deg) scale(1);
    box-shadow: -2px 2px 8px rgba(0, 0, 0, 0.1);
  }
}
</style>