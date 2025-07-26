<template>
  <div class="question-card shadow-sm hover-card glass-card">
    <div class="card-body d-flex glass-body">

      <!-- Left Section: Question Number, Marks and Actions -->
      <div class="question-left">
        <div class="question-number">{{ question.id }}</div>

        <!-- Marks Display/Edit -->
        <div class="question-marks-sidebar">
          <div v-if="!isEditing" class="marks-display">
            <div class="marks-value">{{ question.marks }}</div>
            <div class="marks-label">{{ question.marks === 1 ? 'Mark' : 'Marks' }}</div>
          </div>
          <div v-else class="marks-edit-container">
            <label class="form-label-edit">Marks</label>
            <input 
              type="number" 
              v-model.number="editableQuestion.marks" 
              class="form-control form-control-edit marks-input"
            />
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="question-actions mt-auto" v-if="!isEditing">
          <div class="d-flex flex-column gap-2">
            <button 
              class="btn btn-outline-primary btn-sm glass-btn"
              @click="startEditing"
            >
              <font-awesome-icon icon="edit" /> Edit
            </button>
            <button 
              class="btn btn-outline-danger btn-sm glass-btn"
              @click="deleteQuestion(question)"
            >
              <font-awesome-icon icon="trash" /> Delete
            </button>
          </div>
        </div>

        <!-- Save/Cancel in Edit Mode -->
        <div class="question-actions mt-auto" v-else>
          <div class="d-flex flex-column gap-2">
            <button 
              class="btn btn-outline-success btn-sm glass-btn"
              @click="saveEdit"
            >
              <font-awesome-icon icon="check" /> Save
            </button>
            <button 
              class="btn btn-outline-secondary btn-sm glass-btn"
              @click="cancelEdit"
            >
              <font-awesome-icon icon="times" /> Cancel
            </button>
          </div>
        </div>
      </div>

      <!-- Right Section: Question Content -->
      <div class="question-right flex-grow-1 position-relative">

        <!-- Question Statement -->
        <div class="question-content mb-3">
          <h6 class="question-statement mb-3" v-if="!isEditing">{{ question.question_statement }}</h6>
          <div v-else class="mb-3">
            <label class="form-label form-label-edit">Question Statement</label>
            <input 
              type="text" 
              v-model="editableQuestion.question_statement" 
              class="form-control form-control-edit"
              placeholder="Enter question statement"
              required
            />
          </div>
        </div>

        <!-- Options -->
        <div class="question-options mb-3" v-if="!isEditing">
          <div 
            v-for="(option, index) in question.options" 
            :key="option.id"
            class="option-item mb-2"
            :class="{ 'correct-option': option.is_correct }"
          >
            <div class="option-content">
              <span class="option-label">{{ getOptionLabel(index) }}.</span>
              <span class="option-text">{{ option.option_text }}</span>
            </div>
          </div>
        </div>

        <!-- Editable Options -->
        <div class="question-options mb-3" v-else>
          <label class="form-label form-label-edit mb-2">Answer Options</label>
          <div 
            v-for="(option, index) in editableQuestion.options" 
            :key="option.id || index"
            class="option-edit-item mb-3"
          >
            <div class="option-edit-header mb-2">
              <span class="option-edit-label">Option {{ getOptionLabel(index) }}</span>
              <button 
                class="btn btn-outline-danger btn-sm glass-btn"
                @click="removeOption(index)"
                v-if="editableQuestion.options.length > 2"
              >
                Delete Option <font-awesome-icon icon="trash" />
              </button>
            </div>
            <div class="option-edit-controls">
              <div class="form-check me-3">
                <input 
                  class="form-check-input correct-option-radio"
                  type="radio" 
                  v-model="correctOptionIndex" 
                  :value="index"
                  :id="'correct_' + index"
                />
                <label class="form-check-label correct-option-label" :for="'correct_' + index">
                  Correct Answer
                </label>
              </div>
              <div class="flex-grow-1">
                <input 
                  type="text" 
                  v-model="option.option_text" 
                  class="form-control form-control-edit"
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
      </div>
    </div>

    <!-- Explanation: Full width -->
    <div class="question-explanation" v-if="!isEditing && question.explanation">
      <div class="detail-item">
        <font-awesome-icon icon="info-circle" class="me-1" />
        <strong>Explanation:</strong> {{ question.explanation }}
      </div>
    </div>
    <div class="question-explanation" v-else-if="isEditing">
      <label class="form-label form-label-edit">Explanation</label>
      <textarea 
        v-model="editableQuestion.explanation" 
        class="form-control form-control-edit" 
        placeholder="Enter explanation for this question"
        rows="3">
      </textarea>
    </div>
  </div>
