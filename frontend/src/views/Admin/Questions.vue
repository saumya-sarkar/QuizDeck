<template>
  <div class="questions-container">
    <Navbar />
    <div class="container-fluid py-4">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb :items="breadcrumbItems" />
      
      <!-- Header Section -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="questions-title mb-0">{{ quizName }} Questions</h2>
              <p class="text-muted mb-0">{{ filteredQuestions.length }} of {{ questions.length }} questions available</p>
            </div>
            <div class="d-flex align-items-center">
              <!-- Search Bar -->
              <div class="search-container">
                <div class="input-group">
                  <input 
                    type="text" 
                    class="form-control search-input" 
                    placeholder="Search questions..." 
                    v-model="searchQuery"
                    @input="filterQuestions"
                  >
                  <span v-if="!searchQuery" class="input-group-text search-icon">
                    <font-awesome-icon icon="search" />
                  </span>
                  <span v-if="searchQuery" class="input-group-text clear-icon" @click="clearSearch">
                    <font-awesome-icon icon="times" />
                  </span>
                </div>
              </div>

              <!-- Add Question Button -->
              <button 
                class="btn add-question-btn d-flex align-items-center gap-2"
                @click="showQuestionCreateModal"
              >
                <font-awesome-icon icon="plus" />
                <span class="d-none d-sm-inline">Add Question</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Questions List -->
      <div class="questions-list" v-if="filteredQuestions.length > 0">
        <div 
          v-for="question in filteredQuestions" 
          :key="question.id"
          class="mb-4"
        >
          <QuestionCard 
            :question="question"
            @save-question="handleEditQuestion"
            @delete-question="handleDeleteQuestion"
          />
        </div>
      </div>

      <!-- Empty State - No Questions Found -->
      <div v-else-if="questions.length > 0 && filteredQuestions.length === 0" class="row">
        <div class="col-12 text-center py-5">
          <font-awesome-icon icon="search" class="fa-3x text-white-50 mb-3" />
          <h4 class="text-white">No questions found</h4>
          <p class="text-white-50">
            No questions match "{{ searchQuery }}". Try adjusting your search.
          </p>
          <button 
            class="btn btn-outline-light mt-3"
            @click="clearSearch"
          >
            <font-awesome-icon icon="times" class="me-2" />
            Clear Search
          </button>
        </div>
      </div>

      <!-- Empty State - No Questions Available -->
      <div v-else-if="questions.length === 0" class="row">
        <div class="col-12 text-center py-5">
          <font-awesome-icon icon="question-circle" class="fa-3x text-white-50 mb-3" />
          <h4 class="text-white">No Questions Available</h4>
          <p class="text-white-50">Questions will appear here once they are added to this quiz.</p>
          <button 
            class="btn btn-primary mt-3"
            @click="showQuestionCreateModal"
          >
            <font-awesome-icon icon="plus" class="me-2" />
            Add First Question
          </button>
        </div>
      </div>
    </div>
    <!-- Question Create Modal Component -->
    <QuestionCreateModal 
      ref="questionCreate"
      @question-created="handleQuestionCreated"
    />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';
import QuestionCard from '@/components/Admin/QuestionCard.vue';
import { defineAsyncComponent } from 'vue';
import { useToast } from 'vue-toastification';

// Lazy load components for better performance
const QuestionCreateModal = defineAsyncComponent(() =>
  import(/* webpackChunkName: "question-create-modal", webpackPrefetch: true */ '@/components/Admin/QuestionCreateModal.vue')
);

