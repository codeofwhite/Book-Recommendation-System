<template>
  <div class="activities-page">
    <h1 class="page-title">全部活动</h1>

    <div class="filter-sort-section">
      <p class="section-description">探索我们即将举行或已经结束的精彩活动。从线上读书分享会到线下作家见面会，总有适合你的知识盛宴。</p>
    </div>

    <p v-if="loading" class="loading-message">
    <div class="spinner"></div> 正在加载活动列表，请稍候...
    </p>

    <div v-else class="activities-grid">
      <div v-if="filteredActivities.length === 0" class="no-activities-message">
        <p>抱歉，目前没有找到符合条件的活动。</p>
      </div>
      <div v-for="activity in filteredActivities" :key="activity.id" class="activity-card"
        @click="viewActivityDetails(activity.id)">
        <img :src="activity.image" :alt="activity.title" class="activity-image" />
        <div class="activity-info">
          <h3 class="activity-title">{{ activity.title }}</h3>
          <p class="activity-date">{{ activity.date }}</p>
          <p class="activity-description-short">{{ activity.description }}</p>
          <button class="details-button">查看详情</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// import axios from 'axios'; // 未来用于从后端获取数据时启用

const router = useRouter();
const loading = ref(false); // 初始设置为 false，因为目前是静态数据
const activities = ref([]); // 存放所有活动数据
const filteredActivities = ref([]); // 存放经过筛选的活动数据

// const searchQuery = ref(''); // 搜索关键词 (未来拓展)
// const selectedType = ref(''); // 筛选类型 (未来拓展)

// 模拟的活动数据，未来应从后端 API 获取
const mockActivities = [
  {
    id: 'a1',
    title: '夏日读书挑战赛：奇幻文学专题',
    date: '2025.07.01 - 2025.08.31',
    image: 'https://th.bing.com/th/id/OIP.z8K89wSx6Od2ctAjgdEE5gHaEM?w=310&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3',
    description: '深入奇幻文学的瑰丽世界，挑战阅读极限，赢取丰厚奖励，与书友共度精彩夏日。',
    type: 'challenge',
    status: 'upcoming'
  },
  {
    id: 'a2',
    title: '线上读书分享会：哲学思辨之夜',
    date: '2025.07.15 19:00 (CST)',
    image: 'https://th.bing.com/th/id/OIP.ac8a6uFFGWNUWltXnKib4AHaQY?w=158&h=349&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3',
    description: '邀请知名哲学家，共同探讨人生、宇宙与存在的意义，线上互动交流。',
    type: 'online',
    status: 'upcoming'
  },
  {
    id: 'a3',
    title: '线下作家见面会：历史长河探秘',
    date: '2025.07.20 14:00 (CST)',
    image: 'https://th.bing.com/th/id/OIP.j2QL_B60LLgWU7x-xH6b6gHaHa?w=192&h=193&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3',
    description: '与畅销历史作家面对面，分享创作故事和历史发现的乐趣，现场签售。',
    type: 'offline',
    status: 'upcoming'
  },
  {
    id: 'a4',
    title: '青年创作者工作坊：故事构建技巧',
    date: '2025.08.05 19:30 (CST)',
    image: 'https://th.bing.com/th/id/OIP.w4PWaTPnW8Z79qSTqPk0xwHaC9?w=322&h=139&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3',
    description: '针对青年作家，提升故事构思、人物塑造和情节发展能力。',
    type: 'online',
    status: 'upcoming'
  },
];

onMounted(() => {
  // 模拟从后端获取数据
  loading.value = true;
  setTimeout(() => {
    activities.value = mockActivities;
    filteredActivities.value = mockActivities; // 初始显示所有活动
    loading.value = false;
  }, 500); // 模拟网络请求延迟
});

const viewActivityDetails = (id) => {
  router.push(`/activities/${id}`);
};

// 未来拓展筛选和搜索功能
// const filterActivities = () => {
//   let tempActivities = activities.value;

//   if (selectedType.value) {
//     tempActivities = tempActivities.filter(activity => activity.type === selectedType.value);
//   }

