<template>
  <div class="hello p-6 bg-white rounded-lg shadow-md mb-8">
    <h1 class="text-4xl font-extrabold text-gray-900 mb-4">{{ msg }}</h1>
    <p class="text-lg text-gray-700 leading-relaxed">
      This is a basic Flask-Vue.js setup.
      <br>
      The frontend (Vue.js) is running on <code class="bg-gray-200 p-1 rounded">http://localhost:6060</code>.
      <br>
      The backend (Flask) is running on <code class="bg-gray-200 p-1 rounded">http://127.0.0.1:5050</code>.
    </p>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: String
  }
}
</script>

<style scoped>
/* Scoped CSS for HelloWorld component */
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>