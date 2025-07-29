<template>
  <div class="dashboard-container">
    <Navbar />
    <div class="container-fluid py-4">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb :items="breadcrumbItems" />
      
      <!-- Dashboard Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="dashboard-title">Welcome back, {{ userName }}!</h2>
              <p class="text-muted">Ready to test your knowledge? {{ currentDate }}</p>
            </div>
            <div class="user-avatar">
              <div class="avatar-circle">
                <font-awesome-icon icon="user" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Dashboard Stats Cards -->
      <div class="row g-4 mb-4">
        <div class="col-xl-3 col-md-6">
          <div class="stats-card">
            <div class="stats-icon quizzes-taken">
              <font-awesome-icon icon="clipboard-check" />
            </div>
            <div class="stats-content">
              <h3>{{ totalQuizzesTaken }}</h3>
              <p>Quizzes Completed</p>
            </div>
          </div>
        </div>
        <div class="col-xl-3 col-md-6">
          <div class="stats-card">
            <div class="stats-icon average-score">
              <font-awesome-icon icon="trophy" />
            </div>
            <div class="stats-content">
              <h3>{{ averageScore }}%</h3>
              <p>Average Score</p>
            </div>
          </div>
        </div>
        <div class="col-xl-3 col-md-6">
          <div class="stats-card">
            <div class="stats-icon subjects">
              <font-awesome-icon icon="book" />
            </div>
            <div class="stats-content">
              <h3>{{ subjectsExplored }}</h3>
              <p>Subjects Explored</p>
            </div>
          </div>
        </div>
        <div class="col-xl-3 col-md-6">
          <div class="stats-card">
            <div class="stats-icon streak">
              <font-awesome-icon icon="calendar" />
            </div>
            <div class="stats-content">
              <h3>{{ currentStreak }}</h3>
              <p>Day Streak</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="row g-4 mb-4">
        <div class="col-12">
          <div class="quick-actions-card">
            <h4 class="mb-3">Quick Actions</h4>
            <div class="row g-3">
              <div class="col-lg-3 col-md-6">
                <button 
                  class="btn quick-action-btn w-100"
                  @click="browseSubjects"
                >
                  <font-awesome-icon icon="book" />
                  <span>Browse Subjects</span>
                </button>
              </div>
              <div class="col-lg-3 col-md-6">
                <button 
                  class="btn quick-action-btn w-100"
                  @click="takeQuiz"
                >
                  <font-awesome-icon icon="play-circle" />
                  <span>Take Quiz</span>
                </button>
              </div>
              <div class="col-lg-3 col-md-6">
                <button 
                  class="btn quick-action-btn w-100"
                  @click="viewResults"
                >
                  <font-awesome-icon icon="chart-line" />
                  <span>View Results</span>
                </button>
              </div>
              <div class="col-lg-3 col-md-6">
                <button 
                  class="btn quick-action-btn w-100"
                  @click="viewReports"
                >
                  <font-awesome-icon icon="chart-line" />
                  <span>View Reports</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity & Available Quizzes -->
      <div class="row g-4">
        <div class="col-lg-8">
          <div class="recent-activity-card">
            <h4 class="mb-3">Recent Quiz Activity</h4>
            <div class="activity-list">
              <div 
                v-for="activity in recentQuizzes" 
                :key="activity.id" 
                class="activity-item"
              >
                <div class="activity-icon" :class="getScoreClass(activity.score)">
                  <font-awesome-icon icon="clipboard-check" />
                </div>
                <div class="activity-content">
                  <p class="activity-text">{{ activity.quizName }} - {{ activity.subject }}</p>
                  <small class="activity-time">Score: {{ activity.score }}% • {{ activity.timeAgo }}</small>
                </div>
                <div class="activity-score">
                  <span class="score-badge" :class="getScoreClass(activity.score)">
                    {{ activity.score }}%
                  </span>
                </div>
              </div>
            </div>
            <div class="text-center mt-3" v-if="recentQuizzes.length === 0">
              <p class="text-muted">No quiz attempts yet. Start your learning journey!</p>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="upcoming-quizzes-card">
            <h4 class="mb-3">Available Quizzes</h4>
            <div class="quiz-list">
              <div 
                v-for="quiz in upcomingQuizzes" 
                :key="quiz.id" 
                class="quiz-item"
                @click="startQuiz(quiz)"
              >
                <div class="quiz-info">
                  <h6 class="quiz-title">{{ quiz.name }}</h6>
                  <small class="quiz-details">{{ quiz.subject }} • {{ quiz.questions }} questions</small>
                </div>
                <div class="quiz-action">
                  <font-awesome-icon icon="play-circle" class="text-primary" />
                </div>
              </div>
            </div>
            <div class="text-center mt-3" v-if="upcomingQuizzes.length === 0">
              <p class="text-muted">No quizzes available right now.</p>
            </div>
          </div>
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
import store from '@/store';

