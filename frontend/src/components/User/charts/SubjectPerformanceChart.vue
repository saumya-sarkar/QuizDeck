<template>
  <Bar :data="chartData" :options="chartOptions" />
</template>

<script>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale
} from 'chart.js'

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  name: 'SubjectPerformanceChart',
  components: {
    Bar
  },
  props: {
    subjectPerformance: Array
  },
  computed: {
    chartData() {
      const labels = this.subjectPerformance.map(item => item.subject_name)
      const attempts = this.subjectPerformance.map(item => item.attempts)
      const avgPercentages = this.subjectPerformance.map(item => item.avg_percentage)

      return {
        labels,
        datasets: [
          {
            label: 'Quiz Attempts',
            data: attempts,
            backgroundColor: 'rgba(255, 99, 132, 0.6)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1,
            yAxisID: 'y'
          },
          {
            label: 'Average Score Percentage',
            data: avgPercentages,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            yAxisID: 'y1'
          }
        ]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Subject-wise Attempts and Average Percentage',
            color: '#ffffff',
            font: {
              size: 16,
              weight: 'bold'
            }
          },
          legend: {
            labels: {
              color: '#ffffff'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#ffffff'
            },
            grid: {
              display: false,
              color: 'rgba(255,255,255,0.1)'
            }
          },
          y: {
            type: 'linear',
            position: 'left',
            beginAtZero: true,
            title: {
              display: false, // Hide title for attempts axis
              text: 'Attempts',
              color: '#ffffff'
            },
            ticks: {
              color: '#ffffff'
            },
            grid: {
              display: false,
              color: 'rgba(255,255,255,0.1)'
            }
          },
          y1: {
            type: 'linear',
            position: 'right',
            beginAtZero: true,
            max: 100,
            title: {
              display: false, // Hide title for average percentage axis,
              text: 'Avgerage Percentage',
              color: '#ffffff'
            },
            ticks: {
              color: '#ffffff',
              callback: value => value + '%'
            },
            grid: {
              drawOnChartArea: false // prevent grid overlap
            }
          }
        }
      }
    }
  }
}
</script>
