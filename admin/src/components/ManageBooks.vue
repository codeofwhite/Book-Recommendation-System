<template>
  <div class="admin-panel-card">
    <div class="header-section">
      <h2>Manage Books</h2>
      <p>View, edit, or take down existing book entries.</p>
    </div>

    <div class="search-filter-bar">
      <input type="text" v-model="inputSearchKeyword" placeholder="Search by title, author, ISBN..."
        class="search-input" />
      <button class="search-button" @click="searchBooks">
        <span class="search-icon">🔍</span>
        Search
      </button>
    </div>

    <hr class="section-divider">
    <div class="charts-section">
      <h3>Book Data Insights</h3>

      <div class="chart-container">
        <h4>Book Rating Distribution</h4>
        <v-chart class="chart" :option="ratingDistributionChartOptions" autoresize v-if="allBooks.length > 0" />
        <p v-else-if="loadingBooks" class="loading-message">Loading rating distribution chart...</p>
        <p v-else class="no-data-message">No data available for rating distribution.</p>
      </div>

      <div class="chart-container">
        <h4>Top Authors by Book Count (Top 10)</h4>
        <v-chart class="chart" :option="topAuthorsChartOptions" autoresize v-if="allBooks.length > 0" />
        <p v-else-if="loadingBooks" class="loading-message">Loading top authors chart...</p>
        <p v-else class="no-data-message">No data available for top authors.</p>
      </div>
    </div>
    <hr class="section-divider">

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Author</th>
            <th>ISBN</th>
            <th>Rating</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingBooks">
            <td colspan="6" class="loading-message-cell">Loading books...</td>
          </tr>
          <tr v-else-if="errorBooks">
            <td colspan="6" class="error-message-cell">Error: {{ errorBooks }}</td>
          </tr>
          <tr v-else-if="paginatedBooks.length === 0">
            <td colspan="6" class="no-data-message-cell">No books found.</td>
          </tr>
          <tr v-for="book in paginatedBooks" :key="book.bookId" class="table-row">
            <td>{{ book.bookId }}</td>
            <td class="title-cell">{{ book.title }}</td>
            <td>{{ book.author }}</td>
            <td>{{ book.isbn || 'N/A' }}</td>
            <td>
              <span class="rating-badge">{{ book.rating ? book.rating.toFixed(1) : 'N/A' }}</span>
            </td>
            <td>
              <div class="action-buttons">
                <button class="action-button edit-button" @click="openEditModal(book)">
                  ✏️ Edit
                </button>
                <button class="action-button take-down-button" @click="takeDownBook(book.bookId)">
                  ⤵️ Take Down
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="pagination-btn">
        ← Previous
      </button>
      <span class="pagination-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages" class="pagination-btn">
        Next →
      </button>
    </div>

    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Edit Book</h3>
          <button class="close-button" @click="closeEditModal">×</button>
        </div>
        <form @submit.prevent="saveBook" class="edit-form">
          <div class="form-group">
            <label>Title:</label>
            <input type="text" v-model="editingBook.title" required>
          </div>
          <div class="form-group">
            <label>Author:</label>
            <input type="text" v-model="editingBook.author" required>
          </div>
          <div class="form-group">
            <label>ISBN:</label>
            <input type="text" v-model="editingBook.isbn">
          </div>
          <div class="form-group">
            <label>Description:</label>
            <textarea v-model="editingBook.description" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label>Publisher:</label>
            <input type="text" v-model="editingBook.publisher">
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-button" @click="closeEditModal">Cancel</button>
            <button type="submit" class="save-button">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import VChart from 'vue-echarts'
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, PieChart } from 'echarts/charts'; // 导入 BarChart 和 PieChart
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent // 如果使用DatasetComponent管理数据
} from 'echarts/components';
import { graphic } from 'echarts/core'; // 导入 graphic 对象用于渐变色

// 注册 ECharts 必要的组件
use([
  CanvasRenderer,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent // 注册 DatasetComponent
]);

