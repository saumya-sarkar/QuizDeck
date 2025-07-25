<template>
  <div id="app" class="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
    <img alt="Vue logo" src="./assets/logo.png" class="w-24 h-24 mb-6 animate-bounce-slow">
    <HelloWorld msg="Welcome to Your Flask-Vue.js App"/>
    <div class="mt-8 p-6 bg-white rounded-lg shadow-md text-center">
      <h2 class="text-2xl font-semibold text-gray-800 mb-4">Backend Message:</h2>
      <p v-if="backendMessage" class="text-xl text-blue-600 font-medium">{{ backendMessage }}</p>
      <p v-else class="text-lg text-gray-500">Click on the button to fetch a message from the backend.</p>
      <button
        @click="fetchBackendMessage"
        class="mt-6 px-6 py-3 bg-indigo-600 text-white font-bold rounded-full shadow-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-300 ease-in-out transform hover:scale-105"
      >
        Fetch Message
      </button>
    </div>
  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'

export default {
  name: 'App',
  components: {
    HelloWorld
  },
  data() {
    return {
      backendMessage: ''
    };
  },
  methods: {
    async fetchBackendMessage() {
      try {
        // Ensure this URL matches your Flask backend's address and port
        const response = await fetch('http://127.0.0.1:5050/api/message');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        this.backendMessage = data.message;
      } catch (error) {
        console.error("Error fetching message from backend:", error);
        this.backendMessage = "Failed to load message from backend.";
      }
    }
  },
  // mounted() {
  //   // Fetch message when the component mounts
  //   this.fetchBackendMessage();
  // }
}
</script>

<style>
/* You can add global styles here or use Tailwind CSS */
#app {
  font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}


/* Custom animation for the logo */
@keyframes bounce-slow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
.animate-bounce-slow {
  animation: bounce-slow 3s infinite ease-in-out;
}
</style>