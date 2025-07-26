<template>
  <div class="landing-page">
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg fixed-top custom-navbar">
      <div class="container">
        <a class="navbar-brand fw-bold fs-3" href="#">QuizDeck</a>
        <div class="navbar-nav ms-auto">
          <button @click="showSignIn" class="btn btn-outline-light me-2">Sign In</button>
          <button @click="showRegister" class="btn btn-primary">Get Started</button>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section d-flex align-items-center min-vh-100 position-relative">
      <BackgroundElements />
      
      <div class="container position-relative" style="z-index: 2;">
        <div class="row align-items-center">
          <div class="col-lg-6" :class="{ 'animate-in': loaded }">
            <h1 class="display-2 fw-bold mb-4">
              Test Your Knowledge with
              <span class="gradient-text">QuizDeck</span>
            </h1>
            <p class="lead mb-4 text-light-emphasis">
              Challenge yourself with thousands of curated quizzes across multiple categories. 
              Track your progress and become the ultimate quiz champion.
            </p>
            <div class="d-flex gap-3 flex-wrap">
              <button @click="showRegister" class="btn btn-lg btn-primary px-4">
                Start Quizzing
                <i class="ms-2">→</i>
              </button>
              <button @click="showSignIn" class="btn btn-lg btn-outline-light px-4">
                Sign In
              </button>
            </div>
          </div>
          
          <div class="col-lg-6 mt-5 mt-lg-0" :class="{ 'animate-in': loaded }">
            <div class="quiz-cards">
              <div class="card quiz-card mb-3" v-for="(quiz, index) in featuredQuizzes" :key="index"
                   :style="{ animationDelay: `${index * 0.2}s` }"
                   :class="{ 'slide-in': loaded }">
                <div class="card-body">
                  <div class="d-flex align-items-center">
                    <span class="quiz-icon me-3">{{ quiz.icon }}</span>
                    <div>
                      <h5 class="card-title mb-0">{{ quiz.title }}</h5>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-5 features-section">
      <div class="container">
        <div class="row">
          <div class="col-lg-8 mx-auto text-center mb-5">
            <h2 class="display-5 fw-bold mb-3">Why Choose QuizDeck?</h2>
            <p class="lead text-muted">Everything you need to test and improve your knowledge</p>
          </div>
        </div>
        <div class="row g-4">
          <div class="col-md-6 col-lg-3" v-for="(feature, index) in features" :key="index">
            <div class="card feature-card h-100 border-0"
                 @mouseenter="feature.hovered = true" 
                 @mouseleave="feature.hovered = false"
                 :class="{ 'hovered': feature.hovered }">
              <div class="card-body text-center p-4">
                <div class="feature-icon mb-3">{{ feature.icon }}</div>
                <h5 class="card-title">{{ feature.title }}</h5>
                <p class="card-text text-muted">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="py-5 stats-section">
      <div class="container">
        <div class="row text-center">
          <div class="col-6 col-md-3" v-for="(stat, index) in stats" :key="index">
            <div class="stat-item">
              <div class="stat-number display-4 fw-bold" :class="{ 'count-up': statsVisible }">
                {{ stat.number }}
              </div>
              <p class="stat-label text-muted">{{ stat.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-5 cta-section">
      <div class="container">
        <div class="row">
          <div class="col-lg-8 mx-auto text-center">
            <h2 class="display-5 fw-bold mb-3">Ready to Challenge Yourself?</h2>
            <p class="lead mb-4 text-light-emphasis">Join thousands of quiz enthusiasts today</p>
            <div class="d-flex gap-3 justify-content-center flex-wrap">
              <button @click="showRegister" class="btn btn-lg btn-primary px-5">
                Create Free Account
              </button>
              <button @click="showSignIn" class="btn btn-lg btn-outline-light px-5">
                Sign In
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <FooterComponent />
  </div>
</template>

<script>
import FooterComponent from '@/components/FooterComponent.vue';
import BackgroundElements from '@/components/BackgroundElements.vue';

export default {
  name: 'QuizDeckLandingPage',
  components: {
    FooterComponent, BackgroundElements
  },
  data() {
    return {
      loaded: false,
      statsVisible: false,
      mouseX: 0,
      mouseY: 0,
      featuredQuizzes: [
        { icon: '🧠', title: 'Science & Nature' },
        { icon: '🎭', title: 'Arts & Culture' },
        { icon: '⚽', title: 'Sports' }
      ],
      features: [
        {
          icon: '🎯',
          title: 'Personalized Learning',
          description: 'AI-powered quiz recommendations based on your performance',
          hovered: false
        },
        {
          icon: '🏆',
          title: 'Leaderboards',
          description: 'Compete with friends and climb the global rankings',
          hovered: false
        },
        {
          icon: '📊',
          title: 'Progress Tracking',
          description: 'Monitor your improvement with detailed analytics',
          hovered: false
        },
        {
          icon: '🎨',
          title: 'Multiple Categories',
          description: 'Explore quizzes across science, history, arts, and more',
          hovered: false
        }
      ],
      stats: [
        { number: '10K+', label: 'Active Users' },
        { number: '500+', label: 'Quiz Categories' },
        { number: '1M+', label: 'Questions Answered' },
        { number: '98%', label: 'User Satisfaction' }
      ]
    }
  },
  mounted() {
    setTimeout(() => {
      this.loaded = true;
    }, 100);

    document.addEventListener('mousemove', this.handleMouseMove);

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.statsVisible = true;
        }
      });
    });

    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
      observer.observe(statsSection);
    }
  },
  beforeUnmount() {
    document.removeEventListener('mousemove', this.handleMouseMove);
  },
  methods: {
    handleMouseMove(e) {
      this.mouseX = e.clientX - window.innerWidth / 2;
      this.mouseY = e.clientY - window.innerHeight / 2;
    },
    showSignIn() {
      this.$router.push('/login');
    },
    showRegister() {
      this.$router.push('/register');
    }
  }
}
</script>

