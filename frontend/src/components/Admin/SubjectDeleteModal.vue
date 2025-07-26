<template>
  <!-- Delete Subject Modal -->
  <div class="modal fade" id="subDeleteModal" tabindex="-1" aria-labelledby="subDeleteModalLabel" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="subDeleteModalLabel">
            Deleting Subject
            <span style="color: #ef4444; font-weight: 600;">
              {{ name }}
            </span>
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p class="p-text" v-show="!message">Are you sure you want to delete this subject {{ name }}?</p>

            <div v-if="error" class="alert alert-danger custom-alert-error"  role="alert">
              <font-awesome-icon icon="circle-exclamation" size="lg" style="color: #df6d83;" />   {{ error }}
            </div>
            <div v-if="message" class="alert alert-success custom-alert-success" role="alert">
              <font-awesome-icon icon="circle-check" size="lg" style="color: #129b72;" />   {{ message }}
            </div>
        </div>
        <div class="modal-footer" v-show="!message">
          <button type="button" class="btn btn-success me-auto" data-bs-dismiss="modal">
            Cancel
          </button>
          <button type="button" class="btn btn-danger" @click="deleteSub" :disabled="isDeleting">
            <span v-if="isDeleting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ isDeleting ? 'Deleting...' : 'Delete Subject' }}
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
  name: 'SubjectDeleteModal',
  data() {
    return {
      id: '',
      name: '',
      message:'',
      error: '',
      isDeleting: false,
      modalInstance: null
    };
  },
  mounted() {
    // Initialize modal instance
    this.modalInstance = new Modal(this.$refs.modal);
    
    // Reset form when modal is hidden
    this.$refs.modal.addEventListener('hidden.bs.modal', () => {
        this.id = '';
        this.name = '';
        this.error = '';
        this.message = '';
        this.isDeleting = false;
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
    show(subjectToDelete) {
      if (subjectToDelete) {
        this.id = subjectToDelete.id;
        this.name = subjectToDelete.name;
      }
      this.modalInstance.show();
    },
    
    hide() {
      this.modalInstance.hide();
    },

    async deleteSub() {
      this.error = '';
      this.isDeleting = true;

      try {
        const token = sessionStorage.getItem('access_token');

        if (!token) {
          this.error = 'You must be logged in.';
          this.isDeleting = false;
          setTimeout(() => {
            this.error = 'Redirecting to login...';
            setTimeout(() => {
              this.hide();
              store.dispatch('auth/logoutUser');
            }, 5000);
          }, 5000);
          return;
        }

        const response = await axios.patch(`${BASE_URL}/subject/delete`, {
          id: this.id
        }, 
        {
          headers: {
            Authorization: `${token}`,
          },
        });

        if (response.data.code == 200) {
            this.message = response.data.message
            setTimeout(() => {
              // Emit event to parent component with the deleted subject
              this.$emit('subject-deleted', { id: this.id, name: this.name });
              this.hide();
            }, 3000);
        }

      } catch (err) {
        console.error(err);
        this.error = err.response?.data?.error_message || 'Failed to delete subject. Please try again.';
      } finally {
        this.isDeleting = false;
      }
    }
  }
};
</script>

<style scoped>
/* Modal customizations - Higher specificity */
#subDeleteModal .modal-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: fit-content;
}


#subDeleteModal .modal-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem 3rem 1rem 3rem;
  background: transparent;
}

#subDeleteModal .modal-title {
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

#subDeleteModal .modal-body {
  padding: 1rem 3rem 2rem 3rem;
}

#subDeleteModal .modal-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 3rem 2rem 3rem;
  background: transparent;
}


#subDeleteModal .btn-close {
  filter: invert(1);
  opacity: 0.8;
}

#subDeleteModal .btn-close:hover {
  opacity: 1;
}

.btn-danger {
  background: linear-gradient(135deg, #ea6767 0%, #a24b76 100%);
  border: none;
  border-radius: 8px;
  font-weight: 500;
  padding: 0.5rem 1.5rem;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #d85a5a 0%, #90416a 100%);
  transform: translateY(-1px);
}

.btn-success {
  background: linear-gradient(135deg, #67ea8b 0%, #4ba268 100%);
  border: none;
  border-radius: 8px;
  font-weight: 500;
  padding: 0.5rem 1.5rem;
}

.btn-success:hover {
  background: linear-gradient(135deg, #5ad87a 0%, #41905c 100%);
  transform: translateY(-1px);
}

#subDeleteModal .custom-alert-error {
  background: rgba(220, 53, 69, 0.2) !important;
  border: 1px solid rgba(220, 53, 69, 0.3) !important;
  border-radius: 15px !important;
  backdrop-filter: blur(10px);
  color: #ffcdd2 !important;
}

#subDeleteModal .custom-alert-success {
  background: rgba(25, 135, 84, 0.2) !important;
  border: 1px solid rgba(25, 135, 84, 0.3) !important;
  border-radius: 15px !important;
  backdrop-filter: blur(10px);
  color: #d4edda !important;
}

#subDeleteModal .p-text {
  font-weight: 500;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

</style>