const allBooks = ref([])
const inputSearchKeyword = ref('')
const currentPage = ref(1)
const pageSize = 10
const showEditModal = ref(false)
const editingBook = ref({})
const loadingBooks = ref(false); // 新增加载状态
const errorBooks = ref(null); // 新增错误状态

// 获取书籍信息采用BookList相同接口
const fetchBooks = async () => {
  loadingBooks.value = true; // 开始加载
  errorBooks.value = null; // 清除之前的错误
  try {
    const response = await axios.get('/service-b/api/books')
    allBooks.value = response.data
  } catch (error) {
    console.error('Error fetching books:', error)
    errorBooks.value = 'Failed to load books. Please try again.'; // 设置错误信息
  } finally {
    loadingBooks.value = false; // 结束加载
  }
}

const filteredBooks = computed(() => {
  let filtered = [...allBooks.value]
  if (inputSearchKeyword.value) {
    const keyword = inputSearchKeyword.value.toLowerCase()
    filtered = filtered.filter(book =>
      book.title.toLowerCase().includes(keyword) ||
      book.author.toLowerCase().includes(keyword) ||
      (book.isbn && book.isbn.toLowerCase().includes(keyword))
    )
  }
  return filtered
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredBooks.value.length / pageSize))
)

const paginatedBooks = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredBooks.value.slice(start, start + pageSize)
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const searchBooks = () => {
  currentPage.value = 1
}

const openEditModal = (book) => {
  editingBook.value = { ...book }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingBook.value = {}
}

const saveBook = async () => {
  try {
    // 假设后端返回更新后的书籍数据，如果没有，可以根据需要调整
    const response = await axios.put(`/service-b/api/books/${editingBook.value.bookId}`, editingBook.value)
    const updatedBook = response.data; // 假设后端返回完整的更新后书籍对象

    const index = allBooks.value.findIndex(b => b.bookId === updatedBook.bookId)
    if (index !== -1) {
      allBooks.value[index] = { ...updatedBook } // 使用后端返回的最新数据更新
    } else {
      // 如果是新增书籍（虽然这个页面是编辑），或者bookId没找到，可以重新获取列表
      fetchBooks();
    }
    closeEditModal()
    alert('Book updated successfully!')
  } catch (error) {
    console.error('Error updating book:', error)
    alert('Failed to update book.')
  }
}

const takeDownBook = async (bookId) => { // 将 deleteBook 重命名为 takeDownBook 以匹配模板
  if (!confirm('Are you sure you want to take down this book? This action cannot be undone.')) return

  try {
    await axios.delete(`/service-b/api/books/${bookId}`)
    allBooks.value = allBooks.value.filter(b => b.bookId !== bookId)
    alert('Book taken down successfully!')
    // 重新计算图表数据
  } catch (error) {
    console.error('Error taking down book:', error)
    alert('Failed to take down book.')
  }
}

watch(inputSearchKeyword, () => {
  currentPage.value = 1
})

onMounted(fetchBooks)

// --- 可视化逻辑 ---

