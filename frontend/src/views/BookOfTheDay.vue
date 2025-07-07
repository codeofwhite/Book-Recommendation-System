<template>
<<<<<<< HEAD
  <div
    class="book-of-the-day-container"
    :style="{ backgroundImage: book ? `url(${book.coverUrl})` : 'none' }"
  >
    <div class="background-overlay"></div>
    
=======
  <div class="book-of-the-day-container" :style="{ backgroundImage: book ? `url(${book.coverUrl})` : 'none' }">
    <div class="background-overlay"></div>
    <div class="background-texture"></div>
>>>>>>> zhj
    <div v-if="isLoading" class="loading-spinner"></div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="book" class="content-wrapper" :class="{ loaded: !isLoading }">
<<<<<<< HEAD
      <!-- 左侧图书信息 -->
=======
>>>>>>> zhj
      <div class="info-section">
        <div class="time-display">{{ currentTime }}</div>
        <h1 class="book-title">{{ book.title }}</h1>
        <p class="book-author">{{ book.author }}</p>
        <blockquote class="book-quote">"{{ book.quote }}"</blockquote>
        <router-link :to="`/books/${book.id}`" class="see-more-button">
<<<<<<< HEAD
          >see more
        </router-link>
      </div>

      <!-- 右侧书评面板 -->
      <div class="review-section">
        <BookReviewPanel :book-id="book.id" />
=======
          > 沉浸阅读 (Unfold the Narrative)
        </router-link>
      </div>

      <div class="cover-display-section">
        <img :src="book.coverUrl" :alt="book.title" class="book-cover-image" />
        <div class="cover-frame"></div>
>>>>>>> zhj
      </div>
    </div>
  </div>
</template>

<script setup>
<<<<<<< HEAD
import { ref, onMounted, onUnmounted } from 'vue';
import BookReviewPanel from '../components/BookReviewPanel.vue'; // 导入新组件

// --- 响应式数据 ---
=======
import { ref, onMounted, onUnmounted, watch } from 'vue';
import axios from 'axios'; // 确保导入 axios，如果你要从后端获取每日一书

const props = defineProps({
  initialBook: {
    type: Object,
    default: null
  }
});

>>>>>>> zhj
const isLoading = ref(true);
const error = ref(null);
const book = ref(null);
const currentTime = ref('');
let timerId = null;

<<<<<<< HEAD
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
=======
// 定义 API 基路径，如果你的 BookOfTheDay 是一个独立页面，可能也需要它
const API_BASE_URL = '/service-b/api';

// --- 数据获取 ---
const fetchBookData = async () => {
  isLoading.value = true;
  error.value = null;

  if (props.initialBook) {
    // 如果传入了 initialBook，则直接使用它
    book.value = {
      id: props.initialBook.id || props.initialBook.bookId,
      title: props.initialBook.title,
      author: props.initialBook.author,
      coverUrl: props.initialBook.coverImg || props.initialBook.coverUrl, // 兼容 coverImg 或 coverUrl
      quote: props.initialBook.quote || 'Reading is a good habit.' // 可能没有引用
    };
    isLoading.value = false;
    return; // 结束函数，不再执行 API 请求
  }

  // 如果没有传入 initialBook，则尝试获取每日一书（原逻辑）
  try {
    // 真实 API 请求
    const response = await axios.get(`${API_BASE_URL}/books/daily`);
    const data = response.data;
    if (data) {
      book.value = {
        id: data.id || data.bookId,
        title: data.title,
        author: data.author,
        coverUrl: data.coverImg || data.coverUrl,
        quote: data.quote || 'Reading is a good habit.'
      };
    } else {
      error.value = "今日推荐书籍数据为空。";
    }
>>>>>>> zhj
  } catch (err) {
    console.error("获取每日一书失败:", err);
    error.value = "无法加载今日推荐，请稍后再试。";
  } finally {
    isLoading.value = false;
  }
};

// --- 时间格式化与更新 ---
const formatTime = (date) => {
<<<<<<< HEAD
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


=======
  const year = date.getFullYear();
  const month = date.toLocaleString('en-US', { month: 'short' });
  const day = date.getDate();

  let hours = date.getHours();
  const minutes = date.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12;
  const minutesStr = minutes < 10 ? '0' + minutes : minutes;

  return `${month}. ${day} ${year} ${ampm} ${hours}:${minutesStr}`;
};

