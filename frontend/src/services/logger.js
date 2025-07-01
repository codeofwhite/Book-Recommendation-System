import axios from 'axios';
// 假设你使用 Pinia 或 Vuex 来管理用户状态
import { useUserStore } from '../stores/userStore'; 
useUserStore
// 从环境变量中获取后端日志网关的 URL
const LOG_API_ENDPOINT = import.meta.env.VITE_LOG_API_URL;

/**
 * 格式化并发送用户行为日志到后端网关
 * @param {string} eventType - 事件类型 (例如: 'click_book', 'view_detail', 'search')
 * @param {object} payload - 与事件相关的具体数据 (例如: { bookId: '123', dwellTime: 3500 })
 */
export async function trackEvent(eventType, payload = {}) {
  // 如果 API 地址未配置，则在开发环境下警告，并直接返回
  if (!LOG_API_ENDPOINT) {
    console.warn('VITE_LOG_API_URL is not configured. Logging is disabled.');
    return;
  }
  
  // 1. 获取用户状态 (例如从 Pinia Store)
  const userStore = useUserStore();
  const userId = userStore.isLoggedIn ? userStore.user.id : null; // 获取用户ID，如果未登录则为 null
  const sessionId = userStore.sessionId; // 也可以跟踪会话ID

  // 2. 构建标准化的日志数据结构
  const logData = {
    userId: userId,
    sessionId: sessionId,
    eventType: eventType,
    timestamp: new Date().toISOString(), // 使用 ISO 8601 标准时间格式
    pageUrl: window.location.href,     // 当前页面 URL
    payload: payload                   // 具体的事件数据
  };

  // 3. 异步发送日志到后端
  try {
    // 使用 axios.post 发送数据。我们不需要关心它的返回结果，
    // 而且错误处理也应避免影响用户主流程。
    await axios.post(LOG_API_ENDPOINT, logData, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    // 在开发模式下可以打印日志，方便调试
    if (import.meta.env.DEV) {
      console.log('Log sent:', logData);
    }
  } catch (error) {
    // 日志发送失败不应阻塞应用或向用户报错，仅在控制台记录
    console.error('Failed to send log:', error);
  }
}

// 你还可以导出更具体的埋点函数，来简化组件中的调用
export const trackBookClick = (bookId) => {
  trackEvent('click_book', { bookId: bookId });
};

export const trackBookView = (bookId, dwellTime) => {
  trackEvent('view_book_detail', { bookId: bookId, dwellTime: dwellTime });
};

export const trackSearch = (query) => {
  trackEvent('search', { query: query });
};