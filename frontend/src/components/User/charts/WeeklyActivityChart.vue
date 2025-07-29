<template>
  <Line :data="chartData" :options="chartOptions" />
</template>

<script>
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement);

export default {
  name: 'WeeklyActivityChart',
  components: { Line },
  props: {
    weeklyActivity: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      chartData: {
        labels: [],
        datasets: []
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Weekly Quiz Activity (Last 8 Weeks)',
            font: { size: 16, weight: 'bold' },
            color: '#ffffff'
          },
          legend: {
            position: 'top',
            labels: { color: '#ffffff' }
          }
        },
        scales: {
          x: {
            ticks: { color: '#ffffff' },
            grid: { color: 'rgba(255,255,255,0.1)' }
          },
          y: {
            position: 'left',
            beginAtZero: true,
            title: {
              display: true,
              text: 'Quiz Attempts',
              color: '#ffffff'
            },
            ticks: { color: '#ffffff' },
            grid: { color: 'rgba(255,255,255,0.1)' }
          },
          y1: {
            position: 'right',
            beginAtZero: true,
            max: 100,
            title: {
              display: true,
              text: 'Average Score (%)',
              color: '#ffffff'
            },
            ticks: {
              color: '#ffffff',
              callback: val => `${val}%`
            },
            grid: {
              drawOnChartArea: false
            }
          }
        }
      }
    };
  },
  watch: {
    weeklyActivity: {
      immediate: true,
      handler(newVal) {
        if (!newVal || newVal.length === 0) return;

        const weeks = newVal.map(item => `Week ${item.week.split('-Week')[1]}`);
        const attempts = newVal.map(item => item.attempts);
        const avgScores = newVal.map(item => item.avg_score);

        this.chartData = {
          labels: weeks,
          datasets: [
            {
              label: 'Quiz Attempts',
              data: attempts,
              borderColor: 'rgba(75, 192, 192, 1)',
              backgroundColor: 'rgba(75, 192, 192, 0.1)',
              borderWidth: 3,
              fill: true,
              tension: 0.4,
              yAxisID: 'y'
            },
            {
              label: 'Average Score (%)',
              data: avgScores,
              borderColor: 'rgba(255, 99, 132, 1)',
              backgroundColor: 'rgba(255, 99, 132, 0.1)',
              borderWidth: 3,
              fill: false,
              tension: 0.4,
              yAxisID: 'y1'
            }
          ]
        };
      }
    }
  }
};
</script>

