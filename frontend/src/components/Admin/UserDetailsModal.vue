<template>
  <!-- User Details Modal -->
  <div class="modal fade" id="userDetailsModal" tabindex="-1" aria-labelledby="userDetailsModalLabel" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="userDetailsModalLabel">
            <font-awesome-icon icon="user" class="me-2" />
            User Details - {{ currentUser?.full_name || currentUser?.username }}
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        
        <div class="modal-body" v-if="!loading">
          <!-- User Basic Info Section -->
          <div class="user-info-section mb-4">
            <div class="row">
              <div class="col-md-6">
                <div class="info-card glass-info-card">
                  <h6 class="card-title">
                    <font-awesome-icon icon="user" class="me-2" />
                    Personal Information
                  </h6>
                  <div class="info-grid">
                    <div class="info-item">
                      <label class="info-label">Full Name:</label>
                      <span class="info-value">{{ userDetails?.full_name || 'Not provided' }}</span>
                    </div>
                    <div class="info-item">
                      <label class="info-label">Username:</label>
                      <span class="info-value">{{ userDetails?.username }}</span>
                    </div>
                    <div class="info-item">
                      <label class="info-label">Email:</label>
                      <span class="info-value">{{ userDetails?.email }}</span>
                    </div>
                    <div class="info-item">
                      <label class="info-label">Qualification:</label>
                      <span class="info-value">{{ userDetails?.qualification || 'Not specified' }}</span>
                    </div>
                    <div class="info-item">
                      <label class="info-label">Date of Birth:</label>
                      <span class="info-value">{{ formatDate(userDetails?.date_of_birth) || 'Not provided' }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="info-card glass-info-card">
                  <h6 class="card-title">
                    <font-awesome-icon icon="chart-line" class="me-2" />
                    Account Status
                  </h6>
                  <div class="info-grid">
                    <div class="info-item">
                      <label class="info-label">Status:</label>
                      <span class="info-value">
                        <span class="badge" :class="userDetails?.is_active ? 'bg-success' : 'bg-danger'">
                          {{ userDetails?.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </span>
                    </div>
                    <div class="info-item">
                      <label class="info-label">Total Logins:</label>
                      <span class="info-value">{{ userDetails?.activity?.total_login_count || 0 }}</span>
                    </div>
                    <div class="info-item">
                      <label class="info-label">Last Login:</label>
                      <span class="info-value">{{ userDetails?.activity?.last_login || 'Never' }}</span>
                    </div>
                    <div class="info-item">
                      <label class="info-label">Current IP:</label>
                      <span class="info-value">{{ userDetails?.current_login_ip || 'N/A' }}</span>
                    </div>
                    <div class="info-item">
                      <label class="info-label">Registration:</label>
                      <span class="info-value">{{ formatDate(userDetails?.activity?.registration_date) || 'Unknown' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quiz Statistics Section -->
          <div class="quiz-stats-section mb-4">
            <div class="row">
              <div class="col-lg-4">
                <div class="stats-card glass-info-card">
                  <h6 class="card-title">
                    <font-awesome-icon icon="clipboard-list" class="me-2" />
                    Quiz Statistics
                  </h6>
                  <div class="stats-grid">
                    <div class="stat-item">
                      <div class="stat-value">{{ userDetails?.quiz_stats?.total_attempts || 0 }}</div>
                      <div class="stat-label">Total Attempts</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ userDetails?.quiz_stats?.completed_attempts || 0 }}</div>
                      <div class="stat-label">Completed</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ userDetails?.quiz_stats?.in_progress_attempts || 0 }}</div>
                      <div class="stat-label">In Progress</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ userDetails?.quiz_stats?.average_percentage || 0 }}%</div>
                      <div class="stat-label">Average Percentage</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-lg-8">
                <div class="performance-card glass-info-card">
                  <h6 class="card-title">
                    <font-awesome-icon icon="chart-pie" class="me-2" />
                    Subject-wise Performance
                  </h6>
                  <div v-if="userDetails?.subject_performance?.length > 0" class="subject-performance">
                    <div 
                      v-for="subject in userDetails.subject_performance" 
                      :key="subject.subject_name"
                      class="subject-item mb-3"
                    >
                      <div class="subject-header d-flex justify-content-between align-items-center mb-2">
                        <span class="subject-name">{{ subject.subject_name }}</span>
                        <div class="subject-stats">
                          <span class="attempts-badge">{{ subject.attempts }} attempts</span>
                          <span class="score-badge" :class="getScoreClass(subject.percentage)">
                            {{ subject.percentage }}%
                          </span>
                        </div>
                      </div>
                      <div class="progress-container">
                        <div 
                          class="progress-bar" 
                          :class="getScoreClass(subject.percentage)"
                          :style="{ width: subject.percentage + '%' }"
                        ></div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="no-performance text-center py-3">
                    <font-awesome-icon icon="chart-pie" class="fa-2x text-white-50 mb-2" />
                    <p class="text-white-50 mb-0">No quiz attempts found</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Loading State -->
        <div v-if="loading" class="modal-body text-center py-5">
          <div class="spinner-border text-white mb-3" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <h5 class="text-white">Loading user details...</h5>
        </div>

        <!-- Error State -->
        <div v-if="error" class="modal-body text-center py-5">
          <font-awesome-icon icon="exclamation-triangle" class="fa-3x text-warning mb-3" />
          <h5 class="text-white">Error Loading Details</h5>
          <p class="text-white-50">{{ error }}</p>
          <button class="btn btn-primary" @click="loadUserDetails">
            <font-awesome-icon icon="redo" class="me-2" />
            Retry
          </button>
        </div>

        <div class="modal-footer" v-if="!loading && !error">
          <button 
            type="button" 
            class="btn btn-outline-light me-auto"
            @click="toggleUserStatus"
            :disabled="statusToggling"
          >
            <span v-if="statusToggling" class="spinner-border spinner-border-sm me-2"></span>
            <font-awesome-icon :icon="userDetails?.is_active ? 'user-times' : 'user-check'" class="me-2" />
            {{ userDetails?.is_active ? 'Deactivate User' : 'Activate User' }}
          </button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Close
          </button>
          <button 
            type="button" 
            class="btn btn-primary"
            @click="viewAllAttempts"
          >
            <font-awesome-icon icon="clipboard-list" class="me-2" />
            View All Attempts
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';
import { Modal } from 'bootstrap';
import { useToast } from 'vue-toastification';
import store from '@/store';

