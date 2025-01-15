// stores/cvsStore.js
import { defineStore } from 'pinia';
import { useDataStore } from './dataStore';

export const useCVsStore = defineStore('cvs', {
  state: () => ({
    cvs: [],
  }),
  actions: {
    async fetchCVs() {
      if (this.cvs.length > 0) return;

      const dataStore = useDataStore();
      const response = await dataStore.getData('/cvs');

      if (response.success) {
        this.cvs = response.data;
      } else {
        console.error('Error fetching CVs:', response.data.message);
      }
    },
  },
  getters: {
    getAllCVs(state) {
      return state.cvs;
    },
    getCVById: (state) => (id) => {
      return state.cvs.find((cv) => cv.id === id);
    },
  },
});
