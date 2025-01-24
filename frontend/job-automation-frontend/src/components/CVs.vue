<template>
    <b-container>
      <h1 class="page-title">CVs</h1>
  
      <!-- Filter Section -->
      <b-row class="mb-3">
        <b-col sm="6">
          <b-form-group label="Filter by Job Titile">
            <b-form-input
              v-model="filters.job_title"
              placeholder="Enter job tittle"
                 class="mb-3 custom-search-input"
            ></b-form-input>
          </b-form-group>
        </b-col>
        <b-col sm="6">
          <b-form-group label="Filter by Skill Match">
            <b-form-select
              v-model="filters.skill"
              :options="skillOptions"
              placeholder="Select skill match level"
                class="mb-3 custom-select-border"
            ></b-form-select>
          </b-form-group>
        </b-col>
      </b-row>
  
      <!-- Table -->
      <b-table
        :items="paginatedCVs"
        :fields="fields"
        striped
        hover
        responsive="sm"
        class="custom-table mb-4"
      >
        <!-- Skill Match Level -->
        <template #cell(skill_match_level)="row">
          <span
            :class="{
              'badge badge-high': row.value === 'High',
              'badge badge-average': row.value === 'Average Match',
              'badge badge-low': row.value === 'Low Match',
              'badge badge-no-match': row.value === 'No Match',
            }"
          >
            {{ row.value }}
          </span>
        </template>
        <!-- File URL -->
        <template #cell(file_url)="row">
          <a :href="row.value" target="_blank" class="btn btn-primary btn-sm">
            Download
          </a>
        </template>
      </b-table>
  
      <!-- Pagination -->
      <b-pagination
        v-model="currentPage"
        :total-rows="filteredCVs.length"
        :per-page="pageSize"
        align="center"
        class="mt-3"
      ></b-pagination>
      <!-- <chartjs /> -->
    </b-container>
  </template>
  
  
<script setup>
import { ref, computed, onMounted } from 'vue';
import { useCVsStore } from '@/stores/cvsStore';
// import chartjs from "@/components/chartjs.vue";

const cvsStore = useCVsStore();

onMounted(async () => {
  await cvsStore.fetchCVs();
});

// Filter states
const filters = ref({
  job_title: '',
  skill: '',
});

// Pagination states
const currentPage = ref(1);
const pageSize = ref(10);

// Skill match options for the filter
const skillOptions = [
  { value: 'High', text: 'High' },
  { value: 'Average Match', text: 'Average Match' },
  { value: 'Low Match', text: 'Low Match' },
  { value: 'No Match', text: 'No Match' },
];

// Filtered CVs
const filteredCVs = computed(() => {
  return cvsStore.getAllCVs.filter((cv) => {
    const matchesTitle = !filters.value.job_title || cv.job_title?.toLowerCase().includes(filters.value.job_title.toLowerCase());
    const matchesSkill = !filters.value.skill || cv.skill_match_level === filters.value.skill;
    return matchesTitle && matchesSkill;
  });
});

// Paginated CVs
const paginatedCVs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredCVs.value.slice(start, end);
});

const fields = [
  { key: 'job_title', label: 'Job Title', sortable: true },
//   { key: 'company', label: 'Company', sortable: true },
  { key: 'skill_match_level', label: 'Skill Match', sortable: true },
  { key: 'file_url', label: 'File URL', sortable: false },
  { key: 'created_at', label: 'Created At', sortable: true },
];
</script>

  
  <style scoped>
  .page-title {
    font-weight: bold;
    color: #198754;
    margin-bottom: 20px;
    text-transform: uppercase;
  }
  
  .custom-table {
    border: 1px solid #dee2e6;
    border-radius: 8px;
    background-color: #f8f9fa;
  }
  
  .badge {
    padding: 5px 10px;
    font-size: 0.85rem;
    border-radius: 20px;
    text-transform: capitalize;
  }
  
  .badge-high {
    background-color: #28a745;
    color: #fff;
  }
  
  .badge-average {
    background-color: #ffc107;
    color: #212529;
  }
  
  .badge-low {
    background-color: #dc3545;
    color: #fff;
  }
  
  .badge-no-match {
    background-color: #6c757d;
    color: #fff;
  }
  
  .btn {
    font-size: 0.85rem;
    padding: 5px 10px;
  }
  
  .btn-primary {
    background-color: #007bff;
    border: none;
    color: #fff;
    transition: background-color 0.3s ease;
  }
  
  .btn-primary:hover {
    background-color: #0056b3;
  }
  
  .mb-4 {
    margin-bottom: 1.5rem;
  }
  .custom-search-input {
    border: 1px solid #28a745;
    border-radius: 4px;
  }
 .custom-select-border {
    border: 1px solid #28a745; 
    border-radius: 4px; 
  }
  </style>
  