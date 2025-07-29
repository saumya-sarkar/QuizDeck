<template>
  <Doughnut :data="chartData" :options="chartOptions" />
</template>

<script>
import { Doughnut } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title, Tooltip, Legend, ArcElement
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, ArcElement);

export default {
  name: 'SubjectAttemptsChart',
  components: {
    Doughnut
  },
  props: {
    subjectAttempts: Array
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
        labels: this.subjectAttempts.map(item => item.subject),
        datasets: [{
          data: this.subjectAttempts.map(item => item.attempts),
          backgroundColor: colors.slice(0, this.subjectAttempts.length),
          borderColor: '#fff',
          borderWidth: 2
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
            text: 'Total Quiz Attempts by Subject',
            color: '#fff',
            font: {
              size: 16,
              weight: 'bold'
            }
          },
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              color: '#ffffff'
            }
          }
        }
      };
    }
  }
};
</script>
