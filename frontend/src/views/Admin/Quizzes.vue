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
              <button 
                class="btn add-quiz-btn d-flex align-items-center gap-2"
                @click="showQuizCreateModal"
              >
                <font-awesome-icon icon="plus" />
                <span class="d-none d-sm-inline">Add Quiz</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Quiz Cards View -->
      <div class="cards-view">
        <div class="row g-4">
          <div class="col-lg-4 col-md-6" v-for="quiz in quizzes" :key="quiz.id">
            <QuizCard 
              :quiz="quiz"
              v-on:view-quiz="handleViewQuiz"
              v-on:sent-edit-quiz="showQuizEditModal"
              v-on:sent-delete-quiz="showQuizDeleteModal"
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
    <!-- Quiz Create Modal Component -->
    <QuizCreateModal 
      ref="quizCreate"
      @quiz-created="handleQuizCreated"
    />
    <!-- Quiz Edit Modal Component -->
    <QuizEditModal 
      ref="quizEdit"
      @quiz-edited="handleQuizEdited"
    />
    <!-- Quiz Delete Modal Component -->
    <QuizDeleteModal
      ref="quizDelete"
      @quiz-deleted="handleQuizDeleted"
    />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import QuizCard from '@/components/Admin/QuizCard.vue';
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';
import { defineAsyncComponent } from 'vue';
import { useToast } from 'vue-toastification';

// Lazy load components for better performance
const QuizCreateModal = defineAsyncComponent(() =>
  import(/* webpackChunkName: "quiz-create-modal", webpackPrefetch: true */ '@/components/Admin/QuizCreateModal.vue')
);

const QuizEditModal = defineAsyncComponent(() =>
  import(/* webpackChunkName: "quiz-edit-modal", webpackPrefetch: true */ '@/components/Admin/QuizEditModal.vue')
);

const QuizDeleteModal = defineAsyncComponent(() =>
  import(/* webpackChunkName: "quiz-delete-modal", webpackPrefetch: true */ '@/components/Admin/QuizDeleteModal.vue')
);

export default {
  name: 'Quizzes',
  components: {
    Navbar,
    Breadcrumb,
    QuizCard,
    QuizCreateModal,
    QuizEditModal,
    QuizDeleteModal
  },
  data() {
    return {
      chapter_id: null,
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
      const subjectId = this.$route.params.subjectId;
      const chapterId = this.$route.params.chapterId;
      
      this.breadcrumbItems = [
        {
          name: 'Subjects',
          path: '/admin/subjects',
          icon: 'book'
        },
        {
          name: this.subjectName || 'Chapters',
          path: `/admin/subjects/${subjectId}/chapters`,
          icon: 'book-open'
        },
        {
          name: this.chapterName || 'Chapter',
          icon: 'question-circle'
        }
      ];
    },
    
    showQuizCreateModal() {
      this.$refs.quizCreate.show({
        chapter_name: this.chapterName,
        chapter_id: this.chapter_id
      });
    },

    handleQuizCreated(newQuiz) {
      // Show success toast notification
      const toast = useToast();
      toast.success(`Quiz ${newQuiz.name} created successfully.`, { theme: 'light' });
      // Add to the list
      if (newQuiz) {
        this.quizzes.push(newQuiz);
      } else {
        // If the response doesn't contain the data, refresh the list
        this.fetchQuizzes();
      }
    },

    showQuizEditModal(quizToEdit) {
      this.$refs.quizEdit.show(quizToEdit);
    },

    handleQuizEdited(updatedQuiz) {
      // Show success toast notification
      const toast = useToast();
      toast.success(`Quiz ${updatedQuiz.oldName} updated successfully.`, { theme: 'light' });
      this.fetchQuizzes();
    },

    showQuizDeleteModal(quizToDelete) {
      this.$refs.quizDelete.show(quizToDelete);
    },

    handleQuizDeleted(deletedQuiz) {
      // Show success toast notification
      const toast = useToast();
      toast.success(`Quiz ${deletedQuiz.name} deleted successfully.`, { theme: 'light' });
      // Remove the deleted quiz from the list
      this.quizzes = this.quizzes.filter(quiz => quiz.id !== deletedQuiz.id);
    },
    
    
    handleViewQuiz(quiz) {
      this.$router.push(`quizzes/${quiz.id}/questions`);
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

.add-quiz-btn {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.add-quiz-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.cards-view .quiz-card-container {
  padding: 0;
  background: transparent;
}

.cards-view .quiz-card-container::before {
  display: none;
}
</style>