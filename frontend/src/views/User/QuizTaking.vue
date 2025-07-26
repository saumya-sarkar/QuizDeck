<template>
  <div class="quiz-taking-container">
    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center" style="min-height: 80vh;">
      <div class="text-center">
        <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
        <h4 class="text-white">Loading Quiz...</h4>
      </div>
    </div>

    <!-- Quiz Interface -->
    <div v-else-if="quizData && !submitted" class="quiz-interface">
      <!-- Quiz Header -->
      <div class="quiz-header glass-card mb-4">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h3 class="quiz-title mb-1">{{ quizData.quiz.name }}</h3>
            <p class="quiz-meta mb-0">
              {{ quizData.quiz.subject_name }} > {{ quizData.quiz.chapter_name }}
            </p>
          </div>
          <div class="col-md-4 text-md-end">
            <!-- Timer Display -->
            <div class="timer-display" :class="{ 'timer-warning': timeRemaining <= 300, 'timer-critical': timeRemaining <= 60 }">
              <font-awesome-icon icon="clock" class="me-2" />
              <span class="timer-text">{{ formatTime(timeRemaining) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Question Navigation -->
      <div class="question-nav glass-card mb-4">
        <div class="nav-header mb-3">
          <h6 class="mb-0">Question Navigation</h6>
          <span class="question-counter">{{ currentQuestionIndex + 1 }} of {{ quizData.questions.length }}</span>
        </div>
        <div class="question-buttons">
          <button
            v-for="(question, index) in quizData.questions"
            :key="question.id"
            class="question-nav-btn"
            :class="{
              'active': index === currentQuestionIndex,
              'answered': answers[question.id] !== undefined && answers[question.id] !== null,
              'unanswered': answers[question.id] === undefined || answers[question.id] === null
            }"
            @click="goToQuestion(index)"
          >
            {{ index + 1 }}
          </button>
        </div>
      </div>

      <!-- Question Display -->
      <div class="question-display glass-card mb-4">
        <div v-if="currentQuestion" class="question-content">
          <!-- Question Header -->
          <div class="question-header d-flex align-items-center justify-content-between mb-3 border-bottom pb-3">
              <span class="question-number">Question {{ currentQuestionIndex + 1 }}</span>
              <span class="question-marks ms-auto">{{ currentQuestion.marks }} {{ currentQuestion.marks === 1 ? 'Mark' : 'Marks' }}</span>
          </div>

          <!-- Question Statement -->
          <div class="question-statement mb-4">
            <h5>{{ currentQuestion.question_statement }}</h5>
          </div>

          <!-- Options -->
          <div class="question-options">
            <div
              v-for="(option, index) in currentQuestion.options"
              :key="option.id"
              class="option-item mb-3"
              @click="selectOption(option.id)"
            >
              <div class="form-check option-check">
                <input
                  class="form-check-input"
                  type="radio"
                  :name="'question_' + currentQuestion.id"
                  :id="'option_' + option.id"
                  :value="option.id"
                  v-model="answers[currentQuestion.id]"
                  @change="handleAnswerChange"
                />
                <label class="form-check-label option-label" :for="'option_' + option.id">
                  <span class="option-letter">{{ String.fromCharCode(65 + index) }}.</span>
                  <span class="option-text">{{ option.option_text }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quiz Controls -->
      <div class="quiz-controls glass-card">
        <div class="row align-items-center">
          <div class="col-md-6">
            <div class="d-flex gap-2">
              <button
                class="btn btn-outline-secondary"
                @click="previousQuestion"
                :disabled="currentQuestionIndex === 0"
              >
                <font-awesome-icon icon="chevron-left" class="me-1" />
                Previous
              </button>
              <button
                class="btn btn-outline-secondary"
                @click="nextQuestion"
                :disabled="currentQuestionIndex === quizData.questions.length - 1"
              >
                Next
                <font-awesome-icon icon="chevron-right" class="ms-1" />
              </button>
            </div>
          </div>
          <div class="col-md-6 text-md-end">
            <div class="d-flex gap-2 justify-content-md-end">
              <button
                class="btn btn-warning"
                @click="saveProgress"
                :disabled="saving"
              >
                <font-awesome-icon icon="save" class="me-1" />
                {{ saving ? 'Saving...' : 'Save Progress' }}
              </button>
              <button
                class="btn btn-primary"
                @click="showSubmitConfirmation"
              >
                <font-awesome-icon icon="paper-plane" class="me-1" />
                Submit Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit Confirmation Modal -->
    <div class="modal fade" id="submitModal" tabindex="-1" ref="submitModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Submit Quiz</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="submission-summary">
              <h6>Quiz Summary</h6>
              <div class="summary-stats">
                <div class="stat-item">
                  <span class="stat-label">Total Questions:</span>
                  <span class="stat-value">{{ quizData?.questions.length || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Answered:</span>
                  <span class="stat-value">{{ answeredCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Unanswered:</span>
                  <span class="stat-value">{{ unansweredCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Time Taken:</span>
                  <span class="stat-value">{{ formatTime(timeTaken) }}</span>
                </div>
              </div>
              <div v-if="unansweredCount > 0" class="alert alert-warning mt-3">
                <font-awesome-icon icon="exclamation-triangle" class="me-2" />
                You have {{ unansweredCount }} unanswered questions.
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Continue Quiz
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="submitQuiz"
              :disabled="submitting"
            >
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ submitting ? 'Submitting...' : 'Submit Quiz' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Quiz Result Display -->
    <div v-if="submitted && quizResult" class="quiz-result">
      <QuizResult :result="quizResult" @retake-quiz="retakeQuiz" />
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';
import { useToast } from 'vue-toastification';
import QuizResult from '@/components/User/QuizResult.vue';
import store from '@/store';

export default {
  name: 'QuizTaking',
  components: {
    QuizResult
  },
  data() {
    return {
      loading: true,
      attemptId: null,
      quizData: null,
      currentQuestionIndex: 0,
      answers: {}, // { questionId: optionId }
      
      // Timer related
      startTime: null,
      timeRemaining: 0, // in seconds
      timerInterval: null,
      
      // Save status
      saving: false,
      
      // Submission
      submitting: false,
      submitted: false,
      quizResult: null,
      isAutoSubmit: false,
      
      // Modal
      submitModalInstance: null
    };
  },
  computed: {
    currentQuestion() {
      if (!this.quizData || !this.quizData.questions) return null;
      return this.quizData.questions[this.currentQuestionIndex];
    },
    answeredCount() {
      if (!this.quizData) return 0;
      return this.quizData.questions.filter(question => 
        this.answers[question.id] !== undefined && this.answers[question.id] !== null
      ).length;
    },
    unansweredCount() {
      if (!this.quizData) return 0;
      return this.quizData.questions.length - this.answeredCount;
    },
    timeTaken() {
      if (!this.quizData) return 0;
      // total quiz duration in seconds
      const total = this.quizData.quiz.duration_mins * 60;
      // how many seconds have elapsed so far?
      return total - this.timeRemaining;
    }
  },
  async mounted() {
    // Initialize modal
    this.submitModalInstance = new Modal(this.$refs.submitModal);
    
    // Get quiz attempt ID from route or localStorage
    const quizId = this.$route.params.quizId;
    
    // Check for existing attempt in localStorage
    const savedAttempt = this.loadFromLocalStorage(); 
    
    if (savedAttempt && savedAttempt.quiz_id === parseInt(quizId)) {
      // Resume existing attempt
      this.attemptId = savedAttempt.attempt_id;
      await this.loadQuizData();
      this.loadAnswersFromLocalStorage();
    } else {
      // Start new attempt
      await this.startNewAttempt(quizId);
    }
    
    // Prevent accidental navigation
    this.setupBeforeUnloadHandler();
  },
  beforeUnmount() {
    this.clearTimers();
    window.removeEventListener('beforeunload', this.beforeUnloadHandler);
  },
  methods: {
    async startNewAttempt(quizId) {
      try {
        const token = sessionStorage.getItem('access_token');
        const response = await axios.post(`${BASE_URL}/quiz/start`, {
          quiz_id: parseInt(quizId)
        }, {
          headers: { Authorization: token }
        });
        
        if (response.data.code === 200 || response.data.code === 201) {
          this.attemptId = response.data.attempt.id;
          
          // Save to localStorage
          this.saveToLocalStorage({
            attempt_id: this.attemptId,
            quiz_id: parseInt(quizId),
            started_at: response.data.attempt.started_at
          });
          
          await this.loadQuizData();
        }
      } catch (error) {
        console.error('Error starting quiz:', error);
        const toast = useToast();
        toast.error('Failed to start quiz');
        this.$router.back();
      }
    },
    
    async loadQuizData() {
      try {
        const token = sessionStorage.getItem('access_token');
        const response = await axios.post(`${BASE_URL}/quiz/data`, {
          attempt_id: this.attemptId
        }, {
          headers: { Authorization: token }
        });
        
        if (response.data.code === 200) {
          this.quizData = response.data.data;
          this.startTime = new Date(this.quizData.started_at).getTime();
          
          // Calculate time remaining
          const durationMs = this.quizData.quiz.duration_mins * 60 * 1000;
          const elapsed = Date.now() - this.startTime;
          this.timeRemaining = Math.max(0, Math.floor((durationMs - elapsed) / 1000));
          
          // Load saved answers
          this.loadExistingAnswers();
          
          // Start timer
          this.startTimer();
          
          this.loading = false;
        }
      } catch (error) {
        console.error('Error loading quiz data:', error);
        const toast = useToast();
        toast.error('Failed to load quiz');
        this.$router.back();
      }
    },
    
    loadExistingAnswers() {
      // Load answers from quiz data (from database)
      this.quizData.questions.forEach(question => {
        if (question.selected_option_id) {
          this.answers[question.id] = question.selected_option_id;
        }
      });
    },
    
    startTimer() {
      this.timerInterval = setInterval(() => {
        this.timeRemaining--;
        
        if (this.timeRemaining <= 0) {
          this.autoSubmitQuiz();
        }
      }, 1000);
    },
    
    async saveProgress() {
      this.saving = true;
      
      try {
        // Save all current answers to backend
        const savePromises = Object.entries(this.answers).map(([questionId, optionId]) => {
          if (optionId) {
            return this.saveAnswerToBackend(parseInt(questionId), optionId);
          }
        }).filter(Boolean);
        
        await Promise.all(savePromises);
        
        // Save to localStorage
        this.saveAnswersToLocalStorage();
        
        const toast = useToast();
        toast.success('Progress saved successfully!');
        
      } catch (error) {
        console.error('Error saving progress:', error);
        const toast = useToast();
        toast.error('Failed to save progress');
      } finally {
        this.saving = false;
      }
    },
    
    async saveAnswerToBackend(questionId, selectedOptionId) {
      try {
        const token = sessionStorage.getItem('access_token');
        await axios.post(`${BASE_URL}/quiz/save-answer`, {
          attempt_id: this.attemptId,
          question_id: questionId,
          selected_option_id: selectedOptionId
        }, {
          headers: { Authorization: token }
        });
      } catch (error) {
        console.error('Error saving answer to backend:', error);
      }
    },
    
    selectOption(optionId) {
      if (this.currentQuestion) {
        this.answers[this.currentQuestion.id] = optionId;
        this.handleAnswerChange();
      }
    },
    
    handleAnswerChange() {
      // Save to localStorage immediately
      this.saveAnswersToLocalStorage();
    },
    
    goToQuestion(index) {
      if (index >= 0 && index < this.quizData.questions.length) {
        this.currentQuestionIndex = index;
      }
    },
    
    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
      }
    },
    
    nextQuestion() {
      if (this.currentQuestionIndex < this.quizData.questions.length - 1) {
        this.currentQuestionIndex++;
      }
    },
    
    showSubmitConfirmation() {
      this.submitModalInstance.show();
    },
    
    async submitQuiz() {
      this.submitting = true;
      
      try {
        const token = sessionStorage.getItem('access_token');
        
        // Prepare answers array
        const answersArray = this.quizData.questions.map(question => ({
          question_id: question.id,
          selected_option_id: this.answers[question.id] || null
        }));
        
        const response = await axios.post(`${BASE_URL}/quiz/submit`, {
          attempt_id: this.attemptId,
          answers: answersArray,
          time_taken_seconds: this.timeTaken,
          is_auto_submit: this.isAutoSubmit
        }, {
          headers: { Authorization: token }
        });
        
        if (response.data.code === 200) {
          // Clear localStorage
          this.clearLocalStorage();
          
          // Stop timers
          this.clearTimers();
          
          // Load and show results
          await this.loadQuizResult();
          
          this.submitted = true;
          this.submitModalInstance.hide();
          
          const toast = useToast();
          toast.success(this.isAutoSubmit ? 'Quiz auto-submitted!' : 'Quiz submitted successfully!');
        }
        
      } catch (error) {
        console.error('Error submitting quiz:', error);
        const toast = useToast();
        toast.error('Failed to submit quiz');
      } finally {
        this.submitting = false;
      }
    },
    
    async autoSubmitQuiz() {
      this.isAutoSubmit = true;
      const toast = useToast();
      toast.warning('Time is up! Quiz will be auto-submitted.');
      await this.submitQuiz();
    },
    
    async loadQuizResult() {
      try {
        const token = sessionStorage.getItem('access_token');
        
        const user_id = this.$route.params.userId || this.$store.getters['auth/getUser'].id;
        
        const response = await axios.post(`${BASE_URL}/quiz/result`, {
          attempt_id: this.attemptId,
          user_id: user_id
        }, {
          headers: { Authorization: token }
        });
        
        if (response.data.code === 200) {
          this.quizResult = response.data.data;
        }
      } catch (error) {
        console.error('Error loading quiz result:', error);
      }
    },
    
    // LocalStorage methods
    saveToLocalStorage(data) {
      const storageKey = `quiz_attempt_${this.attemptId}`;
      localStorage.setItem(storageKey, JSON.stringify(data));
    },
    
    loadFromLocalStorage() {
      const keys = Object.keys(localStorage).filter(key => key.startsWith('quiz_attempt_'));
      if (keys.length > 0) {
        const data = localStorage.getItem(keys[0]);
        return data ? JSON.parse(data) : null;
      }
      return null;
    },
    
    saveAnswersToLocalStorage() {
      const answersKey = `quiz_answers_${this.attemptId}`;
      localStorage.setItem(answersKey, JSON.stringify(this.answers));
    },
    
    loadAnswersFromLocalStorage() {
      const answersKey = `quiz_answers_${this.attemptId}`;
      const savedAnswers = localStorage.getItem(answersKey);
      if (savedAnswers) {
        this.answers = { ...this.answers, ...JSON.parse(savedAnswers) };
      }
    },
    
    clearLocalStorage() {
      const keys = Object.keys(localStorage).filter(key => 
        key.startsWith('quiz_attempt_') || key.startsWith('quiz_answers_')
      );
      keys.forEach(key => localStorage.removeItem(key));
    },
    
    // Utility methods
    formatTime(seconds) {
      if (seconds < 0) return '00:00';
      
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      
      if (hours > 0) {
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
      }
      return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    },
    
    clearTimers() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
      }
    },
    
    setupBeforeUnloadHandler() {
      this.beforeUnloadHandler = (event) => {
        if (!this.submitted) {
          event.preventDefault();
          event.returnValue = 'Are you sure you want to leave? Your quiz progress might be lost.';
          return event.returnValue;
        }
      };
      window.addEventListener('beforeunload', this.beforeUnloadHandler);
    },
    
    retakeQuiz() {
      this.clearLocalStorage();
      this.$router.push(`/quiz/${this.quizData.quiz.id}`);
    }
  }
};
</script>

<style scoped>
.quiz-taking-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  padding: 2rem 0;
  position: relative;
}

.quiz-taking-container::before {
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

.quiz-interface {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  position: relative;
  z-index: 1;
}

.glass-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

/* Quiz Header */
.quiz-title {
  color: #ffffff;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.quiz-meta {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
}

/* Timer */
.timer-display {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 15px;
  padding: 0.75rem 1rem;
  text-align: center;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.timer-text {
  font-weight: 700;
  font-size: 1.2rem;
  color: #ffffff;
  font-family: 'Courier New', monospace;
}

.timer-warning {
  background: rgba(255, 193, 7, 0.3);
  border-color: rgba(255, 193, 7, 0.5);
}

.timer-critical {
  background: rgba(220, 53, 69, 0.3);
  border-color: rgba(220, 53, 69, 0.5);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* Question Navigation */
.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ffffff;
  font-weight: 600;
}

.question-counter {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.9rem;
}

.question-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.question-nav-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.question-nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.question-nav-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(255, 255, 255, 0.5);
  transform: scale(1.1);
}

.question-nav-btn.answered {
  background: rgba(40, 167, 69, 0.6);
  border-color: rgba(40, 167, 69, 0.8);
}

.question-nav-btn.unanswered {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

/* Question Display */
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.question-number {
  font-size: 1rem;
  font-weight: 600;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 15px;
}

.question-marks {
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.question-statement {
  color: #ffffff;
  font-weight: 600;
  line-height: 1.6;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Options */
.option-item {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.option-item:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateX(5px);
}

.option-check {
  display: flex;
  align-items: center;
  margin: 0;
}

.option-check .form-check-input {
  margin-right: 1rem;
  margin-top: 0;
  width: 1.2em;
  height: 1.2em;
  background-color: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.4);
}

.option-check .form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.option-label {
  color: #ffffff;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  width: 100%;
  margin: 0;
}

.option-letter {
  font-weight: 700;
  margin-right: 0.75rem;
  min-width: 25px;
  color: rgba(255, 255, 255, 0.9);
}

.option-text {
  flex: 1;
  line-height: 1.5;
}

/* Quiz Controls */
.quiz-controls .btn {
  border-radius: 12px;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.btn-outline-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.btn-outline-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  transform: translateY(-2px);
}

.btn-warning {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.8), rgba(255, 162, 0, 0.9));
  color: #ffffff;
  border-color: rgba(255, 193, 7, 0.5);
}

.btn-warning:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.9), rgba(255, 162, 0, 1));
  transform: translateY(-2px);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-2px);
}

/* Modal Styles */
.modal-content {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  color: #ffffff;
}

.modal-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.modal-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-close {
  filter: invert(1);
  opacity: 0.8;
}

.submission-summary h6 {
  color: #ffffff;
  font-weight: 600;
  margin-bottom: 1rem;
}

.summary-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.stat-value {
  color: #ffffff;
  font-weight: 600;
}

.alert-warning {
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid rgba(255, 193, 7, 0.3);
  color: #ffffff;
  border-radius: 15px;
}

</style>