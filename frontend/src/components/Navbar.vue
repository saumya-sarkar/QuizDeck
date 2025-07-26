<template>
  <nav class="navbar navbar-expand-lg custom-navbar">
    <div class="container">
      <router-link to="/" class="navbar-brand fw-bold fs-3">QuizDeck</router-link>
      
      <!-- Navigation items -->
      <div class="navbar-collapse">
        <ul class="navbar-nav ms-auto">
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
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navbar'
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