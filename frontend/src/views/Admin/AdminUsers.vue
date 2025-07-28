<template>
  <div class="users-container">
    <Navbar />
    <div class="container-fluid py-4">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb :items="breadcrumbItems" />
      
      <!-- Header Section -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="users-title mb-0">User Management</h2>
              <p class="text-muted mb-0">{{ users.length }} users registered</p>
            </div>
            <div class="d-flex gap-3 align-items-center">
              <!-- Search Bar -->
              <div class="search-container">
                <div class="input-group">
                  <input 
                    type="text" 
                    class="form-control search-input" 
                    placeholder="Search users..." 
                    v-model="searchQuery"
                    @input="filterUsers"
                  >
                  <span v-if="!searchQuery" class="input-group-text search-icon">
                    <font-awesome-icon icon="search" />
                  </span>
                  <span v-if="searchQuery" class="input-group-text clear-icon" @click="clearSearch">
                    <font-awesome-icon icon="times" />
                  </span>
                </div>
              </div>
              
              <!-- Filter Dropdown -->
              <div class="filter-container">
                <select class="form-select filter-select" v-model="statusFilter" @change="filterUsers">
                  <option value="all">All Users</option>
                  <option value="active">Active Users</option>
                  <option value="inactive">Inactive Users</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Users Table -->
      <div class="users-table-container glass-card">
        <div class="table-responsive">
          <table class="table table-hover users-table">
            <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">User Info</th>
                <th scope="col">Contact</th>
                <th scope="col">Activity</th>
                <th scope="col">Quiz Stats</th>
                <th scope="col">Status</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(user, index) in filteredUsers" 
                :key="user.id"
                class="user-row"
                :class="{ 'inactive-user': !user.is_active }"
              >
                <td class="user-index">{{ index + 1 }}</td>
                
                <!-- User Info -->
                <td class="user-info">
                  <div class="user-details">
                    <div class="user-name">
                      <strong>{{ user.full_name || user.username }}</strong>
                      <span v-if="user.qualification" class="qualification-badge">
                        {{ user.qualification }}
                      </span>
                    </div>
                    <div class="user-username text-muted">@{{ user.username }}</div>
                  </div>
                </td>
                
                <!-- Contact -->
                <td class="user-contact">
                  <div class="contact-info">
                    <div class="email">
                      <font-awesome-icon icon="envelope" class="me-1" />
                      {{ user.email }}
                    </div>
                  </div>
                </td>
                
                <!-- Activity -->
                <td class="user-activity">
                  <div class="activity-info">
                    <div class="last-login">
                      <small class="text-muted">Last Login:</small><br>
                      <span class="login-time">{{ user.last_login }}</span>
                    </div>
                  </div>
                </td>
                
                <!-- Quiz Stats -->
                <td class="quiz-stats">
                  <div class="stats-grid">
                    <div class="stat-item">
                      <div class="stat-value">{{ user.total_attempts }}</div>
                      <div class="stat-label">Attempts</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value">{{ user.average_score }}%</div>
                      <div class="stat-label">Percentage</div>
                    </div>
                  </div>
                </td>
                
                <!-- Status -->
                <td class="user-status">
                  <div class="status-container">
                    <span 
                      class="badge status-badge"
                      :class="user.is_active ? 'bg-success' : 'bg-danger'"
                    >
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </div>
                </td>
                
                <!-- Actions -->
                <td class="user-actions">
                  <div class="btn-group" role="group">
                    <button 
                      class="btn btn-outline-primary btn-sm"
                      @click="viewUserDetails(user)"
                      :title="`View ${user.username} details`"
                    >
                      <font-awesome-icon icon="eye" />
                      Details
                    </button>
                    <button 
                      class="btn btn-outline-info btn-sm"
                      @click="viewUserAttempts(user)"
                      :title="`View ${user.username} quiz attempts`"
                    >
                      <font-awesome-icon icon="clipboard-list" />
                      Attempts
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Empty State -->
        <div v-if="filteredUsers.length === 0 && !loading" class="empty-state text-center py-5">
          <font-awesome-icon 
            :icon="searchQuery ? 'search' : 'users'" 
            class="fa-3x text-white-50 mb-3" 
          />
          <h4 class="text-white">
            {{ searchQuery ? 'No users found' : 'No users registered' }}
          </h4>
          <p class="text-white-50">
            {{ searchQuery ? `No users match "${searchQuery}". Try adjusting your search.` : 'Users will appear here once they register.' }}
          </p>
          <button 
            v-if="searchQuery" 
            class="btn btn-outline-light mt-3"
            @click="clearSearch"
          >
            <font-awesome-icon icon="times" class="me-2" />
            Clear Search
          </button>
        </div>
        
        <!-- Loading State -->
        <div v-if="loading" class="loading-state text-center py-5">
          <div class="spinner-border text-white mb-3" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <h4 class="text-white">Loading users...</h4>
        </div>
      </div>
    </div>

    <!-- User Details Modal -->
    <UserDetailsModal
      ref="userDetailsModal"
      @user-status-changed="handleUserStatusChanged"
    />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import UserDetailsModal from '@/components/Admin/UserDetailsModal.vue';
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';
import { useToast } from 'vue-toastification';
import store from '@/store';