// 计算书籍评分分布
const ratingDistributionChartOptions = computed(() => {
  if (allBooks.value.length === 0) return {};

  const ratingCounts = {
    '1.0-2.0': 0,
    '2.1-3.0': 0,
    '3.1-4.0': 0,
    '4.1-5.0': 0,
    'Unrated': 0 // 添加未评分类别
  };

  allBooks.value.forEach(book => {
    const rating = book.rating;
    if (typeof rating !== 'number' || isNaN(rating) || rating === 0) { // 假设 0 或非数字为未评分
      ratingCounts['Unrated']++;
    } else if (rating >= 1.0 && rating <= 2.0) {
      ratingCounts['1.0-2.0']++;
    } else if (rating > 2.0 && rating <= 3.0) {
      ratingCounts['2.1-3.0']++;
    } else if (rating > 3.0 && rating <= 4.0) {
      ratingCounts['3.1-4.0']++;
    } else if (rating > 4.0 && rating <= 5.0) {
      ratingCounts['4.1-5.0']++;
    }
  });

  const categories = Object.keys(ratingCounts);
  const seriesData = categories.map(cat => ratingCounts[cat]);

  return {
    title: {
      text: 'Book Rating Distribution',
      left: 'center',
      textStyle: { fontSize: 16, color: '#333' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: '{b}: {c} books'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        rotate: 30,
        color: '#555'
      },
      axisLine: { lineStyle: { color: '#ccc' } }
    },
    yAxis: {
      type: 'value',
      name: 'Number of Books',
      nameTextStyle: { color: '#555' },
      axisLabel: { color: '#555' },
      splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }
    },
    series: [{
      name: 'Number of Books',
      type: 'bar',
      data: seriesData,
      itemStyle: {
        color: new graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#4CAF50' }, // 更柔和的绿色
          { offset: 1, color: '#8BC34A' }
        ]),
        borderRadius: [5, 5, 0, 0]
      },
      emphasis: { itemStyle: { color: '#388E3C' } }
    }]
  };
});

// 计算按作者统计书籍数量 (Top 10)
const topAuthorsChartOptions = computed(() => {
  if (allBooks.value.length === 0) return {};

  const authorCounts = {};
  allBooks.value.forEach(book => {
    if (book.author) {
      authorCounts[book.author] = (authorCounts[book.author] || 0) + 1;
    }
  });

  // 将作者和数量转换为数组并排序
  const sortedAuthors = Object.entries(authorCounts)
    .sort(([, countA], [, countB]) => countB - countA) // 降序排序
    .slice(0, 10); // 取前10位

  const authors = sortedAuthors.map(([author]) => author);
  const bookCounts = sortedAuthors.map(([, count]) => count);

  return {
    title: {
      text: 'Top Authors by Book Count (Top 10)',
      left: 'center',
      textStyle: { fontSize: 16, color: '#333' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: '{b}: {c} books'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value', // 数量作为X轴
      name: 'Number of Books',
      nameTextStyle: { color: '#555' },
      axisLabel: { color: '#555' },
      splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }
    },
    yAxis: {
      type: 'category', // 作者作为Y轴
      data: authors.reverse(), // 反转，使数量最多的在顶部
      axisLabel: {
        color: '#555'
      },
      axisLine: { lineStyle: { color: '#ccc' } }
    },
    series: [{
      name: 'Number of Books',
      type: 'bar',
      data: bookCounts.reverse(), // 数据也需要反转匹配Y轴
      itemStyle: {
        color: new graphic.LinearGradient(0, 0, 1, 0, [ // 水平渐变
          { offset: 0, color: '#FFA07A' }, // 柔和的橙色
          { offset: 1, color: '#FF7F50' }
        ]),
        borderRadius: [0, 5, 5, 0] // 柱子右侧圆角
      },
      emphasis: { itemStyle: { color: '#FF6347' } }
    }]
  };
});
</script>

<style scoped>
/* 保持大部分现有样式，只添加/修改与图表和布局相关的部分 */

.admin-panel-card {
  background-color: #ffffff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.header-section h2 {
  color: #2c3e50;
  font-size: 2.2em;
  margin-bottom: 10px;
}

.header-section p {
  color: #7f8c8d;
  font-size: 1.1em;
}

.search-filter-bar {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 30px;
}

