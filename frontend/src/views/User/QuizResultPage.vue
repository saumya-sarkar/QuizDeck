<template>
  <div class="quiz-result-page">
    <Navbar />
    <div class="container-fluid py-4">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb :items="breadcrumbItems" />
      
      <!-- Loading State -->
      <div v-if="loading" class="d-flex justify-content-center align-items-center" style="min-height: 60vh;">
        <div class="text-center">
          <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
          <h4 class="text-white">Loading Quiz Result...</h4>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="row">
        <div class="col-12 text-center py-5">
          <font-awesome-icon icon="exclamation-triangle" class="fa-3x text-warning mb-3" />
          <h4 class="text-white">{{ error }}</h4>
          <button class="btn btn-primary mt-3" @click="goBack">
            <font-awesome-icon icon="arrow-left" class="me-2" />
            Go Back
          </button>
        </div>
      </div>

      <!-- Quiz Result Component -->
      <div v-else-if="quizResult">
        <QuizResult 
          :result="quizResult" 
          @retake-quiz="handleRetakeQuiz"
        />
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import QuizResult from '@/components/User/QuizResult.vue';
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';
import { useToast } from 'vue-toastification';

export default {
  name: 'QuizResultPage',
  components: {
    Navbar,
    Breadcrumb,
    QuizResult
  },
  data() {
    return {
      quizResult: null,
      loading: true,
      error: null,
      breadcrumbItems: []
    };
  },
  async mounted() {
    await this.loadQuizResult();
    this.setupBreadcrumb();
  },
  methods: {
    async loadQuizResult() {
      const attemptId = this.$route.params.attemptId;
      
      if (!attemptId) {
        this.error = 'No attempt ID provided';
        this.loading = false;
        return;
      }

      try {
        const token = sessionStorage.getItem('access_token');
        
        if (!token) {
          this.$store.dispatch('auth/logoutUser');
          return;
        }
        const userId =  this.$route.params.userId || this.$store.getters['auth/getUser'].id;
        const response = await axios.post(`${BASE_URL}/quiz/result`, {
          attempt_id: parseInt(attemptId),
          user_id: userId
        }, {
          headers: { Authorization: token }
        });
        
        if (response.data.code === 200) {
          this.quizResult = response.data.data;
        } else {
          this.error = response.data.error_message || 'Failed to load quiz result';
        }
      } catch (error) {
        console.error('Error loading quiz result:', error);
        this.error = error.response?.data?.error_message || 'Failed to load quiz result';
        
        const toast = useToast();
        toast.error('Failed to load quiz result');
      } finally {
        this.loading = false;
      }
    },

    setupBreadcrumb() {
      if (!this.quizResult) return;
      
      const userId = this.$route.params.userId;
      
      this.breadcrumbItems = [
        {
          name: 'Quiz Attempts',
          path: `/user/${userId}/quiz-attempts`,
          icon: 'clipboard-list'
        },
        {
          name: this.quizResult.quiz_name,
          icon: 'trophy'
        }
      ];
    },

    handleRetakeQuiz() {
      const userId = this.$route.params.userId;
      const quizId = this.$route.params.quizId;
      this.$router.push(`/user/${userId}/quiz/${quizId}/take`);
    },

    goBack() {
      const userId = this.$route.params.userId;
      this.$router.push(`/user/${userId}/quiz-attempts`);
    }
  }
};
</script>

<style scoped>
.quiz-result-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.quiz-result-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.container-fluid {
  max-width: 1200px;
  position: relative;
  z-index: 1;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 25px;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}
</style>