<template>
  <div class="home-view">
    <header class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">The Grand Tapestry of Knowledge: Charting Paths to Enlightenment</h1>
        <p class="hero-subtitle">A Conclave for Artisans, a Repository for Luminary Works. Discover, Delve, and Disentangle.</p>
        <button class="explore-button" @click="scrollToSection('popular-books')">Embark on the Quest</button>
      </div>
    </header>

    <main class="main-content">
      <p v-if="loading" class="loading-message">
        <div class="spinner"></div> The Quills are Busy, Kindly Stand By...
      </p>

      <div v-else>
        <section class="section-container" id="popular-books">
          <div class="section-header">
            <h2 class="section-title">Volumes of Esteem: Acclaimed by the Cognoscenti</h2>
            <a href="#" class="more-link">Peruse the Archives &gt;</a>
          </div>
          <div class="book-grid">
            <div v-for="book in popularBooks" :key="book.id" class="book-card">
              <img :src="book.coverImage" :alt="book.title" class="book-cover" />
              <div class="book-info">
                <h3 class="book-title">{{ book.title }}</h3>
                <p class="book-author">Authored by: {{ book.author }}</p>
                <p class="book-genre">Genre: {{ book.genre }}</p>
                <button @click="viewBookDetails(book.id)" class="details-button">Unfold the Narrative</button>
              </div>
            </div>
          </div>
        </section>

        <hr class="section-divider" />

        <section class="section-container" id="personalized-books">
          <div class="section-header">
            <h2 class="section-title">Curated for Your Discerning Eye</h2>
            <a href="#" class="more-link">More Selections Befitting Your Taste &gt;</a>
          </div>
          <div class="book-grid">
            <div v-for="book in personalizedBooks" :key="book.id" class="book-card">
              <img :src="book.coverImage" :alt="book.title" class="book-cover" />
              <div class="book-info">
                <h3 class="book-title">{{ book.title }}</h3>
                <p class="book-author">Authored by: {{ book.author }}</p>
                <p class="book-genre">Genre: {{ book.genre }}</p>
                <button @click="viewBookDetails(book.id)" class="details-button">Unfold the Narrative</button>
              </div>
            </div>
          </div>
        </section>

        <hr class="section-divider" />

        <section class="section-container" id="rankings">
          <div class="section-header">
            <h2 class="section-title">The Pantheon of Literary Distinction</h2>
            <a href="#" class="more-link">Behold the Full Register &gt;</a>
          </div>
          <div class="ranking-grid">
            <div v-for="(rankList, index) in bookRankings" :key="index" class="ranking-card">
              <h3>{{ rankList.title }}</h3>
              <ul>
                <li v-for="(book, i) in rankList.books" :key="book.id">
                  <span class="rank-number">{{ i + 1 }}.</span>
                  <a :href="`/books/${book.id}`">{{ book.title }}</a>
                  <span class="rank-author"> - {{ book.author }}</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        <hr class="section-divider" />

        <section class="section-container" id="activities">
          <div class="section-header">
            <h2 class="section-title">Forthcoming Convocations & Salons</h2>
            <a href="#" class="more-link">Discover More Gatherings &gt;</a>
          </div>
          <div class="activity-grid">
            <div v-for="activity in activities" :key="activity.id" class="activity-card">
              <img :src="activity.image" :alt="activity.title" class="activity-image" />
              <div class="activity-info">
                <h4>{{ activity.title }}</h4>
                <p>{{ activity.date }}</p>
                <button class="join-button">Graciously Attend</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(true); // 控制加载状态

// 模拟数据
const mockBooks = [
  { id: '1', title: 'Vue.js 3 实践指南', author: '前端老张', genre: '编程技术', coverImage: 'https://via.placeholder.com/150x200?text=Vue3Book' },
  { id: '2', title: '微服务架构设计', author: '架构师李工', genre: '系统设计', coverImage: 'https://via.placeholder.com/150x200?text=Microservices' },
  { id: '3', title: 'Python Flask 实战', author: 'Python 小白', genre: '后端开发', coverImage: 'https://via.placeholder.com/150x200?text=FlaskBook' },
  { id: '4', title: '算法导论', author: 'Thomas H. Cormen', genre: '计算机科学', coverImage: 'https://via.placeholder.com/150x200?text=Algorithms' },
  { id: '5', title: '三体', author: '刘慈欣', genre: '科幻小说', coverImage: 'https://via.placeholder.com/150x200?text=ThreeBody' },
  { id: '6', title: '设计模式', author: 'Erich Gamma', genre: '编程技术', coverImage: 'https://via.placeholder.com/150x200?text=DesignPatterns' },
  { id: '7', title: '人类简史', author: '尤瓦尔·赫拉利', genre: '历史', coverImage: 'https://via.placeholder.com/150x200?text=Sapiens' },
  { id: '8', title: '非暴力沟通', author: '马歇尔·卢森堡', genre: '心理学', coverImage: 'https://via.placeholder.com/150x200?text=NVC' },
];