export default {
  name: 'UserDashboard',
  components: {
    Navbar,
    Breadcrumb
  },
  data() {
    return {
      userName: 'Student',
      currentDate: new Date().toLocaleDateString('en-IN', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }),
      totalQuizzesTaken: 0,
      averageScore: 0,
      subjectsExplored: 0,
      currentStreak: 0,
      recentQuizzes: [],
      upcomingQuizzes: [],
      breadcrumbItems: [] // Empty for dashboard home
    };
  },

  mounted() {
    this.fetchUserData();
    this.fetchRecentQuizzes();
    this.fetchUpcomingQuizzes();
  },

  methods: {
    async fetchUserData() {
      const token = sessionStorage.getItem('access_token');
      
      if (!token) {
        this.$router.push('/login');
        return;
      }

      try {
        // Fetch user details
        const userResponse = await axios.get(`${BASE_URL}/user/dashboard/stats`, {
          headers: { 'Authorization': token }
        });
        
        this.userName = userResponse.data.username;
        this.totalQuizzesTaken = userResponse.data.totalQuizzesTaken;
        this.averageScore = userResponse.data.averageScore;
        this.subjectsExplored = userResponse.data.subjectsExplored;
        this.currentStreak = userResponse.data.currentStreak || 7; // Default to 7 if not available

      } catch (error) {
        console.error('Error fetching user data:', error);
        // Use default values if API fails
      }
    },

    async fetchRecentQuizzes() {
      // Mock data - replace with actual API call
      this.recentQuizzes = [
        {
          id: 1,
          quizName: 'Python Basics Quiz',
          subject: 'Programming',
          score: 85,
          timeAgo: '2 hours ago'
        },
        {
          id: 2,
          quizName: 'Mathematics Test',
          subject: 'Mathematics',
          score: 92,
          timeAgo: '1 day ago'
        },
        {
          id: 3,
          quizName: 'Science Quiz',
          subject: 'Physics',
          score: 65,
          timeAgo: '3 days ago'
        }
      ];
    },

    async fetchUpcomingQuizzes() {
      // Mock data - replace with actual API call
      this.upcomingQuizzes = [
        {
          id: 1,
          name: 'Advanced Python',
          subject: 'Programming',
          questions: 20
        },
        {
          id: 2,
          name: 'Calculus Basics',
          subject: 'Mathematics',
          questions: 15
        },
        {
          id: 3,
          name: 'Chemistry Quiz',
          subject: 'Chemistry',
          questions: 25
        }
      ];
    },

    getScoreClass(score) {
      if (score >= 80) return 'score-excellent';
      if (score >= 60) return 'score-good';
      return 'score-needs-improvement';
    },

    browseSubjects() {
      const userId = store.getters['auth/getUser'].id;
      this.$router.push(`/user/${userId}/subjects`);
    },

    takeQuiz() {
      const userId = store.getters['auth/getUser'].id;
      this.$router.push(`/user/${userId}/subjects`);
    },

    viewResults() {
      const userId = store.getters['auth/getUser'].id;
      this.$router.push(`/user/${userId}/quiz-attempts`);
    },

    viewReports() {
      const userId = store.getters['auth/getUser'].id;
      this.$router.push(`/user/${userId}/analytics`);
    },

    startQuiz(quiz) {
      const userId = store.getters['auth/getUser'].id;
      this.$router.push(`/user/${userId}/subjects`);
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.dashboard-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
              radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
  pointer-events: none;
}

.dashboard-title {
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.text-muted {
  color: rgba(255, 255, 255, 0.8) !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.container-fluid {
  max-width: 1400px;
  position: relative;
  z-index: 1;
}

.user-avatar {
  display: flex;
  align-items: center;
}

.avatar-circle {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  backdrop-filter: blur(10px);
}

/* Stats Cards */
.stats-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.stats-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stats-icon.quizzes-taken { background: linear-gradient(45deg, #43e97b, #38f9d7); }
.stats-icon.average-score { background: linear-gradient(45deg, #f093fb, #f5576c); }
.stats-icon.subjects { background: linear-gradient(45deg, #667eea, #764ba2); }
.stats-icon.streak { background: linear-gradient(45deg, #4facfe, #00f2fe); }

.stats-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.stats-content p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 0.9rem;
}

/* Quick Actions */
.quick-actions-card, .recent-activity-card, .upcoming-quizzes-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.quick-actions-card h4, .recent-activity-card h4, .upcoming-quizzes-card h4 {
  color: white;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.quick-action-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 1rem;
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  text-decoration: none;
}

.quick-action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  transform: translateY(-2px);
}

.quick-action-btn i {
  font-size: 1.5rem;
}

/* Recent Activity */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
}

.activity-icon.score-excellent { background: linear-gradient(45deg, #43e97b, #38f9d7); }
.activity-icon.score-good { background: linear-gradient(45deg, #4facfe, #00f2fe); }
.activity-icon.score-needs-improvement { background: linear-gradient(45deg, #f093fb, #f5576c); }

.activity-content {
  flex: 1;
}

.activity-text {
  color: white;
  margin: 0;
  font-size: 0.9rem;
  font-weight: 500;
}

.activity-time {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
}

.activity-score {
  margin-left: auto;
}

.score-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
}

.score-badge.score-excellent { background: rgba(67, 233, 123, 0.3); }
.score-badge.score-good { background: rgba(79, 172, 254, 0.3); }
.score-badge.score-needs-improvement { background: rgba(240, 147, 251, 0.3); }

/* Quiz List */
.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.quiz-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.quiz-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(5px);
}

.quiz-title {
  color: white;
  margin: 0;
  font-weight: 600;
  font-size: 0.9rem;
}

.quiz-details {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
}

.quiz-action {
  font-size: 1.2rem;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .stats-card {
    padding: 1.5rem;
  }
  
  .stats-icon {
    width: 50px;
    height: 50px;
    font-size: 1.2rem;
  }
  
  .stats-content h3 {
    font-size: 1.5rem;
  }
  
  .quick-actions-card, .recent-activity-card, .upcoming-quizzes-card {
    padding: 1.5rem;
  }
}
</style>