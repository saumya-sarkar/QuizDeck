<template>
  <div class="quizzes-container">
    <Navbar />
    <div class="container-fluid py-4">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb :items="breadcrumbItems" />
      
      <!-- Header Section -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="quizzes-title mb-0">{{ chapterName }} Quizzes</h2>
              <p class="text-muted mb-0">{{ filteredQuizzes.length }} of {{ quizzes.length }} quizzes available</p>
            </div>
            <div class="d-flex align-items-center gap-3">
              <!-- Status Filter Dropdown -->
              <div class="filter-container">
                <select 
                  class="form-select status-filter" 
                  v-model="statusFilter" 
                  @change="filterQuizzes"
                >
                  <option value="All">All Status</option>
                  <option value="Active">Active/Available</option>
                  <option value="Upcoming">Upcoming</option>
                  <option value="Ended">Ended</option>
                </select>
              </div>
              
              <!-- Search Bar -->
              <div class="search-container">
                <div class="input-group">
                  <input 
                    type="text" 
                    class="form-control search-input" 
                    placeholder="Search quizzes..." 
                    v-model="searchQuery"
                    @input="filterQuizzes"
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

      <!-- Quiz Cards View -->
      <div class="cards-view" v-if="filteredQuizzes.length > 0">
        <div class="row g-4">
          <div class="col-lg-4 col-md-6" v-for="quiz in filteredQuizzes" :key="quiz.id">
            <UserQuizCard 
              :quiz="quiz"
              @start-quiz="handleStartQuiz" 
              @auto-refresh="handleAutoRefresh"
            />
          </div>
        </div>
      </div>

      <!-- Empty State - No Quizzes Found -->
      <div v-else-if="quizzes.length > 0 && filteredQuizzes.length === 0" class="row">
        <div class="col-12 text-center py-5">
          <font-awesome-icon icon="search" class="fa-3x text-white-50 mb-3" />
          <h4 class="text-white">No quizzes found</h4>
          <p class="text-white-50">
            No quizzes match your current filters. Try adjusting your search or status filter.
          </p>
          <button 
            class="btn btn-outline-light mt-3"
            @click="clearSearch"
          >
            <font-awesome-icon icon="times" class="me-2" />
            Clear Filters
          </button>
        </div>
      </div>

      <!-- Empty State - No Quizzes Available -->
      <div v-else-if="quizzes.length === 0" class="row">
        <div class="col-12 text-center py-5">
          <font-awesome-icon icon="question-circle" class="fa-3x text-white-50 mb-3" />
          <h4 class="text-white">No Quizzes Available</h4>
          <p class="text-white-50">Quizzes will appear here once they are added to this chapter.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import UserQuizCard from '@/components/User/UserQuizCard.vue';
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';
import store from '@/store';
import { useToast } from 'vue-toastification';


export default {
  name: 'UserQuizzes',
  components: {
    Navbar,
    Breadcrumb,
    UserQuizCard
  },
  data() {
    return {
      chapter_id: null,
      chapterName: '',
      subjectName: '', 
      quizzes: [],
      filteredQuizzes: [],
      searchQuery: '',
      statusFilter: 'All',
      breadcrumbItems: []
    };
  },
  async mounted() {
    await this.fetchQuizzes();
    this.setupBreadcrumb();
  },
  methods: {
    setupBreadcrumb() {
      const userId = this.$route.params.userId;
      const subjectId = this.$route.params.subjectId;
      const chapterId = this.$route.params.chapterId;
      
      this.breadcrumbItems = [
        {
          name: 'Subjects',
          path: `/user/${userId}/subjects`,
          icon: 'book'
        },
        {
          name: this.subjectName || 'Chapters',
          path: `/user/${userId}/subjects/${subjectId}/chapters`,
          icon: 'book-open'
        },
        {
          name: this.chapterName || 'Chapter',
          icon: 'question-circle'
        }
      ];
    },

    filterQuizzes() {
      let filtered = [...this.quizzes];

      // Apply status filter
      if (this.statusFilter !== 'All') {
        filtered = filtered.filter(quiz => {
          const status = quiz.quiz_status;
          if (this.statusFilter === 'Active') {
            return status === 'Active' || status === 'Available';
          }
          return status === this.statusFilter;
        });
      }

      // Apply search filter
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(quiz => 
          quiz.name.toLowerCase().includes(query) ||
          quiz.difficulty.toLowerCase().includes(query) ||
          quiz.quiz_type.toLowerCase().includes(query)
        );
      }

      this.filteredQuizzes = filtered;
    },

    clearSearch() {
      this.searchQuery = '';
      this.statusFilter = 'All';
      this.filterQuizzes();
    },

    handleAutoRefresh() {
      console.log('Auto-refresh triggered');
      setTimeout(() => {
        this.fetchQuizzes();
      }, 3000);
    },
      
    handleStartQuiz(quiz) {
      const toast = useToast();
      const userId = this.$route.params.userId;
      if (!userId) {
        toast.error('No userId found in route params');
        return;
      }
      // if ( userId !== this.$store.getters['auth/getUser'].id) {
      //   toast.error('User ID mismatch');
      //   store.dispatch('auth/logoutUser');
      //   return;
      // }
      this.$router.push(`/user/${userId}/quiz/${quiz.id}/take`);
    },
    
    async fetchQuizzes() {
      const chapterId = this.$route.params.chapterId;
      
      if (!chapterId) {
        console.warn('No chapterId found in route params');
        return;
      }
      
      const token = sessionStorage.getItem('access_token');

      if (!token) {
        store.dispatch('auth/logoutUser');
        return;
      }
      
      try {
        const response = await axios.post(`${BASE_URL}/chapter`, {
          id: chapterId
        }, {
          headers: { 'Authorization': token }
        });
        
        console.log('Quizzes fetched from API:', response.data.quizzes);
        this.quizzes = response.data.quizzes;
        this.chapterName = response.data.name;
        this.subjectName = response.data.subject_name;
        this.chapter_id = response.data.id;
        this.filterQuizzes(); // Apply initial filtering
      } catch (error) {
        console.error('Error fetching quizzes:', error);
      }
    }
  }
};
</script>

<style scoped>
.quizzes-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.quizzes-container::before {
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

.quizzes-title {
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-muted {
  color: rgba(255, 255, 255, 0.7) !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.cards-view .quiz-card-container {
  padding: 0;
  background: transparent;
}

.cards-view .quiz-card-container::before {
  display: none;
}

/* Filter and Search Styles */
.filter-container {
  margin-right: 1rem;
}

.status-filter {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  backdrop-filter: blur(10px);
  border-radius: 25px !important;
  padding: 0.75rem 1rem !important;
  min-width: 160px;
  font-size: 0.9rem;
}

.status-filter:focus {
  background: rgba(255, 255, 255, 0.25) !important;
  border-color: rgba(255, 255, 255, 0.4) !important;
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25) !important;
  color: white !important;
}

.status-filter option {
  background: #4a5568 !important;
  color: white !important;
  padding: 0.5rem;
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