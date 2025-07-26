<template>
  <div class="quiz-result-container">
    <div class="container py-5">
      <!-- Result Header -->
      <div class="result-header glass-card mb-4">
        <div class="text-center">
          <div class="result-icon mb-3" :class="getResultIconClass()">
            <font-awesome-icon :icon="getResultIcon()" />
          </div>
          <h2 class="result-title mb-2">{{ getResultTitle() }}</h2>
          <h4 class="quiz-name mb-3">{{ result.quiz_name }}</h4>
          <p class="quiz-meta">
            {{ result.subject_name }} > {{ result.chapter_name }}
          </p>
        </div>
      </div>

      <!-- Score Summary -->
      <div class="score-summary glass-card mb-4">
        <div class="row text-center">
          <div class="col-md-3 col-6">
            <div class="score-stat">
              <div class="stat-value">{{ result.user_score }}</div>
              <div class="stat-label">Score Obtained</div>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="score-stat">
              <div class="stat-value">{{ result.total_marks }}</div>
              <div class="stat-label">Total Marks</div>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="score-stat">
              <div class="stat-value">{{ result.percentage }}%</div>
              <div class="stat-label">Percentage</div>
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="score-stat">
              <div class="stat-value">{{ formatTime(result.time_taken_seconds) }}</div>
              <div class="stat-label">Time Taken</div>
            </div>
          </div>
        </div>
        
        <!-- Progress Bar -->
        <div class="progress-container mt-4">
          <div class="progress-bar-container">
            <div 
              class="progress-bar" 
              :class="getProgressBarClass()"
              :style="{ width: result.percentage + '%' }"
            ></div>
          </div>
          <div class="progress-text mt-2">
            {{ result.percentage }}% Complete
          </div>
        </div>

        <!-- Status Badge -->
        <div class="text-center mt-3">
          <span class="badge result-badge" :class="getResultBadgeClass()">
            {{ getResultStatus() }}
          </span>
          <span v-if="result.status === 'auto_submitted'" class="badge auto-submit-badge ms-2">
            Auto Submitted
          </span>
        </div>
      </div>

      <!-- Quiz Performance Chart -->
      <div class="performance-chart glass-card mb-4">
        <h5 class="chart-title mb-4">Performance Breakdown</h5>
        <div class="chart-container">
          <canvas ref="performanceChart" width="400" height="200"></canvas>
        </div>
      </div>

      <!-- Detailed Results -->
      <div class="detailed-results glass-card mb-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="results-title mb-0">Question-wise Results</h5>
          <div class="view-toggle">
            <button 
              class="btn btn-sm toggle-btn"
              :class="{ active: showAllQuestions }"
              @click="showAllQuestions = !showAllQuestions"
            >
              {{ showAllQuestions ? 'Show Summary' : 'Show All Questions' }}
            </button>
          </div>
        </div>

        <!-- Summary View -->
        <div v-if="!showAllQuestions" class="summary-stats">
          <div class="row">
            <div class="col-md-4 mb-3">
              <div class="summary-stat correct">
                <div class="stat-icon">
                  <font-awesome-icon icon="check-circle" />
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ correctAnswers }}</div>
                  <div class="stat-text">Correct Answers</div>
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="summary-stat incorrect">
                <div class="stat-icon">
                  <font-awesome-icon icon="times-circle" />
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ incorrectAnswers }}</div>
                  <div class="stat-text">Incorrect Answers</div>
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="summary-stat unanswered">
                <div class="stat-icon">
                  <font-awesome-icon icon="question-circle" />
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ unansweredQuestions }}</div>
                  <div class="stat-text">Unanswered</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Detailed Questions View -->
        <div v-else class="questions-breakdown">
          <div 
            v-for="(question, index) in result.questions" 
            :key="question.question_id"
            class="question-result-item mb-3"
            :class="getQuestionResultClass(question)"
          >
            <div class="question-header">
              <div class="question-number">Q{{ index + 1 }}</div>
              <div class="question-status">
                <font-awesome-icon :icon="getQuestionIcon(question)" />
                <span class="status-text">{{ getQuestionStatus(question) }}</span>
              </div>
              <div class="question-marks">
                <span class="marks-obtained">{{ question.marks_obtained }}</span>
                <span class="marks-separator">/</span>
                <span class="total-marks">{{ question.marks }}</span>
              </div>
            </div>
            
            <div class="question-content">
              <h6 class="question-text mb-3">{{ question.question_statement }}</h6>
              
              <div class="answer-comparison">
                <div class="row">
                  <div class="col-md-6">
                    <div class="answer-section">
                      <div class="answer-label">Your Answer:</div>
                      <div class="answer-value" :class="question.is_correct ? 'correct-answer' : 'wrong-answer'">
                        {{ question.selected_option_text || 'Not answered' }}
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="answer-section">
                      <div class="answer-label">Correct Answer:</div>
                      <div class="answer-value correct-answer">
                        {{ question.correct_option_text }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-if="question.explanation" class="explanation mt-3">
                <div class="explanation-label">
                  <font-awesome-icon icon="info-circle" class="me-2" />
                  Explanation:
                </div>
                <div class="explanation-text">{{ question.explanation }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="result-actions glass-card text-center">
        <div class="d-flex gap-3 justify-content-center flex-wrap">
          <button class="btn btn-primary btn-lg" @click="goToDashboard">
            <font-awesome-icon icon="tachometer-alt" class="me-2" />
            Back to Dashboard
          </button>
          <button class="btn btn-outline-light btn-lg" @click="viewAllQuizzes">
            <font-awesome-icon icon="list" class="me-2" />
            View All Quizzes
          </button>
          <button class="btn btn-success btn-lg" @click="$emit('retake-quiz')">
            <font-awesome-icon icon="redo" class="me-2" />
            Retake Quiz
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import store from '@/store';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default {
  name: 'QuizResult',
  props: {
    result: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      showAllQuestions: false,
      chart: null
    };
  },
  computed: {
    correctAnswers() {
      return this.result.questions.filter(q => q.is_correct).length;
    },
    incorrectAnswers() {
      return this.result.questions.filter(q => q.selected_option_id && !q.is_correct).length;
    },
    unansweredQuestions() {
      return this.result.questions.filter(q => !q.selected_option_id).length;
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.createPerformanceChart();
    });
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy();
    }
  },
  methods: {
    getResultTitle() {
      const percentage = this.result.percentage;
      if (percentage >= 90) return 'Excellent Performance!';
      if (percentage >= 80) return 'Great Job!';
      if (percentage >= 70) return 'Good Work!';
      if (percentage >= 60) return 'Well Done!';
      if (percentage >= 50) return 'Keep Improving!';
      return 'Better Luck Next Time!';
    },
    
    getResultIcon() {
      const percentage = this.result.percentage;
      if (percentage >= 80) return 'trophy';
      if (percentage >= 60) return 'medal';
      return 'award';
    },
    
    getResultIconClass() {
      const percentage = this.result.percentage;
      if (percentage >= 80) return 'icon-excellent';
      if (percentage >= 60) return 'icon-good';
      return 'icon-average';
    },
    
    getResultStatus() {
      const percentage = this.result.percentage;
      if (percentage >= 90) return 'Outstanding';
      if (percentage >= 80) return 'Excellent';
      if (percentage >= 70) return 'Very Good';
      if (percentage >= 60) return 'Good';
      if (percentage >= 50) return 'Average';
      return 'Needs Improvement';
    },
    
    getResultBadgeClass() {
      const percentage = this.result.percentage;
      if (percentage >= 80) return 'badge-excellent';
      if (percentage >= 60) return 'badge-good';
      if (percentage >= 40) return 'badge-average';
      return 'badge-poor';
    },
    
    getProgressBarClass() {
      const percentage = this.result.percentage;
      if (percentage >= 80) return 'progress-excellent';
      if (percentage >= 60) return 'progress-good';
      if (percentage >= 40) return 'progress-average';
      return 'progress-poor';
    },
    
    getQuestionResultClass(question) {
      if (!question.selected_option_id) return 'question-unanswered';
      return question.is_correct ? 'question-correct' : 'question-incorrect';
    },
    
    getQuestionIcon(question) {
      if (!question.selected_option_id) return 'question-circle';
      return question.is_correct ? 'check-circle' : 'times-circle';
    },
    
    getQuestionStatus(question) {
      if (!question.selected_option_id) return 'Unanswered';
      return question.is_correct ? 'Correct' : 'Incorrect';
    },
    
    formatTime(seconds) {
      if (!seconds) return '00:00';
      
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      
      if (hours > 0) {
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
      }
      return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    },
    
    createPerformanceChart() {
      const ctx = this.$refs.performanceChart.getContext('2d');
      
      this.chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Correct', 'Incorrect', 'Unanswered'],
          datasets: [{
            data: [this.correctAnswers, this.incorrectAnswers, this.unansweredQuestions],
            backgroundColor: [
              'rgba(40, 167, 69, 0.8)',
              'rgba(220, 53, 69, 0.8)',
              'rgba(108, 117, 125, 0.8)'
            ],
            borderColor: [
              'rgba(40, 167, 69, 1)',
              'rgba(220, 53, 69, 1)',
              'rgba(108, 117, 125, 1)'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: '#ffffff',
                font: {
                  size: 14,
                  weight: 'bold'
                },
                padding: 20
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.parsed || 0;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                  return `${label}: ${value} (${percentage}%)`;
                }
              },
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: '#ffffff',
              bodyColor: '#ffffff',
              borderColor: 'rgba(255, 255, 255, 0.3)',
              borderWidth: 1
            }
          }
        }
      });
    },
    
    goToDashboard() {
      const userId = store.getters['auth/getUser'].id;
      this.$router.push(`/user/${userId}`);
    },
    
    viewAllQuizzes() {
      this.$router.push('/quizzes');
    }
  }
};
</script>

