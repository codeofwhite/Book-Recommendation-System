// frontend/src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import AuthView from '../views/AuthView.vue';
import BookList from '../views/BookList.vue'
import AboutView from '../views/AboutView.vue'
import BookDetails from '../components/BookDetails.vue';
import UserView from '../views/UserView.vue'; // 新创建的用户主页组件
import UserOnboarding from '../components/UserOnboarding.vue'; // 问卷页面组件
import BookOfTheDay from "../views/BookOfTheDay.vue";

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
    path: '/auth',
    name: 'auth', // 认证页的命名路由
    component: AuthView
  },
  {
    path: '/userview',
    name: 'UserView', // 用户主页的命名路由 (大写U, 大写V)
    component: UserView,
    meta: { requiresAuth: true }
  },
  {
    path: '/user-onboarding',
    name: 'user-onboarding', // 问卷页的命名路由 (小写)
    component: UserOnboarding,
    meta: { requiresAuth: true }
  },
  {
    path: "/book_of_the_day",
    name: "book_of_the_day",
    component: BookOfTheDay,
    props: true
  },
  {
    path: '/skim', // <-- Add auth route
    name: 'skim',
    component: Skim
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// 全局导航守卫：检查用户是否登录以及是否完成问卷
router.beforeEach((to, from, next) => {
  const storedUserData = localStorage.getItem('user_data');
  let loggedInUser = null;
  if (storedUserData) {
    try {
      loggedInUser = JSON.parse(storedUserData);
    } catch (e) {
      console.error("Router Guard: Error parsing user_data from localStorage:", e);
      // 如果数据损坏，尝试清除它，避免无限循环
      localStorage.removeItem('user_data');
    }
  }

  // isAuthenticated 只有在 user_data 存在且包含 auth_token 时才为 true
  const isAuthenticated = loggedInUser && loggedInUser.auth_token;

  // --- 增强调试日志：请在浏览器控制台查看这些输出 ---
  console.group(`Router Guard: Navigating ${from.path} -> ${to.path} (Name: ${to.name})`);
  console.log(`  localStorage 'user_data':`, storedUserData);
  console.log(`  Parsed loggedInUser:`, loggedInUser);
  console.log(`  isAuthenticated: ${isAuthenticated}`);
  console.log(`  to.meta.requiresAuth: ${!!to.meta.requiresAuth}`);
  console.log(`  is_profile_complete: ${loggedInUser ? loggedInUser.is_profile_complete : 'N/A'}`);
  // --- 调试日志结束 ---

  if (to.meta.requiresAuth && !isAuthenticated) {
    // 1. 如果目标路由需要认证但用户未登录，则重定向到登录页
    console.log("  Action: Redirecting to 'auth' (Requires auth, but not authenticated)");
    next({ name: 'auth' });
  } else if (isAuthenticated && loggedInUser && !loggedInUser.is_profile_complete && to.name !== 'user-onboarding') {
    // 2. 如果用户已登录但资料不完整，且当前不在问卷页，则强制跳转到问卷页
    console.log("  Action: Redirecting to 'user-onboarding' (Authenticated, profile incomplete, not on onboarding page)");
    next({ name: 'user-onboarding' });
  } else if (isAuthenticated && loggedInUser && loggedInUser.is_profile_complete && to.name === 'user-onboarding') {
    // 3. 如果用户已登录且资料完整，但尝试访问问卷页，则重定向到用户主页
    console.log("  Action: Redirecting to 'UserView' (Authenticated, profile complete, on onboarding page)");
    next({ name: 'UserView' });
  } else if (isAuthenticated && (to.name === 'auth')) {
    // 4. 如果用户已登录且尝试访问登录页或根路径，则重定向到用户主页
    console.log("  Action: Redirecting to 'UserView' (Authenticated, on auth/root page)");
    next({ name: 'UserView' });
  } else {
    // 5. 其他情况正常导航
    console.log("  Action: Allowing navigation");
    next();
  }
  console.groupEnd(); // 结束日志组
});

export default router;