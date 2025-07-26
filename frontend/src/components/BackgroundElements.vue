<template>
    <!-- Background Elements -->
    <div class="background-elements">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
    </div>
</template>

<script>
export default {
  name: 'BackgroundElements'
}
</script>

<style scoped>
    /* Background Elements */
    .background-elements {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        overflow: hidden;
        z-index: 1;
    }

    .floating-shape {
        position: absolute;
        border-radius: 50%;
        opacity: 0.1;
        animation: float 6s ease-in-out infinite;
    }

    .shape-1 {
        width: 200px;
        height: 200px;
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        top: 10%;
        left: 10%;
    }

    .shape-2 {
        width: 150px;
        height: 150px;
        background: linear-gradient(45deg, #4ecdc4, #44a08d);
        top: 60%;
        right: 15%;
        animation-delay: 2s;
    }

    .shape-3 {
        width: 100px;
        height: 100px;
        background: linear-gradient(45deg, #f093fb, #f5576c);
        bottom: 20%;
        left: 60%;
        animation-delay: 4s;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }

</style>