<style scoped>
.quiz-result-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.quiz-result-container::before {
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

.container {
  max-width: 1200px;
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

/* Result Header */
.result-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  font-size: 2.5rem;
  color: #ffffff;
}

.icon-excellent {
  background: linear-gradient(135deg, #28a745, #20c997);
  box-shadow: 0 0 30px rgba(40, 167, 69, 0.5);
}

.icon-good {
  background: linear-gradient(135deg, #007bff, #6610f2);
  box-shadow: 0 0 30px rgba(0, 123, 255, 0.5);
}

.icon-average {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
  box-shadow: 0 0 30px rgba(255, 193, 7, 0.5);
}

.result-title {
  color: #ffffff;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.quiz-name {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.quiz-meta {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
}

/* Score Summary */
.score-stat {
  padding: 1rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

/* Progress Bar */
.progress-container {
  text-align: center;
}

.progress-bar-container {
  width: 100%;
  height: 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.progress-bar {
  height: 100%;
  border-radius: 10px;
  transition: width 1s ease-in-out;
}

.progress-excellent {
  background: linear-gradient(90deg, #28a745, #20c997);
}

.progress-good {
  background: linear-gradient(90deg, #007bff, #6610f2);
}

.progress-average {
  background: linear-gradient(90deg, #ffc107, #fd7e14);
}

.progress-poor {
  background: linear-gradient(90deg, #dc3545, #e83e8c);
}

.progress-text {
  color: #ffffff;
  font-weight: 600;
  font-size: 1.1rem;
}

/* Result Badges */
.result-badge {
  font-size: 1rem;
  padding: 0.5rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-excellent {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: #ffffff;
}

.badge-good {
  background: linear-gradient(135deg, #007bff, #6610f2);
  color: #ffffff;
}

.badge-average {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
  color: #ffffff;
}

.badge-poor {
  background: linear-gradient(135deg, #dc3545, #e83e8c);
  color: #ffffff;
}

.auto-submit-badge {
  background: rgba(255, 87, 34, 0.8);
  color: #ffffff;
  padding: 0.3rem 1rem;
  border-radius: 15px;
  font-size: 0.8rem;
}

/* Performance Chart */
.chart-title {
  color: #ffffff;
  font-weight: 600;
  text-align: center;
}

.chart-container {
  height: 300px;
  position: relative;
}

/* Summary Stats */
.summary-stat {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.summary-stat:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.summary-stat.correct {
  border-color: rgba(40, 167, 69, 0.5);
}

.summary-stat.incorrect {
  border-color: rgba(220, 53, 69, 0.5);
}

.summary-stat.unanswered {
  border-color: rgba(108, 117, 125, 0.5);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.summary-stat.correct .stat-icon {
  background: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.summary-stat.incorrect .stat-icon {
  background: rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.summary-stat.unanswered .stat-icon {
  background: rgba(108, 117, 125, 0.2);
  color: #6c757d;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #ffffff;
}

.stat-text {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

/* Question Results */
.results-title {
  color: #ffffff;
  font-weight: 600;
}

.toggle-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 0.5rem 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.toggle-btn:hover,
.toggle-btn.active {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  transform: translateY(-1px);
}

.question-result-item {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.question-result-item:hover {
  background: rgba(255, 255, 255, 0.15);
}

.question-correct {
  border-left: 4px solid #28a745;
}

.question-incorrect {
  border-left: 4px solid #dc3545;
}

.question-unanswered {
  border-left: 4px solid #6c757d;
}

.question-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.question-number {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
}

.question-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ffffff;
  font-weight: 500;
}

.question-marks {
  font-weight: 700;
  color: #ffffff;
}

.marks-obtained {
  color: #28a745;
}

.marks-separator {
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0.25rem;
}

.total-marks {
  color: rgba(255, 255, 255, 0.8);
}

.question-text {
  color: #ffffff;
  font-weight: 600;
  line-height: 1.5;
}

.answer-section {
  margin-bottom: 1rem;
}

.answer-label {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.answer-value {
  padding: 0.75rem;
  border-radius: 10px;
  font-weight: 600;
}

.correct-answer {
  background: rgba(40, 167, 69, 0.2);
  border: 1px solid rgba(40, 167, 69, 0.4);
  color: #ffffff;
}

.wrong-answer {
  background: rgba(220, 53, 69, 0.2);
  border: 1px solid rgba(220, 53, 69, 0.4);
  color: #ffffff;
}

.explanation {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 1rem;
}

.explanation-label {
  color: #ffffff;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.explanation-text {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
}

/* Action Buttons */
.result-actions .btn {
  border-radius: 25px;
  padding: 0.75rem 2rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-2px);
}

.btn-outline-light {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.btn-outline-light:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  color: #ffffff;
  transform: translateY(-2px);
}

.btn-success {
  background: linear-gradient(135deg, #28a745, #20c997);
  border: none;
}

.btn-success:hover {
  background: linear-gradient(135deg, #218838, #1e9ba4);
  transform: translateY(-2px);
}

.chart-container {
  height: 250px;
}

</style>