// frontend/src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import AuthView from '../views/AuthView.vue';
import BookList from '../views/BookList.vue'
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

export default router;
