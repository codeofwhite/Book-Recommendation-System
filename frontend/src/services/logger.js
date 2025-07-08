import { useUserStore } from '../stores/userStore';
import axios from 'axios';

const LOG_API_ENDPOINT = import.meta.env.VITE_LOG_API_URL || '/service-e/api/log';

/**
 * 核心的日志跟踪函数。它负责构建日志对象，并根据 LOG_API_ENDPOINT 的设置
 * 将日志打印到控制台或发送到后端服务器。
 * @param {string} eventType - 事件的类型 (例如: 'page_view', 'button_click')。
 * @param {object} payload - 与事件相关的具体数据 (例如: { pageName: 'BookDetails' })。
 * @param {string | null} customPageUrl - (可选) 显式指定的页面URL，优先于 window.location.href。
 */
export async function trackEvent(eventType, payload = {}, customPageUrl = null) {
  // 1. 从 Pinia store 中获取用户和会话信息
  const userStore = useUserStore();
  console.log('userStore.isLoggedIn:', userStore.isLoggedIn);
  console.log('userStore.user:', userStore.user);
  const userId = userStore.isLoggedIn ? userStore.user.user_id : null; // <--- 保持这里不变，但现在会正确获取到值
  const sessionId = userStore.sessionId; // <--- 确保 sessionId 能正确获取

  // 2. 构建标准化的日志数据结构
  const logData = {
    userId: userId,
    sessionId: sessionId,
    eventType: eventType,
    timestamp: new Date().toISOString(),
    // **【优化】** 优先使用传入的URL，如果未提供，再使用全局的 window.location.href
    pageUrl: customPageUrl || window.location.href,
    payload: payload,
  };

  // 3. 根据环境决定如何处理日志
  if (!LOG_API_ENDPOINT) {
    console.groupCollapsed(`[EVENT LOG] => ${eventType}`);
    console.log('Timestamp:', new Date().toLocaleTimeString());
    console.log('Log Data:', logData);
    console.groupEnd();
    return;
  }

  try {
    await axios.post(LOG_API_ENDPOINT, logData, {
      headers: {
        'Content-Type': 'application/json',
      },
        'Content-Type': 'application/json',
      },
    });
    if (import.meta.env.DEV) {
      console.log('Log successfully sent to backend:', logData);
      console.log('Log successfully sent to backend:', logData);
    }
  } catch (error) {
    console.error('Failed to send log to backend:', error);
    console.error('Failed to send log to backend:', error);
  }
}

// --- 以下是导出的、供组件使用的具体事件跟踪函数 ---

export const trackBookClick = (bookId) => {
  trackEvent('click_book_in_list', { bookId: bookId });
};

/**
 * 跟踪页面浏览事件和停留时长。
 * @param {string} pageName - 被浏览页面的名称 (例如: 'BookList', 'BookDetails')。
 * @param {number} dwellTimeInSeconds - 用户在该页面的总停留时长（单位：秒）。
 * @param {string} pageUrl - 【新增】事件发生时页面的确切URL。
 */
export const trackPageView = (pageName, dwellTimeInSeconds, pageUrl) => {
  // 事件1: 发送“浏览次数”事件 (Page View)
  trackEvent('page_view', { pageName: pageName }, pageUrl);

  // 事件2: 只有在停留时长有效时，才发送“浏览时长”事件
  if (dwellTimeInSeconds > 0) {
    trackEvent('page_view_duration', {
      pageName: pageName,
      dwellTime: dwellTimeInSeconds,
    }, pageUrl);
  }
};

export const trackButtonClick = (buttonName, pageName, context = {}) => {
  trackEvent('button_click', {
    buttonName: buttonName,
    pageName: pageName,
    ...context,
  });
};