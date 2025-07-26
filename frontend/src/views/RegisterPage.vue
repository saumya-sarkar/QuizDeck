<template>
  <div class="register-page">
    <Navbar />
    
    <!-- Background Elements -->
    <BackgroundElements />

    <div class="container d-flex justify-content-center align-items-center" style="min-height: calc(100vh - 80px); padding-top: 30px; padding-bottom: 40px;">
      <div class="register-card">
        <div class="text-center mb-4">
          <h2 class="register-title">Join QuizDeck</h2>
          <p class="register-subtitle">Create your account to get started</p>
        </div>

        <form @submit.prevent="register" novalidate>
          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input
              type="email"
              class="form-control custom-input"
              id="email"
              v-model.trim="email"
              @blur="checkEmail"
              @input="validateEmail"
              placeholder="Enter your email address"
              v-bind:class="{ 'is-invalid': fieldErrors.email }"
              required
            />
            <div class="invalid-feedback" v-if="fieldErrors.email">{{ fieldErrors.email }}</div>
          </div>

          <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input
              type="text"
              class="form-control custom-input"
              id="username"
              v-model.trim="username"
              placeholder="Enter your username"
              @blur="checkUsername"
              v-bind:class="{ 'is-invalid': fieldErrors.username }"
            />
            <div class="invalid-feedback" v-if="fieldErrors.username">{{ fieldErrors.username }}</div>
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
                @input="validatePassword"
                placeholder="Enter your password"
                v-bind:class="{ 'is-invalid': fieldErrors.password }"
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
            <div class="invalid-feedback" v-if="fieldErrors.password">{{ fieldErrors.password }}</div>
          </div>

          <div class="mb-3">
            <label for="full_name" class="form-label">Full Name</label>
            <input
              type="text"
              class="form-control custom-input"
              id="full_name"
              v-model.trim="full_name"
              placeholder="Enter your full name (optional)"
            />
          </div>

          <div class="mb-3">
            <label for="qualification" class="form-label">Education Level</label>
            <select
              class="form-select custom-input"
              id="qualification"
              v-model="qualification"
              @blur="checkqualification"
              v-bind:class="{ 'is-invalid': fieldErrors.qualification }"
              required
            >
              <option value="">Select your education level</option>
              <option v-for="q in qualificationOptions" :key="q.name" :value="q.name">
                {{ q.value }}
              </option>
            </select>
            <div class="invalid-feedback" v-if="fieldErrors.qualification">{{ fieldErrors.qualification }}</div>
          </div>

          <div class="mb-3">
            <label for="dob" class="form-label">Date of Birth</label>
            <input
              type="date"
              class="form-control custom-input"
              id="dob"
              v-bind:max="istDateString"
              @blur="checkDob"
              v-model="dob"
              v-bind:class="{ 'is-invalid': fieldErrors.dob }"
            />
            <div class="invalid-feedback" v-if="fieldErrors.dob">{{ fieldErrors.dob }}</div>
          </div>

          <div class="d-grid gap-2 mb-3">
            <button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Creating Account...' : 'Create Account' }}
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
              Already have an account?
              <router-link to="/login" class="signup-link">Sign in here</router-link>
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
  name: 'RegisterPage',
  components: {
    BackgroundElements, Navbar
  },
  data() {
    return {
      email: '',
      username: '',
      password: '',
      full_name: '',
      qualification: '',
      dob: '',
      showPassword: false,
      loading: false,
      fieldErrors: {},
      errorMessage: '',
      qualificationOptions: [] // match backend enum
    };
  },
  created() {
    axios.get(`${BASE_URL}/qualifications`).then(response => {
      this.qualificationOptions = response.data;
    }).catch(error => {
      console.error('Error loading qualifications:', error);
    });
  },
  computed: {
    istDateString() {
      const date = new Date(); // Get the current date

      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, '0'); // Months are 0-indexed, so add 1
      const day = date.getDate().toString().padStart(2, '0');

      const formattedDate = `${year}-${month}-${day}`;
      return formattedDate;
    }
  },

  watch:{
    email(newEmail){
      this.username = newEmail ? newEmail.split('@')[0] : ''
    }
  },
  
  methods: {
    togglePassword() {
      this.showPassword = !this.showPassword;
    },

    async checkUsername() {
      this.fieldErrors.username = '';
      
      if (!this.username) {
        this.fieldErrors.username = 'Username is required';
        return;
      } else {
        this.fieldErrors.username = '';
      }

      try {
        const res = await axios.post(`${BASE_URL}/check-username`, { username: this.username });
        if (!res.data.valid) {
          this.fieldErrors.username = res.data.message;
        }
      } catch (err) {
        console.error("Username check failed", err);
      }
    },

    async checkEmail() {
      
      if (!this.email) {
          this.fieldErrors.email = 'Email is required';
          return;
      } else {
          this.fieldErrors.email = '';
        }
      this.validateEmail();
      if (!this.fieldErrors.email) {
        this.fieldErrors.email = '';
        try {
          const res = await axios.post(`${BASE_URL}/check-email`, { email: this.email });
          if (!res.data.valid) {
            this.fieldErrors.email = res.data.message;
          } else {
            this.fieldErrors.email = '';
          }
        } catch (err) {
          console.error("Email check failed", err);
        }
      }
    },

    validateEmail() {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(this.email)) {
        this.fieldErrors.email = 'Invalid email format';
      } else {
        this.fieldErrors.email = '';
      }
    },

    checkDob() {
      this.fieldErrors.dob = '';
      if (!this.dob) {
        this.fieldErrors.dob = 'Date of Birth is required';
      } else if (new Date(this.dob) > new Date()) {
        this.fieldErrors.dob = 'Date of Birth cannot be in the future';
      }
    },

    checkPassword() {
      if (!this.password) {
        this.fieldErrors.password = 'Password is required';
      } else {
        this.fieldErrors.password = '';
        this.validatePassword();
      }
      
    },

    validatePassword() {
      this.fieldErrors.password = '';
      // Example password validation: at least 6 characters, 1 uppercase, 1 lowercase, 1 number
      const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{6,}$/;
      if (this.password && !passwordPattern.test(this.password)) {
        this.fieldErrors.password = 'Password must be at least 6 characters long and include uppercase, lowercase, and a number';
      } else {
        this.fieldErrors.password = '';
      }
    },
    
    checkqualification() {
      this.fieldErrors.qualification = '';
      if (!this.qualification) {
        this.fieldErrors.qualification = 'Education level is required';
      } else {
        this.fieldErrors.qualification = '';
      }
    },

    resetForm() {
      this.email = '';
      this.username = '';
      this.password = '';
      this.full_name = '';
      this.qualification = '';
      this.dob = '';
      this.showPassword = false;
      this.loading = false;
      this.fieldErrors = {};
      this.errorMessage = '';
    },

    
    async register() {
      this.fieldErrors = {};
      this.errorMessage = '';
      const toast = useToast();
      
      if (this.loading) return; // Prevent multiple submissions

      if (this.fieldErrors.email || this.fieldErrors.username || this.fieldErrors.password || this.fieldErrors.qualification || this.fieldErrors.dob) {
        toast.error('Please check your inputs before submitting.');
        return;
      }
      try {
        this.loading = true;
        const response = await axios.post(`${BASE_URL}/register`, {
          email: this.email,
          username: this.username,
          password: this.password,
          full_name: this.full_name,
          qualification: this.qualification,
          dob: this.dob
        });

        toast.success('Registered successfully! You can now login.');
        this.resetForm();
        this.$router.push('/login');
      } catch (error) {
        const status = error.response?.status;
        const msg = error.response?.data?.error || 'Something went wrong';

        if (status === 400) {
          if (msg.includes('username')) this.fieldErrors.username = msg;
          else if (msg.includes('Email')) this.fieldErrors.email = msg;
          else if (msg.includes('Password')) this.fieldErrors.password = msg;
          else this.errorMessage = msg;

          toast.error(msg);
        } else {
          this.errorMessage = msg;
          toast.error(msg);
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>

/* Background */
.register-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  position: relative;
  overflow: hidden;
}


/* Register Card */
.container {
  position: relative;
  z-index: 2;
}

.register-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2.4rem;
  width: 600px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.register-title {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(45deg, #fff, #e0e7ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.register-subtitle {
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

/* Select styling */
.form-select.custom-input option {
  background: #965fee;
  color: white;
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