const popularBooks = ref([]);
const personalizedBooks = ref([]);
const bookRankings = ref([
  { title: '畅销榜', books: [mockBooks[4], mockBooks[0], mockBooks[6]] },
  { title: '新书榜', books: [mockBooks[7], mockBooks[5], mockBooks[1]] },
]);
const activities = ref([
  { id: 'a1', title: '夏日读书挑战赛', date: '2025.07.01 - 2025.08.31', image: 'https://via.placeholder.com/300x150?text=ReadingChallenge' },
  { id: 'a2', title: '线上读书分享会', date: '2025.07.15 19:00', image: 'https://via.placeholder.com/300x150?text=BookSharing' },
]);

// 模拟数据获取函数
const fetchData = async () => {
  await new Promise(resolve => setTimeout(resolve, 1500)); // 模拟网络延迟
  popularBooks.value = [mockBooks[0], mockBooks[4], mockBooks[2], mockBooks[6]]; // 示例热门
  personalizedBooks.value = [mockBooks[1], mockBooks[3], mockBooks[5], mockBooks[7]]; // 示例个性化
  loading.value = false;
};

onMounted(() => {
  fetchData();
});

const viewBookDetails = (bookId) => {
  router.push(`/books/${bookId}`);
};

const scrollToSection = (id) => {
  const element = document.getElementById(id);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' });
  }
};
</script>

<style scoped>
/* Global Styles and Typography */
.home-view {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
  /* Choose a serif font for a classical feel */
  font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
  color: #3e2723; /* Deep brown, mimicking ink */
  background-color: #fcf8f0; /* Parchment white, simulating aged paper */
}

/* Hero Section Styles */
.hero-section {
  /* Soft gradient, reminiscent of an aged scroll or painting */
  background: linear-gradient(135deg, #d4b896 0%, #ecd9c7 100%);
  color: #5d4037; /* Deep brown text for contrast */
  text-align: center;
  padding: 100px 30px; /* Increased padding */
  border-bottom-left-radius: 60px; /* Softer rounded corners */
  border-bottom-right-radius: 60px;
  margin-bottom: 50px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15); /* Deeper, more pronounced shadow */
  position: relative;
  overflow: hidden; /* Ensure pseudo-elements don't overflow */
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* Abstract texture, reminiscent of ancient art or subtle paper grain */
  background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM2MDU0NDgiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0bC02LTMuMjctNiA2LjI3di0xMmMwLS41NS40NS0xIDEtMSAxIDAgLjgyLjM3IDEuMTguODhsMi43NiAyLjc2LTMuNjQtMy42NGEuOTk5Ljk5OSAwIDAgMC0xLjQxIDAgMSAxIDAgMCAwIDAgMS40MWwxNC4xMyAxNC4xM2ExLjAxIDEuMDEgMCAwIDAgMS40MiAwIDEgMSAwIDAgMCAwLTEuNDFMMzYgMzR6TTI4IDExbDE3LTE3YzEuMTgtMS4xOCAzLjI3LTEuMTggNC40NSAwIDEuMTguNDUuNzUgMS44MSAwIDIuNTlsLTYuMTIgNi4xMmEyNS40IDI1LjQgMCAwIDAgLjY3IDcuNjNsLTIuNjYtMi42NmMtLjE4LS4xOC0uNDItLjI4LS42Ny0uMjhINzguNWEyMCAyMCAwIDAg0S0yMCAyMHYyMGMwIDEuMTguODIgMiAxLjggMiAwIDAgLjgyLjM3IDEuMTguODhsMi43NiAyLjc2LTMuNjQtMy42NGEuOTk5Ljk5OSAwIDAgMC0xLjQxIDAgMSAxIDAgMCAwIDAgMS40MWwxNC4xMyAxNC4xM2ExLjAxIDEuMDEgMCAwIDAgMS40MiAwIDExIDExIDAgMCAwIDAgLTEuNDFMMzYgMzR6Ii8+PC9nPjwvZz48L3N2Z3U+');
  opacity: 0.1;
  background-repeat: repeat;
}

.hero-content {
  max-width: 900px;
  margin: 0 auto;
  position: relative; /* Ensure content is above texture */
  z-index: 1;
}

.hero-title {
  font-size: 3.8em; /* Grand and imposing */
  margin-bottom: 20px;
  font-weight: 700;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.1); /* Soft shadow */
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.6em;
  opacity: 0.85;
  margin-bottom: 40px;
  font-style: italic; /* Slight italic for elegance */
}

.explore-button {
  background-color: #8d6e63; /* Dignified brown */
  color: white;
  border: 2px solid #5d4037; /* Darker border */
  border-radius: 5px; /* Clean, subtle corners */
  padding: 18px 45px;
  font-size: 1.3em;
  cursor: pointer;
  transition: all 0.4s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  letter-spacing: 1px; /* Increased letter spacing */
}

