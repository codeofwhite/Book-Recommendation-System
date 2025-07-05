// frontend/src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import AuthView from '../views/AuthView.vue';
import BookList from '../views/BookList.vue'
import AboutView from '../views/AboutView.vue'
import BookDetails from '../components/BookDetails.vue';
import UserView from '../views/UserView.vue'; // 新创建的用户主页组件
import save from '../views/save.vue'; // 假设这是保存用户信息的组件
import Skim from '../views/Skim.vue'; // 假设这是 Skim 组件

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
    component: AuthView,
  },
  {
    path: '/userview',
    name: 'UserView',
    component: save,
    meta: { requiresAuth: true } // 添加元信息，表示此路由需要认证
  },
  {
    path: '/skim', // <-- Add auth route
    name: 'skim',
    component: Skim
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
