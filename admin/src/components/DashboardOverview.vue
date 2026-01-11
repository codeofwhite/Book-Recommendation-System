<template>
  <div class="dashboard-container">
    <header class="dashboard-welcome">
      <div class="welcome-text">
        <h2>控制面板概览</h2>
        <p>欢迎回来！这是系统当前的实时运行数据摘要。</p>
      </div>
    </header>

    <div class="stats-grid">
      <div class="stat-card blue">
        <div class="stat-content">
          <span class="label">图书总数</span>
          <h3 class="number">{{ totalBooks }}</h3>
          <span class="trend">馆藏资源总量</span>
        </div>
        <div class="stat-icon">📚</div>
      </div>

      <div class="stat-card purple">
        <div class="stat-content">
          <span class="label">平均评分</span>
          <h3 class="number">{{ averageRating }}</h3>
          <span class="trend">用户满意度反馈</span>
        </div>
        <div class="stat-icon">⭐</div>
      </div>

      <div class="stat-card green">
        <div class="stat-content">
          <span class="label">注册用户</span>
          <h3 class="number">{{ totalUsers }}</h3>
          <span class="trend">活跃读者群体</span>
        </div>
        <div class="stat-icon">👥</div>
      </div>

      <div class="stat-card orange">
        <div class="stat-content">
          <span class="label">评论总数</span>
          <h3 class="number">{{ totalReviews }}</h3>
          <span class="trend">社交互动数据</span>
        </div>
        <div class="stat-icon">💬</div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-wrapper card-shadow">
        <div class="chart-header">
          <h4>用户交互类型分布</h4>
          <span class="sub-title">实时统计各类操作频次</span>
        </div>
        <div class="chart-content">
          <v-chart class="chart" :option="eventTypeChartOptions" autoresize
            v-if="!loadingBehaviorLogs && userBehaviorLogs.length > 0" />
          <div v-else class="chart-placeholder">
            <span v-if="loadingBehaviorLogs">数据加载中...</span>
            <span v-else>暂无交互数据</span>
          </div>
        </div>
      </div>

      <div class="chart-wrapper card-shadow">
        <div class="chart-header">
          <h4>活跃趋势分析 (近7日)</h4>
          <span class="sub-title">用户每日访问与操作波动</span>
        </div>
        <div class="chart-content">
          <v-chart class="chart" :option="dailyActivityChartOptions" autoresize
            v-if="!loadingBehaviorLogs && userBehaviorLogs.length > 0" />
          <div v-else class="chart-placeholder">
            <span v-if="loadingBehaviorLogs">趋势计算中...</span>
            <span v-else>暂无趋势数据</span>
          </div>
        </div>
      </div>
    </div>

    <div class="bottom-section card-shadow">
      <div class="section-header">
        <h4><i class="icon">🕒</i> 最近系统日志</h4>
        <button class="view-all-btn">查看全部记录</button>
      </div>
      <div class="logs-table-wrapper">
        <table class="logs-table">
          <thead>
            <tr>
              <th>时间戳</th>
              <th>事件类型</th>
              <th>操作用户</th>
              <th>关联图书</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(log, index) in latestUserBehaviorLogs" :key="index">
              <td>{{ formatLogTime(log.timestamp) }}</td>
              <td><span class="badge" :class="log.eventType">{{ translateEvent(log.eventType) }}</span></td>
              <td>ID: {{ log.userId }}</td>
              <td>Item: {{ log.item_id }}</td>
              <td><span class="status-dot"></span> 成功</td>
            </tr>
            <tr v-if="latestUserBehaviorLogs.length === 0">
              <td colspan="5" class="empty-row">暂无最近活动记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
// 导入 ECharts 组件和核心模块
import VChart from 'vue-echarts'
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, LineChart, PieChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components';
import { graphic } from 'echarts/core';

// 注册 ECharts 必要的组件
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart, // 如果需要饼图也注册
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
]);

const allBooks = ref([])
const totalUsers = ref(0)
const totalReviews = ref(0)
const loading = ref(false)
const error = ref(null)

const userBehaviorLogs = ref([])
const totalUserBehaviorLogs = computed(() => userBehaviorLogs.value.length)
const loadingBehaviorLogs = ref(false)
const errorBehaviorLogs = ref(null)

const totalBooks = computed(() => allBooks.value.length)