export default {
  name: 'AdminUsers',
  components: {
    Navbar,
    Breadcrumb,
    UserDetailsModal
  },
  data() {
    return {
      users: [],
      filteredUsers: [],
      searchQuery: '',
      statusFilter: 'all',
      loading: false,
      breadcrumbItems: [
        {
          name: 'Users',
          icon: 'users'
        }
      ]
    };
  },

  beforeMount() {
    this.fetchUsers();
  },

  methods: {
    async fetchUsers() {
      this.loading = true;
      const token = sessionStorage.getItem('access_token');
        
      if (!token) {
        store.dispatch('auth/logoutUser');
        return;
      }
      
      try {
        const response = await axios.get(`${BASE_URL}/admin/users`, {
          headers: {
            'Authorization': token,
          },
        });
        
        if (response.data.code === 200) {
          this.users = response.data.users;
          this.filterUsers();
        }
      } catch (error) {
        console.error('Error fetching users:', error);
        const toast = useToast();
        toast.error('Failed to fetch users');
      } finally {
        this.loading = false;
      }
    },

    filterUsers() {
      let filtered = [...this.users];

      // Apply search filter
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(user => 
          user.username.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query) ||
          (user.full_name && user.full_name.toLowerCase().includes(query))
        );
      }

      // Apply status filter
      if (this.statusFilter !== 'all') {
        if (this.statusFilter === 'active') {
          filtered = filtered.filter(user => user.is_active);
        } else if (this.statusFilter === 'inactive') {
          filtered = filtered.filter(user => !user.is_active);
        }
      }

      this.filteredUsers = filtered;
    },

    clearSearch() {
      this.searchQuery = '';
      this.filterUsers();
    },

    viewUserDetails(user) {
      this.$refs.userDetailsModal.show(user);
    },

    viewUserAttempts(user) {
      this.$router.push(`/admin/users/${user.id}/attempts`);
    },

    handleUserStatusChanged(updatedUser) {
      // Update the user in the list
      const userIndex = this.users.findIndex(u => u.id === updatedUser.id);
      if (userIndex !== -1) {
        this.users[userIndex] = { ...this.users[userIndex], ...updatedUser };
        this.filterUsers();
      }
    }
  }
};
</script>

<style scoped>
.users-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.users-container::before {
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
  max-width: 1400px;
  position: relative;
  z-index: 1;
}

.users-title {
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
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

/* Search and Filter Controls */
.search-container {
  margin-right: 1rem;
}

.search-input, .filter-select {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  backdrop-filter: blur(10px);
  border-radius: 25px !important;
  padding: 0.75rem 1rem !important;
}

.search-input {
  width: 300px;
  border-radius: 25px 0 0 25px !important;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6) !important;
}

.search-input:focus, .filter-select:focus {
  background: rgba(255, 255, 255, 0.25) !important;
  border-color: rgba(255, 255, 255, 0.4) !important;
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25) !important;
  color: white !important;
}

.search-icon, .clear-icon {
  background: rgba(255, 255, 255, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-left: none !important;
  color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 0 25px 25px 0 !important;
}

.clear-icon {
  cursor: pointer;
}

.clear-icon:hover {
  background: rgba(255, 255, 255, 0.25) !important;
  color: white !important;
}

.filter-select {
  width: 150px;
}

.filter-select option {
  background: #2c3e50;
  color: white;
}

/* Table Styles */
.users-table-container {
  overflow-x: auto;
}

.users-table {
  color: white;
  margin: 0;
}

.users-table thead th {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-weight: 600;
  border: none;
  padding: 1rem 0.75rem;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.users-table tbody td {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  padding: 1rem 0.75rem;
}

.user-row {
  transition: all 0.3s ease;
}

.user-row:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.user-row.inactive-user {
  opacity: 0.7;
}

.user-index {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

/* User Info */
.user-details {
  min-width: 200px;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.qualification-badge {
  background: rgba(0, 123, 255, 0.3);
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.user-username {
  font-size: 0.85rem;
}

/* Contact Info */
.contact-info {
  min-width: 200px;
}

.email {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
}

/* Activity Info */
.activity-info {
  min-width: 140px;
}

.login-time {
  font-size: 0.85rem;
  color: white;
}

.login-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 0.7rem;
  padding: 0.3rem 0.6rem;
}

/* Quiz Stats */
.stats-grid {
  display: flex;
  gap: 1rem;
  min-width: 180px;
}

.stat-item {
  text-align: left;
}

.stat-value {
  font-weight: 700;
  font-size: 1rem;
  color: white;
}

.stat-label {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Status */
.status-container {
  display: flex;
  justify-content: left;
  align-items: left;
  min-width: 100px;
}

.status-badge {
  font-size: 0.75rem;
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  font-weight: 600;
}

/* Actions */
.user-actions {
  min-width: 140px;
}

.btn-group .btn {
  font-size: 0.8rem;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-weight: 500;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  margin-right: 0.25rem;
}

.btn-group .btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.btn-outline-primary.btn:hover {
  background: rgba(13, 110, 253, 0.8);
  border-color: rgba(13, 110, 253, 0.8);
}

.btn-outline-info.btn:hover {
  background: rgba(23, 162, 184, 0.8);
  border-color: rgba(23, 162, 184, 0.8);
}

/* Empty and Loading States */
.empty-state, .loading-state {
  padding: 3rem 1rem;
}
</style>