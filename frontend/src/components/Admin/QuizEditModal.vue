<template>
  <!-- Edit Quiz Modal -->
  <div class="modal fade" id="quizEditModal" tabindex="-1" aria-labelledby="quizEditModalLabel" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="quizEditModalLabel">
            Editing Quiz
            <span style="color: #00ff88; font-weight: 600;">
              {{ oldQuizName }}
            </span>
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitQuiz" enctype="multipart/form-data" novalidate>
            <!-- Quiz Name -->
            <div class="mb-3">
              <label for="name" class="form-label">Quiz Name</label>
              <input
                type="text"
                id="name"
                v-model="name"
                required
                class="form-control"
                placeholder="Enter quiz name"
              />
            </div>

            <!-- Duration -->
            <!-- <div class="mb-3">
              <label for="duration_mins" class="form-label">Duration (minutes)</label>
              <input
                type="number"
                id="duration_mins"
                v-model="duration_mins"
                class="form-control no-spinners"
                placeholder="Enter duration in minutes"
              />
            </div> -->
            <div class="mb-3">
              <label for="time_duration" class="form-label">Time Duration (HH:MM)</label>
              <input
                type="text"
                id="time_duration"
                v-model="time_duration"
                @blur="validateTimeInput"
                placeholder="HH:MM"
                pattern="^([01]\d|2[0-3]):([0-5]\d)$"
                title="Please enter duration in HH:MM format (01:30)"
                class="form-control"
              />
            </div>

            <!-- Difficulty Level - Radio Buttons -->
            <div class="mb-3">
              <label class="form-label">Difficulty Level</label>
              <div>
                <div class="form-check" v-for="option in difficultyOptions" :key="option.name">
                  <input
                    class="form-check-input"
                    type="radio"
                    :id="'difficulty_' + option.name"
                    :value="option.value"
                    v-model="difficulty"
                  />
                  <label class="form-check-label" :for="'difficulty_' + option.name">
                    {{ option.value }}
                  </label>
                </div>
              </div>
            </div>

            <!-- Quiz Type - Radio Buttons -->
            <div class="mb-3">
              <label class="form-label">Quiz Type</label>
              <div>
                <div class="form-check" v-for="option in quiz_type_options" :key="option.name">
                  <input
                    class="form-check-input"
                    type="radio"
                    :id="'quiz_type_' + option.name"
                    :value="option.value"
                    v-model="quiz_type"
                    required
                  />
                  <label class="form-check-label" :for="'quiz_type_' + option.name">
                    {{ option.value }}
                  </label>
                </div>
              </div>
            </div>

            <!-- Start Date and Time for Mock and Exam -->
            <div v-if="quiz_type === 'Mock' || quiz_type === 'Exam'" class="mb-3">
              <label class="form-label">Start Date and Time</label>
              <div class="row">
                <div class="col-md-6">
                  <input
                    type="date"
                    v-model="start_date"
                    class="form-control"
                    :min="minDate"
                  />
                </div>
                <div class="col-md-6">
                  <input
                    type="time"
                    v-model="start_time"
                    class="form-control"
                  />
                </div>
              </div>
            </div>

            <!-- End Date and Time for Mock only -->
            <div v-if="quiz_type === 'Mock'" class="mb-3">
              <label class="form-label">End Date and Time</label>
              <div class="row">
                <div class="col-md-6">
                  <input
                    type="date"
                    v-model="end_date"
                    class="form-control"
                    :min="start_date || minDate"
                  />
                </div>
                <div class="col-md-6">
                  <input
                    type="time"
                    v-model="end_time"
                    class="form-control"
                  />
                </div>
              </div>
            </div>

            <!-- Error and Success Messages -->
            <div v-if="error" class="alert alert-danger custom-alert-error" role="alert">
              <font-awesome-icon icon="circle-exclamation" size="lg" style="color: #df6d83;" />   {{ error }}
            </div>
            <div v-if="success" class="alert alert-success custom-alert-success" role="alert">
              <font-awesome-icon icon="circle-check" size="lg" style="color: #129b72;" />   Quiz edited successfully.
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light me-auto" @click="resetForm">
            <font-awesome-icon icon="rotate-left" /> Reset Form
          </button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Cancel
          </button>
          <button type="button" class="btn btn-primary" @click="submitQuiz" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ isSubmitting ? 'Editing...' : 'Edit Quiz' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';
import { Modal } from 'bootstrap';
import { useToast } from 'vue-toastification';

