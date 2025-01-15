    // stores/jobsStore.js
    import { defineStore } from 'pinia';
    import { useDataStore } from './dataStore';

    export const useJobsStore = defineStore('jobs', {
    state: () => ({
        jobs: [],
    }),
    actions: {
        async fetchJobs() {
        if (this.jobs.length > 0) return; // Avoid re-fetching if already loaded

        const dataStore = useDataStore();
        const response = await dataStore.getData('/jobs');

        if (response.success) {
            this.jobs = response.data;
            this.jobs = response.data;
            localStorage.setItem('jobs', JSON.stringify(response.data));
        } else {
            console.error('Error fetching jobs:', response.data.message);
        }
        },
    },
    getters: {
        getAllJobs(state) {
        return state.jobs;
        },
        getJobById: (state) => (id) => {
        return state.jobs.find((job) => job.id === id);
        },
    },
    });
