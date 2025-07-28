<template>
  <div class="analytics-container">
    <Navbar />
    <div class="container-fluid py-4">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb :items="breadcrumbItems" />
      
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="analytics-title">Admin Analytics Dashboard</h2>
              <p class="text-muted">Comprehensive insights into your quiz platform</p>
            </div>
            <div>
              <button class="btn refresh-btn" @click="fetchAnalyticsData" :disabled="loading">
                <font-awesome-icon :icon="loading ? 'spinner' : 'sync-alt'" :spin="loading" />
                <span class="ms-2">Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="d-flex justify-content-center align-items-center" style="min-height: 400px;">
        <div class="text-center">
          <div class="spinner-border text-white mb-3" style="width: 3rem; height: 3rem;"></div>
          <h4 class="text-white">Loading Analytics...</h4>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger glass-alert" role="alert">
        <h4 class="alert-heading">Error Loading Analytics</h4>
        <p>{{ error }}</p>
        <button class="btn btn-outline-danger" @click="fetchAnalyticsData">
          <font-awesome-icon icon="redo" class="me-2" />
          Try Again
        </button>
      </div>

      <!-- Analytics Content -->
      <div v-else>
        <!-- Summary Stats -->
        <div class="row g-4 mb-4">
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-icon">
                <font-awesome-icon icon="users" />
              </div>
              <div class="stat-content">
                <h3>{{ totalUsers }}</h3>
                <p>Total Users</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-icon">
                <font-awesome-icon icon="clipboard-list" />
              </div>
              <div class="stat-content">
                <h3>{{ totalAttempts }}</h3>
                <p>Total Quiz Attempts</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-icon">
                <font-awesome-icon icon="book" />
              </div>
              <div class="stat-content">
                <h3>{{ activeSubjects }}</h3>
                <p>Active Subjects</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-icon">
                <font-awesome-icon icon="chart-line" />
              </div>
              <div class="stat-content">
                <h3>{{ platformAverage }}%</h3>
                <p>Platform Average</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Grid -->
        <div class="row g-4">
          <!-- Chart 1: User Registrations -->
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <canvas ref="userRegistrationsChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Chart 2: Subject Attempts -->
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <canvas ref="subjectAttemptsChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Chart 3: Difficulty Scores -->
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <canvas ref="difficultyScoresChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Chart 4: Monthly Activity -->
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <canvas ref="monthlyActivityChart"></canvas>
              </div>
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
import { useToast } from 'vue-toastification';
import * as Chart from 'chart.js';