</template>

<script>
import { useToast } from 'vue-toastification';

export default {
  name: 'QuestionCard',
  props: {
    question: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isEditing: false,
      editableQuestion: null,
      correctOptionIndex: null
    };
  },
  methods: {
    getOptionLabel(index) {
      return String.fromCharCode(65 + index);
    },
    startEditing() {
      this.isEditing = true;
      this.editableQuestion = this.question;

      // Ensure options exist
      if (!this.editableQuestion.options || this.editableQuestion.options.length === 0) {
        this.editableQuestion.options = [
          { option_text: '', is_correct: true },
          { option_text: '', is_correct: false }
        ];
        this.correctOptionIndex = 0;
      } else {
        this.correctOptionIndex = this.editableQuestion.options.findIndex(opt => opt.is_correct);
      }
    },
    cancelEdit() {
      this.isEditing = false;
      this.editableQuestion = null;
      this.correctOptionIndex = null;
    },
    saveEdit() {
        if (!this.editableQuestion) return;
        // Basic validation
        const toast = useToast();
        if (!this.editableQuestion.question_statement?.trim()) {
            toast.error('Question statement is required');
            return;
        }

        if (this.correctOptionIndex === null || this.correctOptionIndex === -1) {
            toast.error('Please select the correct answer');
            return;
        }

        const hasEmptyOptions = this.editableQuestion.options.some(opt => !opt.option_text?.trim());
        if (hasEmptyOptions) {
            toast.error('All options must have text');
            return;
        }

        // Mark correct option
        this.editableQuestion.options.forEach((opt, i) => {
            opt.is_correct = i === this.correctOptionIndex;
        });

        this.$emit('save-question', this.editableQuestion);
        this.isEditing = false;
    },
    deleteQuestion(question) {
      if (confirm('Are you sure you want to delete this question?')) {
        this.$emit('delete-question', question);
      }
    },
    addOption() {
      this.editableQuestion.options.push({ 
        option_text: '', 
        is_correct: false 
      });
    },
    removeOption(index) {
      if (this.editableQuestion.options.length <= 2) {
        const toast = useToast();
        toast.error('A question must have at least 2 options');
        return;
      }
      
      this.editableQuestion.options.splice(index, 1);
      
      // Move correct option index if needed
      if (this.correctOptionIndex === index) {
        this.correctOptionIndex = null;
      } else if (this.correctOptionIndex > index) {
        this.correctOptionIndex--;
      }
    }
  }
};
</script>

<style scoped>
.hover-card {
  transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
  cursor: pointer;
}

.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2) !important;
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.1);
}

.glass-body {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px);
  display: flex;
}

.question-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-width: 120px;
  padding: 1rem;
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  gap: 0.75rem;
}

.question-right {
  padding: 1rem 1.5rem;
  position: relative;
}

/* Marks Sidebar */
.question-marks-sidebar {
  margin: 1rem 0;
  text-align: center;
}

