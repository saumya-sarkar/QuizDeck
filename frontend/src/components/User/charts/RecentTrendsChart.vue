<template>
  <Bar :data="chartData" :options="chartOptions" />
</template>

<script>
import { Bar } from 'vue-chartjs';

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
            text: 'Recent Quiz Performance',
            font: { size: 16, weight: 'bold' },
            color: '#ffffff'
          },
          legend: { display: false },
          tooltip: {
            callbacks: {
              afterLabel: (context) => {
                const item = this.recentTrends[context.dataIndex];
                return `Date: ${item.date}`;
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
            grid: { color: 'rgba(255,255,255,0.1)' }
          },
          x: {
            ticks: {
              color: '#ffffff',
              maxRotation: 45,
              minRotation: 45
            },
            grid: { color: 'rgba(255,255,255,0.1)' }
          }
        }
      }
    };
  },
  mounted() {
    this.chartData.labels = this.recentTrends.map(item =>
      item.quiz.length > 15 ? item.quiz.slice(0, 15) + '...' : item.quiz
    );

    this.chartData.datasets = [{
      label: 'Score (%)',
      data: this.recentTrends.map(item => item.score),
      backgroundColor: this.recentTrends.map(item => {
        if (item.score >= 80) return 'rgba(76, 175, 80, 0.8)';
        if (item.score >= 60) return 'rgba(255, 193, 7, 0.8)';
        return 'rgba(244, 67, 54, 0.8)';
      }),
      borderColor: this.recentTrends.map(item => {
        if (item.score >= 80) return 'rgba(76, 175, 80, 1)';
        if (item.score >= 60) return 'rgba(255, 193, 7, 1)';
        return 'rgba(244, 67, 54, 1)';
      }),
      borderWidth: 2
    }];
  }
};
</script>
