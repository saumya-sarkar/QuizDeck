<template>
  <nav class="navbar navbar-expand-lg custom-navbar">
    <div class="container">
      <router-link to="/" class="navbar-brand fw-bold fs-3">QuizDeck</router-link>
      
      <!-- Navigation items -->
      <div class="navbar-collapse" v-if="!isLoggedIn && !isAdmin">
        <ul class="navbar-nav ms-auto" >
          <li class="nav-item">
            <router-link to="/" class="nav-link">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/login" class="nav-link">Login</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/register" class="nav-link">Register</router-link>
          </li>
        </ul>
      </div>
      <div class="navbar-collapse" v-if="isLoggedIn && isAdmin">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <router-link to="/admin" class="nav-link">Dashboard</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/admin/subjects" class="nav-link">Quizzes</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/admin/users" class="nav-link">Users</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/admin/analytics" class="nav-link">Summary Charts</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/" @click="handleLogout" class="nav-link">Sign Out</router-link>
          </li>
        </ul>
      </div>
      <div class="navbar-collapse" v-if="isLoggedIn && !isAdmin">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <router-link :to="{ name: 'UserDashboard', params: { userId: user_id } }" class="nav-link">Dashboard</router-link>
          </li>
          <li class="nav-item">
            <router-link :to="{ name: 'UserSubjects', params: { userId: user_id } }" class="nav-link">Quizzes</router-link>
          </li>
          <li class="nav-item">
            <router-link :to="{ name: 'UserQuizAttempts', params: { userId: user_id } }" class="nav-link">Quiz Attempts</router-link>
          </li>
          <li class="nav-item">
            <router-link :to="{ name: 'UserAnalytics', params: { userId: user_id } }" class="nav-link">Summary Charts</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/" @click="handleLogout" class="nav-link">Sign Out</router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import store from '@/store';


export default {
  name: 'Navbar',
  data() {
    return {
      isLoggedIn: false,
      isAdmin: false,
      user_id: null
    }
  },

  created() {
    // Check if user is logged in and set the state accordingly
    this.isLoggedIn = store.getters['auth/isAuthenticated'];
    this.isAdmin = store.getters['auth/isAdmin'];
  },
  mounted() {
    if (this.isLoggedIn) {
      this.user_id = store.getters['auth/getUser'].id;
    }
  },

  methods: {
    handleLogout() {
      this.isLoggedIn = false;
      this.isAdmin = false;
      sessionStorage.removeItem("access_token");
    }
  }
}
</script>

<style scoped>
/* Navigation */
.custom-navbar {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  z-index: 1050;
}

.navbar-brand {
  background: linear-gradient(45deg, #fff, #e0e7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-decoration: none;
  transition: all 0.3s ease;
}


/* Navigation Links */
.nav-link {
  color: rgba(255, 255, 255, 0.9) !important;
  padding: 0.5rem 1rem !important;
  margin: 0 0.25rem;
  border-radius: 25px;
  transition: all 0.3s ease;
  text-decoration: none;
  font-weight: 500;
}

.nav-link:hover {
  color: white !important;
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.nav-link.router-link-active {
  color: #00d4ff !important;
  background: rgba(0, 212, 255, 0.15);
  font-weight: 600;
}

</style>