.explore-button:hover {
  background-color: #5d4037; /* Even darker brown */
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

/* Loading Animation */
.loading-message {
  text-align: center;
  font-size: 1.4em;
  color: #795548; /* Soft brown */
  margin-top: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  font-style: italic;
}

.spinner {
  border: 4px solid rgba(121, 85, 72, 0.2); /* Light brown */
  border-top: 4px solid #8d6e63; /* Brown */
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1.2s linear infinite; /* Slightly slower rotation */
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Main Content and Section Containers */
.main-content {
  padding: 0 60px; /* Increased horizontal padding */
}

.section-container {
  margin-bottom: 80px;
  background-color: #fffaf0; /* Softer background, like fine paper */
  border-radius: 10px; /* Gentle rounding */
  padding: 40px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06); /* Lighter shadow */
  border: 1px solid #e0e0e0; /* Subtle border */
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  border-bottom: 1px dashed #c0b2a3; /* Dashed separator for elegance */
  padding-bottom: 20px;
}

.section-title {
  font-size: 2.8em; /* Larger title */
  color: #4e342e; /* Deep coffee brown */
  font-weight: 600;
  position: relative;
  padding-left: 20px; /* For the small ornament */
  letter-spacing: 0.5px;
}

.section-title::before {
  content: '§'; /* Section symbol, adds a classical touch */
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8em;
  color: #a1887f; /* Muted decorative color */
}

.more-link {
  color: #8d6e63; /* Soft brown */
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
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); /* Slightly larger cards */
  gap: 30px; /* Card spacing */
  justify-content: center;
}

.book-card {
  background-color: #ffffff;
  border-radius: 8px; /* Slightly smaller border-radius */
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05); /* Softer shadow */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  min-height: 420px; /* Uniform card height */
  text-align: center;
  border: 1px solid #efebe9; /* Subtle border */
}

.book-card:hover {
  transform: translateY(-8px); /* More pronounced lift effect */
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.12);
}

.book-cover {
  width: 100%;
  height: 200px; /* Fixed cover height */
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
  font-style: italic; /* Author and genre with slight italic */
}

.details-button {
  background-color: #a1887f; /* Muted brownish-grey */
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

/* Ranking Section Styles */
.ranking-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 35px;
}

.ranking-card {
  background-color: #fffaf0; /* Light background, echoing main background */
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  padding: 30px;
  transition: all 0.3s ease;
  border: 1px dashed #d7ccc8; /* Dashed border */
}

.ranking-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
}

.ranking-card h3 {
  font-size: 1.8em;
  color: #6d4c41; /* Soft deep brown */
  margin-top: 0;
  margin-bottom: 25px;
  text-align: center;
  padding-bottom: 15px;
  border-bottom: 1px solid #e7e0da;
  letter-spacing: 0.5px;
}

.ranking-card ul {
  list-style: none;
  padding: 0;
}

.ranking-card li {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 1.15em;
  color: #5d4037;
}

.rank-number {
  font-weight: bold;
  color: #bcaaa4; /* Muted grey */
  margin-right: 12px;
  font-size: 1.3em;
  width: 30px;
  text-align: right;
}

.ranking-card li a {
  color: #4e342e;
  text-decoration: none;
  flex-grow: 1;
  transition: color 0.2s ease;
}

.ranking-card li a:hover {
  color: #8d6e63;
  text-decoration: underline;
}

.rank-author {
  font-size: 0.95em;
  color: #a1887f;
  margin-left: 15px;
  font-style: italic;
}

/* Activities Section Styles */
.activity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 30px;
}

.activity-card {
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid #efebe9;
}

.activity-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.12);
}

.activity-image {
  width: 100%;
  height: 220px; /* Slightly taller images */
  object-fit: cover;
  display: block;
}

.activity-info {
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.activity-info h4 {
  font-size: 1.5em;
  color: #4e342e;
  margin-top: 0;
  margin-bottom: 10px;
  line-height: 1.3;
}

.activity-info p {
  font-size: 1em;
  color: #795548;
  margin-bottom: 20px;
  font-style: italic;
}

.join-button {
  background-color: #8d6e63; /* Dignified brown */
  color: white;
  border: none;
  border-radius: 5px;
  padding: 12px 20px;
  font-size: 1.05em;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  align-self: flex-start;
  margin-top: auto;
  letter-spacing: 0.5px;
}

.join-button:hover {
  background-color: #5d4037;
  transform: translateY(-3px);
}

/* Responsive Design */
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
  .section-title {
    font-size: 2.2em;
  }
  .book-grid, .ranking-grid, .activity-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
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
  .section-title {
    font-size: 1.8em;
  }
  .book-grid, .ranking-grid, .activity-grid {
    grid-template-columns: 1fr; /* Single column layout */
  }
  .book-card, .ranking-card, .activity-card {
    min-height: auto;
  }
  .book-cover, .activity-image {
    height: 180px;
  }
}
</style>