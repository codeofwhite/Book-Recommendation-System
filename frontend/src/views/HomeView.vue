<template>
  <div class="home-view">
    <h1 class="page-title">精选图书推荐</h1>

    <div v-if="recommendedBooks.length === 0" class="loading-message">
      正在加载图书数据...
    </div>

    <div v-else class="book-list">
      <div v-for="book in recommendedBooks" :key="book.id" class="book-card">
        <img :src="book.coverImage" :alt="book.title" class="book-cover" />
        <div class="book-info">
          <h2 class="book-title">{{ book.title }}</h2>
          <p class="book-author">作者：{{ book.author }}</p>
          <p class="book-genre">分类：{{ book.genre}}</p>
          <p class="book-description">{{ truncateDescription(book.description) }}</p>
          <button @click="viewBookDetails(book.id)" class="details-button">查看详情</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

// 使用 useRouter 钩子获取路由实例，用于导航
const router = useRouter();

// 使用 ref 创建响应式数据，存储推荐的图书列表
const recommendedBooks = ref([]);

// 模拟的图书数据
const mockBooks = [
  {
    id: '1',
    title: 'Vue.js 3 实践指南',
    author: '前端老张',
    genre: '编程技术',
    description: '深入浅出地讲解 Vue.js 3 的核心概念和实战技巧，助你从入门到精通。包含 Composition API、Teleport、Suspense 等新特性。',
    coverImage: 'https://via.placeholder.com/150x200?text=Vue3Book'
  },
  {
    id: '2',
    title: '微服务架构设计',
    author: '架构师李工',
    genre: '系统设计',
    description: '本书详细阐述了微服务的设计原则、实践模式、服务间通信、数据管理和部署策略，是构建高可用微服务系统的必备参考。',
    coverImage: 'https://via.placeholder.com/150x200?text=Microservices'
  },
  {
    id: '3',
    title: 'Python Flask 实战',
    author: 'Python 小白',
    genre: '后端开发',
    description: '通过多个项目案例，手把手教你使用 Flask 构建 RESTful API 和 Web 应用，包括数据库集成、认证授权等。',
    coverImage: 'https://via.placeholder.com/150x200?text=FlaskBook'
  },
  {
    id: '4',
    title: '算法导论',
    author: 'Thomas H. Cormen',
    genre: '计算机科学',
    description: '计算机科学领域的经典著作，全面覆盖各种算法和数据结构，是学习算法的权威教材。',
    coverImage: 'https://via.placeholder.com/150x200?text=Algorithms'
  },
  {
    id: '5',
    title: '三体',
    author: '刘慈欣',
    genre: '科幻小说',
    description: '中国科幻文学的里程碑之作，讲述了地球文明与三体文明在宇宙中的生存斗争。',
    coverImage: 'https://via.placeholder.com/150x200?text=ThreeBody'
  }
];

// 模拟从后端获取数据的函数
const fetchRecommendedBooks = () => {
  // 模拟网络请求延迟
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(mockBooks);
    }, 1000); // 1秒延迟
  });
};

// 在组件挂载后执行的生命周期钩子
onMounted(async () => {
  try {
    // 实际项目中这里会用 axios.get('/api/books/recommended')
    const data = await fetchRecommendedBooks();
    recommendedBooks.value = data;
  } catch (error) {
    console.error('获取推荐图书失败:', error);
    // 可以在这里显示错误消息给用户
  }
});

// 截断描述文本的函数
const truncateDescription = (description) => {
  const maxLength = 80; // 最大显示字符数
  if (description.length > maxLength) {
    return description.substring(0, maxLength) + '...';
  }
  return description;
};

// 查看图书详情的函数，点击后跳转到详情页面
const viewBookDetails = (bookId) => {
  // 假设有一个 '/books/:id' 的路由用于显示图书详情
  router.push(`/books/${bookId}`);
};
</script>

<style scoped>
.home-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
}

.page-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 2.5em;
  font-weight: bold;
}

.loading-message {
  text-align: center;
  font-size: 1.2em;
  color: #666;
  margin-top: 50px;
}

.book-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px;
  justify-content: center;
}

.book-card {
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  min-height: 400px; /* 确保卡片高度一致 */
}

.book-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.book-cover {
  width: 100%;
  height: 200px; /* 固定封面高度 */
  object-fit: cover; /* 保持图片比例，裁剪超出部分 */
  display: block;
  border-bottom: 1px solid #eee;
}

.book-info {
  padding: 15px;
  flex-grow: 1; /* 占据剩余空间 */
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 1.4em;
  color: #34495e;
  margin-top: 0;
  margin-bottom: 10px;
  font-weight: 600;
  line-height: 1.3;
}

.book-author,
.book-genre {
  font-size: 0.95em;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.book-description {
  font-size: 0.9em;
  color: #555;
  line-height: 1.6;
  margin-bottom: 15px;
  flex-grow: 1; /* 让描述占据尽可能多的空间 */
}

.details-button {
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 10px 15px;
  font-size: 1em;
  cursor: pointer;
  transition: background-color 0.3s ease;
  align-self: flex-start; /* 让按钮靠左 */
  margin-top: auto; /* 将按钮推到底部 */
}

.details-button:hover {
  background-color: #369c73;
}
</style>