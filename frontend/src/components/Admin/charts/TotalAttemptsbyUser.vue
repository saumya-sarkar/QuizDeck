<!-- components/Admin/charts/TotalAttemptsbyUser.vue -->
<template>
  <Bar :data="chartData" :options="chartOptions" />
</template>

<script>
import { Bar } from 'vue-chartjs';


export default {
  name: 'TotalAttemptsbyUser',
  components: {
    Bar
  },
  props: {
    userAttempts: Array
  },
  computed: {
    chartData() {
      const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 205, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
      ];
      return {
        labels: this.userAttempts.map(item => item.username),
        datasets: [{
          label: 'Total Quiz Attempts by User',
          data: this.userAttempts.map(item => item.attempts),
          borderColor: colors.slice(0, this.userAttempts.length),
          backgroundColor: colors.slice(0, this.userAttempts.length),
          borderWidth: 3,
          fill: true,
          tension: 0.4
        }]
      };
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Total Quiz Attempts by User',
            color: '#fff',
            font: {
              size: 16,
              weight: 'bold'
            }
          },
          legend: { 
            display: false, 
            // position: 'top', 
            // labels: { color: '#fff' } 
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              color: '#ffffff',
              stepSize: 5
            },
            grid: {
              display: false,
              // color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          x: {
            ticks: {
              color: '#ffffff'
            },
            grid: {
              display: false,
              // color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        }
      };
    }
  }
};
</script>
