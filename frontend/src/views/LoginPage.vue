<template>
  
  <div class="login-page">
    <Navbar />
    
    <!-- Background Elements -->
    <BackgroundElements />

    <div class="container d-flex justify-content-center align-items-center min-vh-100">
      <div class="login-card">
        <div class="text-center mb-4">
          <h2 class="login-title">Welcome Back</h2>
          <p class="login-subtitle">Please sign in to continue</p>
        </div>

        <form @submit.prevent="login" novalidate>
          <div class="mb-3">
            <label for="email_username" class="form-label">Email or Username</label>
            <input
              type="text"
              class="form-control custom-input"
              id="email_username"
              v-model.trim="email_username"
              @blur="checkEmailOrUsername"
              v-bind:class="{ 'is-invalid': fieldErrors.email_username }"
              placeholder="Enter your email or username"
              required
            />
            <div class="invalid-feedback" v-if="fieldErrors.email_username">
              {{ fieldErrors.email_username }}
            </div>
          </div>

          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <div class="password-container">
              <input
                v-bind:type="showPassword ? 'text' : 'password'"
                class="form-control password-input-separate"
                id="password"
                v-model="password"
                @blur="checkPassword"
                v-bind:class="{ 'is-invalid': fieldErrors.password }"
                placeholder="Enter your password"
                required
              />
              <button 
                type="button"
                class="password-toggle-separate" 
                @click="togglePassword"
                >
                <font-awesome-icon :icon="showPassword ? 'eye-slash' : 'eye'" />
              </button>
            </div>
            <div class="invalid-feedback" v-if="fieldErrors.password">
              {{ fieldErrors.password }}
            </div>
          </div>

          <div class="form-check mb-4">
            <input
              class="form-check-input"
              type="checkbox"
              id="rememberMe"
              v-model="rememberMe"
            />
            <label class="form-check-label" for="rememberMe">
              Remember me
            </label>
          </div>

          <div class="d-grid gap-2 mb-3">
            <button type="submit" class="btn btn-primary btn-lg" v-bind:disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Signing in...' : 'Sign In' }}
            </button>
          </div>

          <div class="text-center">
            <button type="button" class="btn btn-link reset-btn" @click="resetForm">
              <font-awesome-icon icon="rotate-left" /> Reset Form
            </button>
          </div>

          <div class="alert alert-danger custom-alert" v-if="errorMessage">
            <font-awesome-icon icon="circle-exclamation" size="lg" style="color: #df6d83;" />   {{ errorMessage }}
          </div>

          <div class="text-center">
            <p class="signup-text">
              Don't have an account?
              <router-link to="/register" class="signup-link">Create one here</router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';
import Navbar from '@/components/Navbar.vue';
import BackgroundElements from '@/components/BackgroundElements.vue';
import BASE_URL from '@/config/apiConfig';

export default {
  name: 'LoginPage',
  components: {
    BackgroundElements, Navbar
  },
  data() {
    return {
      email_username: '',
      password: '',
      showPassword: false,
      rememberMe: false,
      errorMessage: '',
      fieldErrors: {},
      loading: false
    };
  },
  mounted() {
    const remembered = localStorage.getItem('remembered_email_username');
    if (remembered) {
      this.email_username = remembered;
      this.rememberMe = true;
    }
  },
  methods: {
    togglePassword() {
      this.showPassword = !this.showPassword;
    },
    checkEmailOrUsername() {
      if (!this.email_username) {
        this.fieldErrors.email_username = 'Email or username is required';
        } else {
          this.fieldErrors.email_username = '';
        }
    },
    checkPassword() {
      if (!this.password) {
          this.fieldErrors.password = 'Password is required';
        } else {
          this.fieldErrors.password = '';
        }
    },
    async login() {
      this.errorMessage = '';
      this.fieldErrors = {};
      const toast = useToast();
      const store = this.$store;
      
      if (this.loading) return; // Prevent multiple submissions while loading

      
      if (this.fieldErrors.email_username || this.fieldErrors.password) {
        toast.error('Please check your input before submitting.');
        return;
      }
       

      try {
        this.loading = true;

        const response = await axios.post(`${BASE_URL}/login`, {
          email_username: this.email_username,
          password: this.password
        });

        const user = response.data.user;
        const token = response.data.authToken;
        sessionStorage.setItem('access_token', token);

        store.commit('auth/setUser', user);

        if (this.rememberMe) {
          localStorage.setItem('remembered_email_username', this.email_username);
        } else {
          localStorage.removeItem('remembered_email_username');
        }

        if (store.getters['auth/isAdmin']) {
          toast.success('Welcome back, Admin!');
          const redirectPath = this.$route.query.redirect || '/admin';
          this.$router.push(redirectPath);
        } else {
          toast.success(`Welcome back, ${user.username || user.email}!`);
          const redirectPath = this.$route.query.redirect || `/user/${user.id}`;
          this.$router.push(redirectPath);
        }
      } catch (error) {
        if (error.response) {
          const status = error.response.status;
          
          let message = 'Unexpected error';

          if (error && error.response && error.response.data && error.response.data.error) {
            message = error.response.data.error;
          }

          if (status === 400 || status === 404) {
            this.errorMessage = message;
            toast.error(message);
          } else if (status === 401) {
            this.errorMessage = 'Invalid password';
            toast.error('Invalid username or password');
          } else if (status === 403) {
            this.errorMessage = 'Access denied. Please contact support.';
            toast.error('Access denied'); 
          } else {
            this.errorMessage = 'Server has encountered an error.';
            toast.error('Server error');
          }
        } else {
          this.errorMessage = 'Network error. Please check your connection.';
          toast.error('Network error');
        } 
      } finally {
          this.loading = false;
        }
    },

    resetForm() {
      this.email_username = '';
      this.password = '';
      this.showPassword = false;
      this.rememberMe = false;
      this.errorMessage = '';
      this.fieldErrors = {};
    }
  }
};
</script>

