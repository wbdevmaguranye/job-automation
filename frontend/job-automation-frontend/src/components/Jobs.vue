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
           :disabled="!isAuthenticated"
           title="Login to enable this filter"
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
          class="toggle-btn small-button"
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
        <div v-if="isAuthenticated">
          <b-badge
            :variant="getSkillMatchBadgeVariant(data.value)"
            class="skill-match-badge"
          >
            {{ data.value || "No Match" }}
          </b-badge>
        </div>
        <div v-else>
          <router-link to="/login" class="text-muted small-text text-success">
    Login to view  
  </router-link>
        </div>
      </template>

      <!-- Job Link -->
      <template #cell(url)="data">
        <a :href="data.value" target="_blank" class="text-success">
          View
        </a>
      </template>

      <!-- CV Actions -->
      <template #cell(actions)="data">
        <b-button
          size="xs"
          variant="primary"
          class="small-button "
          @click="viewCV(data.item.id)"
        >
          View CV
        </b-button>
      </template>

      <!-- Apply for a Job -->
      <template #cell(apply)="data">
        <b-button
          size="sm"
          class="small-button"
          :variant="isJobApplied(data.item.id) ? 'secondary' : 'success'"
          :disabled="isJobApplied(data.item.id)"
          @click="applyForJob(data.item.id)"
        >
          {{ isJobApplied(data.item.id) ? "Applied" : "Apply" }}
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
          <a :href="associatedCV.file_url" target="_blank">{{
            associatedCV.file_url
          }}</a>
        </p>
        <p>
          <strong>Customization Status:</strong>
          {{ associatedCV.customization_status }}
        </p>
        <p><strong>Created At:</strong> {{ associatedCV.created_at }}</p>

        <!-- Buttons Row -->
        <div class="button-row mt-3">
          <b-button size="sm" variant="success" @click="downloadCV">
            Download CV
          </b-button>
          <b-button
            size="sm"
            :variant="collapsedApplyButton ? 'danger' : 'primary'"
            class="ml-2"
            @click="applyCV(associatedCV.file_url, associatedCV.job_id)"
          >
            {{ collapsedApplyButton ? "Undo Apply" : "Apply CV" }}
          </b-button>
        </div>
      </template>
      <p v-else>No CV available for this job.</p>
    </b-modal>
  </b-container>
</template>

<script setup>
import { ref, computed ,watch } from "vue";
import { useToast } from "vue-toastification";
import { useJobsStore } from "@/stores/jobsStore";
import { useCVsStore } from "@/stores/cvsStore";
import { useApplicationsStore } from "@/stores/applicationsStore";
import { useUserStore } from "@/stores/userStore";

// Toast setup
const toast = useToast();

// Table fields for jobs
const fields = [
  { key: "title", label: "Job Title", sortable: true },
  { key: "company", label: "Company", sortable: true },
  { key: "location", label: "Location", sortable: true },
  { key: "skill_match_level", label: "Skill Match", sortable: true },
  { key: "description", label: "Description", sortable: false },
  { key: "url", label: "Link", sortable: false },
  { key: "apply", label: "Apply", sortable: false },
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
const selectedSkillMatchLevel = ref("");
const skillMatchOptions = [
  { value: "", text: "All" },
  { value: "High Match", text: "High Match" },
  { value: "Average Match", text: "Average Match" },
  { value: "Low Match", text: "Low Match" },
  { value: "No Match", text: "No Match" },
];

// Data stores
const userStore = useUserStore();
const isAuthenticated = computed(() => userStore.isAuthenticated);
const jobsStore = useJobsStore();
const cvsStore = useCVsStore();
const applicationsStore = useApplicationsStore();
const applications = ref([]);
const jobs = ref([]);
const cvs = ref([]);
const associatedCV = ref(null);
const showCVModal = ref(false);
const collapsedApplyButton = ref(false);

// Fetch data on load
const fetchData = async () => {
  try {
    await jobsStore.fetchJobs();
    await cvsStore.fetchCVs();
    await applicationsStore.fetchApplications();
    jobs.value = jobsStore.jobs || [];
    cvs.value = cvsStore.cvs || [];
    applications.value = applicationsStore.applications || [];
    collapsedRows.value = Array(jobs.value.length).fill(true);
  } catch (error) {
    toast.error("Failed to fetch data. Please try again later.");
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
      (selectedSkillMatchLevel.value === "" ||
        job.skill_match_level === selectedSkillMatchLevel.value)
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
    toast.warning("No CV available Login for this job.");
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
    toast.error("File URL not available for this CV.");
  }
};

// Apply for a job
const isJobApplied = (jobId) => applicationsStore.isJobApplied(jobId);

const applyForJob = async (jobId) => {
  const cv = cvs.value.find((cv) => cv.job_id === jobId);
  if (!cv) {
    toast.error("No associated CV available Login to apply.");
    return;
  }

  try {
    const response = await applicationsStore.applyForJob(jobId, cv.cv_id);
    if (response.success) {
      toast.success("Job application successful!");
    } else {
      toast.error("Failed to apply for the job.");
    }
  } catch (error) {
    toast.error("An error occurred while applying for the job.");
    console.error("Error applying for the job:", error);
  }
};

// Apply a CV to a job
const applyCV = async (fileUrl, jobId) => {
  const cv = cvs.value.find((cv) => cv.job_id === jobId);

  if (!cv || !fileUrl) {
    toast.error("No CV available Login to apply.");
    return;
  }

  try {
    const response = await applicationsStore.applyForJob(jobId, cv.cv_id);
    if (response.success) {
      toast.success("CV successfully applied!");
    } else {
      toast.error("Failed to apply CV.");
    }
  } catch (error) {
    toast.error("An error occurred while applying the CV.");
    console.error("Error applying CV:", error);
  }
};

const formatDescription = (description) => {
  if (!description) return "N/A";
  return description
    .replace(/(Responsibilities|Requirements|Skills):/gi, "<b>$1:</b>")
    .replace(/\n/g, "<br>");
};

watch(
  () => isAuthenticated.value,
  (newVal, oldVal) => {
    if (!newVal) {
            resetAppliedState();
    }
  }
);
function resetAppliedState() {
    applications.value = []; // Or any logic needed to reflect the change
}
</script>

<style scoped>
.skill-match-badge.bg-success {
  background-color: #0ed862 !important;  /* Custom green */
}
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
.small-button {
  font-size: 10px;
  padding: 4px 5px;
}
.small-text {
  font-size: 0.75rem; 
}
</style>
