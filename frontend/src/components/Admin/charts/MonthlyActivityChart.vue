<template>
  <Line :data="chartData" :options="chartOptions" />
</template>

<script>
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  LineElement, PointElement,
  CategoryScale, LinearScale
} from 'chart.js';

ChartJS.register(
  Title, Tooltip, Legend,
  LineElement, PointElement,
  CategoryScale, LinearScale
);

export default {
  name: 'MonthlyActivityChart',
  components: {
    Line
  },
  props: {
    activity: Array
  },
  computed: {
    chartData() {
      return {
        labels: this.activity.map(item => {
          const [year, month, day] = item.month.split('-');
          return new Date(year, month - 1, day).toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
          });
        }),
        datasets: [
          {
            label: 'Total Attempts',
            data: this.activity.map(item => item.total_attempts),
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#fff',
            pointBorderColor: 'rgba(54, 162, 235, 1)',
            pointRadius: 4
          }
        ]
      };
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Daily Quiz Activity',
            color: '#fff',
            font: {
              size: 16,
              weight: 'bold'
            }
          },
          legend: {
            display: true,
            labels: {
              color: '#ffffff'
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              color: '#ffffff'
            },
            grid: {
              display: false,
              color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          x: {
            ticks: {
              color: '#ffffff'
            },
            grid: {
              display: false,
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        }
      };
    }
  }
};
</script>

