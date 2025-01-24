<template>
    <!-- Skill Match Distribution Chart -->
    <b-card class="mb-4">
      <h4>Skill Match Distribution</h4>
      <canvas id="skillMatchChart"></canvas>
    </b-card>
  </template>
  
  <script setup>
  import { onMounted, watch } from 'vue';
  import { useCVsStore } from '@/stores/cvsStore';
  import Chart from 'chart.js/auto';
  
  // Get CVs store
  const cvsStore = useCVsStore();
  
  const drawChart = () => {
    const ctx = document.getElementById('skillMatchChart').getContext('2d');
  
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['High Match', 'Average Match', 'Low Match', 'No Match'],
        datasets: [
          {
            label: 'Skill Match Distribution',
            data: [
              cvsStore.cvs.filter((cv) => cv.skills_match_category === 'High').length,
              cvsStore.cvs.filter((cv) => cv.skills_match_category === 'Average').length,
              cvsStore.cvs.filter((cv) => cv.skills_match_category === 'Low').length,
              cvsStore.cvs.filter((cv) => cv.skills_match_category === 'No Match').length,
            ],
            backgroundColor: ['#28a745', '#ffc107', '#dc3545', '#6c757d'],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
        },
      },
    });
  };
  
  // Fetch CVs on component mount and draw chart when data is updated
  onMounted(async () => {
    await cvsStore.fetchCVs();
    drawChart();
  });
  
  watch(() => cvsStore.cvs, () => {
    drawChart(); // Redraw the chart if data updates
  });
  </script>
  