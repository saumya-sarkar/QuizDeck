<template>
  <Line :data="chartData" :options="chartOptions" />
</template>

<script>
import { Line } from 'vue-chartjs';

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
          y: {
            title: { display: true, text: 'Quiz Attempts', color: '#ffffff' },
            ticks: { color: '#ffffff' },
            grid: { color: 'rgba(255,255,255,0.1)' }
          },
          y1: {
            position: 'right',
            min: 0,
            max: 100,
            title: { display: true, text: 'Average Score (%)', color: '#ffffff' },
            grid: { drawOnChartArea: false },
            ticks: { color: '#ffffff' }
          },
          x: {
            ticks: { color: '#ffffff' },
            grid: { color: 'rgba(255,255,255,0.1)' }
          }
        }
      }
    };
  },
  mounted() {
    const weeks = this.weeklyActivity.map(item => `Week ${item.week.split('-W')[1]}`);
    const attempts = this.weeklyActivity.map(item => item.attempts);
    const avgScores = this.weeklyActivity.map(item => item.avg_score);

    this.chartData.labels = weeks;
    this.chartData.datasets = [
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
    ];
  }
};
</script>