>>>>>>> zhj
const updateTime = () => {
  currentTime.value = formatTime(new Date());
};

// --- 生命周期钩子 ---
onMounted(() => {
<<<<<<< HEAD
  fetchBookOfTheDay();
=======
  fetchBookData(); // 调用新的数据获取函数
>>>>>>> zhj
  updateTime();
  timerId = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timerId) {
    clearInterval(timerId);
  }
});
<<<<<<< HEAD
=======

// --- 监听 initialBook prop 的变化，以便在 prop 更新时重新加载数据 ---
// 当 BookOfTheDay 组件作为子组件时，父组件可能在异步获取到 dailyBook 后才传入 prop
watch(() => props.initialBook, (newVal) => {
  if (newVal) {
    fetchBookData(); // 当 initialBook 变化时，重新获取数据
  }
}, { immediate: true }); // immediate: true 使得 watch 在组件挂载时也立即执行一次

>>>>>>> zhj
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
<<<<<<< HEAD
  transition: background-image 1s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-family: 'Georgia', 'Times New Roman', Times, serif;
=======
  transition: background-image 1.5s ease-in-out;
  /* 更长的背景图过渡 */
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f8f0e3;
  /* 浅羊皮纸色，作为整体文字颜色 */
  font-family: 'Georgia', 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
  /* 增强衬线字体家族 */
  overflow: hidden;
  /* 防止内容溢出 */
>>>>>>> zhj
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
<<<<<<< HEAD
  background-color: rgba(0, 0, 0, 0.4); /* 半透明黑色遮罩，确保文字可读性 */
  z-index: 1;
}

=======
  background-color: rgba(30, 20, 10, 0.65);
  /* 更深沉、更偏棕色的半透明遮罩 */
  /* backdrop-filter: blur(5px) brightness(0.8); */
  /* 增加模糊和亮度，营造梦幻感 */
  z-index: 1;
  transition: background-color 1.5s ease-in-out;
  /* 遮罩颜色过渡 */
}

.background-texture {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  /* 在背景图和叠加层之间 */
  /* 可以使用一张浅色、低对比度的纸张/纹理图片作为背景 */
  background-image: url('/path/to/your/parchment-texture.png');
  /* 请替换为你的纹理图片路径 */
  background-size: cover;
  background-repeat: repeat;
  /* 纹理重复 */
  opacity: 0.1;
  /* 纹理不宜过亮，保持低透明度 */
  pointer-events: none;
  /* 确保不影响点击事件 */
}

/* 内容容器 */
>>>>>>> zhj
.content-wrapper {
  position: relative;
  z-index: 2;
  display: flex;
<<<<<<< HEAD
  justify-content: space-between;
  align-items: center;
  width: 90%;
  max-width: 1400px;
  padding: 0 5%;
  gap: 4rem;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s;
=======
  justify-content: center;
  /* 默认居中，响应式再调整 */
  align-items: center;
  width: 90%;
  max-width: 1600px;
  /* 增加最大宽度 */
  padding: 40px;
  /* 增加内边距 */
  gap: 6rem;
  /* 增加左右间距 */
  opacity: 0;
  transform: translateY(30px);
  /* 初始位置更低 */
  transition: opacity 1s ease 0.4s, transform 1s ease 0.4s;
  /* 更长的入场动画 */
>>>>>>> zhj
}

.content-wrapper.loaded {
  opacity: 1;
  transform: translateY(0);
}

<<<<<<< HEAD
=======
/* 左侧信息区 */
>>>>>>> zhj
.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
<<<<<<< HEAD
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
=======
  max-width: 60%;
  /* 限制文字宽度，避免过长 */
  text-align: left;
  position: relative;
  /* 用于装饰元素定位 */
  padding-right: 2rem;
  /* 防止与封面部分文字过近 */
}

/* 时间显示 */
.time-display {
  font-size: 1.1rem;
  margin-bottom: 2.5rem;
  letter-spacing: 1.5px;
  opacity: 0.8;
  font-style: italic;
  position: relative;
  /* 添加装饰线 */
}