export default {
  name: 'AdminAnalytics',
  components: {
    Navbar,
    Breadcrumb
  },
  data() {
    return {
      analyticsData: null,
      loading: true,
      error: null,
      charts: {},
      breadcrumbItems: [
        {
          name: 'Analytics',
          icon: 'chart-bar'
        }
      ]
    };
  },
  computed: {
    totalUsers() {
      return this.analyticsData?.user_registrations?.reduce((sum, item) => sum + item.count, 0) || 0;
    },
    totalAttempts() {
      return this.analyticsData?.subject_attempts?.reduce((sum, item) => sum + item.attempts, 0) || 0;
    },
    activeSubjects() {
      return this.analyticsData?.subject_attempts?.length || 0;
    },
    platformAverage() {
      if (!this.analyticsData?.difficulty_scores?.length) return 0;
      const avg = this.analyticsData.difficulty_scores.reduce((sum, item) => sum + item.avg_score, 0) / this.analyticsData.difficulty_scores.length;
      return Math.round(avg);
    }
  },
  async mounted() {
    await this.fetchAnalyticsData();
  },
  beforeUnmount() {
    // Cleanup charts
    Object.values(this.charts).forEach(chart => {
      if (chart) chart.destroy();
    });
  },
  methods: {
    async fetchAnalyticsData() {
      this.loading = true;
      this.error = null;
      
      try {
        const token = sessionStorage.getItem('access_token');
        
        if (!token) {
          store.dispatch('auth/logoutUser');
          return;
        }

        const response = await axios.get(`${BASE_URL}/admin/analytics`, {
          headers: { 'Authorization': token }
        });
        
        if (response.data.code === 200) {
          this.analyticsData = response.data.data;
          this.$nextTick(() => {
            this.createCharts();
          });
        } else {
          throw new Error(response.data.error_message || 'Failed to fetch analytics data');
        }
      } catch (err) {
        console.error('Error fetching analytics:', err);
        this.error = err.response?.data?.error_message || err.message || 'Failed to load analytics';
        const toast = useToast();
        toast.error('Failed to load analytics data');
      } finally {
        this.loading = false;
      }
    },

    createCharts() {
      // Destroy existing charts
      Object.values(this.charts).forEach(chart => {
        if (chart) chart.destroy();
      });

      this.createUserRegistrationsChart();
      this.createSubjectAttemptsChart();
      this.createDifficultyScoresChart();
      this.createMonthlyActivityChart();
    },

    createUserRegistrationsChart() {
      if (!this.$refs.userRegistrationsChart || !this.analyticsData.user_registrations?.length) return;
      
      const ctx = this.$refs.userRegistrationsChart.getContext('2d');
      
      this.charts.userRegistrations = new Chart.Chart(ctx, {
        type: 'line',
        data: {
          labels: this.analyticsData.user_registrations.map(item => {
            const [year, month] = item.month.split('-');
            return new Date(year, month - 1).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
          }),
          datasets: [{
            label: 'New User Registrations',
            data: this.analyticsData.user_registrations.map(item => item.count),
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'User Registration Trend (Last 12 Months)',
              font: { size: 16, weight: 'bold' },
              color: '#ffffff'
            },
            legend: { 
              display: false 
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { 
                stepSize: 1,
                color: '#ffffff' 
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              }
            },
            x: {
              ticks: { color: '#ffffff' },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              }
            }
          }
        }
      });
    },

    createSubjectAttemptsChart() {
      if (!this.$refs.subjectAttemptsChart || !this.analyticsData.subject_attempts?.length) return;
      
      const ctx = this.$refs.subjectAttemptsChart.getContext('2d');
      
      const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 205, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
      ];
      
      this.charts.subjectAttempts = new Chart.Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: this.analyticsData.subject_attempts.map(item => item.subject),
          datasets: [{
            data: this.analyticsData.subject_attempts.map(item => item.attempts),
            backgroundColor: colors.slice(0, this.analyticsData.subject_attempts.length),
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Quiz Attempts by Subject',
              font: { size: 16, weight: 'bold' },
              color: '#ffffff'
            },
            legend: {
              position: 'bottom',
              labels: { 
                padding: 20,
                color: '#ffffff'
              }
            }
          }
        }
      });
    },

    createDifficultyScoresChart() {
      if (!this.$refs.difficultyScoresChart || !this.analyticsData.difficulty_scores?.length) return;
      
      const ctx = this.$refs.difficultyScoresChart.getContext('2d');
      
      const difficultyColors = {
        'Easy': 'rgba(75, 192, 192, 0.8)',
        'Medium': 'rgba(255, 205, 86, 0.8)',
        'Hard': 'rgba(255, 99, 132, 0.8)'
      };
      
      this.charts.difficultyScores = new Chart.Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.analyticsData.difficulty_scores.map(item => item.difficulty),
          datasets: [{
            label: 'Average Score (%)',
            data: this.analyticsData.difficulty_scores.map(item => item.avg_score),
            backgroundColor: this.analyticsData.difficulty_scores.map(item => difficultyColors[item.difficulty] || 'rgba(153, 102, 255, 0.8)'),
            borderColor: this.analyticsData.difficulty_scores.map(item => difficultyColors[item.difficulty]?.replace('0.8', '1') || 'rgba(153, 102, 255, 1)'),
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Average Quiz Scores by Difficulty',
              font: { size: 16, weight: 'bold' },
              color: '#ffffff'
            },
            legend: { 
              display: false 
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function(value) {
                  return value + '%';
                },
                color: '#ffffff'
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              }
            },
            x: {
              ticks: { color: '#ffffff' },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              }
            }
          }
        }
      });
    },

    createMonthlyActivityChart() {
      if (!this.$refs.monthlyActivityChart || !this.analyticsData.monthly_activity?.length) return;
      
      const ctx = this.$refs.monthlyActivityChart.getContext('2d');
      
      this.charts.monthlyActivity = new Chart.Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.analyticsData.monthly_activity.map(item => {
            const [year, month] = item.month.split('-');
            return new Date(year, month - 1).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
          }),
          datasets: [{
            label: 'Total Attempts',
            data: this.analyticsData.monthly_activity.map(item => item.total_attempts),
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2
          }, {
            label: 'Completed Attempts',
            data: this.analyticsData.monthly_activity.map(item => item.completed_attempts),
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Monthly Quiz Activity',
              font: { size: 16, weight: 'bold' },
              color: '#ffffff'
            },
            legend: {
              position: 'top',
              labels: { color: '#ffffff' }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { 
                stepSize: 1,
                color: '#ffffff'
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              }
            },
            x: {
              ticks: { color: '#ffffff' },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              }
            }
          }
        }
      });
    }
  }
};
</script>

<style scoped>
.analytics-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.analytics-container::before {
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
  position: relative;
  z-index: 1;
}

.analytics-title {
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-muted {
  color: rgba(255, 255, 255, 0.8) !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  transform: translateY(-2px);
}

.glass-alert {
  background: rgba(220, 53, 69, 0.15);
  border: 1px solid rgba(220, 53, 69, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  color: #ffffff;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
  background: linear-gradient(45deg, #667eea, #764ba2);
}

.stat-content h3 {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.stat-content p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 0.9rem;
}

.chart-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.chart-container {
  height: 300px;
  position: relative;
}

@media (max-width: 768px) {
  .chart-container {
    height: 250px;
  }
}
</style>