<style scoped>

.landing-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Navigation */
.custom-navbar {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.navbar-brand {
  background: linear-gradient(45deg, #fff, #e0e7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.btn-outline-light:hover {
  transform: translateY(-2px);
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  border: none;
  box-shadow: 0 4px 15px rgba(238, 90, 36, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(238, 90, 36, 0.4);
  background: linear-gradient(45deg, #ff5252, #e53935);
}

/* Hero Section */
.hero-section {
  position: relative;
  overflow: hidden;
}

.gradient-text {
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.animate-in {
  animation: slideInUp 0.8s ease forwards;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Quiz Cards */
.quiz-cards {
  max-width: 400px;
  margin-left: auto;
}

.quiz-card {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white;
  transition: all 0.3s ease;
  opacity: 0;
}

.quiz-card.slide-in {
  animation: slideInRight 0.8s ease forwards;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.quiz-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15) !important;
}

.quiz-icon {
  font-size: 2rem;
}

/* Features Section */
.features-section {
  background: rgba(255, 255, 255, 0.05);
}

.feature-card {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(20px);
  color: white;
  transition: all 0.3s ease;
  cursor: pointer;
}

.feature-card.hovered {
  transform: translateY(-10px);
  background: rgba(255, 255, 255, 0.15) !important;
}

.feature-icon {
  font-size: 3rem;
}

/* Stats Section */
.stats-section {
  background: rgba(0, 0, 0, 0.1);
}

.stat-number {
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease;
}

.stat-number.count-up {
  opacity: 1;
  transform: translateY(0);
}

/* CTA Section */
.cta-section {
  background: rgba(255, 255, 255, 0.05);
}

/* Footer */
footer {
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
}


/* Bootstrap button enhancements */
.btn {
  transition: all 0.3s ease;
  border-radius: 50px;
  font-weight: 600;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn-lg {
  padding: 0.75rem 2rem;
}
</style>