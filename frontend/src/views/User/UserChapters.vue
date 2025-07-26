<template>
  <div class="chapters-container">
    <Navbar />
    <div class="container-fluid py-4">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb :items="breadcrumbItems" />
      
      <!-- Header Section -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="chapters-title mb-0">{{ subjectName }} Chapters</h2>
              <p class="text-muted mb-0">{{ chapters.length }} chapters available</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Chapters List -->
      <div class="chapters-list">
        <div 
          v-for="(chapter, index) in chapters" 
          :key="chapter.id"
          class="chapter-card glass-card-minimal mb-3"
        >
          <div class="row align-items-center">
            <!-- Chapter Number & Icon -->
            <div class="col-auto">
              <div class="chapter-number">
                {{ String(index + 1).padStart(2, '0') }}
              </div>
            </div>

            <!-- Chapter Content -->
            <div class="col">
              <div class="chapter-content">
                <h5 class="chapter-title mb-1">{{ chapter.name }}</h5>
                <p class="chapter-description mb-2">{{ chapter.description }}</p>
                <div class="chapter-meta">
                  <span class="meta-item">
                    <font-awesome-icon icon="question-circle" class="me-1" />
                    {{ chapter.quizCount }} quizzes
                  </span>
                  <span v-if="chapter.isCompleted" class="badge bg-success ms-2">
                    <font-awesome-icon icon="check" class="me-1" />
                    Completed
                  </span>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="col-auto">
              <div class="chapter-actions d-flex gap-2">
                <button 
                  class="btn btn-outline-primary btn-sm glass-btn"
                  @click="handleViewQuizzes(chapter)"
                  :title="'View ' + chapter.title"
                >
                  <font-awesome-icon icon="eye" /> View
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="chapters.length === 0" class="row">
        <div class="col-12 text-center py-5">
          <font-awesome-icon icon="book" class="fa-3x text-white-50 mb-3" />
          <h4 class="text-white">No Chapters Available</h4>
          <p class="text-white-50">Chapters will appear here once they are added to this subject.</p>
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
  name: 'UserChapters',
  components: {
    Navbar,
    Breadcrumb
  },
  data() {
    return {
      subjectName: '',
      subjectId: null, 
      chapters: [],
      breadcrumbItems: []
    };
  },
  async mounted() {
    await this.fetchChapters();
    this.setupBreadcrumb();
  },
  methods: {
    
    setupBreadcrumb() {
        const userId = this.$route.params.userId;
        this.breadcrumbItems = [
        {
          name: 'Subjects',
          path: `/user/${userId}/subjects`,
          icon: 'book'
        },
        {
          name: this.subjectName || 'Subject',
          icon: 'book-open'
        }
      ];
    },

    handleViewQuizzes(chapter) {
      // Navigate to quizzes page
      this.$router.push(`chapters/${chapter.id}/quizzes`);
    },
    
    async fetchChapters() {
      const subjectId = parseInt(this.$route.params.subjectId);
      
      if (!subjectId) {
        console.warn('No subjectId found in route params');
        return;
      }
      
      const token = sessionStorage.getItem('access_token');

      if (!token) {
        store.dispatch('auth/logoutUser');
        return;
      }
      
      try {
        const response = await axios.post(`${BASE_URL}/subject`, {
          id: subjectId
        }, {
          headers: { 'Authorization': token }
        });
        console.log('Chapters fetched from API:', response.data);
        this.chapters = response.data.chapters || [];
        this.subjectName = response.data.name;
        this.subjectId = response.data.id;
      } catch (error) {
        console.error('Error fetching chapters:', error);
      }
    }
  }
};
</script>

<style scoped>
.chapters-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.chapters-container::before {
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

.chapters-title {
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-muted {
  color: rgba(255, 255, 255, 0.7) !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.glass-btn-minimal {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
}

.glass-btn-minimal:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.chapters-list {
  max-width: 100%;
}

.chapter-card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.chapter-card:hover {
  transform: translateX(8px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.glass-card-minimal {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 1.25rem;
}

.chapter-number {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  color: #ffffff;
  backdrop-filter: blur(10px);
}

.chapter-content {
  padding-left: 1rem;
}

.chapter-title {
  color: #ffffff;
  font-weight: 600;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.chapter-description {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 0.75rem;
}

.chapter-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.meta-item {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  display: flex;
  align-items: center;
}

.badge {
  font-size: 0.7rem;
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
}

.chapter-actions .btn {
  border-radius: 8px;
  padding: 0.4rem 0.7rem;
  font-size: 0.85rem;
}

.glass-btn {
  border-radius: 12px;
  font-weight: 500;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-outline-primary.glass-btn {
  color: #0d6efd;
  border-color: rgba(13, 110, 253, 0.3);
}

.btn-outline-primary.glass-btn:hover {
  color: #fff;
  background: rgba(13, 110, 253, 0.8);
  border-color: rgba(13, 110, 253, 0.8);
}

</style>