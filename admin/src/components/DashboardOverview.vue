<template>
  <div class="admin-panel-card">
    <h2>Dashboard Overview</h2>
    <p>Welcome to your Book Management Dashboard. Here you can see a quick summary of your data.</p>

    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-icon">📚</div>
        <h3>Total Books</h3>
        <p class="stat-number">{{ totalBooks }}</p>
      </div>
      <div class="stat-item">
        <div class="stat-icon">⭐</div>
        <h3>Avg. Rating</h3>
        <p class="stat-number">{{ averageRating }}</p>
      </div>
      <div class="stat-item">
        <div class="stat-icon">👥</div>
        <h3>Total Users</h3>
        <p class="stat-number">{{ totalUsers }}</p>
      </div>
      <div class="stat-item">
        <div class="stat-icon">💬</div>
        <h3>Total Reviews</h3>
        <p class="stat-number">{{ totalReviews }}</p>
      </div>
      <div class="stat-item">
        <div class="stat-icon">📈</div>
        <h3>Total Behavior Logs</h3>
        <p class="stat-number">{{ totalUserBehaviorLogs }}</p>
      </div>
    </div>

    <hr class="section-divider">

    <div class="charts-section">
      <h3>User Behavior Insights</h3>

      <div class="chart-container">
        <h4>Event Type Distribution</h4>
        <v-chart class="chart" :option="eventTypeChartOptions" autoresize
          v-if="!loadingBehaviorLogs && userBehaviorLogs.length > 0" />
        <p v-else-if="loadingBehaviorLogs" class="loading-message">Loading event type chart data...</p>
        <p v-else-if="errorBehaviorLogs" class="error-message">Error loading chart: {{ errorBehaviorLogs }}</p>
        <p v-else class="no-data-message">No data available for event type distribution.</p>
      </div>

      <div class="chart-container">
        <h4>Daily Activity Trend</h4>
        <v-chart class="chart" :option="dailyActivityChartOptions" autoresize
          v-if="!loadingBehaviorLogs && userBehaviorLogs.length > 0" />
        <p v-else-if="loadingBehaviorLogs" class="loading-message">Loading daily activity chart data...</p>
        <p v-else-if="errorBehaviorLogs" class="error-message">Error loading chart: {{ errorBehaviorLogs }}</p>
        <p v-else class="no-data-message">No data available for daily activity trend.</p>
      </div>
    </div>

    <hr class="section-divider">

    <div class="recent-logs-section">
      <h3>Recent User Behavior Logs (Last 5)</h3>
      <div v-if="latestUserBehaviorLogs.length > 0">
        <ul>
          <li v-for="(log, index) in latestUserBehaviorLogs" :key="index">
            <span class="log-timestamp">{{ log.timestamp }}:</span>
            <span class="log-event">{{ log.event_type }}</span>
            by user <span class="log-user">{{ log.user_id }}</span>
            on book <span class="log-item">{{ log.item_id }}</span>
          </li>
        </ul>
      </div>
      <div v-else-if="loadingBehaviorLogs">
        <p class="loading-message">Loading recent user behavior logs...</p>
      </div>
      <div v-else-if="errorBehaviorLogs">
        <p class="error-message">Error: {{ errorBehaviorLogs }}</p>
      </div>
      <div v-else>
        <p class="no-data-message">No user behavior logs found.</p>
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
import { graphic } from 'echarts/core'; // <--- 新增这行，导入 graphic 对象

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
    const response = await axios.get('/service-c/api/reviews?page=1&per_page=1');

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

// -----------------------------------------------------------
// 新增可视化逻辑
// -----------------------------------------------------------

// ... (其他代码)

