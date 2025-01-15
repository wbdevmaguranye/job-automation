<template>
  <b-container>
    <!-- Jobs and CVs Stats -->
    <b-row class="mb-4">
      <b-col>
        <b-card title="" class="text-center text-white bg-success">
          <h4>Jobs: {{ jobs.length }}</h4>
        </b-card>
      </b-col>
      <b-col>
        <b-card title="" class="text-center text-white bg-success">
          <h4>Custom CVs: {{ cvs.length }}</h4>
        </b-card>
      </b-col>
    </b-row>

    <!-- Filters -->
    <b-row class="mb-4">
      <b-col>
        <b-form-input
          v-model="searchTitle"
          placeholder="Search by Title"
          class="mb-3 custom-search-input"
        ></b-form-input>
      </b-col>
      <b-col>
        <b-form-input
          v-model="searchCompany"
          placeholder="Search by Company"
          class="mb-3 custom-search-input"
        ></b-form-input>
      </b-col>
      <b-col>
        <b-form-select
  v-model="selectedSkillMatchLevel"
  :options="skillMatchOptions"
  class="mb-3 custom-select-border"
  placeholder="Filter by Skill Match Level"
></b-form-select>

      </b-col>
    </b-row>

    <!-- Jobs Table -->
    <b-table
      striped
      hover
      bordered
      :items="paginatedJobs"
      :fields="fields"
      responsive="sm"
      class="mb-4 custom-table"
    >
      <!-- Collapsible Description -->
      <template #cell(description)="data">
  <b-button
    size="sm"
    variant="success"
    class="toggle-btn"
    @click="toggleDescription(data.index)"
  >
    {{ collapsedRows[data.index] ? "Show More" : "Show Less" }}
  </b-button>
  <b-collapse :visible="!collapsedRows[data.index]" class="mt-2">
    <div v-html="formatDescription(data.value || 'N/A')"></div>
  </b-collapse>
</template>


      <!-- Skill Match Level -->
      <template #cell(skill_match_level)="data">
        <b-badge
          :variant="getSkillMatchBadgeVariant(data.value)"
          class="skill-match-badge"
        >
          {{ data.value || "No Match" }}
        </b-badge>
      </template>

      <!-- Job Link -->
      <template #cell(url)="data">
        <a :href="data.value" target="_blank" class="text-success font-weight-bold">
          View Job
        </a>
      </template>

      <!-- CV Actions -->
      <template #cell(actions)="data">
        <b-button size="sm" variant="primary" @click="viewCV(data.item.id)">
          View CV
        </b-button>
      </template>
    </b-table>

    <!-- Pagination -->
    <b-pagination
      v-model="currentJobsPage"
      :total-rows="filteredJobs.length"
      :per-page="jobsPerPage"
      class="mt-3"
    ></b-pagination>

    <div v-if="filteredJobs.length === 0">
      <p>No jobs available.</p>
    </div>

    <!-- CV Modal -->
    <b-modal
      id="cv-modal"
      v-model="showCVModal"
      title="Associated CV"
      size="lg"
    >
      <template v-if="associatedCV">
        <p><strong>CV ID:</strong> {{ associatedCV.id }}</p>
        <p>
          <strong>File URL:</strong>
          <a :href="associatedCV.file_url" target="_blank">{{ associatedCV.file_url }}</a>
        </p>
        <p><strong>Customization Status:</strong> {{ associatedCV.customization_status }}</p>
        <p><strong>Created At:</strong> {{ associatedCV.created_at }}</p>

        <!-- Buttons Row -->
        <div class="button-row mt-3">
          <b-button size="sm" variant="success" @click="downloadCV">Download CV</b-button>
          <b-button
            size="sm"
            variant="primary"
            class="ml-2"
            @click="applyCV(associatedCV.file_url, associatedCV.job_id)"
            :disabled="!associatedCV.file_url"
          >
            Apply CV
          </b-button>
        </div>
      </template>
      <p v-else>No CV available for this job.</p>
    </b-modal>
  </b-container>
</template>

<script setup>
import { ref, computed } from "vue";
import { useJobsStore } from "@/stores/jobsStore";
import { useCVsStore } from "@/stores/cvsStore";

// Table fields for jobs
const fields = [
  { key: "title", label: "Job Title", sortable: true },
  { key: "company", label: "Company", sortable: true },
  { key: "location", label: "Location", sortable: true },
  { key: "skill_match_level", label: "Skill Match ", sortable: true },
  { key: "description", label: "Description", sortable: false },
  { key: "url", label: "Link", sortable: false },
  { key: "actions", label: "Actions" },
];

