<template>
  <div class="quiz-card h-100 shadow-sm hover-card glass-card">
    <!-- Quiz Type Header -->
    <div class="quiz-type-header" v-bind:class="getQuizTypeHeaderClass(quiz.quiz_type)">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-2">
          <div class="quiz-type-icon" v-bind:class="getQuizTypeIconClass(quiz.quiz_type)">
            <font-awesome-icon v-bind:icon="getQuizTypeIcon(quiz.quiz_type)" />
          </div>
          <span class="quiz-type-label">{{ quiz.quiz_type }}</span>
        </div>
        <div class="quiz-status-indicator" :class="getStatusClass(quiz)">
          {{ quiz.quiz_status }}
        </div>
      </div>
    </div>

    <div class="card-body d-flex flex-column glass-body">
      <!-- Quiz Title & Badges -->
      <div class="quiz-header-section mb-3">
        <h5 class="quiz-title mb-3">{{ quiz.name }}</h5>
        <div class="d-flex gap-2 align-items-center">
          <span class="badge difficulty-badge" :class="getDifficultyBadgeClass(quiz.difficulty)">
            {{ quiz.difficulty }}
          </span>
          <span v-if="quiz.is_locked" class="badge locked-badge">
            <font-awesome-icon icon="lock" class="me-1" />
            Locked
          </span>
        </div>
      </div>

      <!-- Quiz Stats -->
      <div class="quiz-stats mb-3">
        <div class="row g-2">
          <div class="col-4">
            <div class="stat-item text-center glass-stat">
              <font-awesome-icon icon="clock" class="mb-1" style="color: #74900e;" />
              <div class="stat-number">{{ quiz.duration_mins }}</div>
              <small class="stat-label text-muted">Minutes</small>
            </div>
          </div>
          
          <div class="col-4">
            <div class="stat-item text-center glass-stat">
              <font-awesome-icon icon="question-circle" class="mb-1" style="color: #005eff;" />
              <div class="stat-number">{{ quiz.total_questions || 0 }}</div>
              <small class="stat-label text-muted">Questions</small>
            </div>
          </div>
          
          <div class="col-4">
            <div class="stat-item text-center glass-stat">
              <font-awesome-icon icon="trophy" class="mb-1" style="color: #c94ac5;"/>
              <div class="stat-number">{{ quiz.total_marks || 0 }}</div>
              <small class="stat-label text-muted">Marks</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Enhanced Schedule Info (for timed quizzes) -->
      <div v-if="quiz.start_time" class="schedule-info mb-3">
        <div class="schedule-card glass-stat">
          <!-- Schedule Header -->
          <div class="schedule-header mb-2">
            <font-awesome-icon icon="calendar" class="schedule-icon me-2" />
            <span class="schedule-title">Quiz Schedule</span>
          </div>
          
          <!-- Schedule Details -->
          <div class="schedule-details">
            <!-- Start Time -->
            <div class="schedule-row">
              <div class="schedule-label">
                <font-awesome-icon icon="play-circle" class="me-1" style="color: #28a745;" />
                <span>Starts</span>
              </div>
              <div class="schedule-value">
                <div class="single-line-datetime">
                  {{ formatDateTime(quiz.start_time) }}
                </div>
              </div>
            </div>
            
            <!-- End Time -->
            <div class="schedule-row">
              <div class="schedule-label">
                <font-awesome-icon icon="stop-circle" class="me-1" style="color: #dc3545;" />
                <span>Ends</span>
              </div>
              <div class="schedule-value">
                <div class="single-line-datetime">
                  {{ formatDateTime(quiz.end_time) }}
                </div>
              </div>
            </div>
            
            <!-- Duration Info -->
             <div class="schedule-row">
              <div class="schedule-label">
                <font-awesome-icon icon="clock" class="me-1" style="color: #6c757d;" />
                <span>Quiz Period</span>
              </div>
              <div class="schedule-value">
                <div class="single-line-datetime">
                  {{ quiz.available_for }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- Countdown or Status -->
          <div v-if="shouldShowCountdown()" class="countdown-section">
            <div class="countdown-label">{{ getCountdownLabel() }}</div>
            <div class="countdown-value">{{ getCountdownTime() }}</div>
          </div>
        </div>
      </div>
      
      <!-- Enhanced Schedule Info (for practice quizzes) -->
      <div v-if="quiz.quiz_type == 'Practice'" class="schedule-info mb-3">
        <div class="schedule-card glass-stat">
          <!-- Schedule Header -->
          <div class="schedule-header mb-2">
            <font-awesome-icon icon="calendar" class="schedule-icon me-2" />
            <span class="schedule-title">Quiz Schedule</span>
          </div>
          
          <!-- Schedule Details -->
          <div class="schedule-details">
            <!-- Start Time -->
            <div class="schedule-row">
              <div class="schedule-label">
                <font-awesome-icon icon="play-circle" class="me-1" style="color: #28a745;" />
                <span>Starts</span>
              </div>
              <div class="schedule-value">
                <div class="single-line-datetime">
                  {{ formatDateTime(quiz.updated_at || quiz.created_at) }}
                </div>
              </div>
            </div>
            
            <!-- End Time -->
            <div class="schedule-row">
              <div class="schedule-label">
                <font-awesome-icon icon="stop-circle" class="me-1" style="color: #dc3545;" />
                <span>Ends</span>
              </div>
              <div class="schedule-value">
                <div class="single-line-datetime">
                  {{ formatDateTime("2025-12-31") }}
                </div>
              </div>
            </div>
            
            <!-- Duration Info -->
             <div class="schedule-row">
              <div class="schedule-label">
                <font-awesome-icon icon="clock" class="me-1" style="color: #6c757d;" />
                <span>Quiz Period</span>
              </div>
              <div class="schedule-value">
                <div class="single-line-datetime">
                  {{ calculateAvailableForPractice().diff }}
                </div>
              </div>
            </div>
          </div>
          <!-- Countdown or Status -->
          <div v-if="quiz.quiz_type == 'Practice'" class="countdown-section">
            <div class="countdown-label">Ends in:</div>
            <div class="countdown-value">{{ calculateAvailableForPractice().remaining }}</div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="quiz-actions mt-auto">
        <div class="chapter-actions d-flex justify-content-between">
          <button 
            class="btn btn-outline-success btn-lg glass-btn"
            @click="onViewQuiz(quiz)"
          >
            <font-awesome-icon icon="eye" /> View
          </button>
          <button 
            class="btn btn-outline-primary btn-lg glass-btn"
            @click="sendEditQuiz(quiz)"
          >
            <font-awesome-icon icon="edit" /> Edit
          </button>
          <button 
            class="btn btn-outline-danger btn-lg glass-btn"
            @click="sendDeleteQuiz(quiz)"
          >
            <font-awesome-icon icon="trash" /> Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuizCard',
  props: {
    quiz: {
      type: Object,
      required: true
    }
  },
  methods: {
    getQuizTypeIcon(type) {
      const icons = {
        'Practice': 'pen-nib',
        'Mock': 'clipboard-check',
        'Exam': 'graduation-cap'
      };
      return icons[type];
    },
    
    getQuizTypeHeaderClass(type) {
      const classes = {
        'Practice': 'header-practice',
        'Mock': 'header-mock',
        'Exam': 'header-exam'
      };
      return classes[type];
    },
    
    getQuizTypeIconClass(type) {
      const classes = {
        'Practice': 'icon-practice',
        'Mock': 'icon-mock',
        'Exam': 'icon-exam'
      };
      return classes[type];
    },
    
    getDifficultyBadgeClass(difficulty) {
      const classes = {
        'Easy': 'bg-success',
        'Medium': 'bg-warning',
        'Hard': 'bg-danger'
      };
      return classes[difficulty];
    },
    
    getStatusClass(quiz) {
      const now = new Date();
      const startTime = quiz.start_time ? new Date(quiz.start_time) : null;
      const endTime = quiz.end_time ? new Date(quiz.end_time) : null;
      
      if (quiz.quiz_type === 'Practice') return 'status-available';
      if (!startTime) return 'status-available';
      
      if (now < startTime) return 'status-upcoming';
      if (endTime && now > endTime) return 'status-ended';
      return 'status-active';
    },
    
    formatDateTime(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-IN', { 
        weekday: 'short',
        month: 'long', 
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    },
    
    
    shouldShowCountdown() {
      if (!this.quiz.start_time || !this.quiz.end_time) return false;
      
      const now = new Date();
      const startTime = new Date(this.quiz.start_time);
      const endTime = new Date(this.quiz.end_time);
      
      // Show countdown if quiz is upcoming or currently active
      return now < endTime;
    },
    
    getCountdownLabel() {
      const now = new Date();
      const startTime = new Date(this.quiz.start_time);
      
      if (now < startTime) {
        return 'Starts in:';
      } else {
        return 'Ends in:';
      }
    },
    
    getCountdownTime() {
      const now = new Date();
      const startTime = new Date(this.quiz.start_time);
      const endTime = new Date(this.quiz.end_time);
      
      let targetTime;
      if (now < startTime) {
        targetTime = startTime;
      } else {
        targetTime = endTime;
      }
      
      const time_diff = targetTime - now;
      
      if (time_diff <= 0) return 'Ended';
      
      const days = Math.floor(time_diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((time_diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((time_diff % (1000 * 60 * 60)) / (1000 * 60));
      
      if (days > 0) {
        return `${days} Days ${hours} Hours ${minutes} Minutes`;
      } else if (hours > 0) {
        return `${hours} Hours ${minutes} Minutes`;
      } else {
        return `${minutes} Minutes`;
      }
    },

    onViewQuiz(quiz) {
      this.$emit('view-quiz', quiz);
    },
    
    sendEditQuiz(quiz) {
      this.$emit('sent-edit-quiz', quiz);
    },
    
    sendDeleteQuiz(quiz) {
      this.$emit('sent-delete-quiz', quiz);
    },
    calculateAvailableForPractice() {
      let start = new Date();
      if (!this.quiz.updated_at){
        start = new Date(this.quiz.created_at);
      } else {
        start = new Date(this.quiz.updated_at);
      }
      const end = new Date("2025-12-31"); // Placeholder end date for practice quizzes
      
      const diff = end - start;
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));

      let now = new Date();

      const remainingDays = Math.floor((end - now) / (1000 * 60 * 60 * 24));

      return {"diff": `${days} Days`, "remaining": `${remainingDays} Days Remaining`};
    }

  }
};
</script>

<style scoped>
.quiz-card-container {
  position: relative;
}

.hover-card {
  transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
  cursor: pointer;
}

.hover-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2) !important;
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.1);
}

