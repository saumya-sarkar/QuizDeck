<template>
  <!-- Create Subject Modal -->
  <div class="modal fade" id="subCreateModal" tabindex="-1" aria-labelledby="subCreateModalLabel" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="subCreateModalLabel">Create Subject</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitSubject" enctype="multipart/form-data" novalidate>
            <div class="mb-3">
              <label for="name" class="form-label">Subject Name</label>
              <input
                type="text"
                id="name"
                v-model="form.name"
                required
                class="form-control"
                placeholder="Enter subject name"
              />
            </div>

            <div class="mb-3">
              <label for="description" class="form-label">Description</label>
              <textarea
                id="description"
                v-model="form.description"
                rows="3"
                required
                class="form-control"
                placeholder="Enter subject description"
              ></textarea>
            </div>

            <div class="mb-3">
              <label for="cover" class="form-label">Cover Image</label>
              <input
                type="file"
                id="cover"
                accept="image/*"
                class="form-control"
                ref="fileInput"
                @change="handleFileUpload"
              />
              <div v-if="previewUrl" class="mt-3 text-center">
                <img v-bind:src="previewUrl" alt="Cover Preview" class="img-thumbnail" style="max-height: 200px;" />
              </div>
            </div>

            <div v-if="error" class="alert alert-danger custom-alert-error"  role="alert">
              <font-awesome-icon icon="circle-exclamation" size="lg" style="color: #df6d83;" />   {{ error }}
            </div>
            <div v-if="success" class="alert alert-success custom-alert-success" role="alert">
              <font-awesome-icon icon="circle-check" size="lg" style="color: #129b72;" />   Subject created successfully.
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light me-auto" @click="resetForm"><font-awesome-icon icon="rotate-left" /> Reset Form</button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="button" class="btn btn-primary" @click="submitSubject" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ isSubmitting ? 'Creating...' : 'Create Subject' }}
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
  name: 'SubjectCreateModal',
  data() {
    return {
      form: {
        name: '',
        description: '',
      },
      file: null,
      previewUrl: null,
      error: '',
      success: false,
      isSubmitting: false,
      modalInstance: null
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
    show() {
      this.resetForm();
      this.modalInstance.show();
    },
    
    hide() {
      this.modalInstance.hide();
    },

    handleFileUpload(event) {
      const uploadedFile = event.target.files[0];
      if (uploadedFile) {
        this.file = uploadedFile;
        this.previewUrl = URL.createObjectURL(uploadedFile);
      }
    },

    async submitSubject() {
      this.error = '';
      this.success = false;
      this.isSubmitting = true;
      const toast = useToast();

      // Basic validation
      if (!this.form.name.trim()) {
        this.error = 'Subject name is required';
        this.isSubmitting = false;
        return;
      }

      if (!this.form.description.trim()) {
        this.error = 'Description is required';
        this.isSubmitting = false;
        return;
      }

      const formData = new FormData();
      formData.append('name', this.form.name);
      formData.append('description', this.form.description);
      if (this.file) {
        formData.append('file', this.file);
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

        const response = await axios.post(`${BASE_URL}/subject/update`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `${token}`,
          },
        });

        this.success = true;
        
        setTimeout(() => {
          // Emit event to parent component with the created subject
          this.$emit('subject-created', response.data);
          this.hide();
        }, 3000);

      } catch (err) {
        console.error(err);
        this.error = err.response?.data?.error_message || 'Failed to create subject. Please try again.';
      } finally {
        this.isSubmitting = false;
      }
    },

    resetForm() {
      this.form.name = '';
      this.form.description = '';
      this.file = null;
      this.previewUrl = null;
      this.error = '';
      this.success = false;
      this.isSubmitting = false;
      
      // Reset file input
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = null;
      }
    }
  }
};
</script>

<style scoped>
/* Modal customizations - Higher specificity */
#subCreateModal .modal-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}


#subCreateModal .modal-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem 3rem 1rem 3rem;
  background: transparent;
}

#subCreateModal .modal-title {
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

#subCreateModal .modal-body {
  padding: 1rem 3rem 2rem 3rem;
}

#subCreateModal .modal-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 3rem 2rem 3rem;
  background: transparent;
}

#subCreateModal .form-label {
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 0.5rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

#subCreateModal .form-control {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  backdrop-filter: blur(10px);
}

#subCreateModal .form-control::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

#subCreateModal .form-control:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

#subCreateModal .btn-close {
  filter: invert(1);
  opacity: 0.8;
}

#subCreateModal .btn-close:hover {
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

#subCreateModal .custom-alert-error {
  background: rgba(220, 53, 69, 0.2) !important;
  border: 1px solid rgba(220, 53, 69, 0.3) !important;
  border-radius: 15px !important;
  backdrop-filter: blur(10px);
  color: #ffcdd2 !important;
}

#subCreateModal .custom-alert-success {
  background: rgba(25, 135, 84, 0.2) !important;
  border: 1px solid rgba(25, 135, 84, 0.3) !important;
  border-radius: 15px !important;
  backdrop-filter: blur(10px);
  color: #d4edda !important;
}

</style>