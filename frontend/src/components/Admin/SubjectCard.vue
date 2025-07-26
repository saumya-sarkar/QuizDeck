<template>
  <div class="card h-100 shadow-sm hover-card glass-card">
    <!-- Image Section -->
    <div class="card-img-container" @click="onViewChapters">
      <img 
        v-if="subject.cover_url && !imageError"
        v-bind:src="subject.cover_url" 
        v-bind:alt="subject.name"
        class="card-img-top"
        @error="handleImageError"
        @load="handleImageLoad"
      />
      <div 
        v-else 
        class="card-img-placeholder d-flex align-items-center justify-content-center"
      >
        <div class="placeholder-content text-center">
          <font-awesome-icon icon="book" class="placeholder-icon mb-2" />
          <div class="placeholder-text">{{ getImagePlaceholderText() }}</div>
        </div>
      </div>
    </div>

    <div class="card-body d-flex flex-column glass-body" @click="onViewChapters">
      <!-- Header Section -->
      <div class="card-header-section mb-3">
        <div class="d-flex align-items-center justify-content-between">
          <h5 class="card-title text-primary mb-0 flex-grow-1">{{ subject.name }}</h5>
          <!-- Badge beside title -->
          <div v-if="subject.badge" class="ms-2">
            <span 
              class="badge glass-badge"
              v-bind:class="getBadgeClass(subject.badge)"
            >
              {{ subject.badge }}
            </span>
          </div>
        </div>
      </div>

      <!-- Description Section -->
      <p class="card-text text-secondary flex-grow-1">
        {{ subject.description }}
      </p>

      <!-- Stats Section -->
      <div class="card-stats mb-3">
        <div class="row g-2">
          <div class="col-4" v-if="subject.totalUsers !== undefined">
            <div class="stat-item text-center glass-stat">
              <font-awesome-icon icon="users" class="text-info mb-1" />
              <div class="stat-number">{{ subject.totalUsers }}</div>
              <small class="stat-label text-muted">Users</small>
            </div>
          </div>
          
          <div class="col-4" v-if="subject.totalChapters !== undefined">
            <div class="stat-item text-center glass-stat">
              <font-awesome-icon icon="book" class="text-success mb-1" />
              <div class="stat-number">{{ subject.totalChapters }}</div>
              <small class="stat-label text-muted">Chapters</small>
            </div>
          </div>
          
          <div class="col-4" v-if="subject.totalQuizzes !== undefined">
            <div class="stat-item text-center glass-stat">
              <font-awesome-icon icon="question-circle" class="text-warning mb-1" />
              <div class="stat-number">{{ subject.totalQuizzes }}</div>
              <small class="stat-label text-muted">Quizzes</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="card-actions mt-auto" @click.stop>
        <div class="d-flex gap-2">
          <button 
            class="btn btn-outline-primary flex-fill glass-btn"
            @click="sendEditSubject"
          >
            <font-awesome-icon icon="edit" class="me-1" />
            Edit
          </button>
          <button 
            class="btn btn-outline-danger glass-btn"
            @click="sendDeleteSubject"
          >
            <font-awesome-icon icon="trash" />
          </button>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="imageLoading" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SubjectCard',
  props: {
    subject: {
      type: Object,
      required: true,
      validator(value) {
        return value.description && value.name;
      }
    }
  },
  data() {
    return {
      imageError: false,
      imageLoading: false
    };
  },
  methods: {
    onViewChapters() {
      this.$emit('view-chapters', this.subject);
    },
    sendEditSubject() {
      // Emit event to parent component to handle editing
      this.$emit('sent-edit-subject', this.subject);
    },
    sendDeleteSubject() {
      this.$emit('sent-delete-subject', this.subject);
    },
    getBadgeClass(badge) {
      const badgeClasses = {
        'Popular': 'bg-danger',
        'New': 'bg-success',
        'Featured': 'bg-warning text-dark',
        'Updated': 'bg-info'
      };
      return badgeClasses[badge] || 'bg-secondary';
    },
    handleImageError() {
      this.imageError = true;
      this.imageLoading = false;
    },
    handleImageLoad() {
      this.imageLoading = false;
    },
    getImagePlaceholderText() {
      return this.subject.name;
    }
  },
  watch: {
    'subject.cover_url'() {
      // Reset image state when image URL changes
      this.imageError = false;
      this.imageLoading = !!this.subject.cover_url;
    }
  },
  mounted() {
    // Set initial loading state if image exists
    if (this.subject.cover_url) {
      this.imageLoading = true;
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

.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.05) 100%);
  pointer-events: none;
  z-index: 1;
}

.card-img-container {
  position: relative;
  height: 250px;
  overflow: hidden;
  cursor: pointer;
  z-index: 2;
}

.glass-body {
  cursor: pointer;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 2;
}

.card-img-top {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-img-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.placeholder-content {
  padding: 1rem;
}

.placeholder-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.placeholder-text {
  font-size: 1.1rem;
  font-weight: 600;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  backdrop-filter: blur(5px);
}

.card-header-section {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 0.75rem;
}

.card-title {
  font-weight: 600;
  font-size: 1.1rem;
  color: #2c3e50 !important;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.glass-badge {
  font-size: 0.7rem;
  padding: 0.4rem 0.6rem;
  border-radius: 12px;
  white-space: nowrap;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.card-text {
  font-size: 0.9rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: #444 !important;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.3);
}

.glass-stat {
  padding: 0.5rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.stat-number {
  font-weight: 600;
  font-size: 1.1rem;
  color: #2c3e50;
}

.stat-label {
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  color: #666 !important;
}

.card-actions {
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
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

.position-absolute {
  z-index: 10;
}
</style>