const averageRating = computed(() => {
  if (allBooks.value.length === 0) return '0.0'
  const sum = allBooks.value.reduce((acc, book) => acc + (book.rating || 0), 0)
  return (sum / allBooks.value.length).toFixed(1)
})

// 计算属性：获取最新的5条用户行为日志
const latestUserBehaviorLogs = computed(() => {
  if (!userBehaviorLogs.value || userBehaviorLogs.value.length === 0) {
    return [];
  }
  // 创建一个副本以避免修改原始数组
  const sortedLogs = [...userBehaviorLogs.value].sort((a, b) => {
    return new Date(b.timestamp) - new Date(a.timestamp); // 按时间降序排序 (最新在前)
  });
  return sortedLogs.slice(0, 5); // 取前5条
});

// Fetch users from API
const fetchTotalUsers = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await axios.get('/service-a/api/users')
    totalUsers.value = response.data.total || 0
  } catch (err) {
    console.error('Error fetching total users:', err)
    error.value = err.response?.data?.error || 'Failed to fetch user statistics'
  } finally {
    loading.value = false
  }
}

const fetchBooks = async () => {
  try {
    const response = await axios.get('/service-b/api/books')
    allBooks.value = response.data
  } catch (error) {
    console.error('Error fetching books:', error)
  }
}

const fetchTotalReviews = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await axios.get('/service-c/api/admin/reviews?page=1&per_page=1');

    if (response.data && typeof response.data.total !== 'undefined') {
      totalReviews.value = response.data.total;
    } else {
      console.warn('Backend API /api/reviews did not return "total" field, or it was undefined.');
      totalReviews.value = 0;
    }
  } catch (err) {
    console.error('Error fetching total reviews:', err);
    error.value = err.response?.data?.error || 'Failed to fetch review statistics';
  } finally {
    loading.value = false;
  }
}

const fetchUserBehaviorLogs = async () => {
  loadingBehaviorLogs.value = true
  errorBehaviorLogs.value = null
  try {
    // 确保这里的 URL 与你的 Flask 后端地址一致
    const response = await axios.get('service-g/data/user_behavior_logs')

    if (response.data.status === 'success') {
      userBehaviorLogs.value = response.data.data
      console.log(`Fetched ${userBehaviorLogs.value.length} user behavior logs.`) // 调试信息
    } else if (response.data.status === 'warning') {
      console.warn('No user behavior logs found:', response.data.message)
      userBehaviorLogs.value = []
    } else {
      console.error('Backend error fetching user behavior logs:', response.data.message)
      errorBehaviorLogs.value = response.data.message || 'Unknown error from backend'
    }
  } catch (err) {
    console.error('Error fetching user behavior logs:', err)
    errorBehaviorLogs.value = err.response?.data?.message || 'Failed to fetch user behavior logs'
  } finally {
    loadingBehaviorLogs.value = false
  }
}

