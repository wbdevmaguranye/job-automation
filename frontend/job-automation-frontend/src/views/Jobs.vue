<template>
    <b-container>
      <h1>Jobs</h1>
      <!-- <b-table :items="jobs" :fields="fields" striped hover></b-table> -->
    </b-container>
  </template>
  
  <script>
//   import { useApiStore } from '../stores/apiStore';
  
  export default {
    setup() {
      const apiStore = useApiStore();
      apiStore.fetchJobs();
  
      return {
        jobs: apiStore.jobs,
        fields: ['id', 'title', 'company', 'location', 'date_posted'],
      };
    },
  };
  </script>
  