<style scoped>

/* Background */
.login-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  position: relative;
  overflow: hidden;
}


/* Login Card */
.container {
  position: relative;
  z-index: 2;
}

.login-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 3rem;
  width: 450px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.login-title {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(45deg, #fff, #e0e7ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  margin-bottom: 0;
}

/* Form Styling */
.form-label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.custom-input {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: 15px !important;
  color: white !important;
  padding: 0.75rem 1rem !important;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.custom-input:focus {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.5) !important;
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25) !important;
  color: white !important;
}

.custom-input::placeholder {
  color: rgba(255, 255, 255, 0.6) !important;
}

/* Password Container */
.password-container {
  display: flex;
  gap: 10px;
  align-items: stretch;
}

.password-input-separate {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: 15px !important;
  color: white !important;
  padding: 0.75rem 1rem !important;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  flex: 1;
}

.password-input-separate:focus {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.5) !important;
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25) !important;
  color: white !important;
}

.password-input-separate::placeholder {
  color: rgba(255, 255, 255, 0.6) !important;
}

.password-toggle-separate {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: 15px !important;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 0.75rem 1rem;
  min-width: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.password-toggle-separate:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
}

.form-check-label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

/* Buttons */
.btn-primary {
  background: linear-gradient(45deg, #ff6b6b, #ee5a24) !important;
  border: none !important;
  border-radius: 15px !important;
  padding: 0.75rem 1.5rem !important;
  font-weight: 600 !important;
  font-size: 1.1rem !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 4px 15px rgba(238, 90, 36, 0.3) !important;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(238, 90, 36, 0.4) !important;
  background: linear-gradient(45deg, #ff5252, #e53935) !important;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.reset-btn {
  color: rgba(255, 255, 255, 0.8) !important;
  text-decoration: none !important;
  font-weight: 500;
}

.reset-btn:hover {
  color: white !important;
  text-decoration: underline !important;
}

/* Alert */
.custom-alert {
  background: rgba(220, 53, 69, 0.2) !important;
  border: 1px solid rgba(220, 53, 69, 0.3) !important;
  border-radius: 15px !important;
  backdrop-filter: blur(10px);
  color: #ffebee !important;
}

/* Signup Link */
.signup-text {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0;
}

.signup-link {
  color: #e0e7ff !important;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  text-shadow: 0 0 10px rgba(224, 231, 255, 0.3);
}

.signup-link:hover {
  color: #ffffff !important;
  text-decoration: underline;
  text-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
  transform: translateY(-1px);
}

/* Invalid Feedback */
.invalid-feedback {
  color: #ffcdd2;
  font-weight: 500;
  display: flex !important; 
}

.is-invalid {
  border-color: rgba(244, 67, 54, 0.5) !important;
  box-shadow: 0 0 0 0.2rem rgba(244, 67, 54, 0.25) !important;
}
</style>