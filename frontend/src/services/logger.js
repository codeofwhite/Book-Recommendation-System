
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

  const logData = {
    userId: userId,
    sessionId: sessionId,
    eventType: eventType,
    timestamp: new Date().toISOString(),
    pageUrl: window.location.href,
    payload: payload
  };

  if (!LOG_API_ENDPOINT) {
    console.groupCollapsed(`[EVENT LOG] => ${eventType}`);
    console.log('Timestamp:', new Date().toLocaleTimeString());
    console.log('Log Data:', logData);
    console.groupEnd();
    return;
  }
  
  // Backend sending logic remains here for when we re-enable it
}

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