.search-input {
  padding: 12px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  width: 400px;
  font-size: 1em;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.search-input:focus {
  border-color: #3498db;
  box-shadow: 0 0 8px rgba(52, 152, 219, 0.2);
  outline: none;
}

.search-button {
  padding: 12px 25px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1em;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.search-button:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}

.search-icon {
  font-size: 1.2em;
}

/* --- 分隔线 --- */
.section-divider {
  border: none;
  border-top: 1px dashed #e0e0e0;
  margin: 40px 0;
  /* 调整间距，将图表与上下区域分隔开 */
}

/* --- 图表区域 --- */
.charts-section {
  margin-top: 20px;
  /* 与分隔线保持间距 */
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  /* 确保至少两列，每列最小450px */
  gap: 30px;
  /* 增加图表之间的间距 */
  padding: 0 20px;
  /* 稍微内缩，避免太靠近边缘 */
}

.charts-section h3 {
  grid-column: 1 / -1;
  /* 标题占据所有列 */
  text-align: center;
  color: #2c3e50;
  font-size: 1.8em;
  margin-bottom: 25px;
  padding-top: 10px;
}

.chart-container {
  background-color: #ffffff;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
  min-height: 400px;
  /* 确保图表容器有足够的最小高度 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  /* 垂直居中内容 */
  align-items: center;
  /* 水平居中内容 */
  transition: box-shadow 0.3s ease;
}

.chart-container:hover {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.chart-container h4 {
  margin-top: 0;
  color: #34495e;
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.4em;
}

.chart {
  height: 300px;
  /* 图表实际渲染的高度 */
  width: 100%;
  /* 图表宽度填充容器 */
}

/* --- 表格区域 --- */
.table-container {
  overflow-x: auto;
  /* 允许表格水平滚动 */
  margin-top: 30px;
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  /* 边框 */
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 15px 20px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.data-table thead th {
  background-color: #f8f9fa;
  color: #555;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.9em;
}

.data-table tbody tr:hover {
  background-color: #f5f5f5;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.title-cell {
  font-weight: 600;
  color: #333;
}

.rating-badge {
  display: inline-block;
  padding: 5px 10px;
  background-color: #e0f7fa;
  color: #007bbd;
  border-radius: 5px;
  font-weight: bold;
  font-size: 0.85em;
}

/* --- 操作按钮 --- */
.action-buttons {
  display: flex;
  gap: 10px;
}

.action-button {
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.edit-button {
  background-color: #28a745;
  color: white;
}

.edit-button:hover {
  background-color: #218838;
  transform: translateY(-1px);
}

.take-down-button {
  background-color: #dc3545;
  color: white;
}

.take-down-button:hover {
  background-color: #c82333;
  transform: translateY(-1px);
}

/* --- 分页 --- */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
  margin-bottom: 20px;
}

.pagination-btn {
  padding: 10px 20px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  color: #555;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #e0e0e0;
  border-color: #bbb;
}

.pagination-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.pagination-info {
  font-size: 1em;
  color: #666;
  font-weight: 500;
}

/* --- 模态框样式 --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 600px;
  position: relative;
  animation: modal-fade-in 0.3s ease-out;
}

@keyframes modal-fade-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5em;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.8em;
  cursor: pointer;
  color: #888;
  transition: color 0.3s ease;
}

.close-button:hover {
  color: #333;
}

.edit-form .form-group {
  margin-bottom: 15px;
}

.edit-form label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
}

.edit-form input[type="text"],
.edit-form textarea {
  width: calc(100% - 22px);
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1em;
  transition: border-color 0.3s ease;
}

.edit-form input[type="text"]:focus,
.edit-form textarea:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 5px rgba(52, 152, 219, 0.2);
}

.edit-form textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 25px;
}

.cancel-button,
.save-button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  font-weight: 500;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.cancel-button {
  background-color: #f0f0f0;
  color: #555;
}

.cancel-button:hover {
  background-color: #e0e0e0;
}

.save-button {
  background-color: #007bff;
  color: white;
}

.save-button:hover {
  background-color: #0056b3;
}

/* 消息样式 */
.loading-message,
.no-data-message {
  text-align: center;
  color: #7f8c8d;
  font-style: italic;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.error-message {
  color: #e74c3c;
  background-color: #fce8e6;
  border: 1px solid #e74c3c;
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

/* 表格内部的消息样式 */
.loading-message-cell,
.error-message-cell,
.no-data-message-cell {
  text-align: center !important;
  font-style: italic;
  color: #7f8c8d;
  padding: 20px;
}

.error-message-cell {
  color: #e74c3c;
}
</style>