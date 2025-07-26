<template>
  <div class="dashboard-container">
    <Navbar />
    <div class="container-fluid py-4">
      <!-- Breadcrumb Navigation -->
      <Breadcrumb :items="breadcrumbItems" />
      
      <!-- Dashboard Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="dashboard-title">Subject Management</h2>
              <p class="text-muted">Manage all your subjects and their content</p>
            </div>
            <div>
              <button 
                class="btn add-subject-btn d-flex align-items-center gap-2"
                @click="showSubjectCreateModal"
              >
                <font-awesome-icon icon="plus" />
                <span class="d-none d-sm-inline">Add Subject</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Subject Cards Grid -->
      <div class="row g-4">
        <div 
          class="col-xl-3" 
          v-for="subject in subjects" 
          :key="subject.id"
        >
          <SubjectCard 
            v-bind:subject="subject"
            v-on:view-chapters="handleViewChapters"
            v-on:sent-edit-subject="showSubjectEditModal"
            v-on:sent-delete-subject="showSubjectDeleteModal"
          />
        </div>
      </div>
    </div>

    <!-- Subject Create Modal Component -->
    <SubjectCreateModal 
      ref="subjectCreate"
      @subject-created="handleSubjectCreated"
    />
    <!-- Subject Edit Modal Component -->
    <SubjectEditModal 
      ref="subjectEdit"
      @subject-edited="handleSubjectEdited"
    />
    <!-- Subject Delete Modal Component -->
    <SubjectDeleteModal
      ref="subjectDelete"
      @subject-deleted="handleSubjectDeleted"
    />
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue';
import Navbar from '@/components/Navbar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import axios from 'axios';
import BASE_URL from '@/config/apiConfig'
import SubjectCard from '@/components/Admin/SubjectCard.vue';
import { useToast } from 'vue-toastification';

// Lazy load components for better performance
const SubjectCreateModal = defineAsyncComponent(() =>
  import(/* webpackChunkName: "subject-create-modal", webpackPrefetch: true */ '@/components/Admin/SubjectCreateModal.vue')
);

const SubjectEditModal = defineAsyncComponent(() =>
  import(/* webpackChunkName: "subject-edit-modal", webpackPrefetch: true */ '@/components/Admin/SubjectEditModal.vue')
);

const SubjectDeleteModal = defineAsyncComponent(() =>
  import(/* webpackChunkName: "subject-delete-modal", webpackPrefetch: true */ '@/components/Admin/SubjectDeleteModal.vue')
);


export default {
  name: 'Subjects',
  components: {
    SubjectCard, 
    Navbar,
    Breadcrumb,
    SubjectCreateModal,
    SubjectEditModal,
    SubjectDeleteModal
  },
  data() {
    return {
      subjects:  [],
      // Breadcrumb items for navigation
      breadcrumbItems: [
        {
          name: 'Subjects',
          icon: 'book'
        }
      ]
    };
  },

  beforeMount() {
    // Fetch subjects from API
    this.fetchSubjects();
  },

  methods: {
    showSubjectCreateModal() {
      this.$refs.subjectCreate.show();
    },

    handleSubjectCreated(newSubject) {
      // Show success toast notification
      const toast = useToast();
      toast.success(`Subject ${newSubject.name} created successfully.`, { theme: 'light' });
      // Add to the list
      if (newSubject) {
        this.subjects.push(newSubject);
      } else {
        // If the response doesn't contain the data, refresh the list
        this.fetchSubjects();
      }
    },

    showSubjectEditModal(subjectToEdit) {
      this.$refs.subjectEdit.show(subjectToEdit);
    },

    handleSubjectEdited(updatedSubject) {
      // Show success toast notification
      const toast = useToast();
      toast.success(`Subject ${updatedSubject.oldName} updated successfully.`, { theme: 'light' });
      this.fetchSubjects();
    },

    showSubjectDeleteModal(subjectToDelete) {
      this.$refs.subjectDelete.show(subjectToDelete);
    },
    
    handleSubjectDeleted(deletedSubject) {
      // Show success toast notification
      const toast = useToast();
      toast.success(`Subject ${deletedSubject.name} deleted successfully.`, { theme: 'light' });
      // Remove the deleted subject from the list
      this.subjects = this.subjects.filter(subject => subject.id !== deletedSubject.id);
    },

    handleViewChapters(subject) {
      // Navigate to chapters page
      this.$router.push(`subjects/${subject.id}/chapters`);
    },

    async fetchSubjects() {
      const token = sessionStorage.getItem('access_token');
        
      if (!token) {
        store.dispatch('auth/logoutUser');
      }
      
      try {
        const response = await axios.get(`${BASE_URL}/subject`, {
          headers: {
            'Authorization': token,
          },
        });
        this.subjects = response.data;
      } catch (error) {
        console.error('Error fetching subjects:', error);
      }
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.dashboard-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
              radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
  pointer-events: none;
}

.dashboard-title {
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.text-muted {
  color: rgba(255, 255, 255, 0.8) !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.container-fluid {
  max-width: 1400px;
  position: relative;
  z-index: 1;
}

.add-subject-btn {
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

.add-subject-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.add-subject-btn:active {
  transform: translateY(0);
}

.add-subject-btn i {
  font-size: 0.8rem;
}

/* Mobile responsiveness */
@media (max-width: 575px) {
  .add-subject-btn {
    padding: 0.6rem 1rem;
    min-width: 44px;
  }
}
</style>