<template>
  <!-- Create Question Modal -->
  <div class="modal fade" id="questionCreateModal" tabindex="-1" aria-labelledby="questionCreateModalLabel" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="questionCreateModalLabel">Adding Question to {{ quiz_name }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitQuestion" novalidate>
            <!-- Question Statement -->
            <div class="mb-3">
              <label for="question_statement" class="form-label">Question Statement</label>
              <textarea
                id="question_statement"
                v-model="question_statement"
                required
                class="form-control"
                placeholder="Enter your question here"
                rows="3"
              ></textarea>
            </div>

            <!-- Marks -->
            <div class="mb-3">
              <label for="marks" class="form-label">Marks</label>
              <input
                type="number"
                id="marks"
                v-model.number="marks"
                class="form-control no-spinners"
                placeholder="Enter marks for this question"
              />
            </div>

            <!-- Answer Options -->
            <div class="mb-3">
              <label class="form-label">Answer Options</label>
              <div 
                v-for="(option, index) in options" 
                :key="index"
                class="option-create-item mb-3"
              >
                <div class="option-create-header mb-2">
                  <span class="option-create-label">Option {{ getOptionLabel(index) }}</span>
                  <button 
                    class="btn btn-sm btn-outline-danger ms-2"
                    @click="removeOption(index)"
                    v-if="options.length > 2"
                    type="button"
                  >
                    Delete Option <font-awesome-icon icon="times" />
                  </button>
                </div>
                <div class="option-create-controls">
                  <div class="form-check me-3">
                    <input 
                      class="form-check-input correct-option-radio"
                      type="radio" 
                      v-model="correctOptionIndex" 
                      :value="index"
                      :id="'correct_' + index"
                      required
                    />
                    <label class="form-check-label correct-option-label" :for="'correct_' + index">
                      Correct Answer
                    </label>
                  </div>
                  <div class="flex-grow-1">
                    <input 
                      type="text" 
                      v-model="option.option_text" 
                      class="form-control"
                      :placeholder="'Enter option ' + getOptionLabel(index)"
                      required
                    />
                  </div>
                </div>
              </div>
              <button 
                class="btn btn-outline-secondary btn-sm glass-btn mt-2" 
                @click="addOption"
                type="button"
              >
                <font-awesome-icon icon="plus" /> Add Option
              </button>
            </div>

            <!-- Explanation -->
            <div class="mb-3">
              <label for="explanation" class="form-label">Explanation</label>
              <textarea
                id="explanation"
                v-model="explanation"
                class="form-control"
                placeholder="Enter explanation for this question"
                rows="3"
              ></textarea>
            </div>

            <!-- Error and Success Messages -->
            <div v-if="error" class="alert alert-danger custom-alert-error" role="alert">
              <font-awesome-icon icon="circle-exclamation" size="lg" style="color: #df6d83;" />   {{ error }}
            </div>
            <div v-if="success" class="alert alert-success custom-alert-success" role="alert">
              <font-awesome-icon icon="circle-check" size="lg" style="color: #129b72;" />   Question created successfully.
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light me-auto" @click="resetForm">
            <font-awesome-icon icon="rotate-left" /> Reset Form
          </button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-primary" @click="submitQuestion" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ isSubmitting ? 'Creating...' : 'Create Question' }}
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
  name: 'QuestionCreateModal',
  data() {
    return {
        question_statement: '',
        marks: 1,
        options: [
          { option_text: '', is_correct: false },
          { option_text: '', is_correct: false }
        ],
        correctOptionIndex: null,
        explanation: '',
        error: '',
        success: false,
        isSubmitting: false,
        modalInstance: null,
        quiz_name: '',
        quiz_id: null
    };
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
  methods: {
    show(data) {
      this.resetForm();
      this.quiz_name = data.quiz_name;
      this.quiz_id = data.quiz_id;
      this.modalInstance.show();
    },
    
    hide() {
      this.modalInstance.hide();
    },

    getOptionLabel(index) {
      return String.fromCharCode(65 + index);
    },

    addOption() {
      this.options.push({ 
        option_text: '', 
        is_correct: false 
      });
    },

    removeOption(index) {
      if (this.options.length <= 2) {
        this.error = 'A question must have at least 2 options';
        return;
      }
      this.options.splice(index, 1);

      // Move correct option index if needed
      if (this.correctOptionIndex === index) {
        this.correctOptionIndex = null;
      } else if (this.correctOptionIndex > index) {
        this.correctOptionIndex--;
      }
    },

    async submitQuestion() {
      this.error = '';
      this.success = false;
      this.isSubmitting = true;

      // Basic validation
      if (!this.question_statement.trim()) {
        this.error = 'Question statement is required';
        this.isSubmitting = false;
        return;
      }

      if (this.correctOptionIndex === null || this.correctOptionIndex === -1) {
        this.error = 'Please select the correct answer';
        this.isSubmitting = false;
        return;
      }

      const hasEmptyOptions = this.options.some(opt => !opt.option_text?.trim());
      if (hasEmptyOptions) {
        this.error = 'All options must have text';
        this.isSubmitting = false;
        return;
      }


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

        // Mark correct option
        this.options.forEach((opt, i) => {
          opt.is_correct = i === this.correctOptionIndex;
        });

        const response = await axios.post(`${BASE_URL}/question/update`, {
          question_statement: this.question_statement,
          marks: this.marks,
          explanation: this.explanation || null,
          quiz_id: this.quiz_id,
          question_options: this.options
        }, {
          headers: {
            Authorization: `${token}`,
          },
        });

        this.success = true;
        
        setTimeout(() => {
          // Emit event to parent component with the created question
          this.$emit('question-created', response.data);
          this.hide();
        }, 3000);

      } catch (err) {
        console.error(err);
        this.error = err.response?.data?.error_message || 'Failed to create question.';
      } finally {
        this.isSubmitting = false;
      }
    },

    resetForm() {
        this.question_statement = '';
        this.marks = 1;
        this.options = [
          { option_text: '', is_correct: false },
          { option_text: '', is_correct: false }
        ];
        this.correctOptionIndex = null;
        this.explanation = '';
        this.error = '';
        this.success = false;
        this.isSubmitting = false;
    }
  }
};
</script>

