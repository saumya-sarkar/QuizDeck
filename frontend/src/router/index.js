import { createRouter, createWebHistory } from 'vue-router'
import QuizDeckLandingPage from '@/views/QuizDeckLandingPage.vue';
import UserRoutes from "./UserRoutes";
import AdminRoutes from "./AdminRoutes";
import store from '@/store';


const HomeRoutes = [
  {
    path: '/',
    name: 'QuizDeckLandingPage',
    component: QuizDeckLandingPage,
    meta: {
      title: 'QuizDeck Home',
      requiresAuth: false
    }
  },
  {
    path: '/login',
    name: 'Login',
    // route level code-splitting
    // this generates a separate chunk (with name login) for this route
    // which is lazy-loaded when the route is visited.
    // webpackPrefetch: true is used to prefetch the chunk in the background
    // to improve performance when the user navigates to this route.
    component: () => import(/* webpackChunkName: "login", webpackPrefetch: true */ '../views/LoginPage.vue'),
    meta: {
      title: 'Login',
      requiresAuth: false
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import(/* webpackChunkName: "register", webpackPrefetch: true */ '../views/RegisterPage.vue'),
    meta: {
      title: 'Register',
      requiresAuth: false
    }
  }
];

const routes = [...HomeRoutes, ...AdminRoutes, ...UserRoutes];


const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})




// Global Navigation Guard
router.beforeEach(async (to, from, next) => {
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresAdmin = to.meta.requiresAdmin ? to.meta.requiresAdmin : false;
  

  // If the route requires authentication
  if (requiresAuth) {
    // Ensure user details are fetched before checking auth status
    await store.dispatch('auth/userDetails');
    const isAuthenticated = store.getters['auth/isAuthenticated'];
    const isAdmin = store.getters['auth/isAdmin'];
    
    if (!isAuthenticated) {
      next({
        name: 'Login',
        query: { redirect: to.fullPath }, // Store the intended path for redirect after login
      });
    } else {
      // Authenticated, now check roles
      if (requiresAdmin) {
        if (isAdmin) {
          next();
        } else {
          // User authenticated but is not admin, redirect to unauthorized
          next({ name: 'Unauthorized' });
        }
      } else {
        next(); // Requires authentication only, proceed
      }
    }
  } else {
    next(); // Route does not require authentication, proceed
  }
});


export default router;