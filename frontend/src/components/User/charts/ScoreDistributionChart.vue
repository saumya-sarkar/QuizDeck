<template>
  <Pie :data="chartData" :options="chartOptions" />
</template>

<script>
import { Pie } from 'vue-chartjs';

export default {
  name: 'ScoreDistributionChart',
  components: { Pie },
  props: {
    scoreDistribution: {
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
            text: 'Score Distribution',
            color: '#ffffff',
            font: { size: 16, weight: 'bold' }
          },
          legend: {
            position: 'bottom',
            labels: {
              color: '#ffffff',
              padding: 20
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const value = context.parsed;
                const percent = ((value / total) * 100).toFixed(1);
                return `${context.label}: ${value} (${percent}%)`;
              }
            }
          }
        }
      }
    };
  },
  mounted() {
    const colors = {
      '90-100%': 'rgba(76, 175, 80, 0.8)',
      '80-89%': 'rgba(139, 195, 74, 0.8)',
      '70-79%': 'rgba(255, 193, 7, 0.8)',
      '60-69%': 'rgba(255, 152, 0, 0.8)',
      '50-59%': 'rgba(255, 87, 34, 0.8)',
      'Below 50%': 'rgba(244, 67, 54, 0.8)'
    };

    const borderColors = '#fff';

    this.chartData.labels = this.scoreDistribution.map(item => item.range);
    this.chartData.datasets = [{
      data: this.scoreDistribution.map(item => item.count),
      backgroundColor: this.scoreDistribution.map(item => colors[item.range] || 'rgba(158, 158, 158, 0.8)'),
      borderColor: borderColors,
      borderWidth: 2
    }];
  }
};
</script>