// Collapsed state for job descriptions
const collapsedRows = ref([]);

// Pagination for jobs
const currentJobsPage = ref(1);
const jobsPerPage = 10;

// Search filters
const searchTitle = ref("");
const searchCompany = ref("");
const searchLocation = ref("");
const selectedSkillMatchLevel = ref("");
const skillMatchOptions = [
  { value: "", text: "All" },
  { value: "High Match", text: "High Match" },
  { value: "Average Match", text: "Average Match" },
  { value: "Low Match", text: "Low Match" },
  { value: "No Match", text: "No Match" },
];

// Data stores
const jobsStore = useJobsStore();
const cvsStore = useCVsStore();
const jobs = ref([]);
const cvs = ref([]);
const associatedCV = ref(null);
const showCVModal = ref(false);

// Fetch data on load
const fetchData = async () => {
  try {
    await jobsStore.fetchJobs();
    await cvsStore.fetchCVs();
    jobs.value = jobsStore.jobs || [];
    cvs.value = cvsStore.cvs || [];
    collapsedRows.value = Array(jobs.value.length).fill(true);
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};
fetchData();

// Filtered jobs based on search
const filteredJobs = computed(() =>
  (jobs.value || []).filter(
    (job) =>
      job.title?.toLowerCase().includes(searchTitle.value.toLowerCase()) &&
      job.company?.toLowerCase().includes(searchCompany.value.toLowerCase()) &&
      job.location?.toLowerCase().includes(searchLocation.value.toLowerCase()) &&
      (selectedSkillMatchLevel.value === "" || job.skill_match_level === selectedSkillMatchLevel.value)
  )
);

// Paginated jobs
const paginatedJobs = computed(() =>
  filteredJobs.value.slice(
    (currentJobsPage.value - 1) * jobsPerPage,
    currentJobsPage.value * jobsPerPage
  )
);

// Toggle description visibility
const toggleDescription = (index) => {
  collapsedRows.value[index] = !collapsedRows.value[index];
};

// Get badge variant based on skill match level
const getSkillMatchBadgeVariant = (skillMatchLevel) => {
  switch (skillMatchLevel) {
    case "High Match":
      return "success";
    case "Average Match":
      return "warning";
    case "Low Match":
      return "danger";
    default:
      return "secondary";
  }
};

// View CV
const viewCV = (jobId) => {
  associatedCV.value = cvs.value.find((cv) => cv.job_id === jobId) || null;
  if (associatedCV.value) {
    showCVModal.value = true;
  } else {
    alert("No CV available for this job.");
  }
};

// Download CV
const downloadCV = () => {
  if (associatedCV.value && associatedCV.value.file_url) {
    const a = document.createElement("a");
    a.href = associatedCV.value.file_url;
    a.download = `CV_${associatedCV.value.id}.docx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else {
    alert("File URL not available for this CV.");
  }
};

// Apply CV
const applyCV = (fileUrl, jobId) => {
  if (!fileUrl) {
    alert("No CV to apply.");
    return;
  }

  const job = jobs.value.find((job) => job.id === jobId);
  if (!job || !job.url) {
    alert("No job URL available.");
    return;
  }

  const confirmation = confirm("Are you sure you want to apply to this job?");
  if (confirmation) {
    window.open(job.url, "_blank");
  }
};
const formatDescription = (description) => {
  return description
    .replace(/•/g, '<li>')
    .replace(/\n/g, '<br>') 
    .replace(/([A-Za-z ]+:)/g, '<strong>$1</strong>');
};
</script>

<style scoped>
/* Styling for Dashboard */
h1 {
  color: #28a745;
  font-weight: bold;
}

.custom-table {
  background-color: #f9f9f9;
  border: 1px solid #28a745;
}

.custom-table th {
  background-color: #28a745;
  color: white;
}

.custom-search-input {
  border: 1px solid #28a745;
  border-radius: 4px;
}

.toggle-btn {
  text-transform: uppercase;
  font-size: 0.8rem;
}

.button-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.skill-match-badge {
  font-size: 0.85rem;
}
.custom-select-border {
  border: 1px solid #28a745; 
  border-radius: 4px; 
}
/* Improve readability of formatted job descriptions */
.formatted-description ul {
  margin: 0;
  padding-left: 20px;
}

.formatted-description li {
  margin-bottom: 8px;
}

.formatted-description strong {
  color: #28a745;
}
</style>
