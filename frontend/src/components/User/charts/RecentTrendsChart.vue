<template>
  <div style="position: relative; height: 300px;">
    <Bar v-if="chartReady" :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'

export default {
  name: 'RecentTrendsChart',
  components: { Bar },
  props: {
    recentTrends: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      chartReady: false,
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
            text: 'Last 10 Quiz Performance',
            font: { size: 16, weight: 'bold' },
            color: '#ffffff'
          },
          legend: { display: false },
          tooltip: {
            callbacks: {
              afterLabel: (context) => {
                const item = this.recentTrends[context.dataIndex]
                return `Date: ${item.date}`
              }
            }
          }
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
              color: 'rgba(255,255,255,0.1)' 
            }
          },
          x: {
            ticks: {
              color: '#ffffff',
              maxRotation: 45,
              minRotation: 45
            },
            grid: {
              display: false,
              color: 'rgba(255,255,255,0.1)'
            }
          }
        }
      }
    }
  },
  watch: {
    recentTrends: {
      handler(newVal) {
        if (!newVal || !newVal.length) return

        this.chartData = {
          labels: newVal.map(item =>
            item.quiz.length > 15 ? item.quiz.slice(0, 15) + '...' : item.quiz
          ),
          datasets: [
            {
              label: 'Score (%)',
              data: newVal.map(item => item.score),
              backgroundColor: newVal.map(item => {
                if (item.score >= 80) return 'rgba(76, 175, 80, 0.8)'
                if (item.score >= 60) return 'rgba(255, 193, 7, 0.8)'
                return 'rgba(244, 67, 54, 0.8)'
              }),
              borderColor: newVal.map(item => {
                if (item.score >= 80) return 'rgba(76, 175, 80, 1)'
                if (item.score >= 60) return 'rgba(255, 193, 7, 1)'
                return 'rgba(244, 67, 54, 1)'
              }),
              borderWidth: 2
            }
          ]
        }

        this.chartReady = true
      },
      immediate: true,
      deep: true
    }
  }
}
</script>