<style scoped>
/* Modal customizations - Higher specificity */
#questionCreateModal .modal-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

#questionCreateModal .modal-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem 3rem 1rem 3rem;
  background: transparent;
}

#questionCreateModal .modal-title {
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

#questionCreateModal .modal-body {
  padding: 1rem 3rem 2rem 3rem;
}

#questionCreateModal .modal-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 3rem 2rem 3rem;
  background: transparent;
}

#questionCreateModal .form-label {
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  font-size: 0.9rem;
}

#questionCreateModal .form-control {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: 15px !important;
  color: #2c3e50 !important;
  padding: 0.75rem 1rem !important;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  font-weight: 500;
}

#questionCreateModal .form-control::placeholder {
  color: rgba(237, 239, 241, 0.6) !important;
}

#questionCreateModal .form-control:focus {
  background: rgba(255, 255, 255, 0.25) !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25) !important;
  color: #2c3e50 !important;
}

/* Options Section */
.option-create-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 1rem;
  backdrop-filter: blur(5px);
}

.option-create-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.option-create-label {
  font-weight: 600;
  color: #ffffff;
  font-size: 0.95rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.option-create-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Form Check - Radio buttons with better visibility */
#questionCreateModal .form-check {
  display: flex;
  align-items: center;
  min-height: 1.5rem;
}

#questionCreateModal .correct-option-radio {
  background-color: rgba(255, 255, 255, 0.2) !important;
  border: 2px solid rgba(255, 255, 255, 0.4) !important;
  margin-right: 0.5rem !important;
}

#questionCreateModal .correct-option-radio:checked {
  background-color: #0d6efd !important;
  border-color: #0d6efd !important;
}

#questionCreateModal .correct-option-label {
  color: #ffffff;
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
  margin-bottom: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

#questionCreateModal .btn-close {
  filter: invert(1);
  opacity: 0.8;
}

#questionCreateModal .btn-close:hover {
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

.glass-btn {
  border-radius: 12px;
  font-weight: 500;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.btn-outline-secondary.glass-btn {
  color: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-outline-secondary.glass-btn:hover {
  color: #fff;
  background: rgba(108, 117, 125, 0.8);
  border-color: rgba(108, 117, 125, 0.8);
  transform: translateY(-1px);
}

.btn-outline-danger {
  background: rgba(220, 53, 69, 0.1) !important;
  border: 1px solid rgba(220, 53, 69, 0.3) !important;
  color: #f36c7a !important;
  backdrop-filter: blur(10px);
  border-radius: 6px !important;
  transition: all 0.2s ease;
}

.btn-outline-danger:hover {
  background: rgba(220, 53, 69, 0.2) !important;
  border-color: rgba(220, 53, 69, 0.5) !important;
  color: #ffffff !important;
  transform: translateY(-1px);
}

#questionCreateModal .custom-alert-error {
  background: rgba(220, 53, 69, 0.2) !important;
  border: 1px solid rgba(220, 53, 69, 0.3) !important;
  border-radius: 15px !important;
  backdrop-filter: blur(10px);
  color: #ffcdd2 !important;
}

#questionCreateModal .custom-alert-success {
  background: rgba(25, 135, 84, 0.2) !important;
  border: 1px solid rgba(25, 135, 84, 0.3) !important;
  border-radius: 15px !important;
  backdrop-filter: blur(10px);
  color: #d4edda !important;
}

/* Remove number input spinners */
#questionCreateModal .no-spinners::-webkit-outer-spin-button,
#questionCreateModal .no-spinners::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

#questionCreateModal .no-spinners[type=number] {
  appearance: textfield;
  -moz-appearance: textfield;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  #questionCreateModal .modal-body {
    padding: 1rem 1.5rem;
  }
  
  #questionCreateModal .modal-header {
    padding: 1.5rem 1.5rem 1rem 1.5rem;
  }
  
  #questionCreateModal .modal-footer {
    padding: 1rem 1.5rem 1.5rem 1.5rem;
  }
  
  .option-create-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>