.time-display::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -10px;
  /* 在时间下方 */
  width: 60px;
  /* 线条长度 */
  height: 1px;
  background-color: rgba(248, 240, 227, 0.5);
  /* 线条颜色 */
}


/* 书名 */
.book-title {
  font-size: 5.5rem;
  /* 字体更大 */
  font-weight: 700;
  /* 更粗的标题 */
  margin: 0;
  line-height: 1.05;
  /* 更紧凑的行高 */
  text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.6);
  /* 更深的阴影 */
  position: relative;
  padding-bottom: 15px;
  /* 标题下方的装饰线 */
}

.book-title::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 80%;
  /* 根据标题长度调整 */
  height: 2px;
  background: linear-gradient(to right, #c0b2a3, transparent);
  /* 渐变装饰线 */
  opacity: 0.7;
}

/* 作者 */
.book-author {
  font-size: 2.2rem;
  /* 字体更大 */
  font-style: normal;
  margin: 1.5rem 0 3rem 0;
  /* 调整间距 */
  opacity: 0.85;
  text-shadow: 1px 1px 6px rgba(0, 0, 0, 0.5);
  color: #dcd3c5;
  /* 略浅一点的颜色，与标题区分 */
}

/* 引用 */
.book-quote {
  font-size: 1.35rem;
  /* 引用字体稍大 */
  line-height: 1.7;
  max-width: 55ch;
  /* 调整最大宽度 */
  margin: 0;
  font-style: italic;
  opacity: 0.9;
  position: relative;
  padding-left: 20px;
  /* 增加左侧内边距，配合装饰 */
  border-left: 3px solid rgba(248, 240, 227, 0.5);
  /* 引用左侧装饰线 */
  color: #f0e6da;
  /* 引用颜色略有不同 */
}

/* 查看更多按钮 */
.see-more-button {
  margin-top: 4rem;
  /* 增加上边距 */
  color: #dcd3c5;
  /* 按钮颜色与作者文字接近 */
  text-decoration: none;
  font-weight: bold;
  font-size: 1.25rem;
  /* 字体更大 */
  transition: transform 0.3s ease-out, color 0.3s ease;
  /* 添加颜色过渡 */
  display: inline-flex;
  /* 允许内部元素对齐 */
  align-items: center;
  gap: 8px;
  /* 箭头与文字间距 */
  padding: 10px 20px;
  /* 增加点击区域 */
  border: 2px solid #dcd3c5;
  /* 边框 */
  border-radius: 5px;
  background-color: rgba(141, 110, 99, 0.2);
  /* 半透明背景 */
  backdrop-filter: blur(2px);
  /* 增加一点模糊效果 */
}

.see-more-button:hover {
  transform: translateX(15px);
  /* 更明显的位移 */
  color: #fff;
  /* 悬停时变亮 */
  border-color: #fff;
  /* 边框也变亮 */
  background-color: rgba(141, 110, 99, 0.4);
  /* 背景色更深 */
}

.see-more-button::before {
  content: '→';
  /* 使用更现代的右箭头，或者可以换成图标字体 */
  font-size: 1.5em;
  /* 调整箭头大小 */
  margin-right: 5px;
  /* 调整箭头与文字的间距 */
  transition: transform 0.3s ease-out;
}

.see-more-button:hover::before {
  transform: translateX(5px);
  /* 箭头在悬停时也稍微移动 */
}


/* --- 右侧书籍封面展示区 (新增) --- */
.cover-display-section {
  flex-shrink: 0;
  width: 350px;
  /* 固定宽度 */
  height: 500px;
  /* 固定高度 */
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 1000px;
  /* 3D 效果的基础 */
}

.book-cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  box-shadow: 10px 10px 30px rgba(0, 0, 0, 0.5), -5px -5px 15px rgba(255, 255, 255, 0.1);
  /* 复杂阴影，模拟立体感 */
  border: 5px solid #dcd3c5;
  /* 粗边框，类似古籍装帧 */
  border-radius: 5px;
  /* 轻微圆角 */
  transform: rotateY(10deg) rotateX(5deg) scale(0.95);
  /* 轻微倾斜，增加立体感 */
  transition: transform 0.8s ease-out;
  /* 入场动画 */
  opacity: 0;
  animation: cover-entry 1.2s ease-out 0.6s forwards;
  /* 封面入场动画，延迟播放 */
}

