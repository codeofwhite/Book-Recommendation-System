<template>
  <div class="activities-page">
    <div class="header-section">
      <h1 class="page-title">墨香雅集</h1>
      <p class="section-description">
        从指尖的云端分享到线下的墨香重逢，在这里，每一次相遇都是一场文学的奇遇。
      </p>
    </div>

    <div class="filter-sort-section">
      <div class="search-bar">
        <span class="icon">🔍</span>
        <input type="text" placeholder="搜寻感兴趣的雅集..." />
      </div>
      <div class="tab-filters">
        <button class="tab-btn active">全部雅集</button>
        <button class="tab-btn">读书挑战</button>
        <button class="tab-btn">线上分享</button>
        <button class="tab-btn">线下见面</button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="custom-spinner"></div>
      <p>正在翻阅雅集名录...</p>
    </div>

    <div v-else class="activities-content">
      <div v-if="filteredActivities.length === 0" class="no-activities-message">
        <div class="empty-icon">🏮</div>
        <p>暂无相关雅集，换个搜索词试试吧</p>
      </div>

      <div class="activities-grid">
        <div v-for="activity in filteredActivities" 
             :key="activity.id" 
             class="activity-card"
             @click="viewActivityDetails(activity.id)">
          
          <div class="activity-image-wrapper">
            <img :src="activity.image" :alt="activity.title" class="activity-image" />
            <div class="activity-badge" :class="activity.type">
              {{ getActivityTypeLabel(activity.type) }}
            </div>
          </div>

          <div class="activity-info">
            <div class="meta-row">
              <span class="date-icon">📅</span>
              <span class="activity-date">{{ activity.date }}</span>
            </div>
            <h3 class="activity-title">{{ activity.title }}</h3>
            <p class="activity-description-short">{{ activity.description }}</p>
            
            <div class="card-footer">
              <button class="details-button">
                <span>参会详情</span>
                <i class="arrow-right">→</i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);
const activities = ref([]);
const filteredActivities = ref([]);

// 类型标签转换
const getActivityTypeLabel = (type) => {
  const labels = {
    'challenge': '读书挑战',
    'online': '线上分享',
    'offline': '线下见面'
  };
  return labels[type] || '专题活动';
};

const mockActivities = [
  {
    id: 'a1',
    title: '夏日读书挑战赛：奇幻文学专题',
    date: '2025.07.01 - 2025.08.31',
    image: 'https://images.unsplash.com/photo-1514539079130-25950c84af65?auto=format&fit=crop&q=80&w=800',
    description: '深入奇幻文学的瑰丽世界，挑战阅读极限，赢取丰厚奖励，与书友共度精彩夏日。',
    type: 'challenge'
  },
  {
    id: 'a2',
    title: '线上读书分享会：哲学思辨之夜',
    date: '2025.07.15 19:00 (CST)',
    image: 'https://images.unsplash.com/photo-1521714161819-15534968fc5f?auto=format&fit=crop&q=80&w=800',
    description: '邀请知名哲学家，共同探讨人生、宇宙与存在的意义，线上互动交流。',
    type: 'online'
  },
  {
    id: 'a3',
    title: '线下作家见面会：历史长河探秘',
    date: '2025.07.20 14:00 (CST)',
    image: 'https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&q=80&w=800',
    description: '与畅销历史作家面对面，分享创作故事和历史发现的乐趣，现场签售。',
    type: 'offline'
  },
  {
    id: 'a4',
    title: '青年创作者工作坊：故事构建技巧',
    date: '2025.08.05 19:30 (CST)',
    image: 'https://images.unsplash.com/photo-1455849318743-b2233052fcff?auto=format&fit=crop&q=80&w=800',
    description: '针对青年作家，提升故事构思、人物塑造和情节发展能力。',
    type: 'online'
  },
];

onMounted(() => {
  loading.value = true;
  setTimeout(() => {
    activities.value = mockActivities;
    filteredActivities.value = mockActivities;
    loading.value = false;
  }, 600);
});

const viewActivityDetails = (id) => {
  router.push(`/activities/${id}`);
};
</script>

<style scoped>
/* 延续“书遇”配色体系 */
.activities-page {
  --primary-accent: #8B6B4D;
  --secondary-bg: #F9F5F0;
  --text-rich: #3A2E26;
  --text-muted: #8E7E74;
  --shadow-soft: 0 10px 30px rgba(58, 46, 38, 0.08);

  max-width: 1200px;
  margin: 3rem auto;
  padding: 0 20px;
}

/* 头部样式 */
.header-section {
  text-align: center;
  margin-bottom: 4rem;
}

.page-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 2.8rem;
  color: var(--text-rich);
  margin-bottom: 1rem;
}

.section-description {
  color: var(--text-muted);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.8;
  font-size: 1.1rem;
}

/* 筛选区域优化 */
.filter-sort-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.search-bar {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.search-bar input {
  width: 100%;
  padding: 12px 20px 12px 45px;
  border-radius: 30px;
  border: 1px solid rgba(139, 107, 77, 0.2);
  background: white;
  outline: none;
  transition: all 0.3s ease;
}

.search-bar input:focus {
  border-color: var(--primary-accent);
  box-shadow: 0 0 0 4px rgba(139, 107, 77, 0.1);
}

.search-bar .icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.5;
}

.tab-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.tab-btn {
  padding: 8px 20px;
  border-radius: 20px;
  border: none;
  background: white;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  border: 1px solid transparent;
}

.tab-btn:hover, .tab-btn.active {
  background: var(--primary-accent);
  color: white;
}

/* 网格与卡片 */
.activities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px;
}

.activity-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(139, 107, 77, 0.05);
  cursor: pointer;
}

.activity-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(58, 46, 38, 0.12);
}

.activity-image-wrapper {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.activity-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.activity-card:hover .activity-image {
  transform: scale(1.1);
}

.activity-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 5px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
  backdrop-filter: blur(4px);
}

.activity-badge.challenge { background: #E67E22; }
.activity-badge.online { background: #3498DB; }
.activity-badge.offline { background: #27AE60; }

.activity-info {
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.activity-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.25rem;
  color: var(--text-rich);
  line-height: 1.4;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.8em;
}

.activity-description-short {
  font-size: 0.95rem;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  margin-top: auto;
}

.details-button {
  width: 100%;
  padding: 12px;
  background: var(--secondary-bg);
  border: 1px solid rgba(139, 107, 77, 0.1);
  border-radius: 12px;
  color: var(--primary-accent);
  font-weight: 600;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.activity-card:hover .details-button {
  background: var(--primary-accent);
  color: white;
}

.arrow-right {
  transition: transform 0.3s ease;
}

.details-button:hover .arrow-right {
  transform: translateX(5px);
}

/* Loading Spinner 优化 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100px 0;
  color: var(--text-muted);
}

.custom-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid var(--secondary-bg);
  border-top-color: var(--primary-accent);
  border-radius: 50%;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 600px) {
  .activities-grid { grid-template-columns: 1fr; }
  .page-title { font-size: 2rem; }
}
</style>