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
              <p class="text-muted mb-0">{{ quizzes.length }} quizzes available</p>
            </div>
            <div class="d-flex gap-3 align-items-center">
            </div>
          </div>
        </div>
      </div>

      <!-- Quiz Cards View -->
      <div class="cards-view">
        <div class="row g-4">
          <div class="col-lg-4 col-md-6" v-for="quiz in quizzes" :key="quiz.id">
            <UserQuizCard 
              :quiz="quiz"
              @start-quiz="handleStartQuiz" 
            />
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="quizzes.length === 0" class="row">
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
      chapterName: '',
      subjectName: '', 
      quizzes: [],
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
        this.quizzes = response.data.quizzes || [];
        this.chapterName = response.data.name || 'Chapter';
        this.subjectName = response.data.subject_name || 'Subject';
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
</style>