<template>
  <div class="admin-container">
    <div class="page-header">
      <div class="header-content">
        <h2>图书库管理</h2>
        <p>检索、编辑或下架系统中的书籍资源</p>
      </div>
      <div class="header-actions">
        <div class="search-box">
          <input type="text" v-model="inputSearchKeyword" placeholder="输入书名、作者或 ISBN..." @keyup.enter="searchBooks" />
          <button class="btn-search" @click="searchBooks">🔍 搜索</button>
        </div>
      </div>
    </div>

    <div class="stats-overview">
      <div class="stat-card card-shadow">
        <div class="card-title">
          <span class="dot green"></span>
          <h4>评分分布统计</h4>
        </div>
        <div class="chart-wrapper">
          <v-chart class="chart" :option="ratingDistributionChartOptions" autoresize v-if="allBooks.length > 0" />
          <div v-else class="chart-placeholder">数据加载中...</div>
        </div>
      </div>

      <div class="stat-card card-shadow">
        <div class="card-title">
          <span class="dot orange"></span>
          <h4>高产作者排行 (TOP 10)</h4>
        </div>
        <div class="chart-wrapper">
          <v-chart class="chart" :option="topAuthorsChartOptions" autoresize v-if="allBooks.length > 0" />
          <div v-else class="chart-placeholder">数据加载中...</div>
        </div>
      </div>
    </div>

    <div class="data-section card-shadow">
      <div class="section-header">
        <h3>书籍列表</h3>
        <span class="total-count">共 {{ filteredBooks.length }} 本书籍</span>
      </div>

      <div class="table-responsive">
        <table class="modern-table">
          <thead>
            <tr>
              <th width="80">ID</th>
              <th>图书标题</th>
              <th>作者</th>
              <th>ISBN</th>
              <th>评分</th>
              <th width="200">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingBooks">
              <td colspan="6" class="status-cell">
                <div class="loader"></div> 正在同步数据...
              </td>
            </tr>
            <tr v-else-if="paginatedBooks.length === 0">
              <td colspan="6" class="status-cell">📭 未找到相关书籍</td>
            </tr>
            <tr v-for="book in paginatedBooks" :key="book.bookId">
              <td class="id-text">#{{ book.bookId }}</td>
              <td>
                <div class="title-wrap">
                  <span class="main-title">{{ book.title }}</span>
                </div>
              </td>
              <td><span class="author-tag">{{ book.author }}</span></td>
              <td class="isbn-text">{{ book.isbn || '---' }}</td>
              <td>
                <span :class="['rating-pill', getRatingClass(book.rating)]">
                  {{ book.rating ? book.rating.toFixed(1) : '无评分' }}
                </span>
              </td>
              <td>
                <div class="row-actions">
                  <button class="btn-icon edit" @click="openEditModal(book)" title="编辑书籍">
                    <span class="icon">✏️</span> 编辑
                  </button>
                  <button class="btn-icon delete" @click="takeDownBook(book.bookId)" title="下架书籍">
                    <span class="icon">🗑️</span> 下架
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination-container">
        <div class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</div>
        <div class="page-controls">
          <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">上一页</button>
          <div class="page-numbers">
            <span v-for="p in totalPages" :key="p" :class="{ active: p === currentPage }" @click="goToPage(p)">{{ p
              }}</span>
          </div>
          <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">下一页</button>
        </div>
      </div>
    </div>

    <transition name="modal">
      <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
        <div class="modal-window" @click.stop>
          <div class="modal-head">
            <h3>修改图书信息</h3>
            <button class="btn-close" @click="closeEditModal">×</button>
          </div>
          <form @submit.prevent="saveBook" class="modal-form">
            <div class="form-grid">
              <div class="form-group">
                <label>图书标题</label>
                <input type="text" v-model="editingBook.title" required>
              </div>
              <div class="form-group">
                <label>作者</label>
                <input type="text" v-model="editingBook.author" required>
              </div>
              <div class="form-group">
                <label>ISBN 编码</label>
                <input type="text" v-model="editingBook.isbn">
              </div>
              <div class="form-group">
                <label>出版社</label>
                <input type="text" v-model="editingBook.publisher">
              </div>
              <div class="form-group full-width">
                <label>内容简介</label>
                <textarea v-model="editingBook.description" rows="3"></textarea>
              </div>
            </div>
            <div class="modal-foot">
              <button type="button" class="btn-cancel" @click="closeEditModal">取消</button>
              <button type="submit" class="btn-save">保存更新</button>
            </div>
          </form>
        </div>
      </div>
    </transition>
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

const getRatingClass = (rating) => {
  if (!rating) return 'gray';
  if (rating >= 4.5) return 'excellent';
  if (rating >= 3.5) return 'good';
  return 'average';
}

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
.admin-container {
  padding: 24px;
  background-color: #f1f5f9;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
}

/* 顶部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
}

.header-content h2 {
  font-size: 1.8rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.header-content p {
  color: #64748b;
  margin: 5px 0 0;
}

.search-box {
  display: flex;
  background: white;
  padding: 6px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.search-box input {
  border: none;
  padding: 8px 16px;
  width: 280px;
  outline: none;
  font-size: 0.9rem;
}

.btn-search {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

/* 图表区 */
.stats-overview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.card-title h4 {
  margin: 0;
  font-size: 0.95rem;
  color: #334155;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.green {
  background: #10b981;
}

.dot.orange {
  background: #f59e0b;
}

.chart-wrapper {
  height: 300px;
  width: 100%;
}

/* 表格区 */
.data-section {
  background: white;
  border-radius: 16px;
  padding: 0;
  overflow: hidden;
}

.section-header {
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f1f5f9;
}

.section-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.total-count {
  font-size: 0.85rem;
  color: #94a3b8;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
}

.modern-table th {
  background: #f8fafc;
  padding: 14px 24px;
  text-align: left;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.05em;
}

.modern-table td {
  padding: 16px 24px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.9rem;
  color: #334155;
}

.id-text {
  color: #94a3b8;
  font-family: monospace;
}

.main-title {
  font-weight: 700;
  color: #1e293b;
}

.author-tag {
  background: #eff6ff;
  color: #2563eb;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
}

/* 评分 Pill */
.rating-pill {
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.8rem;
}

.rating-pill.excellent {
  background: #dcfce7;
  color: #166534;
}

.rating-pill.good {
  background: #fef9c3;
  color: #854d0e;
}

.rating-pill.average {
  background: #f1f5f9;
  color: #475569;
}

/* 操作按钮 */
.row-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.btn-icon.edit:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.btn-icon.delete:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}

/* 分页 */
.pagination-container {
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.page-numbers {
  display: flex;
  gap: 5px;
}

.page-numbers span {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
}

.page-numbers span.active {
  background: #3b82f6;
  color: white;
}

.page-controls button {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  cursor: pointer;
}

/* 模态框美化 */
.modal-window {
  background: white;
  width: 600px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-head {
  padding: 20px 24px;
  background: #f8fafc;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-form {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.full-width {
  grid-column: span 2;
}

.modal-form label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 6px;
  color: #475569;
}

.modal-form input,
.modal-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-sizing: border-box;
}

.modal-foot {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-save {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.btn-cancel {
  background: #f1f5f9;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}

.card-shadow {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
}
</style>