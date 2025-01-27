import { defineStore } from 'pinia';
import { useDataStore } from './dataStore';

export const useJobAnalyticsStore = defineStore('jobAnalytics', {
  state: () => ({
    analytics: [], // Holds job analytics data
  }),
  actions: {
    async fetchJobAnalytics() {
      if (this.analytics.length > 0) return; // Avoid fetching if already fetched

      const dataStore = useDataStore();
      const response = await dataStore.getData('/job-analytics'); // API endpoint for analytics

      if (response.success) {
        this.analytics = response.data;
      } else {
        console.error('Error fetching job analytics:', response.data.message);
      }
    },
  },
  getters: {
    getAllAnalytics(state) {
      return state.analytics;
    },
    getAnalyticsBySkillMatch: (state) => (skillMatchLevel) => {
      return state.analytics.filter((entry) => entry.skill_match_level === skillMatchLevel);
    },
    getAnalyticsByLocation: (state) => (location) => {
      return state.analytics.filter((entry) => entry.location === location);
    },
    getAnalyticsSummary(state) {
      const summary = {};

      state.analytics.forEach((entry) => {
        if (!summary[entry.skill_match_level]) {
          summary[entry.skill_match_level] = 0;
        }
        summary[entry.skill_match_level] += entry.count;
      });

      return summary;
    },
  },
});
