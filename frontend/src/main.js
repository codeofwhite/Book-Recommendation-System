// src/main.js
import { createApp } from "vue";
import { createPinia } from 'pinia' // 导入 Pinia
import App from "./App.vue";
import router from "./router";


const app = createApp(App);
app.use(router);

// 创建 Pinia 实例并让整个应用使用它
const pinia = createPinia()
app.use(pinia)

// 辅助函数：等待 gtag 加载
function waitForGtag(callback, retries = 10, delay = 100) {
  if (typeof window.gtag === 'function') {
    callback();
  } else if (retries > 0) {
    setTimeout(() => {
      waitForGtag(callback, retries - 1, delay);
    }, delay);
  } else {
    console.warn('gtag function not found after multiple retries. GA4 page_view might not be sent.');
  }
}

// 在路由导航守卫中发送 page_view 事件
router.afterEach((to, from) => {
  waitForGtag(() => {
    window.gtag('event', 'page_view', {
      page_path: to.fullPath,
      page_location: window.location.origin + to.fullPath,
      page_title: document.title
    });
    console.log('GA4 page_view sent for:', to.fullPath);
  });
});

app.mount("#app");