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
              <h2 class="analytics-title">My Performance Dashboard</h2>
              <p class="text-muted">Track your quiz performance and learning progress</p>
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
          <h4 class="text-white">Loading Your Analytics...</h4>
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
                <font-awesome-icon icon="clipboard-check" />
              </div>
              <div class="stat-content">
                <h3>{{ totalAttempts }}</h3>
                <p>Total Attempts</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-icon">
                <font-awesome-icon icon="trophy" />
              </div>
              <div class="stat-content">
                <h3>{{ overallAverage }}%</h3>
                <p>Overall Average</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-icon">
                <font-awesome-icon icon="book" />
              </div>
              <div class="stat-content">
                <h3>{{ subjectsAttempted }}</h3>
                <p>Subjects Attempted</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-icon">
                <font-awesome-icon icon="chart-line" />
              </div>
              <div class="stat-content">
                <h3>{{ recentQuizzes }}</h3>
                <p>Recent Quizzes</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Grid -->
        <div class="row g-4">
          <!-- Chart 1: Subject Performance -->
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <canvas ref="subjectPerformanceChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Chart 2: Weekly Activity -->
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <canvas ref="weeklyActivityChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Chart 3: Score Distribution -->
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <canvas ref="scoreDistributionChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Chart 4: Recent Trends -->
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <canvas ref="recentTrendsChart"></canvas>
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
  name: 'UserAnalytics',
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
          name: 'My Analytics',
          icon: 'chart-bar'
        }
      ]
    };
  },
  computed: {
    totalAttempts() {
      return this.analyticsData?.subject_performance?.reduce((sum, item) => sum + item.attempts, 0) || 0;
    },
    overallAverage() {
      if (!this.analyticsData?.subject_performance?.length) return 0;
      const avg = this.analyticsData.subject_performance.reduce((sum, item) => sum + item.avg_score, 0) / this.analyticsData.subject_performance.length;
      return Math.round(avg);
    },
    subjectsAttempted() {
      return this.analyticsData?.subject_performance?.length || 0;
    },
    recentQuizzes() {
      return this.analyticsData?.recent_trends?.length || 0;
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

        const response = await axios.get(`${BASE_URL}/user/analytics`, {
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

      this.createSubjectPerformanceChart();
      this.createWeeklyActivityChart();
      this.createScoreDistributionChart();
      this.createRecentTrendsChart();
    },

    createSubjectPerformanceChart() {
      if (!this.$refs.subjectPerformanceChart || !this.analyticsData.subject_performance?.length) return;
      
      const ctx = this.$refs.subjectPerformanceChart.getContext('2d');
      
      this.charts.subjectPerformance = new Chart.Chart(ctx, {
        type: 'radar',
        data: {
          labels: this.analyticsData.subject_performance.map(item => item.subject),
          datasets: [{
            label: 'Average Score (%)',
            data: this.analyticsData.subject_performance.map(item => item.avg_score),
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderWidth: 3,
            pointBackgroundColor: 'rgba(54, 162, 235, 1)',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Performance by Subject (Last 6 Months)',
              font: { size: 16, weight: 'bold' },
              color: '#ffffff'
            },
            legend: { 
              display: false 
            }
          },
          scales: {
            r: {
              beginAtZero: true,
              max: 100,
              ticks: {
                stepSize: 20,
                callback: function(value) {
                  return value + '%';
                },
                color: '#ffffff'
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.2)'
              },
              angleLines: {
                color: 'rgba(255, 255, 255, 0.2)'
              },
              pointLabels: {
                color: '#ffffff'
              }
            }
          }
        }
      });
    },

    createWeeklyActivityChart() {
      if (!this.$refs.weeklyActivityChart || !this.analyticsData.weekly_activity?.length) return;
      
      const ctx = this.$refs.weeklyActivityChart.getContext('2d');
      
      this.charts.weeklyActivity = new Chart.Chart(ctx, {
        type: 'line',
        data: {
          labels: this.analyticsData.weekly_activity.map(item => `Week ${item.week.split('-W')[1]}`),
          datasets: [{
            label: 'Quiz Attempts',
            data: this.analyticsData.weekly_activity.map(item => item.attempts),
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            yAxisID: 'y'
          }, {
            label: 'Average Score (%)',
            data: this.analyticsData.weekly_activity.map(item => item.avg_score),
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            borderWidth: 3,
            fill: false,
            tension: 0.4,
            yAxisID: 'y1'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Weekly Quiz Activity (Last 8 Weeks)',
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
              type: 'linear',
              display: true,
              position: 'left',
              beginAtZero: true,
              title: {
                display: true,
                text: 'Quiz Attempts',
                color: '#ffffff'
              },
              ticks: { color: '#ffffff' },
              grid: { color: 'rgba(255, 255, 255, 0.1)' }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              min: 0,
              max: 100,
              title: {
                display: true,
                text: 'Average Score (%)',
                color: '#ffffff'
              },
              grid: {
                drawOnChartArea: false,
              },
              ticks: { color: '#ffffff' }
            },
            x: {
              ticks: { color: '#ffffff' },
              grid: { color: 'rgba(255, 255, 255, 0.1)' }
            }
          }
        }
      });
    },

    createScoreDistributionChart() {
      if (!this.$refs.scoreDistributionChart || !this.analyticsData.score_distribution?.length) return;
      
      const ctx = this.$refs.scoreDistributionChart.getContext('2d');
      
      const scoreColors = {
        '90-100%': 'rgba(76, 175, 80, 0.8)',
        '80-89%': 'rgba(139, 195, 74, 0.8)',
        '70-79%': 'rgba(255, 193, 7, 0.8)',
        '60-69%': 'rgba(255, 152, 0, 0.8)',
        '50-59%': 'rgba(255, 87, 34, 0.8)',
        'Below 50%': 'rgba(244, 67, 54, 0.8)'
      };
      
      this.charts.scoreDistribution = new Chart.Chart(ctx, {
        type: 'pie',
        data: {
          labels: this.analyticsData.score_distribution.map(item => item.range),
          datasets: [{
            data: this.analyticsData.score_distribution.map(item => item.count),
            backgroundColor: this.analyticsData.score_distribution.map(item => scoreColors[item.range] || 'rgba(158, 158, 158, 0.8)'),
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
              text: 'Score Distribution',
              font: { size: 16, weight: 'bold' },
              color: '#ffffff'
            },
            legend: {
              position: 'bottom',
              labels: { 
                padding: 20,
                color: '#ffffff'
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = ((context.parsed / total) * 100).toFixed(1);
                  return `${context.label}: ${context.parsed} (${percentage}%)`;
                }
              }
            }
          }
        }
      });
    },

    createRecentTrendsChart() {
      if (!this.$refs.recentTrendsChart || !this.analyticsData.recent_trends?.length) return;
      
      const ctx = this.$refs.recentTrendsChart.getContext('2d');
      
      this.charts.recentTrends = new Chart.Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.analyticsData.recent_trends.map(item => 
            item.quiz.length > 15 ? item.quiz.substring(0, 15) + '...' : item.quiz
          ),
          datasets: [{
            label: 'Score (%)',
            data: this.analyticsData.recent_trends.map(item => item.score),
            backgroundColor: this.analyticsData.recent_trends.map(item => {
              if (item.score >= 80) return 'rgba(76, 175, 80, 0.8)';
              if (item.score >= 60) return 'rgba(255, 193, 7, 0.8)';
              return 'rgba(244, 67, 54, 0.8)';
            }),
            borderColor: this.analyticsData.recent_trends.map(item => {
              if (item.score >= 80) return 'rgba(76, 175, 80, 1)';
              if (item.score >= 60) return 'rgba(255, 193, 7, 1)';
              return 'rgba(244, 67, 54, 1)';
            }),
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Recent Quiz Performance',
              font: { size: 16, weight: 'bold' },
              color: '#ffffff'
            },
            legend: { 
              display: false 
            },
            tooltip: {
              callbacks: {
                afterLabel: (context) => {
                  const item = this.analyticsData.recent_trends[context.dataIndex];
                  return `Date: ${item.date}`;
                }
              }
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
              grid: { color: 'rgba(255, 255, 255, 0.1)' }
            },
            x: {
              ticks: {
                maxRotation: 45,
                minRotation: 45,
                color: '#ffffff'
              },
              grid: { color: 'rgba(255, 255, 255, 0.1)' }
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