export default {
  name: 'QuizEditModal',
  data() {
    return {
        id: null,
        name: '',
        duration_mins: null,
        time_duration: '',
        isValidTimeInput: false, // Track if time input is valid
        difficulty: '',
        quiz_type: '',
        start_date: '',
        start_time: '',
        end_date: '',
        end_time: '',
        error: '',
        success: false,
        isSubmitting: false,
        modalInstance: null,
        chapter_name: '',
        chapter_id: null,
        difficultyOptions: [
          { name: 'easy', value: 'Easy' },
          { name: 'medium', value: 'Medium' },
          { name: 'hard', value: 'Hard' }
        ],
        quiz_type_options: [
          { name: 'practice', value: 'Practice' },
          { name: 'mock', value: 'Mock' },
          { name: 'exam', value: 'Exam' }
        ],
        oldQuizName: ''
    };
  },
  computed: {
    minDate() {
      const today = new Date();
      return today.toISOString().split('T')[0];
    }
  },
  mounted() {
    // Initialize modal instance
    this.modalInstance = new Modal(this.$refs.modal);
    
    // Reset form when modal is hidden
    this.$refs.modal.addEventListener('hidden.bs.modal', () => {
      this.resetForm();
    });
  },
  watch: {
    error(newError) {
      if (newError !== '') {
        const toast = useToast();
        toast.error(newError, { theme: 'light' });
      }
    }
  },
  computed: {
    calculatedDuration() {
      if (this.time_duration && this.isValidTimeInput) {
        const [hours, minutes] = this.time_duration.split(':').map(Number);
        this.duration_mins = hours * 60 + minutes; // Convert to total minutes
      }
    }
  },
  methods: {

    show(quizToEdit) {
      if (quizToEdit) {
        this.id = quizToEdit.id;
        this.name = quizToEdit.name;
        this.duration_mins = quizToEdit.duration_mins;
        if (quizToEdit.duration_mins) {
          // Format duration to HH:MM
          let hours = Math.floor(quizToEdit.duration_mins / 60);
          let minutes = quizToEdit.duration_mins % 60;
          this.time_duration = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
        } else {
          this.time_duration = '';
        }
        this.isValidTimeInput = true; // Reset to true for valid input
        this.difficulty = quizToEdit.difficulty;
        this.quiz_type = quizToEdit.quiz_type;
        if (quizToEdit.start_time) {
          this.start_date = quizToEdit.start_time.split(' ')[0];
          this.start_time = quizToEdit.start_time.split(' ')[1].substring(0, 5);
        } else {
          this.start_date = '';
          this.start_time = '';
        }
        if (quizToEdit.end_time) {
          this.end_date = quizToEdit.end_time.split(' ')[0];
          this.end_time = quizToEdit.end_time.split(' ')[1].substring(0, 5);
        } else {
          this.end_date = '';
          this.end_time = '';
        }
        this.oldQuizName = quizToEdit.name;
        this.chapter_name = quizToEdit.chapter_name;
        this.chapter_id = quizToEdit.chapter_id;
      } else {
        this.resetForm();
      }
      this.modalInstance.show();
    },
    
    hide() {
      this.modalInstance.hide();
    },

    validateTimeInput() {
      const regex = /^([01]\d|2[0-3]):([0-5]\d)$/; // HH:MM regex (00:00 to 23:59)
      if (!regex.test(this.time_duration)) {
        this.error = 'Invalid time format. Please use HH:MM (01:30).';
        this.isValidTimeInput = false;
      } else {
        this.error = '';
        this.isValidTimeInput = true;
        // const [hours, minutes] = this.time_duration.split(':').map(Number);
        // this.duration_mins = hours * 60 + minutes; // Convert to total minutes
        
      }
    },

    formatDateTimeForSubmission() {
      // Format datetime for backend submission
      if (this.start_date && this.start_time) {
        const startDateTime = `${this.start_date} ${this.start_time}:00`;
        
        if (this.quiz_type === 'Mock' && this.end_date && this.end_time) {
            const endDateTime = `${this.end_date} ${this.end_time}:00`;
            return { start_time: startDateTime, end_time: endDateTime };
        } else if (this.quiz_type === 'Exam' && this.duration_mins) {
            return { start_time: startDateTime, end_time: null };
        } 
      }
      return { start_time: null, end_time: null };
    },
    async submitQuiz() {
      this.error = '';
      this.success = false;
      this.isSubmitting = true;

      // Basic validation
      if (!this.name.trim()) {
        this.error = 'Quiz name is required';
        this.isSubmitting = false;
        return;
      }
      if (!this.duration_mins || this.duration_mins <= 0) {
        this.error = 'Duration must be a positive number';
        this.isSubmitting = false;
        return;
      }

      if (!this.quiz_type) {
        this.error = 'Quiz type is required';
        this.isSubmitting = false;
        return;
      }

      if(this.isValidTimeInput === false || !this.time_duration) {
        this.error = 'Please enter a valid time duration in HH:MM format (01:30)';
        this.isSubmitting = false;
        return;
      }

      if (this.time_duration && this.duration_mins <= 0) {
        this.error = 'Duration must be greater than 0 minutes';
        this.isSubmitting = false;
        return;
      }

      if (this.time_duration && isNaN(this.duration_mins)) {
        this.error = 'Time Duration must be a valid number in HH:MM format (01:30)';
        this.isSubmitting = false;
        return;
      }

      const { start_time, end_time } = this.formatDateTimeForSubmission();

      const quizData = {
        id: this.id,
        name: this.name,
        duration_mins: this.duration_mins,
        difficulty: this.difficulty,
        quiz_type: this.quiz_type,
        start_time,
        end_time,
        chapter_id: this.chapter_id
      };

      try {
        const token = sessionStorage.getItem('access_token');
        
        if (!token) {
          this.error = 'You must be logged in.';
          this.isSubmitting = false;
          setTimeout(() => {
            this.error = 'Redirecting to login...';
            setTimeout(() => {
              this.hide();
              this.resetForm();
              store.dispatch('auth/logoutUser');
            }, 5000);
          }, 5000);
          return;
        }

        const response = await axios.put(`${BASE_URL}/quiz/update`, quizData, {
          headers: { Authorization: `${token}` }
        });

        this.success = true;

        setTimeout(() => {
          // Emit event to parent component with the edited quiz
          this.$emit('quiz-edited', {data: response.data, oldName: this.oldQuizName});
          this.hide();
        }, 3000);

      } catch (err) {
        console.error(err);
        this.error = err.response?.data?.error_message || 'Failed to edit quiz.';
      } finally {
        this.isSubmitting = false;
      }
    },
    

    resetForm() {
        this.name = '';
        this.duration_mins = null;
        this.time_duration = '';
        this.isValidTimeInput = false;
        this.difficulty = '';
        this.quiz_type = '';
        this.start_date = '';
        this.start_time = '';
        this.end_date = '';
        this.end_time = '';
        this.error = '';
        this.success = false;
        this.isSubmitting = false;
    }
  }
};
</script>

