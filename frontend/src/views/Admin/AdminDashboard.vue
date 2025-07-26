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
              <h2 class="dashboard-title">Admin Dashboard</h2>
              <p class="text-muted">Welcome back! Today is {{ currentTime }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Dashboard Stats Cards -->
      <div class="row g-4 mb-4">
        <div class="col-xl-3 col-md-6">
          <div class="stats-card">
            <div class="stats-icon subjects">
              <font-awesome-icon icon="book" />
            </div>
            <div class="stats-content">
              <h3>{{ totalSubjects }}</h3>
              <p>Total Subjects</p>
            </div>
          </div>
        </div>
        <div class="col-xl-3 col-md-6">
          <div class="stats-card">
            <div class="stats-icon chapters">
              <font-awesome-icon icon="list" />
            </div>
            <div class="stats-content">
              <h3>{{ totalChapters }}</h3>
              <p>Total Chapters</p>
            </div>
          </div>
        </div>
        <div class="col-xl-3 col-md-6">
          <div class="stats-card">
            <div class="stats-icon students">
              <font-awesome-icon icon="users" />
            </div>
            <div class="stats-content">
              <h3>{{ totalStudents }}</h3>
              <p>Active Students</p>
            </div>
          </div>
        </div>
        <div class="col-xl-3 col-md-6">
          <div class="stats-card">
            <div class="stats-icon tests">
              <font-awesome-icon icon="clipboard-check" />
            </div>
            <div class="stats-content">
              <h3>{{ totalTests }}</h3>
              <p>Tests Created</p>
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
                  @click="navigateToSubjects"
                >
                  <font-awesome-icon icon="book" />
                  <span>Manage Subjects</span>
                </button>
              </div>
              <div class="col-lg-3 col-md-6">
                <button 
                  class="btn quick-action-btn w-100"
                  @click="navigateToUsers"
                >
                  <font-awesome-icon icon="users" />
                  <span>View Students</span>
                </button>
              </div>
              <div class="col-lg-3 col-md-6">
                <button 
                  class="btn quick-action-btn w-100"
                  @click="navigateToTests"
                >
                  <font-awesome-icon icon="clipboard-check" />
                  <span>Create Test</span>
                </button>
              </div>
              <div class="col-lg-3 col-md-6">
                <button 
                  class="btn quick-action-btn w-100"
                  @click="navigateToReports"
                >
                  <font-awesome-icon icon="chart-line" />
                  <span>View Reports</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="row g-4">
        <div class="col-lg-8">
          <div class="recent-activity-card">
            <h4 class="mb-3">Recent Activity</h4>
            <div class="activity-list">
              <div 
                v-for="activity in recentActivities" 
                :key="activity.id" 
                class="activity-item"
              >
                <div class="activity-icon" :class="activity.type">
                  <i :class="activity.icon"></i>
                </div>
                <div class="activity-content">
                  <p class="activity-text">{{ activity.text }}</p>
                  <small class="activity-time">{{ activity.time }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="system-status-card">
            <h4 class="mb-3">System Status</h4>
            <div class="status-item">
              <span class="status-label">Server Status</span>
              <span class="status-badge online">Online</span>
            </div>
            <div class="status-item">
              <span class="status-label">Database</span>
              <span class="status-badge online">Connected</span>
            </div>
            <div class="status-item">
              <span class="status-label">Last Backup</span>
              <span class="status-badge">2 hours ago</span>
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

export default {
  name: 'AdminDashboard',
  components: {
    Navbar,
    Breadcrumb
  },
  data() {
    return {
      currentTime: new Date().toLocaleString('en-IN', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }),
      timer: null,
      totalSubjects: 0,
      totalChapters: 0,
      totalStudents: 0,
      totalTests: 0,
      recentActivities: [
        {
          id: 1,
          type: 'subject',
          icon: 'fas fa-book',
          text: 'New subject "Mathematics" was created',
          time: '2 minutes ago'
        },
        {
          id: 2,
          type: 'student',
          icon: 'fas fa-user',
          text: 'Student John Doe registered',
          time: '15 minutes ago'
        },
        {
          id: 3,
          type: 'test',
          icon: 'fas fa-clipboard-check',
          text: 'Test "Physics Quiz" was completed by 5 students',
          time: '1 hour ago'
        },
        {
          id: 4,
          type: 'chapter',
          icon: 'fas fa-list',
          text: 'Chapter "Algebra Basics" was updated',
          time: '2 hours ago'
        }
      ],
      breadcrumbItems: [] // Breadcrumb base
    };
  },

  mounted() {
    this.fetchDashboardStats();
    this.timer = setInterval(() => {
      this.currentTime = new Date().toLocaleString('en-IN', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }, 60000); // Update every minute
  },

  beforeDestroy() {
    clearInterval(this.timer);
  },

  methods: {
    async fetchDashboardStats() {
      const token = sessionStorage.getItem('access_token');
      
      if (!token) {
        this.$router.push('/login');
        return;
      }

      try {
        // You can create separate API endpoints for dashboard stats
        // For now, using dummy data
        this.totalSubjects = 12;
        this.totalChapters = 48;
        this.totalStudents = 156;
        this.totalTests = 23;
        
        // Uncomment and modify when you have actual API endpoints
        // const response = await axios.get(`${BASE_URL}/dashboard/stats`, {
        //   headers: {
        //     'Authorization': token,
        //   },
        // });
        // this.totalSubjects = response.data.subjects;
        // this.totalChapters = response.data.chapters;
        // this.totalStudents = response.data.students;
        // this.totalTests = response.data.tests;
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      }
    },

    navigateToSubjects() {
      this.$router.push('/admin/subjects');
    },

    navigateToUsers() {
      this.$router.push('/admin/users');
    },

    navigateToTests() {
      this.$router.push('/admin/tests');
    },

    navigateToReports() {
      this.$router.push('/admin/reports');
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

.stats-icon.subjects { background: linear-gradient(45deg, #667eea, #764ba2); }
.stats-icon.chapters { background: linear-gradient(45deg, #f093fb, #f5576c); }
.stats-icon.students { background: linear-gradient(45deg, #4facfe, #00f2fe); }
.stats-icon.tests { background: linear-gradient(45deg, #43e97b, #38f9d7); }

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
.quick-actions-card, .recent-activity-card, .system-status-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.quick-actions-card h4, .recent-activity-card h4, .system-status-card h4 {
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

.activity-icon.subject { background: linear-gradient(45deg, #667eea, #764ba2); }
.activity-icon.student { background: linear-gradient(45deg, #4facfe, #00f2fe); }
.activity-icon.test { background: linear-gradient(45deg, #43e97b, #38f9d7); }
.activity-icon.chapter { background: linear-gradient(45deg, #f093fb, #f5576c); }

.activity-content {
  flex: 1;
}

.activity-text {
  color: white;
  margin: 0;
  font-size: 0.9rem;
}

.activity-time {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
}

/* System Status */
.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.status-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.online {
  background: linear-gradient(45deg, #43e97b, #38f9d7);
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
  
  .quick-actions-card, .recent-activity-card, .system-status-card {
    padding: 1.5rem;
  }
}
</style>