<template>
  <Bar :data="chartData" :options="chartOptions" />
</template>

<script>
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

export default {
  name: 'DifficultyScoresChart',
  components: {
    Bar
  },
  props: {
    scores: Array
  },
  computed: {
    chartData() {
      const colors = {
        'Easy': 'rgba(75, 192, 192, 0.8)',
        'Medium': 'rgba(255, 205, 86, 0.8)',
        'Hard': 'rgba(255, 99, 132, 0.8)'
      };
      return {
        labels: this.scores.map(item => item.difficulty),
        datasets: [{
          label: 'Average Score Percentage',
          data: this.scores.map(item => item.avg_score),
          backgroundColor: this.scores.map(item => colors[item.difficulty] || 'rgba(153, 102, 255, 0.8)'),
          borderColor: this.scores.map(item => (colors[item.difficulty] || '').replace('0.8', '1') || 'rgba(153, 102, 255, 1)'),
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
            text: 'Average Score Percentage by Quiz Difficulty',
            color: '#fff',
            font: {
              size: 16,
              weight: 'bold'
            }
          },
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              color: '#ffffff',
              callback: value => value + '%'
            },
            grid: {
              display: false,
              // color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          x: {
            ticks: { color: '#ffffff' },
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