.cover-frame {
  position: absolute;
  top: -20px;
  /* 框架比封面大 */
  left: -20px;
  right: -20px;
  bottom: -20px;
  border: 1px dashed rgba(248, 240, 227, 0.3);
  /* 虚线框架，模拟内部画框 */
  border-radius: 8px;
  pointer-events: none;
  opacity: 0;
  animation: frame-fade-in 1.5s ease-out 0.8s forwards;
  /* 框架入场动画，延迟播放 */
}

/* 封面入场动画 */
@keyframes cover-entry {
  0% {
    opacity: 0;
    transform: rotateY(30deg) rotateX(15deg) scale(0.8) translateX(50px);
  }

  100% {
    opacity: 1;
    transform: rotateY(10deg) rotateX(5deg) scale(0.95);
  }
}

/* 框架入场动画 */
@keyframes frame-fade-in {
  0% {
    opacity: 0;
    transform: scale(0.9);
  }

  100% {
    opacity: 1;
    transform: scale(1);
  }
>>>>>>> zhj
}

/* 加载和错误状态 */
.loading-spinner {
  z-index: 3;
  border: 5px solid rgba(255, 255, 255, 0.2);
  border-top-color: #fff;
  border-radius: 50%;
<<<<<<< HEAD
  width: 50px;
  height: 50px;
=======
  width: 60px;
  /* 稍大 */
  height: 60px;
>>>>>>> zhj
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  z-index: 3;
<<<<<<< HEAD
  font-size: 1.5rem;
  background-color: rgba(211, 47, 47, 0.8);
  padding: 1rem 2rem;
  border-radius: 8px;
}

/* 响应式设计 */
=======
  font-size: 1.8rem;
  /* 字体更大 */
  background-color: rgba(160, 0, 0, 0.8);
  /* 更深的错误背景 */
  padding: 1.5rem 3rem;
  /* 更多内边距 */
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .content-wrapper {
    gap: 3rem;
    /* 减小间距 */
    padding: 30px;
  }

  .book-title {
    font-size: 4rem;
    /* 字体缩小 */
  }

  .book-author {
    font-size: 1.8rem;
  }

  .book-quote {
    font-size: 1.2rem;
  }

  .cover-display-section {
    width: 300px;
    height: 450px;
  }
}

>>>>>>> zhj
@media (max-width: 992px) {
  .content-wrapper {
    flex-direction: column;
    justify-content: center;
    text-align: center;
    gap: 3rem;
<<<<<<< HEAD
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
=======
    padding: 20px;
  }

  .info-section {
    align-items: center;
    max-width: 90%;
    /* 小屏幕上文字可以更宽 */
    padding-right: 0;
  }

  .time-display,
  .book-quote,
  .book-title::after,
  .time-display::after {
    text-align: center;
    margin-left: auto;
    margin-right: auto;
    left: unset;
    /* 取消左对齐的定位 */
  }

  .book-quote {
    padding-left: 0;
    border-left: none;
    /* 移除左侧边框 */
    padding-top: 10px;
    border-top: 1px solid rgba(248, 240, 227, 0.5);
    /* 顶部加线 */
  }

  .book-title {
    font-size: 3.5rem;
  }

  .book-author {
    font-size: 1.6rem;
  }

  .cover-display-section {
    width: 250px;
    /* 封面更小 */
    height: 380px;
    margin-top: 2rem;
    /* 与上方文字拉开距离 */
  }

  .see-more-button {
    padding: 8px 15px;
    font-size: 1.1rem;
  }

  .see-more-button:hover {
    transform: translateX(0);
    /* 小屏幕上不进行位移 */
  }
}

@media (max-width: 600px) {
  .book-title {
    font-size: 2.8rem;
  }

  .book-author {
    font-size: 1.4rem;
  }

  .book-quote {
    font-size: 1.1rem;
  }

  .cover-display-section {
    width: 200px;
    height: 300px;
  }
}
</style>
>>>>>>> zhj
