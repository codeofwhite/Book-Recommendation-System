import { useUserStore } from '../stores/userStore';

// 注意：我们暂时让 LOG_API_ENDPOINT 为空，来激活“仅前端输出”模式
const LOG_API_ENDPOINT = null; // import.meta.env.VITE_LOG_API_URL;

/**
 * 格式化并处理用户行为日志。
 * 如果 LOG_API_ENDPOINT 未配置，日志将直接打印到浏览器控制台，而不会发送到后端。
 * @param {string} eventType - 事件类型 (例如: 'click_book', 'view_detail', 'search')
 * @param {object} payload - 与事件相关的具体数据 (例如: { bookId: '123' })
 */
export async function trackEvent(eventType, payload = {}) {
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

  // 3. 核心修改：判断是发送到后端还是仅在前端打印
  if (!LOG_API_ENDPOINT) {
    // 如果 API 地址未配置，则进入“前端调试模式”
    console.groupCollapsed(`[EVENT LOG] => ${eventType}`); // 使用可折叠的组，让控制台更整洁
    console.log('Timestamp:', new Date().toLocaleTimeString());
    console.log('Log Data:', logData); // 打印完整的日志对象
    console.groupEnd();
    return; // 直接返回，不执行后续的 axios 调用
  }

  // --- 以下是原始的后端发送逻辑，在调试模式下不会被执行 ---
  try {
    await axios.post(LOG_API_ENDPOINT, logData, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    // 在开发模式下可以打印日志，方便调试
    if (import.meta.env.DEV) {
      console.log('Log sent to backend:', logData);
    }
  } catch (error) {
    console.error('Failed to send log:', error);
  }
}

// 导出的具体埋点函数保持不变，组件中的调用也无需任何改动
export const trackBookClick = (bookId) => {
  trackEvent('click_book', { bookId: bookId });
};

export const trackBookView = (bookId, dwellTime) => {
  trackEvent('view_book_detail', { bookId: bookId, dwellTime: dwellTime });
};

export const trackSearch = (query) => {
  trackEvent('search', { query: query });
};