.marks-display {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.75rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.marks-value {
  font-weight: 700;
  font-size: 1.5rem;
  color: #2c3e50;
}

.marks-label {
  font-weight: 500;
  font-size: 0.8rem;
  color: #2c3e50;
  letter-spacing: 0.5px;
  margin-top: 0.25rem;
}

.marks-edit-container {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.75rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
}

.marks-input {
  width: 100%;
  text-align: center;
  font-weight: 600;
}

/* Remove number input spinners for marks */
.marks-input::-webkit-outer-spin-button,
.marks-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.marks-input[type=number] {
  appearance: textfield;
  -moz-appearance: textfield;
}

/* Question Number */
.question-number {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  color: #ffffff;
  backdrop-filter: blur(10px);
}

/* Question Text */
.question-statement {
  font-weight: 700;
  font-size: 1.2rem;
  color: #2c3e50;
  line-height: 1.6;
}

/* Form Controls - Improved visibility for edit mode */
.form-control-edit {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: 15px !important;
  color: #2c3e50 !important;
  padding: 0.75rem 1rem !important;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  font-weight: 500;
}

.form-control-edit:focus {
  background: rgba(255, 255, 255, 0.25) !important;
  border: 1px solid rgba(255, 255, 255, 0.5) !important;
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25) !important;
  color: #2c3e50 !important;
}

.form-control-edit::placeholder {
  color: rgba(44, 62, 80, 0.6) !important;
}

.form-label-edit {
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  font-size: 0.9rem;
}

/* Options Display */
.option-item {
  padding: 0.75rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.option-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

.option-item.correct-option {
  background: rgba(40, 167, 69, 0.2);
  border-color: rgba(40, 167, 69, 0.4);
}

.option-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.option-label {
  font-weight: 700;
  color: #2c3e50;
  min-width: 20px;
}

.option-text {
  color: #2c3e50;
  font-weight: 500;
}

/* Options Edit */
.option-edit-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 1rem;
  backdrop-filter: blur(5px);
}

.option-edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.option-edit-label {
  font-weight: 600;
  color: #ffffff;
  font-size: 0.95rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.option-edit-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Form Check - Radio buttons with better visibility */
.form-check {
  display: flex;
  align-items: center;
  min-height: 1.5rem;
}

.correct-option-radio {
  background-color: rgba(255, 255, 255, 0.2) !important;
  border: 2px solid rgba(255, 255, 255, 0.4) !important;
  margin-right: 0.5rem !important;
}

.correct-option-radio:checked {
  background-color: #0d6efd !important;
  border-color: #0d6efd !important;
}

.correct-option-label {
  color: #ffffff;
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
  margin-bottom: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* Explanation Full Width */
.question-explanation {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

.detail-item {
  color: #2c3e50;
  font-size: 1rem;
  line-height: 1.5;
}

/* Buttons - Consistent with existing glass buttons */
.glass-btn {
  border-radius: 12px;
  font-weight: 500;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.btn-outline-primary.glass-btn {
  color: #0d6efd;
  border-color: rgba(13, 110, 253, 0.3);
}

.btn-outline-primary.glass-btn:hover {
  color: #fff;
  background: rgba(13, 110, 253, 0.8);
  border-color: rgba(13, 110, 253, 0.8);
  transform: translateY(-1px);
}

.btn-outline-danger.glass-btn {
  color: #dc3545;
  border-color: rgba(220, 53, 69, 0.3);
}

.btn-outline-danger.glass-btn:hover {
  color: #fff;
  background: rgba(220, 53, 69, 0.8);
  border-color: rgba(220, 53, 69, 0.8);
  transform: translateY(-1px);
}

.btn-outline-success.glass-btn {
  color: #198754;
  border-color: rgba(25, 135, 84, 0.3);
}

.btn-outline-success.glass-btn:hover {
  color: #fff;
  background: rgba(25, 135, 84, 0.8);
  border-color: rgba(25, 135, 84, 0.8);
  transform: translateY(-1px);
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

/* Responsive adjustments */
@media (max-width: 768px) {
  .question-right {
    padding: 1rem;
  }
  
  .question-left {
    min-width: 100px;
  }
  
  .marks-edit-container {
    padding: 0.5rem;
  }
  
  .option-edit-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .marks-value {
    font-size: 1.2rem;
  }
}
</style>