<style scoped>
/* Modal customizations - Higher specificity */
#quizEditModal .modal-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

#quizEditModal .modal-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem 3rem 1rem 3rem;
  background: transparent;
}

#quizEditModal .modal-title {
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

#quizEditModal .modal-body {
  padding: 1rem 3rem 2rem 3rem;
}

#quizEditModal .modal-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 3rem 2rem 3rem;
  background: transparent;
}

#quizEditModal .form-label {
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 0.5rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

#quizEditModal .form-control {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  backdrop-filter: blur(10px);
}

#quizEditModal .form-control::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

#quizEditModal .form-control:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

#quizEditModal .form-check-label {
  color: rgba(255, 255, 255, 0.9);
  margin-left: 0.5rem;
}

#quizEditModal .form-check-input {
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

#quizEditModal .form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

#quizEditModal .btn-close {
  filter: invert(1);
  opacity: 0.8;
}

#quizEditModal .btn-close:hover {
  opacity: 1;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  font-weight: 500;
  padding: 0.5rem 1.5rem;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-1px);
}

.btn-secondary {
  border-radius: 8px;
  font-weight: 500;
  padding: 0.5rem 1.5rem;
}

.btn-light {
  border-radius: 8px;
  font-weight: 500;
  padding: 0.5rem 1.5rem;
}

#quizEditModal .custom-alert-error {
  background: rgba(220, 53, 69, 0.2) !important;
  border: 1px solid rgba(220, 53, 69, 0.3) !important;
  border-radius: 15px !important;
  backdrop-filter: blur(10px);
  color: #ffcdd2 !important;
}

#quizEditModal .custom-alert-success {
  background: rgba(25, 135, 84, 0.2) !important;
  border: 1px solid rgba(25, 135, 84, 0.3) !important;
  border-radius: 15px !important;
  backdrop-filter: blur(10px);
  color: #d4edda !important;
}

/* Remove number input spinners */
/* #quizEditModal .no-spinners::-webkit-outer-spin-button,
#quizEditModal .no-spinners::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

#quizEditModal .no-spinners[type=number] {
  appearance: textfield;
  -moz-appearance: textfield;
} */
</style>