export default {
  name: 'Questions',
  components: {
    Navbar,
    Breadcrumb,
    QuestionCard,
    QuestionCreateModal
  },
  data() {
    return {
        quizName: '',
        chapterName: '',
        subjectName: '',
        quiz_id: '',
        questions: [],
        filteredQuestions: [],
        searchQuery: '',
        breadcrumbItems: []
    };
  },
  async mounted() {
    await this.fetchQuestions();
    this.setupBreadcrumb();
  },
  methods: {
      setupBreadcrumb() {
        const subjectId = this.$route.params.subjectId;
        const chapterId = this.$route.params.chapterId;
        const quizId = this.$route.params.quizId;

        this.breadcrumbItems = [
          {
          name: 'Subjects',
          path: '/admin/subjects',
          icon: 'book'
        },
        {
          name: this.subjectName,
          path: `/admin/subjects/${subjectId}/chapters`,
          icon: 'book-open'
        },
        {
          name: this.chapterName,
          path: `/admin/subjects/${subjectId}/chapters/${chapterId}/quizzes`,
          icon: 'question-circle'
        },
        {
          name: this.quizName,
          path: `/admin/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}/questions`,
          icon: 'clipboard-question'
        }
      ]
    },

    filterQuestions() {
      let filtered = [...this.questions];

      // Apply search filter
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(question => 
          question.question_statement.toLowerCase().includes(query)
        );
      }

      this.filteredQuestions = filtered;
    },

    clearSearch() {
      this.searchQuery = '';
      this.filterQuestions();
    },

    async fetchQuestions() {
      const quizId = this.$route.params.quizId;

      if (!quizId) {
        console.warn('No quizId found in route params');
        return;
      }
      
      const token = sessionStorage.getItem('access_token');

      if (!token) {
        store.dispatch('auth/logoutUser');
        return;
      }
      
      try {
        const response = await axios.post(`${BASE_URL}/quiz`, {
          id: quizId
        }, {
          headers: { 'Authorization': token }
        });

        console.log('Questions fetched from API:', response.data.questions);
        this.questions = response.data.questions;
        this.quizName = response.data.name;
        this.chapterName = response.data.chapter_name;
        this.subjectName = response.data.subject_name;
        this.quiz_id = response.data.id;
        this.filterQuestions(); // Apply initial filtering
      } catch (error) {
        console.error('Error fetching questions:', error);
      }
    },

    showQuestionCreateModal() {
      this.$refs.questionCreate.show({
        quiz_name: this.quizName,
        quiz_id: this.quiz_id
      });
    },

    handleQuestionCreated(newQuestion) {
      // Show success toast notification
      const toast = useToast();
      toast.success(`New question added to ${this.quizName} successfully.`, { theme: 'light' });
      // Add to the list
      if (newQuestion) {
        this.questions.push(newQuestion);
        this.filterQuestions(); // Apply filters to include the new question
      } else {
        // If the response doesn't contain the data, refresh the list
        this.fetchQuestions();
      }
    },

    async handleEditQuestion(updatedQuestion) {
      const toast = useToast();
      try {
        const token = sessionStorage.getItem('access_token');
        
        if (!token) {
          toast.error('You must be logged in.');
          setTimeout(() => {
            toast.error('Redirecting to login...');
            setTimeout(() => {
              store.dispatch('auth/logoutUser');
            }, 5000);
          }, 5000);
          return;
        }

        const response = await axios.put(`${BASE_URL}/question/update`, updatedQuestion, {
          headers: { Authorization: `${token}` }
        });
        if (response.data.code == 200) {
          toast.success(`Question ${updatedQuestion.id} updated successfully.`, { theme: 'light' });
        }
      } catch (err) {
        console.error(err);
        toast.error(err.response?.data?.error_message || 'Failed to edit question.');
      } finally {  
        this.fetchQuestions();
      }   
    },
    
    async handleDeleteQuestion(question) {
      const toast = useToast();
      // Remove from local array for now
      this.questions = this.questions.filter(q => q.id !== question.id);
      this.filterQuestions(); // Apply filters after deletion
      
      try {
        const token = sessionStorage.getItem('access_token');
        
        if (!token) {
          toast.error('You must be logged in.');
          setTimeout(() => {
            toast.error('Redirecting to login...');
            setTimeout(() => {
              store.dispatch('auth/logoutUser');
            }, 5000);
          }, 5000);
          return;
        }

        const response = await axios.patch(`${BASE_URL}/question/delete`, { id: question.id }, {
          headers: { Authorization: `${token}` }
        });
        if (response.data.code == 200) {
          toast.success(`Question ${question.id} deleted successfully from ${this.quizName}.`, { theme: 'light' });
        }
      } catch (err) {
        console.error(err);
        toast.error(err.response?.data?.error_message || 'Failed to delete question.');
      }
    }
  }
};
</script>

<style scoped>
.questions-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.questions-container::before {
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

.questions-title {
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-muted {
  color: rgba(255, 255, 255, 0.7) !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
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

.add-question-btn {
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

.add-question-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.questions-list {
  max-width: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 25px;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .questions-list .question-card {
    margin-bottom: 1rem;
  }
  
  .add-question-btn {
    padding: 0.6rem 1rem;
    min-width: 44px;
  }

  .search-input {
    width: 250px;
  }
}

@media (max-width: 480px) {
  .search-input {
    width: 200px;
  }
}
</style>