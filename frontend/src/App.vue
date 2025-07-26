<template>
  
  <router-view></router-view>
</template>

<script>
export default {
  mounted() {
    this.$store.dispatch("auth/userDetails")
      .then(() => {
        // Set the document title based on the current route
        const title = this.$route.meta.title || 'QuizDeck';
        document.title = title;
      })
      .catch(error => {
        console.error("Error fetching user details:", error);
      });
  }
};
</script>


<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;700&display=swap');

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: 'Poppins', sans-serif;
}
</style>