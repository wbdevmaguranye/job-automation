import { defineStore } from 'pinia';
import { useDataStore } from './dataStore';

export const useSkillGapStore = defineStore('skillGap', {
  state: () => ({
    skillGapResult: null,
  }),
  actions: {
    async analyzeSkillGap(cv_id, job_id) {
      const dataStore = useDataStore();
      const response = await dataStore.postData('/skill-gap', { cv_id, job_id });

      if (response.success) {
        this.skillGapResult = response.data;
      } else {
        console.error('Error analyzing skill gap:', response.data.message);
      }
    },
  },
  getters: {
    getSkillGapResult(state) {
      return state.skillGapResult;
    },
  },
});
