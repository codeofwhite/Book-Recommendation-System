<template>
  <div
    class="book-of-the-day-container"
    :style="{ backgroundImage: book ? `url(${book.coverUrl})` : 'none' }"
  >
    <div class="background-overlay"></div>
    
    <div v-if="isLoading" class="loading-spinner"></div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="book" class="content-wrapper" :class="{ loaded: !isLoading }">
      <!-- 左侧图书信息 -->
      <div class="info-section">
        <div class="time-display">{{ currentTime }}</div>
        <h1 class="book-title">{{ book.title }}</h1>
        <p class="book-author">{{ book.author }}</p>
        <blockquote class="book-quote">"{{ book.quote }}"</blockquote>
        <router-link :to="`/books/${book.id}`" class="see-more-button">
          >see more
        </router-link>
      </div>

      <!-- 右侧书评面板 -->
      <div class="review-section">
        <BookReviewPanel :book-id="book.id" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import BookReviewPanel from '../components/BookReviewPanel.vue'; // 导入新组件

// --- 响应式数据 ---
const isLoading = ref(true);
const error = ref(null);
const book = ref(null);
const currentTime = ref('');
let timerId = null;

// --- 数据获取 ---
const fetchBookOfTheDay = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    // 使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 200)); // 模拟网络延迟
    book.value = {
      id: '9787532788226',
      title: '沙丘',
      author: '弗兰克·赫伯特',
      // 请确保这个图片URL是有效的，并且允许跨域访问
      coverUrl: 'https://pic3.zhimg.com/v2-e27b6692c148f856de9ff7da8a23c046_r.jpg',
      quote: '我绝不能恐惧。恐惧是思维杀手。恐惧是带来彻底毁灭的小小死神。'
    };
  } catch (err) {
    console.error("获取每日一书失败:", err);
    error.value = "无法加载今日推荐，请稍后再试。";
  } finally {
    isLoading.value = false;
  }
};

// --- 时间格式化与更新 ---
const formatTime = (date) => {
    const year = date.getFullYear();
    const month = date.toLocaleString('en-US', { month: 'short' });
    const day = date.getDate();
    
    // 格式化时间为 AM/PM
    let hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    const minutesStr = minutes < 10 ? '0' + minutes : minutes;

    // 组合成 "Jul. 3 2025 AM 10:59" 格式
    return `${month}. ${day} ${year} ${ampm} ${hours}:${minutesStr}`;
};


const updateTime = () => {
  currentTime.value = formatTime(new Date());
};

// --- 生命周期钩子 ---
onMounted(() => {
  fetchBookOfTheDay();
  updateTime();
  timerId = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timerId) {
    clearInterval(timerId);
  }
});
</script>

<style scoped>
.book-of-the-day-container {
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  transition: background-image 1s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-family: 'Georgia', 'Times New Roman', Times, serif;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4); /* 半透明黑色遮罩，确保文字可读性 */
  z-index: 1;
}

.content-wrapper {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 90%;
  max-width: 1400px;
  padding: 0 5%;
  gap: 4rem;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s;
}

.content-wrapper.loaded {
  opacity: 1;
  transform: translateY(0);
}

.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.time-display {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  letter-spacing: 1px;
}

.book-title {
  font-size: 4.5rem;
  font-weight: normal;
  margin: 0;
  line-height: 1.1;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
}

.book-author {
  font-size: 2rem;
  font-style: normal; /* 按照图片样式，改为非斜体 */
  margin: 1rem 0 2.5rem 0;
  opacity: 0.9;
  text-shadow: 1px 1px 6px rgba(0, 0, 0, 0.5);
}

.book-quote {
  font-size: 1.2rem;
  line-height: 1.6;
  max-width: 50ch;
  margin: 0;
  font-style: italic; /* 引用内容使用斜体 */
}

.see-more-button {
  margin-top: 3rem;
  color: white;
  text-decoration: none;
  font-weight: bold;
  font-size: 1.1rem;
  transition: transform 0.3s;
  display: inline-block;
}

.see-more-button:hover {
  transform: translateX(10px);
}

.review-section {
  flex-shrink: 0; /* 防止书评面板被压缩 */
}

/* 加载和错误状态 */
.loading-spinner {
  z-index: 3;
  border: 5px solid rgba(255, 255, 255, 0.2);
  border-top-color: #fff;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  z-index: 3;
  font-size: 1.5rem;
  background-color: rgba(211, 47, 47, 0.8);
  padding: 1rem 2rem;
  border-radius: 8px;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .content-wrapper {
    flex-direction: column;
    justify-content: center;
    text-align: center;
    gap: 3rem;
  }
  .info-section {
    align-items: center;
  }
  .book-quote {
    padding-left: 0;
    text-align: center;
  }
  .book-title {
    font-size: 3rem;
  }
  .book-author {
    font-size: 1.5rem;
  }
}
</style>
