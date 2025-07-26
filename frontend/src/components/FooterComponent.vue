<template>
  <footer class="footer-component py-4 border-top">
    <div class="container">
      <div class="row gy-3">
        <!-- Brand Section -->
        <div class="col-md-6">
          <h5 class="fw-bold mb-2 brand-title">QuizDeck</h5>
          <p class="text-muted mb-3">
            Challenge your mind, expand your knowledge, and compete with quiz enthusiasts worldwide.
          </p>
          <div class="social-links">
            <a href="#" class="social-link me-2" aria-label="Facebook">
              <font-awesome-icon :icon="['fab', 'facebook-f']" />
            </a>
            <a href="#" class="social-link me-2" aria-label="Twitter">
              <font-awesome-icon :icon="['fab', 'twitter']" />
            </a>
            <a href="#" class="social-link me-2" aria-label="Instagram">
              <font-awesome-icon :icon="['fab', 'instagram']" />
            </a>
            <a href="#" class="social-link" aria-label="LinkedIn">
              <font-awesome-icon :icon="['fab', 'linkedin-in']" />
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="col-md-6">
          <h6 class="fw-semibold mb-3">Quick Links</h6>
          <div class="row">
            <div class="col-6">
              <ul class="list-unstyled">
                <li class="mb-2">
                  <a href="#" class="footer-link">About Us</a>
                </li>
                <li class="mb-2">
                  <a href="#" class="footer-link">Help Center</a>
                </li>
                <li class="mb-2">
                  <a href="#" class="footer-link">Contact</a>
                </li>
              </ul>
            </div>
            <div class="col-6">
              <ul class="list-unstyled">
                <li class="mb-2">
                  <a href="#" class="footer-link">Privacy Policy</a>
                </li>
                <li class="mb-2">
                  <a href="#" class="footer-link">Terms of Service</a>
                </li>
                <li class="mb-2">
                  <a href="#" class="footer-link">FAQ</a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Section -->
      <hr class="my-3 border-secondary">
      <div class="row align-items-center">
        <div class="col-md-6">
          <p class="text-muted mb-0 small">
            &copy; 2025 QuizDeck. All rights reserved.
          </p>
        </div>
        <div class="col-md-6 text-md-end mt-2 mt-md-0">
          <p class="mb-0 small">
            Made with ❤️ by Saumya Sarkar
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'FooterComponent',
}
</script>

<style scoped>
.footer-component {
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: white;
}

.brand-title {
  background: linear-gradient(45deg, #fff, #e0e7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.footer-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.footer-link:hover {
  color: #ff6b6b;
  text-decoration: none;
  transform: translateX(3px);
}

.social-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 35px;
  height: 35px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 50%;
  text-decoration: none;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.social-link:hover {
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(238, 90, 36, 0.3);
}

.border-secondary {
  border-color: rgba(255, 255, 255, 0.2) !important;
}

@media (max-width: 768px) {
  .text-md-end {
    text-align: left !important;
  }
}
</style>