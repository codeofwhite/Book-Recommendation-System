import { createRouter, createWebHistory } from "vue-router"

import DashboardOverview from "../components/DashboardOverview.vue"
import ManageBooks from "../components/ManageBooks.vue"
import AddBook from "../components/AddBook.vue"
import ManageReviews from "../components/ManageReviews.vue"
import ManageUsers from "../components/ManageUsers.vue"
import AdminAuth from "../components/AdminAuth.vue"

const routes = [
  {
    path: "/login",
    component: AdminAuth,
    name: "Login",
    meta: { requiresGuest: true }, 
  },
  {
    path: "/dashboard",
    component: DashboardOverview,
    name: "Dashboard",
    meta: { requiresAuth: true },
  },
  {
    path: "/books",
    component: ManageBooks,
    name: "ManageBooks",
    meta: { requiresAuth: true },
  },
  {
    path: "/add-book",
    component: AddBook,
    name: "AddBook",
    meta: { requiresAuth: true },
  },
  {
    path: "/reviews",
    component: ManageReviews,
    name: "ManageReviews",
    meta: { requiresAuth: true },
  },
  {
    path: "/users",
    component: ManageUsers,
    name: "ManageUsers",
    meta: { requiresAuth: true },
  },
  {
    path: "/",
    redirect: "/login", // Redirect root to login
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})


const isAuthenticated = () => {
  const token = localStorage.getItem("adminToken")
  const user = localStorage.getItem("adminUser")
  return !!(token && user)
}

// Navigation guard
router.beforeEach((to, from, next) => {
  const authenticated = isAuthenticated()

  if (to.meta.requiresAuth && !authenticated) {
    next("/login")
    return
  }

  if (to.meta.requiresGuest && authenticated) {
    next("/dashboard")
    return
  }

  next()
})

export default router