export default {
  name: 'UserDetailsModal',
  data() {
    return {
      currentUser: null,
      userDetails: null,
      loading: false,
      statusToggling: false,
      error: null,
      modalInstance: null
    };
  },
  mounted() {
    // Initialize modal instance
    this.modalInstance = new Modal(this.$refs.modal);
    
    // Reset data when modal is hidden
    this.$refs.modal.addEventListener('hidden.bs.modal', () => {
      this.resetModal();
    });
  },
  methods: {
    show(user) {
      this.currentUser = user;
      this.modalInstance.show();
      this.loadUserDetails();
    },
    
    hide() {
      this.modalInstance.hide();
    },

    resetModal() {
      this.currentUser = null;
      this.userDetails = null;
      this.loading = false;
      this.statusToggling = false;
      this.error = null;
    },

    async loadUserDetails() {
      if (!this.currentUser) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        const token = sessionStorage.getItem('access_token');
        
        if (!token) {
          this.error = 'Authentication required';
          store.dispatch('auth/logoutUser');
          return;
        }

        const response = await axios.post(`${BASE_URL}/admin/users/details`, {
          id: this.currentUser.id
        }, {
          headers: { Authorization: token }
        });
        
        if (response.data.code === 200) {
          this.userDetails = response.data.user_details;
        } else {
          this.error = response.data.error_message || 'Failed to load user details';
        }
      } catch (error) {
        console.error('Error loading user details:', error);
        this.error = error.response?.data?.error_message || 'Failed to load user details';
      } finally {
        this.loading = false;
      }
    },

    async toggleUserStatus() {
      if (!this.userDetails) return;
      
      this.statusToggling = true;
      const toast = useToast();
      
      try {
        const token = sessionStorage.getItem('access_token');
        
        if (!token) {
          toast.error('You must be logged in.');
          store.dispatch('auth/logoutUser');
          return;
        }

        const response = await axios.patch(`${BASE_URL}/admin/users/toggle-status`, {
          id: this.userDetails.id
        }, {
          headers: { Authorization: token }
        });
        
        if (response.data.code === 200) {
          // Update local user details
          this.userDetails.is_active = response.data.is_active;
          
          // Emit event to parent component
          this.$emit('user-status-changed', {
            id: this.userDetails.id,
            is_active: response.data.is_active
          });
          
          toast.success(response.data.message);
        }
      } catch (error) {
        console.error('Error toggling user status:', error);
        toast.error(error.response?.data?.error_message || 'Failed to update user status');
      } finally {
        this.statusToggling = false;
      }
    },

    viewAllAttempts() {
      if (this.userDetails) {
        this.hide();
        this.$router.push(`/admin/users/${this.userDetails.id}/attempts`);
      }
    },

    // Utility methods
    formatDate(dateString) {
      if (!dateString) return null;
      return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },

    getScoreClass(percentage) {
      if (percentage >= 80) return 'score-excellent';
      if (percentage >= 60) return 'score-good';
      if (percentage >= 40) return 'score-average';
      return 'score-poor';
    }
  }
};
</script>

<style scoped>
/* Modal Styles */
.modal-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  color: #ffffff;
}

.modal-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem 2rem 1rem 2rem;
}

.modal-title {
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.modal-body {
  padding: 1rem 2rem;
  max-height: 70vh;
  overflow-y: auto;
}

.modal-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 2rem 2rem 2rem;
}

.btn-close {
  filter: invert(1);
  opacity: 0.8;
}

.btn-close:hover {
  opacity: 1;
}

/* Info Cards */
.glass-info-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 15px;
  padding: 1.5rem;
  height: 100%;
}

.card-title {
  color: #ffffff;
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* Info Grid */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.info-label {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  min-width: 120px;
}

.info-value {
  color: #ffffff;
  font-weight: 600;
  text-align: right;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Subject Performance */
.subject-item {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.subject-header {
  margin-bottom: 0.5rem;
}

.subject-name {
  font-weight: 600;
  color: #ffffff;
}

.subject-stats {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.attempts-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-size: 0.7rem;
}

.score-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
  color: white;
}

/* Progress Container */
.progress-container {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 10px;
  transition: width 0.5s ease;
}

/* Score Classes */
.score-excellent, .progress-bar.score-excellent {
  background: linear-gradient(90deg, #28a745, #20c997);
}

.score-good, .progress-bar.score-good {
  background: linear-gradient(90deg, #007bff, #6610f2);
}

.score-average, .progress-bar.score-average {
  background: linear-gradient(90deg, #ffc107, #fd7e14);
}

.score-poor, .progress-bar.score-poor {
  background: linear-gradient(90deg, #dc3545, #e83e8c);
}

/* Empty States */
.no-performance {
  padding: 2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-body {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .info-label {
    min-width: auto;
  }
  
  .info-value {
    text-align: left;
  }
  
  .subject-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>