// 计算属性：事件类型分布图的 ECharts 配置
const eventTypeChartOptions = computed(() => {
  if (!userBehaviorLogs.value || userBehaviorLogs.value.length === 0) {
    return {};
  }

  const eventCounts = {};
  userBehaviorLogs.value.forEach(log => {
    eventCounts[log.event_type] = (eventCounts[log.event_type] || 0) + 1;
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



onMounted(() => {
  fetchBooks()
  fetchTotalUsers()
  fetchTotalReviews()
  fetchUserBehaviorLogs()
})
</script>

<style scoped>
/* 整个卡片容器 */
.admin-panel-card {
  background-color: #ffffff;
  padding: 30px;
  /* 增加内边距 */
  border-radius: 12px;
  /* 更大的圆角 */
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  /* 更明显的阴影 */
  margin-bottom: 30px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  /* 更改字体 */
  color: #333;
}

h2 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.8em;
  text-align: center;
}

p {
  color: #7f8c8d;
  line-height: 1.8;
  margin-bottom: 25px;
  text-align: center;
}

/* 指标网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(50px, 1fr));
  /* 调整最小宽度 */
  gap: 25px;
  /* 增加间距 */
  margin-top: 30px;
  margin-bottom: 30px;
}

.stat-item {
  background: linear-gradient(135deg, #f0f4f8, #e6edf3);
  /* 渐变背景 */
  padding: 20px;
  /* 增加内边距 */
  border-radius: 10px;
  /* 更大的圆角 */
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  /* 柔和阴影 */
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  /* 过渡动画 */
}

.stat-item:hover {
  transform: translateY(-5px);
  /* 悬停上浮效果 */
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  /* 悬停阴影 */
}

.stat-icon {
  font-size: 3em;
  /* 更大的图标 */
  margin-bottom: 15px;
  color: #3498db;
  /* 图标颜色 */
}

.stat-item h3 {
  color: #34495e;
  margin-bottom: 8px;
  font-size: 1.3em;
  font-weight: 600;
}

.stat-number {
  font-size: 2.2em;
  /* 更大的数字 */
  font-weight: 700;
  color: #2980b9;
  /* 数字颜色 */
  display: block;
  /* 确保独占一行 */
}

/* 分隔线 */
.section-divider {
  border: none;
  border-top: 1px dashed #e0e0e0;
  /* 虚线分隔 */
  margin: 40px 0;
  /* 增加上下间距 */
}

/* 图表区域 */
.charts-section {
  margin-top: 20px;
  /* 与分隔线间距 */
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
  /* 调整列宽，适应更多内容 */
  gap: 30px;
  /* 增加图表之间的间距 */
}

.charts-section h3 {
  grid-column: 1 / -1;
  /* 标题占据所有列 */
  text-align: center;
  color: #2c3e50;
  font-size: 1.6em;
  margin-bottom: 25px;
}

.chart-container {
  background-color: #ffffff;
  /* 图表背景设置为白色，与卡片背景一致，但有更强的阴影 */
  padding: 25px;
  /* 增加内边距 */
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
  /* 强阴影 */
  min-height: 480px;
  /* 确保图表容器有足够的最小高度 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: box-shadow 0.3s ease;
}

.chart-container:hover {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  /* 悬停时更强的阴影 */
}

.chart-container h4 {
  margin-top: 0;
  color: #34495e;
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.4em;
}

.chart {
  height: 380px;
  /* 图表实际渲染的高度，根据容器高度调整 */
  width: 100%;
}

/* 消息样式 */
.loading-message,
.error-message,
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
}

/* 近期日志样式 */
.recent-logs-section {
  margin-top: 40px;
  padding: 25px;
  background-color: #fbfcfe;
  /* 浅色背景 */
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.recent-logs-section h3 {
  color: #2c3e50;
  font-size: 1.6em;
  margin-bottom: 20px;
  text-align: center;
}

.recent-logs-section ul {
  list-style: none;
  /* 移除默认列表点 */
  padding: 0;
  margin: 0;
}

.recent-logs-section li {
  background-color: #ffffff;
  border-left: 5px solid #3498db;
  /* 左侧强调线 */
  padding: 12px 15px;
  margin-bottom: 10px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  font-size: 0.95em;
  line-height: 1.4;
}

.log-timestamp {
  font-weight: bold;
  color: #555;
}

.log-event {
  font-weight: 600;
  color: #2ecc71;
  /* 事件类型颜色 */
}

.log-user,
.log-item {
  color: #3498db;
  /* 用户ID和项目ID颜色 */
  font-weight: 500;
}
</style>