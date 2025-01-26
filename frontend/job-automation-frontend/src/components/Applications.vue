<template>
    <b-container>
      <h1 class="page-title">My Applications</h1>
  
          <b-row class="mb-4">
               <b-col lg="4">
          <b-form-group label="Start Date">
            <b-form-input
              type="date"
              v-model="filters.startDate"
              placeholder="Start Date"
              class="custom-search-input"
            />
          </b-form-group>
        </b-col>
        <b-col lg="4">
          <b-form-group label="End Date">
            <b-form-input
              type="date"
              v-model="filters.endDate"
              placeholder="End Date"
              class="custom-search-input"
            />
          </b-form-group>
        </b-col>
  
               <b-col lg="4">
          <b-form-group label="Status">
            <b-form-select
              v-model="filters.status"
              :options="statusOptions"
              placeholder="Select Status"
              class="custom-search-input"
            />
          </b-form-group>
        </b-col>
      </b-row>
  
      <b-table
        striped
        hover
        :items="paginatedApplications"
        :fields="fields"
        responsive="sm"
      >
      
        <template #cell(cv_file_url)="row">
          <a
            v-if="row.item.cv_file_url"
            :href="row.item.cv_file_url"
            target="_blank"
            class="btn btn-link "
          >
            Download CV
          </a>
          <span v-else>N/A</span>
        </template>
  
        <!-- Actions -->
        <template #cell(actions)="row">
          <b-button
            class="small-button"
            variant="danger"
            @click="deleteApplication(row.item.application_id)"
          >
            Delete
          </b-button>
        </template>
      </b-table>
  
 
      <b-pagination
        v-model="currentPage"
        :total-rows="filteredApplications.length"
        :per-page="perPage"
        aria-controls="applications-table"
        class="mt-3"
      ></b-pagination>
    </b-container>
  </template>
  
  
  <script setup>
import { onMounted, computed, ref } from "vue";
import { useToast } from "vue-toastification";
import { useApplicationsStore } from "@/stores/applicationsStore";

const applicationsStore = useApplicationsStore();
const toast = useToast();

// Pagination state
const currentPage = ref(1);
const perPage = ref(10); 

// Filters
const filters = ref({
  startDate: null,
  endDate: null,
  status: null,
});

const statusOptions = [
  { value: null, text: "All" },
  { value: "Pending", text: "Pending" },
  { value: "Approved", text: "Approved" },
  { value: "Rejected", text: "Rejected" },
];

// Computed property to filter applications based on criteria
const filteredApplications = computed(() => {
  return applicationsStore.getAllApplications.filter((app) => {
    const applicationDate = new Date(app.application_date);
    const startDate = filters.value.startDate
      ? new Date(filters.value.startDate)
      : null;
    const endDate = filters.value.endDate
      ? new Date(filters.value.endDate)
      : null;
    const status = filters.value.status;

    // Filter by date range
    if (startDate && applicationDate < startDate) return false;
    if (endDate && applicationDate > endDate) return false;

    // Filter by status
    if (status && app.status !== status) return false;

    return true;
  });
});

// Paginated applications
const paginatedApplications = computed(() => {
  const start = (currentPage.value - 1) * perPage.value;
  const end = start + perPage.value;
  return filteredApplications.value.slice(start, end);
});

const fields = [
  { key: "job_title", label: "Job Title", sortable: true },
  { key: "application_date", label: "Application Date", sortable: true },
  { key: "status", label: "Status", sortable: true },
  { key: "cv_file_url", label: "CV" },
  { key: "actions", label: "Actions" },
];

const deleteApplication = async (applicationId) => {
  console.log("Deleting application with ID:", applicationId);
  if (!applicationId) {
    toast.error("Invalid application ID.");
    return;
  }
  try {
    await applicationsStore.deleteApplication(applicationId);
    applicationsStore.removeApplication(applicationId);

    

    toast.success(`Record with ID ${applicationId} was deleted successfully.`);
  } catch (error) {
    const errorMessage =
      error.response?.data?.message || "Failed to delete the record.";
    toast.error(errorMessage); 
  }
};

onMounted(async () => {
  await applicationsStore.fetchApplications();
});
</script>

  
  
  <style scoped>
  .page-title {
    font-weight: bold;
    color: #198754;
    margin-bottom: 20px;
  }
  .small-button {
  font-size: 10px; 
  padding: 4px 5px; 
}
.custom-search-input {
    border: 1px solid #28a745;
    border-radius: 4px;
  }
  
  </style>
  