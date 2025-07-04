// src/services/analytics.js

// 1. 【确保】只在文件顶部导入一次 gtagEvent
import { event as gtagEvent } from 'vue-gtag-next';

// 2. 定义所有需要使用 gtagEvent 的函数

/**
 * 跟踪用户点击某本书籍。
 * @param {object} book - 被点击的书籍对象。
 */
export const trackBookClick = (book) => {
    gtagEvent('select_content', {
        content_type: 'book',
        item_id: book.bookId,
    });
    console.log(`GA Event: select_content for bookId: ${book.bookId}`);
}

/**
 * 跟踪用户的搜索行为。
 * @param {string} term - 用户输入的搜索关键词。
 */
export const trackSearch = (term) => {
    if (!term || term.trim() === '') return;

    gtagEvent('search', {
        search_term: term.trim()
    });

    console.log(`GA Event: search, search_term: "${term.trim()}"`);
};

// ... 您未来可以继续在这里添加更多使用 gtagEvent 的函数 ...
// export const someOtherFunction = () => {
//   gtagEvent(...);
// };