.quiz-type-header {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(15px);
}

.header-practice {
  background: linear-gradient(135deg, rgba(74, 144, 226, 0.3), rgba(74, 144, 226, 0.1));
}

.header-mock {
  background: linear-gradient(135deg, rgba(142, 68, 173, 0.3), rgba(142, 68, 173, 0.1));
}

.header-exam {
  background: linear-gradient(135deg, rgba(26, 188, 156, 0.3), rgba(26, 188, 156, 0.1));
}

.quiz-type-icon {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: #ffffff;
  border: 2px solid rgba(255, 255, 255, 0.4);
}

.icon-practice {
  background: rgba(74, 144, 226, 0.4);
}

.icon-mock {
  background: rgba(142, 68, 173, 0.4);
}

.icon-exam {
  background: rgba(26, 188, 156, 0.4);
}

.quiz-type-label {
  font-weight: 600;
  color: #ffffff;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.quiz-status-indicator {
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.status-available {
  background: rgba(40, 167, 69, 0.3);
  color: #ffffff;
}

.status-upcoming {
  background: rgba(255, 193, 7, 0.3);
  color: #ffffff;
}

.status-active {
  background: rgba(0, 123, 255, 0.3);
  color: #ffffff;
}

.status-ended {
  background: rgba(108, 117, 125, 0.3);
  color: rgba(255, 255, 255, 0.7);
}

.glass-body {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px);
  position: relative;
  padding: 1.5rem;
}

