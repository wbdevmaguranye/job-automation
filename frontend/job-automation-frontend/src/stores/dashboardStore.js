import { defineStore } from "pinia";
import { useDataStore } from "./dataStore";

export const useDashboardStore = defineStore("dashboard", {
  state: () => ({
    summary: {
      total_jobs: 0,
      total_cvs: 0,
      recent_jobs: [],
    },
  }),

  actions: {
    async fetchDashboardSummary() {
      const token = localStorage.getItem("token");
      if (!token) {
        console.error("No token found. User might not be logged in.");
        return;
      }

      const response = await useDataStore().getData("/dashboard/summary");
      if (response.success) {
        this.summary = response.data;
        console.log("Dashboard summary fetched:", this.summary);
      } else {
        console.error(
          "Error fetching dashboard summary:",
          response?.data?.message || "Unknown error"
        );
      }
    },
  },

  getters: {
  
    totalJobs: (state) => state.summary.total_jobs || 0,

    
    totalCVs: (state) => state.summary.total_cvs || 0,

   
    recentJobs: (state) => state.summary.recent_jobs || [],
  },
});
