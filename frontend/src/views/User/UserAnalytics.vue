<template>
  <div class="analytics-container">
    <Navbar />
    <div class="container-fluid py-4">
      <!-- Breadcrumb -->
      <Breadcrumb :items="breadcrumbItems" />

      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12 d-flex justify-content-between align-items-center">
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

      <!-- Loading -->
      <div v-if="loading" class="d-flex justify-content-center align-items-center" style="min-height: 400px;">
        <div class="text-center">
          <div class="spinner-border text-white mb-3" style="width: 3rem; height: 3rem;"></div>
          <h4 class="text-white">Loading Your Analytics...</h4>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-danger glass-alert" role="alert">
        <h4 class="alert-heading">Error Loading Analytics</h4>
        <p>{{ error }}</p>
        <button class="btn btn-outline-danger" @click="fetchAnalyticsData">
          <font-awesome-icon icon="redo" class="me-2" />
          Try Again
        </button>
      </div>

      <!-- Main Analytics -->
      <div v-else>
        <!-- Stat Cards -->
        <!-- <div class="row g-4 mb-4">
          <div class="col-md-3" v-for="(stat, index) in statCards" :key="index">
            <div class="stat-card">
              <div class="stat-icon">
                <font-awesome-icon :icon="stat.icon" />
              </div>
              <div class="stat-content">
                <h3>{{ stat.value }}</h3>
                <p>{{ stat.label }}</p>
              </div>
            </div>
          </div>
        </div> -->

        <!-- Chart Components -->
        <div class="row g-4">
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <SubjectPerformanceChart :subject-performance="analyticsData.subject_performance" />
              </div>
            </div>
          </div>
          <!-- <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <WeeklyActivityChart :weekly-activity="analyticsData.weekly_activity" />
              </div>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <ScoreDistributionChart :score-distribution="analyticsData.score_distribution" />
              </div>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="chart-card">
              <div class="chart-container">
                <RecentTrendsChart :recent-trends="analyticsData.recent_trends" />
              </div>
            </div>
          </div> -->
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

// Chart Components
import SubjectPerformanceChart from '@/components/User/charts/SubjectPerformanceChart.vue';
// import WeeklyActivityChart from '@/components/User/charts/WeeklyActivityChart.vue';
// import ScoreDistributionChart from '@/components/User/charts/ScoreDistributionChart.vue';
// import RecentTrendsChart from '@/components/User/charts/RecentTrendsChart.vue';

export default {
  name: 'UserAnalytics',
  components: {
    Navbar,
    Breadcrumb,
    SubjectPerformanceChart,
    // WeeklyActivityChart,
    // ScoreDistributionChart,
    // RecentTrendsChart
  },
  data() {
    return {
      analyticsData: null,
      loading: true,
      error: null,
      breadcrumbItems: [{ name: 'My Analytics', icon: 'chart-bar' }]
    };
  },
  computed: {
    statCards() {
      const subjectPerformance = this.analyticsData?.subject_performance || [];
      const totalAttempts = subjectPerformance.reduce((sum, item) => sum + item.attempts, 0);
      const avgScore = subjectPerformance.length
        ? Math.round(subjectPerformance.reduce((sum, item) => sum + item.avg_score, 0) / subjectPerformance.length)
        : 0;

      return [
        { icon: 'clipboard-check', label: 'Total Attempts', value: totalAttempts },
        { icon: 'trophy', label: 'Overall Average', value: `${avgScore}%` },
        { icon: 'book', label: 'Subjects Attempted', value: subjectPerformance.length },
        { icon: 'chart-line', label: 'Recent Quizzes', value: this.analyticsData?.recent_trends?.length || 0 }
      ];
    }
  },
  async mounted() {
    await this.fetchAnalyticsData();
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
          headers: { Authorization: token }
        });

        if (response.data.code === 200) {
          this.analyticsData = response.data.data;
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