.quiz-title {
  font-weight: 600;
  font-size: 1.2rem;
  color: #2c3e50;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

/* Improved badge styles consistent with glass morphism design */
.badge {
  font-size: 0.7rem;
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.difficulty-badge.bg-success {
  background: rgba(40, 167, 69, 0.3);
  color: #ffffff;
  border-color: rgba(40, 167, 69, 0.4);
}

.difficulty-badge.bg-warning {
  background: rgba(245, 185, 4, 0.8) !important;
  color: #ffffff;
  border-color: rgba(255, 193, 7, 0.9);
}

.difficulty-badge.bg-danger {
  background: rgba(220, 53, 69, 0.3);
  color: #ffffff;
  border-color: rgba(220, 53, 69, 0.4);
}

.difficulty-badge.bg-secondary {
  background: rgba(108, 117, 125, 0.3);
  color: #ffffff;
  border-color: rgba(108, 117, 125, 0.4);
}

.locked-badge {
  background: rgba(255, 87, 34, 0.3);
  color: #ffffff;
  border-color: rgba(255, 87, 34, 0.4);
  font-weight: 600;
}

.glass-stat {
  padding: 0.75rem 0.5rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: none;
}

.stat-number {
  font-weight: 700;
  font-size: 1.2rem;
  color: #2c3e50;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.stat-label {
  font-size: 0.7rem;
  letter-spacing: 0.5px;
  color: #666 !important;
  text-transform: uppercase;
}

/* Enhanced Schedule Info Styles */
.schedule-info {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 1rem;
}

.schedule-card {
  padding: 1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.schedule-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.schedule-icon {
  color: #4a90e2;
  font-size: 1.1rem;
}

.schedule-title {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
  flex: 1;
}


.schedule-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.schedule-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.schedule-row:last-child {
  border-bottom: none;
}

.schedule-label {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 500;
  color: #2c3e50;
  min-width: 60px;
}

.schedule-value {
  text-align: right;
}

/* UPDATED: Single line datetime styles */
.single-line-datetime {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.8rem;
  text-align: right;
}

.countdown-section {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}

.countdown-label {
  font-family: 'Poppins', sans-serif;
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
  margin-bottom: 0.25rem;
  letter-spacing: 0.5px;
}

.countdown-value {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  color: #2c3e50;
  font-weight: 550;
  letter-spacing: 0.3px;
}

.quiz-actions {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 1rem;
}

.quiz-actions .btn {
  border-radius: 8px;
  padding: 0.4rem 1.4rem;
  font-size: 0.9rem;
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

.btn-outline-danger.glass-btn {
  color: #dc3545;
  border-color: rgba(220, 53, 69, 0.3);
}

.btn-outline-danger.glass-btn:hover {
  color: #fff;
  background: rgba(220, 53, 69, 0.8);
  border-color: rgba(220, 53, 69, 0.8);
}

.btn-outline-success.glass-btn {
  color: #198754;
  border-color: rgba(25, 135, 84, 0.3);
}

.btn-outline-success.glass-btn:hover {
  color: #fff;
  background: rgba(25, 135, 84, 0.8);
  border-color: rgba(25, 135, 84, 0.8);
}

</style>