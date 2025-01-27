<template>
    <b-container>
      <h1 class="text-success">Job Analytics</h1>
      <b-row>
        <b-col>
          <h5>Skill Match Levels</h5>
          <canvas id="skillMatchChart"></canvas>
        </b-col>
        <b-col>
          <h5>Jobs by Location</h5>
          <canvas id="jobsByLocationChart"></canvas>
        </b-col>
      </b-row>
    </b-container>
  </template>
  
  <script setup>
  import { onMounted, computed } from "vue";
  import Chart from "chart.js/auto";
  import { useJobAnalyticsStore } from "@/stores/jobAnalyticsStore";
  
  // Initialize the job analytics store
  const jobAnalyticsStore = useJobAnalyticsStore();
  
  // Computed properties for analytics data
  const skillMatchData = computed(() => {
    const summary = jobAnalyticsStore.getAnalyticsSummary;
    return {
      labels: Object.keys(summary),
      counts: Object.values(summary),
    };
  });
  
  const locationData = computed(() => {
    const analytics = jobAnalyticsStore.getAllAnalytics;
    const locations = {};
    analytics.forEach((entry) => {
      if (!locations[entry.location]) {
        locations[entry.location] = 0;
      }
      locations[entry.location] += entry.count;
    });
    return {
      labels: Object.keys(locations),
      counts: Object.values(locations),
    };
  });
  
  // Chart rendering functions
  const renderSkillMatchChart = (data) => {
    const ctx = document.getElementById("skillMatchChart").getContext("2d");
    new Chart(ctx, {
      type: "pie",
      data: {
        labels: data.labels,
        datasets: [
          {
            data: data.counts,
            backgroundColor: ["#28a745", "#ffc107", "#dc3545", "#6c757d"],
          },
        ],
      },
    });
  };
  
  const renderLocationChart = (data) => {
    const ctx = document.getElementById("jobsByLocationChart").getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [
          {
            label: "Jobs by Location",
            data: data.counts,
            backgroundColor: "#007bff",
          },
        ],
      },
    });
  };
  
  // Fetch data and render charts on mount
  onMounted(async () => {
    try {
      await jobAnalyticsStore.fetchJobAnalytics(); // Fetch data from the store
      renderSkillMatchChart(skillMatchData.value);
      renderLocationChart(locationData.value);
    } catch (error) {
      console.error("Error rendering analytics:", error);
    }
  });
  </script>
  
  <style scoped>
  h1 {
    font-weight: bold;
    margin-bottom: 20px;
  }
  </style>
  