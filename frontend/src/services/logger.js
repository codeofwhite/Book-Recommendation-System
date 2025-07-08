import { useUserStore } from '../stores/userStore';

// 开发模式标志：
// 设置为 null 表示仅在浏览器控制台打印日志，不向后端发请求。
// 若要连接后端，可设置为 import.meta.env.VITE_LOG_API_URL。
const LOG_API_ENDPOINT = null;

/**
 * 核心的日志跟踪函数。它负责构建日志对象，并根据 LOG_API_ENDPOINT 的设置
 * 将日志打印到控制台或发送到后端服务器。
 * @param {string} eventType - 事件的类型 (例如: 'page_view', 'button_click')。
 * @param {object} payload - 与事件相关的具体数据 (例如: { pageName: 'BookDetails' })。
 */
export async function trackEvent(eventType, payload = {}) {
  // 1. 从 Pinia store 中获取用户和会话信息
  const userStore = useUserStore();
  const userId = userStore.isLoggedIn ? userStore.user.id : null;
  const sessionId = userStore.sessionId;

  // 2. 构建标准化的日志数据结构
  const logData = {
    userId: userId,
    sessionId: sessionId,
    eventType: eventType,
    timestamp: new Date().toISOString(),
    pageUrl: window.location.href, // 记录事件发生的当前页面URL
    payload: payload,
  };

  // 3. 根据环境决定如何处理日志
  if (!LOG_API_ENDPOINT) {
    // “仅前端”的调试模式。使用折叠的日志组让控制台更整洁。
    console.groupCollapsed(`[EVENT LOG] => ${eventType}`);
    console.log('Timestamp:', new Date().toLocaleTimeString());
    console.log('Log Data:', logData);
    console.groupEnd();
    return; // 在此停止执行
  }

  // 生产环境或与后端连接的模式 (此部分当前未激活)
  try {
    // 当 LOG_API_ENDPOINT 设置后，这部分代码会执行
    await axios.post(LOG_API_ENDPOINT, logData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    // 可选: 在开发模式下打印成功信息以供确认
    if (import.meta.env.DEV) {
      console.log('Log successfully sent to backend:', logData);
    }
  } catch (error) {
    console.error('Failed to send log to backend:', error);
  }
}

// --- 以下是导出的、供组件使用的具体事件跟踪函数 ---

/**
 * 跟踪用户在书籍列表页点击了某本书的行为。
 * @param {string} bookId - 被点击书籍的ID。
 */
export const trackBookClick = (bookId) => {
  // 我们给这个事件一个更清晰的名称，以区别于书本内的点击
  trackEvent('click_book_in_list', { bookId: bookId });
};

/**
 * 跟踪页面浏览事件和停留时长。
 * 此函数被调用时，会一次性发送两个独立的日志事件：
 * 1. 'page_view': 记录一次页面访问，用于统计浏览次数 (PV)。
 * 2. 'page_view_duration': 记录本次访问的具体停留时长。
 * @param {string} pageName - 被浏览页面的名称 (例如: 'BookList', 'BookDetails')。
 * @param {number} dwellTimeInSeconds - 用户在该页面的总停留时长（单位：秒）。
 */
export const trackPageView = (pageName, dwellTimeInSeconds) => {
  // 事件1: 发送“浏览次数”事件 (Page View)
  trackEvent('page_view', { pageName: pageName });

  // 事件2: 只有在停留时长有效时，才发送“浏览时长”事件
  if (dwellTimeInSeconds > 0) {
    trackEvent('page_view_duration', {
      pageName: pageName,
      dwellTime: dwellTimeInSeconds,
    });
  }
};

/**
 * 跟踪页面内通用按钮的点击事件。
 * @param {string} buttonName - 被点击按钮的清晰、唯一的名称 (例如: 'LikeButton', 'ToggleDescription')。
 * @param {string} pageName - 按钮所在的页面名称。
 * @param {object} [context={}] - (可选) 与该次点击相关的上下文信息 (例如: { bookId: '123' })。
 */
export const trackButtonClick = (buttonName, pageName, context = {}) => {
  trackEvent('button_click', {
    buttonName: buttonName,
    pageName: pageName,
    ...context, // 将上下文信息（如 bookId）合并到 payload 中
  });
};