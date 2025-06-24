<template>
  <div class="book-list">
    <!-- 搜索区域 -->
    <div class="search-bar flex justify-center mb-10 gap-4">
      <input type="text" v-model="inputSearchKeyword" placeholder="搜索图书名称..." @keyup.enter="handleSearch"
        class="flex-grow max-w-md p-3 border border-gray-300 rounded-lg shadow-sm text-base focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <button @click="handleSearch"
        class="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition ease-in-out duration-150 transform hover:scale-105">
        搜索
      </button>
    </div>
    <p v-if="loading">加载中...</p>
    <p v-else-if="!books || books.length === 0">没有找到相关书籍。</p>
    <div v-else v-for="book in books" :key="book.bookId" class="book-card">
      <div class="book-cover">
        <img :src="book.coverImg" :alt="book.title" class="rounded-lg shadow-md" />
      </div>
      <div class="book-details">
        <router-link :to="{ name: 'BookDetails', params: { bookId: book.bookId } }"
          class="text-blue-600 hover:underline">
          <h2 class="text-2xl font-bold mb-1">{{ book.title }}</h2>
        </router-link>
        <h3 v-if="book.series" class="text-lg text-gray-600 mb-2">Part of {{ book.series }}</h3>
        <p class="author text-gray-700 mb-2">By {{ book.author }}</p>
        <div class="rating flex items-center mb-2">
          <span class="stars text-yellow-500 text-xl mr-1">{{ '★'.repeat(Math.round(book.rating)) }}{{ '☆'.repeat(5 -
            Math.round(book.rating)) }}</span>
          <span class="text-sm text-gray-500">({{ book.rating }} from {{ book.numRatings }} ratings)</span>
        </div>
        <p class="description text-gray-800 leading-relaxed mb-3">{{ truncateDescription(book.description) }}</p>
        <div class="meta flex flex-wrap gap-x-4 gap-y-2 text-sm text-gray-600 mb-3">
          <span><strong>Published:</strong> {{ book.publishDate }}</span>
          <span><strong>Pages:</strong> {{ book.pages }}</span>
          <span><strong>Price:</strong> ${{ book.price }}</span>
        </div>
        <div class="genres flex flex-wrap gap-2">
          <span v-for="genre in book.genres.slice(0, 5)" :key="genre"
            class="genre-tag bg-gray-200 text-gray-700 px-3 py-1 rounded-full text-xs font-medium">{{ genre }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'BookList',
  props: {
    // 接收从 App.vue 传来的搜索关键词
    searchKeyword: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      // 用于输入框的双向绑定
      inputSearchKeyword: '',
      // 实际用于触发图书列表更新的关键词
      searchKeyword: '',
      books: [],
      loading: true,
    };
  },
  watch: {
    // 监听 searchKeyword 变化，重新加载书籍列表
    searchKeyword: {
      immediate: true, // 立即执行一次，用于初始加载或无搜索词的情况
      handler(newKeyword) {
        this.fetchBooks(newKeyword);
      },
    },
  },
  methods: {
    /**
     * 处理搜索操作，更新 searchKeyword 以触发监听器。
     */
    handleSearch() {
      // 当用户点击搜索或按回车时，更新 searchKeyword
      this.searchKeyword = this.inputSearchKeyword;
    },
    /**
     * 根据关键词获取图书列表。
     * 如果关键词为空，则获取所有图书。
     * @param {string} keyword - 搜索关键词。
     */
    async fetchBooks(keyword) {
      this.loading = true;
      try {
        // 构建请求 URL，如果关键词存在则使用搜索接口，否则使用获取所有图书接口
        const url = keyword
          ? `http://localhost:5000/api/search_local_books?keyword=${encodeURIComponent(keyword)}`
          : 'http://localhost:5000/api/books';

        const response = await axios.get(url);
        this.books = response.data;
      } catch (error) {
        console.error('Error fetching books:', error);
        this.books = []; // 清空数据或显示错误信息
      } finally {
        this.loading = false;
      }
    },
    /**
     * 截断描述文本，使其不超过指定长度并添加省略号。
     * @param {string} desc - 原始描述文本。
     * @returns {string} 截断后的描述文本。
     */
    truncateDescription(desc) {
      if (!desc) return '';
      return desc.length > 200 ? desc.substring(0, 200) + '...' : desc;
    },
  },
};
</script>

<style scoped>
.book-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.book-card {
  display: flex;
  background-color: #fff;
  border-radius: 12px;
  /* 更大的圆角 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  /* 更明显的阴影 */
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  /* 悬停动画 */
}

.book-card:hover {
  transform: translateY(-5px);
  /* 悬停时向上轻微浮动 */
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  /* 悬停时阴影更深 */
}

.book-cover {
  flex-shrink: 0;
  width: 150px;
  /* 固定宽度 */
  height: 220px;
  /* 固定高度 */
  overflow: hidden;
  background-color: #f0f0f0;
  /* 占位背景色 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* 确保图片覆盖整个区域 */
  border-radius: 8px;
  /* 图片圆角 */
}

.book-details {
  padding: 20px;
  text-align: left;
  flex-grow: 1;
}

.book-details h2 {
  font-size: 1.8em;
  color: #333;
  margin-bottom: 5px;
}

.book-details h3 {
  font-size: 1.1em;
  color: #666;
  margin-top: 0;
  margin-bottom: 10px;
}

.book-details .author {
  font-size: 1em;
  color: #555;
  margin-bottom: 10px;
}

.rating .stars {
  color: #f39c12;
  font-size: 1.2em;
}

.rating span {
  font-size: 0.85em;
  color: #777;
  margin-left: 5px;
}

.description {
  line-height: 1.6;
  color: #444;
  margin-bottom: 15px;
  font-size: 0.95em;
}

.meta {
  margin-top: 10px;
  font-size: 0.9em;
  color: #666;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.genres {
  margin-top: 15px;
}

.genre-tag {
  display: inline-block;
  background-color: #e9ecef;
  color: #495057;
  padding: 4px 10px;
  border-radius: 5px;
  margin-right: 5px;
  margin-bottom: 5px;
  font-size: 0.8em;
  text-transform: uppercase;
}

.loading,
.not-found {
  text-align: center;
  padding: 50px;
  font-size: 1.2em;
  color: #777;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .book-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .book-cover {
    width: 100%;
    height: 250px;
    /* 移动端封面高度 */
    border-bottom: 1px solid #eee;
    margin-bottom: 15px;
  }

  .book-cover img {
    border-radius: 8px 8px 0 0;
  }

  .book-details {
    padding: 15px;
  }

  .book-details h2 {
    font-size: 1.5em;
  }

  .book-details h3 {
    font-size: 1em;
  }

  .meta,
  .genres {
    justify-content: center;
  }
}

.search-bar {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  gap: 10px;
}

.search-bar input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  /* 圆角 */
  font-size: 1em;
  width: 300px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  /* 轻微阴影 */
}

.search-bar button {
  padding: 10px 20px;
  background-color: #42b983;
  /* 绿色按钮 */
  color: white;
  border: none;
  border-radius: 8px;
  /* 圆角 */
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease, transform 0.2s ease;
  /* 过渡效果 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  /* 按钮阴影 */
}

.search-bar button:hover {
  background-color: #369b6f;
  /* 鼠标悬停时的颜色 */
  transform: translateY(-2px);
  /* 向上轻微移动 */
}

.search-bar button:active {
  transform: translateY(0);
  /* 点击时的效果 */
}
</style>