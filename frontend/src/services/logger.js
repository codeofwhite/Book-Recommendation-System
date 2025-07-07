<<<<<<< HEAD

import { useUserStore } from '../stores/userStore';

const LOG_API_ENDPOINT = null; // Still in frontend-only debug mode

/**
 * Formats and processes user behavior logs.
 * In debug mode (LOG_API_ENDPOINT is null), it prints to the console.
 * @param {string} eventType - The type of event.
 * @param {object} payload - Event-specific data.
 */
export async function trackEvent(eventType, payload = {}) {
  const userStore = useUserStore();
  const userId = userStore.isLoggedIn ? userStore.user.id : null;
  const sessionId = userStore.sessionId;
=======
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
>>>>>>> zhj

  const logData = {
    userId: userId,
    sessionId: sessionId,
    eventType: eventType,
    timestamp: new Date().toISOString(),
<<<<<<< HEAD
    pageUrl: window.location.href,
    payload: payload
  };

=======
    // **【优化】** 优先使用传入的URL，如果未提供，再使用全局的 window.location.href
    pageUrl: customPageUrl || window.location.href,
    payload: payload,
  };

  // 3. 根据环境决定如何处理日志
>>>>>>> zhj
  if (!LOG_API_ENDPOINT) {
    console.groupCollapsed(`[EVENT LOG] => ${eventType}`);
    console.log('Timestamp:', new Date().toLocaleTimeString());
    console.log('Log Data:', logData);
    console.groupEnd();
    return;
<<<<<<< HEAD
=======
  }

  try {
    await axios.post(LOG_API_ENDPOINT, logData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (import.meta.env.DEV) {
      console.log('Log successfully sent to backend:', logData);
    }
  } catch (error) {
    console.error('Failed to send log to backend:', error);
>>>>>>> zhj
  }
  
  // Backend sending logic remains here for when we re-enable it
}

<<<<<<< HEAD
/**
 * Tracks a user clicking on a book.
 * @param {string} bookId - The ID of the book that was clicked.
 */
export const trackBookClick = (bookId) => {
  trackEvent('click_book', { bookId });
};

/**
 * NEW: Tracks how long a user viewed a book's details page.
 * @param {string} bookId - The ID of the book being viewed.
 * @param {number} dwellTimeInSeconds - The total time in seconds the user spent on the page.
 */
export const trackBookView = (bookId, dwellTimeInSeconds) => {
  trackEvent('view_book_detail', { 
    bookId: bookId, 
    dwellTime: dwellTimeInSeconds 
  });
};
=======
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
>>>>>>> zhj