//   if (searchQuery.value) {
//     const query = searchQuery.value.toLowerCase();
//     tempActivities = tempActivities.filter(activity =>
//       activity.title.toLowerCase().includes(query) ||
//       activity.description.toLowerCase().includes(query)
//     );
//   }
//   filteredActivities.value = tempActivities;
// };
</script>

<style scoped>
.activities-page {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
  font-family: var(--font-family-sans-serif);
}

.page-title {
  text-align: center;
  font-size: var(--font-size-hero-title);
  color: var(--color-heading);
  margin-bottom: 2rem;
  position: relative;
  padding-bottom: 0.5rem;
}

.page-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background-color: var(--color-primary);
  border-radius: 2px;
}

.section-description {
  text-align: center;
  color: var(--color-text-light);
  font-size: var(--font-size-medium);
  margin-bottom: 3rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}


.filter-sort-section {
  display: flex;
  justify-content: center;
  /* 居中 */
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  /* 允许换行 */
}

.filter-sort-section input[type="text"],
.filter-sort-section select {
  padding: 0.8rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-small);
  background-color: var(--color-background-soft);
  color: var(--color-text);
  font-size: var(--font-size-medium);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.filter-sort-section input[type="text"]:focus,
.filter-sort-section select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.2);
}

.activities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.activity-card {
  background-color: var(--color-background-card);
  border-radius: var(--border-radius-large);
  box-shadow: var(--shadow-medium);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
}

.activity-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-hover);
}

.activity-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-bottom: 1px solid var(--color-border);
}

.activity-info {
  padding: 1.5rem;
  flex-grow: 1;
  /* 让内容区域占据剩余空间 */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.activity-title {
  font-size: var(--font-size-large);
  color: var(--color-heading);
  margin-bottom: 0.5rem;
  line-height: 1.4;
  height: 2.8em;
  /* 限制标题行数 */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  /* 限制为2行 */
  -webkit-box-orient: vertical;
}

.activity-date {
  font-size: var(--font-size-small);
  color: var(--color-text-light);
  margin-bottom: 0.8rem;
}

.activity-description-short {
  font-size: var(--font-size-medium);
  color: var(--color-text);
  margin-bottom: 1rem;
  line-height: 1.5;
  height: 4.5em;
  /* 限制描述行数 */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  /* 限制为3行 */
  -webkit-box-orient: vertical;
}

.details-button {
  display: block;
  /* 按钮占据整行 */
  width: 100%;
  padding: 0.8rem 1rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-small);
  cursor: pointer;
  font-size: var(--font-size-medium);
  text-align: center;
  transition: background-color 0.2s ease;
  margin-top: auto;
  /* 按钮推到底部 */
}

.details-button:hover {
  background-color: var(--color-primary-dark);
}

.no-activities-message {
  grid-column: 1 / -1;
  /* 让消息占据所有列 */
  text-align: center;
  padding: 3rem;
  font-size: var(--font-size-large);
  color: var(--color-text-light);
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-large);
  box-shadow: var(--shadow-small);
}

/* Loading spinner styles */
.loading-message {
  text-align: center;
  font-size: var(--font-size-large);
  color: var(--color-text);
  margin-top: 5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: var(--color-primary);
  border-radius: 50%;
  width: 40px;
  height: 40px;
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

/* 响应式调整 */
@media (max-width: 768px) {
  .page-title {
    font-size: var(--font-size-title);
  }

  .activities-grid {
    grid-template-columns: 1fr;
    /* 小屏幕下单列显示 */
  }

  .activity-card {
    flex-direction: row;
    /* 小屏幕上图片和信息横向排列 */
    align-items: flex-start;
  }

  .activity-image {
    width: 120px;
    height: 120px;
    border-bottom: none;
    border-right: 1px solid var(--color-border);
    border-radius: var(--border-radius-small) 0 0 var(--border-radius-small);
  }

  .activity-info {
    padding: 1rem;
  }

  .activity-title {
    font-size: var(--font-size-medium);
    height: auto;
    /* 不再限制行数 */
    -webkit-line-clamp: unset;
  }

  .activity-description-short {
    display: none;
    /* 小屏幕上隐藏描述 */
  }

  .details-button {
    width: auto;
    /* 按钮宽度自适应 */
    margin-top: 0.5rem;
  }
}
</style>