<template>
  <div class="review-panel-container" :class="{ loaded: !isLoading }">
    <div v-if="isLoading" class="spinner"></div>
    <div v-if="error" class="error-text">{{ error }}</div>
    <div v-if="review" class="review-content">
      <h2 class="review-title">{{ review.title }}</h2>
      <hr class="separator" />
      <p class="review-body">{{ review.content }}</p>
      <a href="#" @click.prevent="seeMore" class="see-more-link"> >see more </a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// 接收父组件传递的图书ID
const props = defineProps({
  bookId: {
    type: String,
    required: true,
  },
});

const isLoading = ref(true);
const error = ref(null);
const review = ref(null);

// 伪代码/后端交互：根据bookId获取书评
const fetchReview = async () => {
  isLoading.value = true;
  error.value = null;
  console.log(`Fetching review for book ID: ${props.bookId}`);

  try {
    // 伪代码:
    // const response = await axios.get(`/api/reviews/${props.bookId}`);
    // review.value = response.data;

    // 使用模拟数据
    await new Promise((resolve) => setTimeout(resolve, 1000)); // 模拟网络延迟
    if (props.bookId === '9787532788226') {
      review.value = {
        title: '一部献给未来的史诗',
        content:
          '《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。《沙丘》不仅仅是科幻小说，它探讨了政治、宗教、生态和人性的复杂交织。弗兰克·赫伯特的想象力构建了一个无比真实、令人沉浸的世界，其深度和广度至今仍难以超越。',
      };
    } else {
      throw new Error('找不到对应的书评。');
    }
  } catch (err) {
    console.error('获取书评失败:', err);
    error.value = '无法加载书评。';
  } finally {
    isLoading.value = false;
  }
};

const seeMore = () => {
  // 在真实应用中，这里可能会弹出一个模态框显示完整书评，或跳转到专门的书评页面
  alert(`查看更多关于《${review.value.title}》的书评`);
};

onMounted(() => {
  fetchReview();
});
</script>

<style scoped>
.review-panel-container {
  background-color: rgba(245, 245, 245, 0.85); /* 半透明浅灰色背景 */
  backdrop-filter: blur(10px); /* 毛玻璃效果 */
  -webkit-backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px 35px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  color: #333;
  transition: opacity 0.5s ease;
  opacity: 0;
  min-height: 320px; /* 确保加载时有最小高度 */
  max-height: 720px;
  display: flex;
}

.review-panel-container.loaded {
  opacity: 1;
}

.review-content {
  min-height: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.review-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 15px 0;
  text-align: center;
}

.separator {
  border: none;
  height: 1px;
  background-color: #ccc;
  margin: 0 0 20px 0;
}

.review-body {
  font-size: 1rem;
  line-height: 1.7;
  flex-grow: 1; /* 让内容占据多余空间 */
  margin: 0;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 21;
  overflow: hidden;
}

.see-more-link {
  text-align: right;
  margin-top: 20px;
  color: #555;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.3s;
}

.see-more-link:hover {
  color: #000;
}

/* 加载和错误状态的样式 */
.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #333;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-text {
  margin: auto;
  font-size: 1.1rem;
  color: #d32f2f;
}
</style>