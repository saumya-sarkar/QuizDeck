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
              <h2 class="dashboard-title">Available Subjects</h2>
              <p class="text-muted">Learning starts with a simple click!</p>
            </div>
            <div class="d-flex align-items-center">
              <!-- Search Bar -->
              <div class="search-container">
                <div class="input-group">
                  <input 
                    type="text" 
                    class="form-control search-input" 
                    placeholder="Search..." 
                    v-model="searchQuery"
                    @input="filterSubjects"
                  >
                  <span v-if="!searchQuery" class="input-group-text search-icon">
                    <font-awesome-icon icon="search" />
                  </span>
                  <span v-if="searchQuery" class="input-group-text clear-icon" @click="clearSearch">
                    <font-awesome-icon icon="times" />
                  </span>

                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Subject Cards Grid -->
      <div class="row g-4" v-if="filteredSubjects.length > 0">
        <div 
          class="col-xl-3 col-lg-4 col-md-6" 
          v-for="subject in filteredSubjects" 
          :key="subject.id"
        >
          <UserSubjectCard 
            v-bind:subject="subject"
            v-on:view-chapters="handleViewChapters"
          />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="row">
        <div class="col-12 text-center py-5">
          <font-awesome-icon 
            :icon="searchQuery ? 'search' : 'book'" 
            class="fa-3x text-white-50 mb-3" 
          />
          <h4 class="text-white">
            'No subjects found'
          </h4>
          <p class="text-white-50">
            {{ `No subjects match "${searchQuery}". Try adjusting your search.` }}
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
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="row">
        <div class="col-12 text-center py-5">
          <div class="spinner-border text-white mb-3" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <h4 class="text-white">Loading subjects...</h4>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import UserSubjectCard from '@/components/User/UserSubjectCard.vue';
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';

export default {
  name: 'UserSubjects',
  components: {
    UserSubjectCard, 
    Navbar,
    Breadcrumb
  },
  data() {
    return {
      subjects: [],
      filteredSubjects: [],
      searchQuery: '',
      loading: false,
      // Breadcrumb items for navigation
      breadcrumbItems: [
        {
          name: 'Subjects',
          icon: 'book'
        }
      ]
    };
  },

  beforeMount() {
    // Fetch subjects from API
    this.fetchSubjects();
  },

  methods: {
    handleViewChapters(subject) {
      // Navigate to chapters page for users
      this.$router.push(`subjects/${subject.id}/chapters`);
    },

    filterSubjects() {
      let filtered = [...this.subjects];

      // Apply search filter
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(subject => 
          subject.name.toLowerCase().includes(query)
        );
      }

      this.filteredSubjects = filtered;
    },

    clearSearch() {
      this.searchQuery = '';
      this.filterSubjects();
    },

    async fetchSubjects() {
      this.loading = true;
      const token = sessionStorage.getItem('access_token');
        
      if (!token) {
        this.$store.dispatch('auth/logoutUser');
        return;
      }
      
      try {
        const response = await axios.get(`${BASE_URL}/subject`, {
          headers: {
            'Authorization': token,
          },
        });
        this.subjects = response.data;
        this.filterSubjects(); // Apply initial filtering
      } catch (error) {
        console.error('Error fetching subjects:', error);
      } finally {
        this.loading = false;
      }
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

/* Search Bar Styles */
.search-container {
  margin-right: 1rem;
}

.search-input {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  backdrop-filter: blur(10px);
  border-radius: 25px 0 0 25px !important;
  padding: 0.75rem 1rem !important;
  width: 300px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6) !important;
}

.search-input:focus {
  background: rgba(255, 255, 255, 0.25) !important;
  border-color: rgba(255, 255, 255, 0.4) !important;
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25) !important;
  color: white !important;
}

.search-icon {
  background: rgba(255, 255, 255, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-left: none !important;
  color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 0 25px 25px 0 !important;
}

.clear-icon {
  background: rgba(255, 255, 255, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-left: none !important;
  color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 0 25px 25px 0 !important;
  cursor: pointer;
}

.clear-icon:hover {
  background: rgba(255, 255, 255, 0.25) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
  color: white !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}
</style>