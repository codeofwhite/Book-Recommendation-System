import { createRouter, createWebHistory } from 'vue-router';

// Import your component placeholders
import DashboardOverview from '../components/DashboardOverview.vue';
import ManageBooks from '../components/ManageBooks.vue';
import AddBook from '../components/AddBook.vue';
import ManageReviews from '../components/ManageReviews.vue';
import ManageUsers from '../components/ManageUsers.vue';

const routes = [
  { path: '/dashboard', component: DashboardOverview, name: 'Dashboard' },
  { path: '/books', component: ManageBooks, name: 'ManageBooks' },
  { path: '/add-book', component: AddBook, name: 'AddBook' },
  { path: '/reviews', component: ManageReviews, name: 'ManageReviews' },
  { path: '/users', component: ManageUsers, name: 'ManageUsers' },
  { path: '/', redirect: '/dashboard' } // Redirect root to dashboard
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;