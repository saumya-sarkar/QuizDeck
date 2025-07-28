<template>
  <div class="quiz-attempts-container">
    <Navbar />
    <div class="container-fluid py-4">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb :items="breadcrumbItems" />
      
      <!-- Header Section -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="attempts-title mb-0">Quiz Attempts</h2>
              <p class="text-muted mb-0">{{ totalAttempts }} attempts completed</p>
            </div>
            <div class="stats-summary glass-card-mini d-flex gap-3">
              <div class="stat-item">
                <div class="stat-value">{{ averageScore }}%</div>
                <div class="stat-label">Avg Score</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ totalAttempts }}</div>
                <div class="stat-label">Total Attempts</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="row">
        <div class="col-12 text-center py-5">
          <div class="spinner-border text-white mb-3" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <h4 class="text-white">Loading your quiz attempts...</h4>
        </div>
      </div>

      <!-- Quiz Attempts List -->
      <div v-else-if="attempts.length > 0" class="attempts-list">
        <div 
          v-for="attempt in attempts" 
          :key="attempt.id"
          class="attempt-card glass-card mb-3"
        >
          <div class="row align-items-center">
            <!-- Quiz Info -->
            <div class="col-md-5">
              <div class="quiz-info">
                <h5 class="quiz-name mb-1">{{ attempt.quiz_name }}</h5>
                <p class="quiz-path mb-2">
                  <font-awesome-icon icon="book" class="me-1" />
                  {{ attempt.subject_name }} > {{ attempt.chapter_name }}
                </p>
                <div class="quiz-badges d-flex gap-2">
                  <span class="badge quiz-type-badge" :class="getQuizTypeBadgeClass(attempt.quiz_type)">
                    {{ attempt.quiz_type }}
                  </span>
                  <span class="badge difficulty-badge" :class="getDifficultyBadgeClass(attempt.difficulty)">
                    {{ attempt.difficulty }}
                  </span>
                  <span v-if="attempt.status === 'auto_submitted'" class="badge auto-submit-badge">
                    Auto Submitted
                  </span>
                </div>
              </div>
            </div>

            <!-- Attempt Stats Matrix (3x1) -->
            <div class="col-md-5">
              <div class="attempt-stats-matrix">
                <!-- Row 1: Score -->
                <div class="stats-row">
                  <div class="stat-icon">
                    <font-awesome-icon icon="trophy" />
                  </div>
                  <div class="stat-info">
                    <span class="stat-label">Score:</span>
                    <span class="stat-value">{{ attempt.user_score }}/{{ attempt.total_marks }}</span>
                  </div>
                  <div class="stat-percentage" :class="getScoreClass(attempt.percentage)">
                    {{ attempt.percentage }}%
                  </div>
                </div>

                <!-- Row 2: Time Taken -->
                <div class="stats-row">
                  <div class="stat-icon">
                    <font-awesome-icon icon="clock" />
                  </div>
                  <div class="stat-info">
                    <span class="stat-label">Time Taken:</span>
                    <span class="stat-value">{{ formatTime(attempt.time_taken_seconds) }}</span>
                  </div>
                  <div class="stat-badge">
                    <span class="badge time-badge">
                      {{ getTimeStatus(attempt.time_taken_seconds) }}
                    </span>
                  </div>
                </div>

                <!-- Row 3: Submission Date -->
                <div class="stats-row">
                  <div class="stat-icon">
                    <font-awesome-icon icon="calendar" />
                  </div>
                  <div class="stat-info">
                    <span class="stat-label">Submitted:</span>
                    <span class="stat-value">{{ formatDate(attempt.submitted_at) }}</span>
                  </div>
                  <div class="stat-badge">
                    <span class="badge date-badge">
                      {{ getDateStatus(attempt.submitted_at) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="col-md-2 text-end">
              <button 
                class="btn btn-outline-primary glass-btn"
                @click="viewDetails(attempt)"
              >
                <font-awesome-icon icon="eye" class="me-1" />
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="row">
        <div class="col-12 text-center py-5">
          <font-awesome-icon icon="clipboard-list" class="fa-3x text-white-50 mb-3" />
          <h4 class="text-white">No Quiz Attempts Yet</h4>
          <p class="text-white-50">Start taking quizzes to see your attempts here.</p>
          <button 
            class="btn btn-primary mt-3"
            @click="goToQuizzes"
          >
            <font-awesome-icon icon="play" class="me-2" />
            Browse Quizzes
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';
import { useToast } from 'vue-toastification';

export default {
  name: 'QuizAttempts',
  components: {
    Navbar,
    Breadcrumb
  },
  data() {
    return {
      attempts: [],
      loading: true,
      breadcrumbItems: [
        {
          name: 'Quiz Attempts',
          icon: 'clipboard-list'
        }
      ]
    };
  },
  computed: {
    totalAttempts() {
      return this.attempts.length;
    },
    averageScore() {
      if (this.attempts.length === 0) return 0;
      const total = this.attempts.reduce((sum, attempt) => sum + attempt.percentage, 0);
      return Math.round(total / this.attempts.length);
    }
  },
  async mounted() {
    await this.fetchAttempts();
  },
  methods: {
    async fetchAttempts() {
      this.loading = true;
      const token = sessionStorage.getItem('access_token');
      
      if (!token) {
        this.$store.dispatch('auth/logoutUser');
        return;
      }
      
      const user_id = this.$route.params.currentUserId

      try {
        const response = await axios.post(`${BASE_URL}/user/quiz-attempts`, {
          user_id: user_id
        },
        {
          headers: { Authorization : token }
        });
        
        if (response.data.code === 200) {
          this.attempts = response.data.attempts;
        }
      } catch (error) {
        console.error('Error fetching quiz attempts:', error);
        const toast = useToast();
        toast.error('Failed to load quiz attempts');
      } finally {
        this.loading = false;
      }
    },

    viewDetails(attempt) {
      const userId = this.$route.params.currentUserId;
      this.$router.push(`/admin/users/${userId}/attempts/${attempt.id}`);
    },

    goToQuizzes() {
      this.$router.push(`/admin/subjects`);
    },

    getQuizTypeBadgeClass(type) {
      const classes = {
        'Practice': 'bg-info',
        'Mock': 'bg-warning',
        'Exam': 'bg-success'
      };
      return classes[type] || 'bg-secondary';
    },

    getDifficultyBadgeClass(difficulty) {
      const classes = {
        'Easy': 'bg-success',
        'Medium': 'bg-warning',
        'Hard': 'bg-danger'
      };
      return classes[difficulty] || 'bg-secondary';
    },

    getScoreClass(percentage) {
      if (percentage >= 80) return 'score-excellent';
      if (percentage >= 60) return 'score-good';
      if (percentage >= 40) return 'score-average';
      return 'score-poor';
    },

    getTimeStatus(seconds) {
      if (!seconds) return 'Unknown';
      if (seconds < 300) return 'Quick'; // Less than 5 minutes
      if (seconds < 1800) return 'Normal'; // Less than 30 minutes
      return 'Extended'; // More than 30 minutes
    },

    getDateStatus(dateString) {
      if (!dateString) return 'Unknown';
      const date = new Date(dateString);
      const now = new Date();
      const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) return 'Today';
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays}d ago`;
      if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
      return `${Math.floor(diffDays / 30)}m ago`;
    },

    formatTime(seconds) {
      if (!seconds) return '00:00';
      
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      
      if (hours > 0) {
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
      }
      return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-IN', { 
        year: 'numeric',
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
};
</script>

<style scoped>
.quiz-attempts-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.quiz-attempts-container::before {
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

.attempts-title {
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-muted {
  color: rgba(255, 255, 255, 0.7) !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.glass-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.glass-card:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.glass-card-mini {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 1rem;
}

.stats-summary .stat-item {
  text-align: center;
}

.stats-summary .stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  display: block;
}

.stats-summary .stat-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.attempt-card {
  transition: all 0.3s ease;
}

.quiz-name {
  color: #ffffff;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.quiz-path {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}

.quiz-badges .badge {
  font-size: 0.7rem;
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.quiz-type-badge.bg-info {
  background: rgba(13, 202, 240, 0.8) !important;
}

.quiz-type-badge.bg-warning {
  background: rgba(255, 193, 7, 0.8) !important;
}

.quiz-type-badge.bg-success {
  background: rgba(25, 135, 84, 0.8) !important;
}

.difficulty-badge.bg-success {
  background: rgba(40, 167, 69, 0.8) !important;
}

.difficulty-badge.bg-warning {
  background: rgba(255, 193, 7, 0.8) !important;
}

.difficulty-badge.bg-danger {
  background: rgba(220, 53, 69, 0.8) !important;
}

.auto-submit-badge {
  background: rgba(255, 87, 34, 0.8) !important;
  color: #ffffff !important;
}

/* 3x1 Stats Matrix Styles */
.attempt-stats-matrix {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.stats-row {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 0.75rem;
  transition: all 0.3s ease;
}

.stats-row:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(3px);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
}

.stat-icon i {
  color: #ffffff;
  font-size: 1rem;
}

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  font-weight: 500;
}

.stat-value {
  color: #ffffff;
  font-weight: 600;
  font-size: 0.9rem;
}

.stat-percentage {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.85rem;
  color: #ffffff;
  flex-shrink: 0;
}

.score-excellent {
  background: rgba(40, 167, 69, 0.8);
  border: 1px solid #28a745;
}

.score-good {
  background: rgba(0, 123, 255, 0.8);
  border: 1px solid #007bff;
}

.score-average {
  background: rgba(255, 193, 7, 0.8);
  border: 1px solid #ffc107;
}

.score-poor {
  background: rgba(220, 53, 69, 0.8);
  border: 1px solid #dc3545;
}

.stat-badge {
  flex-shrink: 0;
}

.stat-badge .badge {
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
  border-radius: 10px;
  font-weight: 600;
}

.time-badge {
  background: rgba(108, 117, 125, 0.8) !important;
  color: #ffffff !important;
}

.date-badge {
  background: rgba(111, 66, 193, 0.8) !important;
  color: #ffffff !important;
}

.glass-btn {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  padding: 0.5rem 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.glass-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
  transform: translateY(-1px);
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

/* Mobile responsiveness */
@media (max-width: 768px) {
  .stats-summary {
    flex-direction: column;
    gap: 1rem !important;
  }
  
  .attempt-card .row {
    text-align: center;
  }
  
  .attempt-card .col-md-2 {
    margin-top: 1rem;
  }
  
  .stats-row {
    padding: 0.5rem;
  }
  
  .stat-icon {
    width: 35px;
    height: 35px;
    margin-right: 0.75rem;
  }
  
  .stat-info {
    gap: 0;
  }
  
  .stat-label {
    font-size: 0.75rem;
  }
  
  .stat-value {
    font-size: 0.85rem;
  }
}
</style>