// stores/applicationsStore.js
import { defineStore } from "pinia";
import { useDataStore } from "./dataStore";

export const useApplicationsStore = defineStore("applications", {
  state: () => ({
    applications: [],
  }),
  actions: {
    async applyForJob(jobId, cvId) {
        const dataStore = useDataStore();
        const response = await dataStore.postData("/applications", {
          job_id: jobId,
          cv_id: cvId,
        });
  
        if (response.success) {
          this.applications.push(response.data); // Update local applications state
        } else {
          console.error("Error applying for job:", response.data.message);
        }
  
        return response;
      },
  
      isJobApplied(jobId) {
        return this.applications.some((app) => app.job_id === jobId);
      },
    async fetchApplications() {
        if (this.applications.length > 0) return;

        const dataStore = useDataStore();
        const response = await dataStore.getData('/applications');

        if (response.success) {
            this.applications = response.data;
        } else {
            console.error('Error fetching applications:', response.data.message);
        }
    },
    async deleteApplication(applicationId) {
      console.log(applicationId)
      if (!applicationId) {
        throw new Error("Invalid application ID.");
      }
      try {
        await useDataStore().deleteData(`/applications/${applicationId}`);
      } catch (error) {
        console.error("Error deleting application:", error);
        throw error;
      }
    },
    removeApplication(applicationId) {
      if (!applicationId) return;
      this.applications = this.applications.filter(
        (application) => application.application_id !== applicationId
      );
    }
    
    
  },
  getters: {
    getAllApplications(state) {
      return state.applications;
    },
    getApplicationById: (state) => (id) => {
        return state.applications.find((app) => app.id === id);
    },
  },
});
