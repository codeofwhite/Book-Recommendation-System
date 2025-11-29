// frontend/src/router/index.js

import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import AuthView from '../views/AuthView.vue';
import BookList from '../views/BookList.vue'
import AboutView from '../views/AboutView.vue'
import BookDetails from '../components/BookDetails.vue';
import UserView from '../views/UserView.vue'; // 新创建的用户主页组件
import BookOfTheDay from "../views/BookOfTheDay.vue";
import EpubReader from "../components/EpubReader.vue";
import UserOnboarding from '../components/UserOnboarding.vue'; // 问卷页面组件

// 【新增】导入活动相关的页面组件
import ActivitiesPage from '../views/ActivitiesPage.vue';
import ActivityDetails from '../views/ActivityDetails.vue';


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
    path: "/book_of_the_day",
    name: "book_of_the_day",
    component: BookOfTheDay,
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
  // 注意：这个 book_of_the_day 路由重复了，建议删除上面一个
  // {
  //   path: "/book_of_the_day",
  //   name: "book_of_the_day",
  //   component: BookOfTheDay,
  //   props: true
  // },
  {
    path: '/read/:bookId',
    name: 'EpubReader',
    component: EpubReader
  },
  // --- 【新增】活动相关路由 ---
  {
    path: '/activities',
    name: 'activities', // 活动列表页
    component: ActivitiesPage,
  },
  {
    path: '/activities/:id',
    name: 'activity-details', // 单个活动详情页
    component: ActivityDetails,
    props: true // 将路由参数 :id 作为 prop 传递给组件
  },
  // --- 新增结束 ---
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (to.path.startsWith('/read/')) {
      return { top: 110 }; // 匹配 /read/xxx 的所有路径
    }
    // 增加对活动详情页的滚动行为控制，确保每次进入页面都在顶部
    if (to.name === 'activity-details') {
      return { top: 0 };
    }
    return savedPosition || { top: 0 }; // 其他情况保持默认
  },
});

// 全局导航守卫 (保持不变，已包含在你提供的代码中)
router.beforeEach((to, from, next) => {
  const storedUserData = localStorage.getItem('user_data');
  let loggedInUser = null;
  if (storedUserData) {
    try {
      loggedInUser = JSON.parse(storedUserData);
    } catch (e) {
      console.error("Router Guard: Error parsing user_data from localStorage:", e);
      localStorage.removeItem('user_data');
    }
  }

  const isAuthenticated = loggedInUser && loggedInUser.auth_token;

  console.group(`Router Guard: Navigating ${from.path} -> ${to.path} (Name: ${to.name})`);
  console.log(`  localStorage 'user_data':`, storedUserData);
  console.log(`  Parsed loggedInUser:`, loggedInUser);
  console.log(`  isAuthenticated: ${isAuthenticated}`);
  console.log(`  to.meta.requiresAuth: ${!!to.meta.requiresAuth}`);
  console.log(`  is_profile_complete: ${loggedInUser ? loggedInUser.is_profile_complete : 'N/A'}`);

  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log("  Action: Redirecting to 'auth' (Requires auth, but not authenticated)");
    next({ name: 'auth' });
  } else if (isAuthenticated && loggedInUser && !loggedInUser.is_profile_complete && to.name !== 'user-onboarding') {
    console.log("  Action: Redirecting to 'user-onboarding' (Authenticated, profile incomplete, not on onboarding page)");
    next({ name: 'user-onboarding' });
  } else if (isAuthenticated && loggedInUser && loggedInUser.is_profile_complete && to.name === 'user-onboarding') {
    console.log("  Action: Redirecting to 'UserView' (Authenticated, profile complete, on onboarding page)");
    next({ name: 'UserView' });
  } else if (isAuthenticated && (to.name === 'auth')) {
    console.log("  Action: Redirecting to 'UserView' (Authenticated, on auth/root page)");
    next({ name: 'UserView' });
  } else {
    console.log("  Action: Allowing navigation");
    next();
  }
  console.groupEnd();
});

export default router;