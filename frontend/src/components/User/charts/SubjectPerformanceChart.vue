<template>
  <Radar :data="chartData" :options="chartOptions" />
</template>

<script>
import { Radar } from 'vue-chartjs';

export default {
  name: 'SubjectPerformanceChart',
  components: { Radar },
  props: {
    subjectPerformance: {
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
            text: 'Performance by Subject (Last 6 Months)',
            color: '#ffffff',
            font: { size: 16, weight: 'bold' }
          },
          legend: { display: false }
        },
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            ticks: {
              color: '#ffffff',
              callback: value => value + '%'
            },
            grid: {
              color: 'rgba(255,255,255,0.2)'
            },
            angleLines: {
              color: 'rgba(255,255,255,0.2)'
            },
            pointLabels: {
              color: '#ffffff'
            }
          }
        }
      }
    };
  },
  mounted() {
    const labels = this.subjectPerformance.map(item => item.subject);
    const scores = this.subjectPerformance.map(item => item.avg_score);
    this.chartData.labels = labels;
    this.chartData.datasets = [{
      label: 'Average Score (%)',
      data: scores,
      borderColor: 'rgba(54, 162, 235, 1)',
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      borderWidth: 3,
      pointBackgroundColor: 'rgba(54, 162, 235, 1)',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 6
    }];
  }
};
</script>
