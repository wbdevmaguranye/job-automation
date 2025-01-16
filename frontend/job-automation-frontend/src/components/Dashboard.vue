<template>
  <div v-if="isLoading">Loading...</div>
  <div v-else>
    <b-container>
      <h1 class="dashboard-title">Dashboard</h1>

      <!-- Key Metrics Section -->
      <b-row class="mb-4">
        <b-col lg="4">
          <b-card class="text-center stats-card bg-success text-white">
            <h4>Total Jobs</h4>
            <h2>{{ dashboardStore.totalJobs }}</h2>
          </b-card>
        </b-col>
        <b-col lg="4">
          <b-card class="text-center stats-card bg-primary text-white">
            <h4>Total CVs</h4>
            <h2>{{ dashboardStore.totalCVs }}</h2>
          </b-card>
        </b-col>
        <b-col lg="4">
          <b-card class="text-center stats-card bg-warning text-white">
            <h4>Applications Submitted</h4>
            <h2>{{ totalApplications }}</h2>
          </b-card>
        </b-col>
      </b-row>

      <!-- Recent Jobs Section -->
      <h3>Recent Jobs</h3>
      <b-table
        striped
        hover
        :items="dashboardStore.recentJobs"
        :fields="recentJobsFields"
        responsive="sm"
        class="mb-4"
      ></b-table>

      <!-- Quick Actions Section -->
      <h3>Quick Actions</h3>
      <b-row>
        <b-col lg="4">
          <b-card class="text-center quick-action-card" @click="navigateTo('/jobs')">
            <b-icon icon="briefcase" class="action-icon"></b-icon>
            <h5>Browse Jobs</h5>
          </b-card>
        </b-col>
        <b-col lg="4">
          <b-card class="text-center quick-action-card" @click="navigateTo('/cvs')">
            <b-icon icon="file-earmark-text" class="action-icon"></b-icon>
            <h5>View CVs</h5>
          </b-card>
        </b-col>
        <b-col lg="4">
          <b-card class="text-center quick-action-card" @click="navigateTo('/applications')">
            <b-icon icon="check-circle" class="action-icon"></b-icon>
            <h5>View Applications</h5>
          </b-card>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useDashboardStore } from "@/stores/dashboardStore";
import { useRouter } from "vue-router";


const dashboardStore = useDashboardStore();
const router = useRouter();


const isLoading = ref(true);


const totalApplications = 15; // Example static value
const recentJobsFields = [
  { key: "title", label: "Job Title", sortable: true },
  { key: "company", label: "Company", sortable: true },
];

// Fetch Dashboard Data
const fetchSummary = async () => {
  isLoading.value = true;
  try {
    await dashboardStore.fetchDashboardSummary();
  } catch (error) {
    console.error("Error fetching dashboard summary:", error);
  } finally {
    isLoading.value = false;
  }
};

// Navigate to Other Pages
const navigateTo = (path) => {
  router.push(path);
};

// Fetch data on component mount
onMounted(() => {
  fetchSummary();
});
</script>

<style scoped>
.dashboard-title {
  font-weight: bold;
  color: #198754;
  margin-bottom: 20px;
}

.stats-card {
  padding: 20px;
  border-radius: 8px;
}

.quick-action-card {
  cursor: pointer;
  border: 1px solid #ddd;
  padding: 20px;
  border-radius: 8px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.quick-action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.action-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: #198754;
}
</style>