// 计算属性：事件类型分布图的 ECharts 配置
const eventTypeChartOptions = computed(() => {
  if (!userBehaviorLogs.value || userBehaviorLogs.value.length === 0) {
    return {};
  }

  const eventCounts = {};
  userBehaviorLogs.value.forEach(log => {
    eventCounts[log.eventType] = (eventCounts[log.eventType] || 0) + 1;
  });

  const categories = Object.keys(eventCounts);
  const seriesData = categories.map(cat => eventCounts[cat]);

  return {
    title: {
      text: 'Event Type Distribution',
      left: 'center',
      textStyle: {
        fontSize: 16,
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
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
        interval: 0,
        rotate: 30, // 旋转标签以防重叠
        color: '#555'
      },
      axisLine: {
        lineStyle: {
          color: '#ccc'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: 'Number of Events',
      nameTextStyle: {
        color: '#555'
      },
      axisLabel: {
        color: '#555'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      }
    },
    series: [{
      name: 'Event Count',
      type: 'bar',
      data: seriesData,
      itemStyle: {
        // 将 echarts.graphic.LinearGradient 替换为 graphic.LinearGradient
        color: new graphic.LinearGradient(
          0, 0, 0, 1,
          [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ]
        ),
        borderRadius: [5, 5, 0, 0] // 柱子顶部圆角
      },
      emphasis: {
        itemStyle: {
          color: '#3BA272' // 鼠标悬停颜色
        }
      }
    }]
  };
});


// 计算属性：每日活动趋势图的 ECharts 配置
const dailyActivityChartOptions = computed(() => {
  if (!userBehaviorLogs.value || userBehaviorLogs.value.length === 0) {
    return {};
  }

  const dailyCounts = {};
  userBehaviorLogs.value.forEach(log => {
    // 解析时间戳并获取日期 (YYYY-MM-DD)
    const date = new Date(log.timestamp).toISOString().split('T')[0];
    dailyCounts[date] = (dailyCounts[date] || 0) + 1;
  });

  // 对日期进行排序
  const sortedDates = Object.keys(dailyCounts).sort((a, b) => new Date(a) - new Date(b));
  const seriesData = sortedDates.map(date => dailyCounts[date]);

  return {
    title: {
      text: 'Daily User Activity Trend',
      left: 'center',
      textStyle: {
        fontSize: 16,
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>Events: {c}', // 显示日期和事件数量
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: sortedDates,
      axisLabel: {
        rotate: 45, // 旋转日期标签以防重叠
        color: '#555'
      },
      axisLine: {
        lineStyle: {
          color: '#ccc'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: 'Number of Events',
      nameTextStyle: {
        color: '#555'
      },
      axisLabel: {
        color: '#555'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      }
    },
    series: [
      {
        name: 'Daily Events',
        type: 'line',
        stack: 'total', // 如果有多个系列可以堆叠
        areaStyle: {
          // 将 echarts.graphic.LinearGradient 替换为 graphic.LinearGradient
          color: new graphic.LinearGradient(0, 0, 0, 1, [{
            offset: 0,
            color: 'rgba(145, 204, 117, 0.8)' // 起始颜色
          }, {
            offset: 1,
            color: 'rgba(145, 204, 117, 0)' // 结束颜色
          }])
        }, // 填充面积
        emphasis: {
          focus: 'series'
        },
        data: seriesData,
        itemStyle: {
          color: '#91CC75' // 折线颜色
        },
        lineStyle: {
          width: 3 // 折线宽度
        },
        smooth: true // 平滑曲线
      }
    ]
  };
});

const translateEvent = (event) => {
  const map = {
    'click': '点击详情',
    'view': '页面浏览',
    'rate': '评分行为',
    'comment': '发表评论',
    'search': '关键词搜索'
  }
  return map[event] || event
}

const formatLogTime = (ts) => {
  const d = new Date(ts)
  return `${d.getMonth() + 1}-${d.getDate()} ${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
}

onMounted(() => {
  fetchBooks()
  fetchTotalUsers()
  fetchTotalReviews()
  fetchUserBehaviorLogs()
})
</script>

<style scoped>
.dashboard-container {
  padding: 10px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-welcome {
  margin-bottom: 30px;
}

.dashboard-welcome h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1c23;
  margin: 0;
}

.dashboard-welcome p {
  color: #718096;
  margin-top: 5px;
}

/* 指标卡片重构 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  padding: 24px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card.blue {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.purple {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.green {
  background: linear-gradient(135deg, #b1f4cf 0%, #53a7f0 100%);
}

/* 也可以用蓝绿 */
.stat-card.orange {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-content .label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.stat-content .number {
  font-size: 2rem;
  margin: 8px 0;
  font-weight: 700;
}

.stat-content .trend {
  font-size: 0.75rem;
  opacity: 0.8;
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.3;
}

/* 图表区 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.chart-wrapper {
  background: white;
  padding: 20px;
  border-radius: 12px;
  min-height: 400px;
}

.chart-header {
  margin-bottom: 20px;
}

.chart-header h4 {
  margin: 0;
  color: #2d3748;
  font-size: 1.1rem;
}

.chart-header .sub-title {
  font-size: 0.8rem;
  color: #a0aec0;
}

.chart-content {
  height: 320px;
  width: 100%;
}

/* 日志表格 */
.bottom-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.view-all-btn {
  padding: 6px 16px;
  font-size: 0.8rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th {
  text-align: left;
  padding: 12px;
  background: #f8fafc;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 600;
}

.logs-table td {
  padding: 15px 12px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.9rem;
  color: #334155;
}

/* 徽章样式 */
.badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge.click {
  background: #ebf8ff;
  color: #3182ce;
}

.badge.rate {
  background: #f0fff4;
  color: #38a169;
}

.card-shadow {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #48bb78;
  border-radius: 50%;
  margin-right: 5px;
}
</style>