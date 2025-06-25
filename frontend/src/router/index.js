// frontend/src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import AuthView from '../views/AuthView.vue';
import BookList from '../views/BookList.vue'
import AboutView from '../views/AboutView.vue'
import BookDetails from '../components/BookDetails.vue';

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/books",
    name: "books",
    component: BookList,
  },
  {
    path: "/about",
    name: "about",
    component: AboutView,
  },
  {
    path: '/books/:bookId',
    name: 'BookDetails',
    component: BookDetails,
    props: true
  },
  {
    path: '/auth', // <-- Add auth route
    name: 'auth',
    component: AuthView
  },

];

const router = createRouter({
  // 使用 Vite 的环境变量访问方式
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// 添加路由导航守卫
router.afterEach((to) => {
  if (window.dataLayer) {
    window.dataLayer.push({
      event: 'pageview',  // 自定义事件名称（需与GTM触发器匹配）
      pagePath: to.fullPath,
      pageTitle: to.meta.title || document.title,
    });
  }
});

export default router;
